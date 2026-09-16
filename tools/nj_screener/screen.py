"""NJ statewide land screener.

Takes ~1.9M NJ parcels down to a ranked shortlist that satisfies:

  1. district school rating at or above the threshold
  2. statewide, with Central/South preferred (bonus, not a gate, by default)
  3. R or C zoning  (greenhouse is flexible — Track B can be a second parcel)
  4. cluster / subdivision potential preferred

Order matters. Cheap attribute filters run first and remove ~97% of parcels
before any geometry math happens; the expensive overlays only ever see the
survivors.

    py screen.py                     # full run
    py screen.py --county WARREN     # one county, for testing
    py screen.py --limit 5000        # cap input size, for testing
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

from common import (
    FEET_PER_MILE,
    SQFT_PER_ACRE,
    load_config,
    load_lookup,
    log,
    norm,
    region_for_county,
    resolve_column,
    resolve_path,
)

REJECTS: list[dict] = []


def reject(pin, muni, reason) -> None:
    REJECTS.append({"pin": pin, "municipality": muni, "reason": reason})


# ---------------------------------------------------------------- stage 1
def load_parcels(cfg: dict, county: str | None, limit: int | None) -> gpd.GeoDataFrame:
    path = resolve_path(cfg, "parcels")
    if not path.exists():
        sys.exit(f"[fatal] parcels not found at {path}. Run fetch_data.py first.")

    layer = cfg["paths"].get("parcels_layer")
    log(f"reading parcels from {path.name} …")
    gdf = gpd.read_file(path, layer=layer, rows=limit) if limit else \
        gpd.read_file(path, layer=layer)
    log(f"  {len(gdf):,} parcels loaded")

    cols = {
        "pin": resolve_column(gdf, "PAMS_PIN", "GIS_PIN", "PIN", "PCL_PIN"),
        "county": resolve_column(gdf, "COUNTY", "COUNTY_NAME", "CTY_NAME"),
        "muni": resolve_column(gdf, "MUN_NAME", "MUNICIPALITY", "MUN", "PCL_MUN"),
        "prop_class": resolve_column(gdf, "PROP_CLASS", "PROPCLASS", "PROP_USE",
                                     "PROPERTY_CLASS"),
        "acres": resolve_column(gdf, "CALC_ACRE", "ACREAGE", "ACRES", "CALCACRE",
                                required=False),
        "owner": resolve_column(gdf, "OWNER_NAME", "OWNERNAME", "OWNER",
                                required=False),
        "address": resolve_column(gdf, "PROP_LOC", "PROPLOC", "SITE_ADDRESS",
                                  required=False),
        "land_val": resolve_column(gdf, "LAND_VAL", "LANDVALUE", required=False),
        "tax": resolve_column(gdf, "LAST_YR_TX", "LASTYRTAX", "TAXES",
                              required=False),
        "block": resolve_column(gdf, "PCLBLOCK", "BLOCK", required=False),
        "lot": resolve_column(gdf, "PCLLOT", "LOT", required=False),
    }
    gdf.attrs["cols"] = cols

    if county:
        gdf = gdf[norm(gdf[cols["county"]]) == county.upper().strip()]
        log(f"  {len(gdf):,} in {county.upper()}")

    return gdf


def filter_to_listings(gdf: gpd.GeoDataFrame, path: Path) -> gpd.GeoDataFrame:
    """Narrow the parcel set to lots that are actually FOR SALE.

    The whole NJ land market is only ~3,000-4,000 lots (LandWatch 3,742,
    LandSearch 2,721, counted 2026-09-15), so screening the flow is cheap once
    you have the list. This function takes that list however you legitimately
    obtained it — MLS/IDX export, broker spreadsheet, hand-built CSV — and
    matches it onto the parcel polygons.

    The CSV needs either a `pin`/`apn` column (exact match, preferred) or
    `address` + `municipality` (fuzzy, uppercase-normalised).
    """
    c = gdf.attrs["cols"]
    listings = pd.read_csv(path, dtype=str).fillna("")
    log(f"  listings file: {len(listings):,} rows")

    pin_col = next((x for x in ("pin", "apn", "pams_pin", "parcel_id")
                    if x in {k.lower() for k in listings.columns}), None)
    if pin_col:
        real = next(k for k in listings.columns if k.lower() == pin_col)
        wanted = set(norm(listings[real]))
        out = gdf[norm(gdf[c["pin"]]).isin(wanted)]
        log(f"  matched on {real}: {len(out):,} of {len(listings):,} listings")
        return out

    if not c["address"]:
        sys.exit("[fatal] listings CSV has no pin/apn column and parcels have "
                 "no address column to fall back on")

    addr_col = next((k for k in listings.columns
                     if k.lower() in ("address", "prop_loc", "street")), None)
    muni_col = next((k for k in listings.columns
                     if k.lower() in ("municipality", "city", "town", "mun_name")), None)
    if not addr_col:
        sys.exit("[fatal] listings CSV needs 'pin'/'apn' or 'address'")

    key = norm(listings[addr_col])
    if muni_col:
        key = key + "|" + norm(listings[muni_col])
        gkey = norm(gdf[c["address"]]) + "|" + gdf.municipality
    else:
        gkey = norm(gdf[c["address"]])

    out = gdf[gkey.isin(set(key))]
    log(f"  matched on address: {len(out):,} of {len(listings):,} listings")
    if len(out) < len(listings) * 0.5:
        log("  ! low match rate — addresses differ between MLS and MOD-IV. "
            "Add a pin/apn column to the listings CSV for an exact join.")
    return out



def attribute_filter(gdf: gpd.GeoDataFrame, cfg: dict) -> gpd.GeoDataFrame:
    c = gdf.attrs["cols"]
    f = cfg["attribute_filters"]
    start = len(gdf)

    wanted = {str(x).upper().strip() for x in f["property_classes"]}
    klass = norm(gdf[c["prop_class"]])
    dropped = gdf[~klass.isin(wanted)]
    for _, r in dropped.head(0).iterrows():
        pass  # class rejects are bulk noise; counted, not itemised
    gdf = gdf[klass.isin(wanted)]
    log(f"  property class {sorted(wanted)}: {start:,} -> {len(gdf):,}")

    # Acreage: prefer the tax-record acreage, fall back to geometry.
    if c["acres"]:
        acres = pd.to_numeric(gdf[c["acres"]], errors="coerce")
    else:
        acres = pd.Series(math.nan, index=gdf.index)
    need_geom = acres.isna()
    if need_geom.any():
        geom_acres = gdf.geometry.to_crs(cfg["crs"]["working"]).area / SQFT_PER_ACRE
        acres = acres.fillna(geom_acres)
    gdf = gdf.assign(gross_acres=acres)

    before = len(gdf)
    gdf = gdf[(gdf.gross_acres >= f["min_acres"]) & (gdf.gross_acres <= f["max_acres"])]
    log(f"  acreage {f['min_acres']}–{f['max_acres']} ac: {before:,} -> {len(gdf):,}")

    if c["owner"] and f.get("exclude_owner_patterns"):
        pat = "|".join(p.upper() for p in f["exclude_owner_patterns"])
        owner = norm(gdf[c["owner"]])
        before = len(gdf)
        gdf = gdf[~owner.str.contains(pat, regex=True, na=False)]
        log(f"  non-saleable owners removed: {before:,} -> {len(gdf):,}")

    return gdf


# ---------------------------------------------------------------- stage 2
def join_lookups(gdf: gpd.GeoDataFrame, cfg: dict) -> gpd.GeoDataFrame:
    c = gdf.attrs["cols"]
    req = cfg["requirements"]

    gdf = gdf.assign(
        municipality=norm(gdf[c["muni"]]),
        county_name=norm(gdf[c["county"]]),
    )
    gdf["region"] = gdf.county_name.map(region_for_county)

    # --- schools (district-level rating, 0-10) ---
    schools = load_lookup(resolve_path(cfg, "school_ratings"),
                          ["municipality", "county"], "school_ratings.csv")
    schools["rating"] = pd.to_numeric(schools.get("rating"), errors="coerce")
    gdf = gdf.merge(
        schools[["municipality", "county", "district", "rating"]].rename(
            columns={"county": "county_name", "rating": "school_rating"}),
        on=["municipality", "county_name"], how="left",
    )

    missing = gdf.school_rating.isna().sum()
    if missing:
        log(f"  ! {missing:,} parcels have no school rating on file "
            f"({gdf[gdf.school_rating.isna()].municipality.nunique()} municipalities)")

    if req["school_rating_is_hard_filter"]:
        before = len(gdf)
        for _, r in gdf[gdf.school_rating.isna()].iterrows():
            reject(r[c["pin"]], r.municipality, "school rating unknown")
        for _, r in gdf[gdf.school_rating < req["min_school_rating"]].iterrows():
            reject(r[c["pin"]], r.municipality,
                   f"school rating {r.school_rating} < {req['min_school_rating']}")
        gdf = gdf[gdf.school_rating >= req["min_school_rating"]]
        log(f"  school rating >= {req['min_school_rating']}: {before:,} -> {len(gdf):,}")

    # --- region ---
    if req["region_mode"] == "require":
        before = len(gdf)
        keep = gdf.region.isin(req["preferred_regions"])
        for _, r in gdf[~keep].iterrows():
            reject(r[c["pin"]], r.municipality, f"region {r.region} not preferred")
        gdf = gdf[keep]
        log(f"  region in {req['preferred_regions']}: {before:,} -> {len(gdf):,}")

    # --- cluster / subdivision municipal flags ---
    flags = load_lookup(resolve_path(cfg, "muni_flags"),
                        ["municipality", "county"], "municipal_flags.csv")
    gdf = gdf.merge(
        flags[["municipality", "county", "allows_cluster", "notes"]].rename(
            columns={"county": "county_name", "notes": "muni_notes"}),
        on=["municipality", "county_name"], how="left",
    )
    gdf["allows_cluster"] = gdf.allows_cluster.fillna("UNKNOWN")

    return gdf


def attach_zoning(gdf: gpd.GeoDataFrame, cfg: dict) -> gpd.GeoDataFrame:
    """Spatial-join the municipal zoning layer onto parcel centroids."""
    work = cfg["crs"]["working"]
    zpath = resolve_path(cfg, "zoning")
    req = cfg["requirements"]
    c = gdf.attrs["cols"]

    if not zpath.exists():
        log(f"  ! zoning layer missing at {zpath} — zone category set to UNKNOWN")
        gdf["zone_code"] = "UNKNOWN"
    else:
        zoning = gpd.read_file(zpath).to_crs(work)
        zcol = resolve_column(zoning, "ZONING", "ZONE", "ZONE_CODE", "ZONECODE",
                              "ZONE_ABBR")
        pts = gdf.to_crs(work).copy()
        pts["geometry"] = pts.geometry.representative_point()
        joined = gpd.sjoin(pts[["geometry"]], zoning[[zcol, "geometry"]],
                           how="left", predicate="within")
        joined = joined[~joined.index.duplicated(keep="first")]
        gdf["zone_code"] = norm(joined[zcol]).reindex(gdf.index).fillna("UNKNOWN")

    # zone_rules.csv maps a raw zone code to a category (C/R/AG/OTHER) and a
    # minimum lot size in acres — the input to the subdivision estimate.
    rules = load_lookup(resolve_path(cfg, "zone_rules"),
                        ["municipality", "zone_code"], "zone_rules.csv")
    rules["min_lot_acres"] = pd.to_numeric(rules.get("min_lot_acres"), errors="coerce")
    rules["ag_permitted"] = norm(rules.get("ag_permitted", pd.Series(dtype=str)))

    gdf = gdf.merge(
        rules[["municipality", "zone_code", "zone_category", "min_lot_acres",
               "ag_permitted"]],
        on=["municipality", "zone_code"], how="left",
    )
    gdf["zone_category"] = norm(gdf.zone_category.fillna("UNKNOWN"))
    gdf["ag_permitted"] = gdf.ag_permitted.fillna("UNKNOWN")

    if req["require_zoning_match"]:
        wanted = {x.upper() for x in req["zoning_categories_wanted"]}
        before = len(gdf)
        keep = gdf.zone_category.isin(wanted)
        for _, r in gdf[~keep].iterrows():
            reject(r[c["pin"]], r.municipality,
                   f"zone {r.zone_code} category {r.zone_category} not in {sorted(wanted)}")
        gdf = gdf[keep]
        log(f"  zoning category in {sorted(wanted)}: {before:,} -> {len(gdf):,}")

    return gdf


# ---------------------------------------------------------------- stage 3
def _load_overlay(path: Path, work: str, label: str):
    if not path.exists():
        log(f"  ! {label} missing at {path} — that check is SKIPPED, not passed")
        return None
    gdf = gpd.read_file(path).to_crs(work)
    log(f"  {label}: {len(gdf):,} features")
    return gdf


def geometry_screen(gdf: gpd.GeoDataFrame, cfg: dict) -> gpd.GeoDataFrame:
    work = cfg["crs"]["working"]
    hs = cfg["hard_stops"]
    c = gdf.attrs["cols"]
    g = gdf.to_crs(work).copy()
    g["geom_acres"] = g.geometry.area / SQFT_PER_ACRE

    # --- wetlands: real polygon-on-polygon intersection, not a point buffer ---
    wet = _load_overlay(resolve_path(cfg, "wetlands"), work, "wetlands")
    if wet is not None:
        inter = gpd.overlay(g[["geometry"]].reset_index(), wet[["geometry"]],
                            how="intersection", keep_geom_type=False)
        wet_ac = (inter.geometry.area / SQFT_PER_ACRE).groupby(inter["index"]).sum()
        g["wetland_acres"] = wet_ac.reindex(g.index).fillna(0.0)
        g["wetland_pct"] = 100.0 * g.wetland_acres / g.geom_acres.replace(0, math.nan)
        g["wetland_pct"] = g.wetland_pct.fillna(0.0)

        if hs["drop_if_centroid_in_wetland"]:
            cent = g.copy()
            cent["geometry"] = cent.geometry.representative_point()
            hit = gpd.sjoin(cent[["geometry"]], wet[["geometry"]], how="inner",
                            predicate="within").index.unique()
            g["centroid_in_wetland"] = g.index.isin(hit)
        else:
            g["centroid_in_wetland"] = False

        before = len(g)
        bad = (g.wetland_pct > hs["wetland_pct_max"]) | g.centroid_in_wetland
        for _, r in g[bad].iterrows():
            reject(r[c["pin"]], r.municipality,
                   f"wetlands {r.wetland_pct:.1f}%"
                   + (" / centroid inside wetland" if r.centroid_in_wetland else ""))
        g = g[~bad]
        log(f"  wetlands <= {hs['wetland_pct_max']}%: {before:,} -> {len(g):,}")
    else:
        g["wetland_acres"] = math.nan
        g["wetland_pct"] = math.nan
        g["centroid_in_wetland"] = False

    g["net_buildable_acres"] = (g.geom_acres - g.wetland_acres.fillna(0.0)).clip(lower=0)

    # --- groundwater contamination (CEA) ---
    cea = _load_overlay(resolve_path(cfg, "cea"), work, "CEA zones")
    if cea is not None:
        inside = gpd.sjoin(g[["geometry"]], cea[["geometry"]], how="inner",
                           predicate="intersects").index.unique()
        g["in_cea"] = g.index.isin(inside)
        if hs["drop_if_in_cea"]:
            before = len(g)
            for _, r in g[g.in_cea].iterrows():
                reject(r[c["pin"]], r.municipality, "inside CEA contamination zone")
            g = g[~g.in_cea]
            log(f"  CEA clear: {before:,} -> {len(g):,}")
        near = gpd.sjoin_nearest(g[["geometry"]], cea[["geometry"]],
                                 how="left", distance_col="_d")
        near = near[~near.index.duplicated(keep="first")]
        g["cea_miles"] = (near["_d"] / FEET_PER_MILE).reindex(g.index)
        g["cea_proximity_flag"] = g.cea_miles < hs["cea_proximity_flag_miles"]
    else:
        g["in_cea"] = False
        g["cea_miles"] = math.nan
        g["cea_proximity_flag"] = False

    # --- Highlands / Pinelands: track A stops, not all-track stops ---
    g["highlands"] = "NONE"
    hl = _load_overlay(resolve_path(cfg, "highlands"), work, "Highlands")
    if hl is not None:
        col = resolve_column(hl, "AREA", "AREA_TYPE", "DESIGNATION", "REGION",
                             "LABEL", required=False)
        cols = ["geometry"] + ([col] if col else [])
        j = gpd.sjoin(g[["geometry"]], hl[cols], how="left", predicate="intersects")
        j = j[~j.index.duplicated(keep="first")]
        g["highlands"] = norm(j[col]).reindex(g.index).fillna("NONE") if col \
            else j.index.isin(j.dropna().index).astype(str)

    g["pinelands"] = "NONE"
    pl = _load_overlay(resolve_path(cfg, "pinelands"), work, "Pinelands")
    if pl is not None:
        col = resolve_column(pl, "MGMT_AREA", "AREA", "PMA", "LABEL", "DESIGNATION",
                             required=False)
        cols = ["geometry"] + ([col] if col else [])
        j = gpd.sjoin(g[["geometry"]], pl[cols], how="left", predicate="intersects")
        j = j[~j.index.duplicated(keep="first")]
        g["pinelands"] = norm(j[col]).reindex(g.index).fillna("NONE") if col \
            else j.index.isin(j.dropna().index).astype(str)

    # --- FEMA floodway: all-track stop where the layer is available ---
    g["in_floodway"] = False
    fema = _load_overlay(resolve_path(cfg, "fema"), work, "FEMA NFHL")
    if fema is not None:
        zcol = resolve_column(fema, "ZONE_SUBTY", "SFHA_TF", "FLD_ZONE",
                              required=False)
        fw = fema[norm(fema[zcol]).str.contains("FLOODWAY", na=False)] if zcol else fema
        if len(fw):
            hit = gpd.sjoin(g[["geometry"]], fw[["geometry"]], how="inner",
                            predicate="intersects").index.unique()
            g["in_floodway"] = g.index.isin(hit)
            if hs["drop_if_fema_floodway"]:
                before = len(g)
                for _, r in g[g.in_floodway].iterrows():
                    reject(r[c["pin"]], r.municipality, "FEMA floodway")
                g = g[~g.in_floodway]
                log(f"  outside floodway: {before:,} -> {len(g):,}")

    return g


# ---------------------------------------------------------------- stage 4
def evaluate(g: gpd.GeoDataFrame, cfg: dict) -> gpd.GeoDataFrame:
    req = cfg["requirements"]
    hs = cfg["hard_stops"]
    w = cfg["scoring"]["weights"]
    b = cfg["scoring"]["bonuses"]
    c = g.attrs["cols"] if "cols" in g.attrs else {}

    hl_pres = g.highlands.str.contains("PRESERV", na=False)
    pl_stop = g.pinelands.str.contains("FOREST|PRESERV", na=False)

    # Track A — plaza. Needs commercial zoning and no Highlands/Pinelands stop.
    g["track_a"] = (g.zone_category == "C")
    if hs["track_a_drop_highlands_preservation"]:
        g["track_a"] &= ~hl_pres
    if hs["track_a_drop_pinelands_forest_preservation"]:
        g["track_a"] &= ~pl_stop

    # Track B — farm market under the Right to Farm Act.
    # Gate 1: agriculture must be a permitted use in the zone.
    # Gate 2: 5+ acres -> $2,500/yr threshold; under 5 -> $50,000/yr.
    big = g.net_buildable_acres >= hs["track_b_min_acres_for_cheap_threshold"]
    g["track_b_gate1"] = g.ag_permitted.isin(["Y", "YES", "TRUE"])
    g["track_b_threshold"] = pd.Series(
        ["$2,500/yr" if x else "$50,000/yr" for x in big], index=g.index)
    g["track_b"] = g.track_b_gate1 & ~pl_stop
    g.loc[g.ag_permitted == "UNKNOWN", "track_b"] = False
    g["track_b_unverified"] = g.ag_permitted == "UNKNOWN"

    # Subdivision estimate: net buildable acres / zone minimum lot size.
    g["est_lots"] = (g.net_buildable_acres / g.min_lot_acres).apply(
        lambda x: int(x) if pd.notna(x) and x > 0 else pd.NA)
    g["subdividable"] = g.est_lots.apply(
        lambda x: bool(pd.notna(x) and x >= req["min_estimated_lots"]))
    if req["subdivision_mode"] == "require":
        before = len(g)
        for _, r in g[~g.subdividable].iterrows():
            reject(r.get(c.get("pin"), ""), r.municipality,
                   "no subdivision potential at zone minimum lot size")
        g = g[g.subdividable]
        log(f"  subdividable (>= {req['min_estimated_lots']} lots): {before:,} -> {len(g):,}")

    # ---- scoring ----
    def commercial_points(r) -> int:
        if r.track_a:
            return w["commercial_path"]                      # retail by right
        if r.track_b and r.net_buildable_acres >= 5:
            return int(w["commercial_path"] * 0.75)          # farm market, cheap gate
        if r.track_b:
            return int(w["commercial_path"] * 0.45)          # farm market, $50k gate
        if r.track_b_unverified:
            return int(w["commercial_path"] * 0.30)          # needs ordinance read
        return 0

    def env_points(r) -> float:
        pts = w["environmental"]
        if pd.notna(r.wetland_pct):
            pts -= min(r.wetland_pct, 40) / 40 * (w["environmental"] * 0.5)
        if r.cea_proximity_flag:
            pts -= w["environmental"] * 0.25
        if r.highlands != "NONE":
            pts -= w["environmental"] * 0.15
        return max(pts, 0.0)

    def acreage_points(r) -> float:
        # 8-25 net buildable acres is the sweet spot: big enough to subdivide or
        # farm, small enough to carry.
        a = r.net_buildable_acres
        if 8 <= a <= 25:
            return w["acreage_price"]
        if a < 8:
            return w["acreage_price"] * (a / 8)
        return w["acreage_price"] * max(0.5, 25 / a)

    g["score_commercial"] = g.apply(commercial_points, axis=1)
    g["score_environmental"] = g.apply(env_points, axis=1)
    g["score_acreage"] = g.apply(acreage_points, axis=1)
    g["score_schools"] = (g.school_rating.fillna(0) / 10.0) * w["schools"]
    # Location, utilities, privacy and permitting need parcel-level research;
    # they are seeded at half weight and refined by the evaluation skill.
    g["score_location"] = w["location_access"] * 0.5
    g["score_utilities"] = w["utilities"] * 0.5
    g["score_privacy"] = w["privacy_setting"] * 0.5
    g["score_permitting"] = g.apply(
        lambda r: w["permitting_runway"] * (1.0 if r.track_a else 0.6), axis=1)

    g["bonus"] = (
        g.region.isin(req["preferred_regions"]).astype(int) * b["preferred_region"]
        + g.subdividable.astype(int) * b["subdividable"]
        + (norm(g.get("prop_class_norm", pd.Series("", index=g.index))) == "3B")
        .astype(int) * b["farmland_assessed"]
    )
    if g.allows_cluster.isin(["Y", "YES", "TRUE"]).any():
        g["bonus"] += g.allows_cluster.isin(["Y", "YES", "TRUE"]).astype(int) * 2

    g["score"] = (
        g.score_location + g.score_acreage + g.score_commercial
        + g.score_environmental + g.score_utilities + g.score_schools
        + g.score_privacy + g.score_permitting + g.bonus
    ).clip(upper=100).round(1)

    g["verdict"] = g.apply(
        lambda r: "TRACK A + B" if r.track_a and r.track_b
        else "TRACK A (plaza)" if r.track_a
        else "TRACK B (farm market)" if r.track_b
        else "TRACK B — verify ag permitted" if r.track_b_unverified
        else "LIFESTYLE ONLY", axis=1)

    return g.sort_values("score", ascending=False)


# ---------------------------------------------------------------- output
def write_outputs(g: gpd.GeoDataFrame, cfg: dict) -> Path:
    out_dir = cfg["_root"] / cfg["output"]["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    thresh = cfg["scoring"]["report_threshold"]

    keep = g[g.score >= thresh].copy()
    log(f"  {len(keep):,} parcels score >= {thresh}")

    cols = [c for c in [
        "pin", "municipality", "county_name", "region", "address", "zone_code",
        "zone_category", "ag_permitted", "gross_acres", "geom_acres",
        "wetland_acres", "wetland_pct", "net_buildable_acres", "highlands",
        "pinelands", "cea_miles", "cea_proximity_flag", "school_rating",
        "district", "allows_cluster", "min_lot_acres", "est_lots", "subdividable",
        "track_a", "track_b", "track_b_threshold", "verdict", "score",
    ] if c in keep.columns]

    out = keep.to_crs(cfg["crs"]["output"])
    pd.DataFrame(out[cols]).to_csv(out_dir / cfg["output"]["csv"], index=False)
    out[cols + ["geometry"]].to_file(out_dir / cfg["output"]["geojson"],
                                     driver="GeoJSON")
    if REJECTS:
        pd.DataFrame(REJECTS).to_csv(out_dir / cfg["output"]["rejects"], index=False)

    log(f"  wrote {out_dir / cfg['output']['csv']}")
    log(f"  wrote {out_dir / cfg['output']['geojson']}")
    return out_dir / cfg["output"]["geojson"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    ap.add_argument("--county", default=None, help="restrict to one county")
    ap.add_argument("--limit", type=int, default=None, help="cap parcels read")
    ap.add_argument("--listings", metavar="CSV", default=None,
                    help="screen only lots in this for-sale list "
                         "(pin/apn column, or address + municipality)")
    ap.add_argument("--no-map", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args.config)

    log("STAGE 1 — attribute filters")
    gdf = load_parcels(cfg, args.county, args.limit)
    cols = gdf.attrs["cols"]
    if args.listings:
        log("  restricting to for-sale listings")
        gdf = filter_to_listings(gdf, Path(args.listings))
        gdf.attrs["cols"] = cols
        if gdf.empty:
            sys.exit("[fatal] no listings matched any parcel")
    gdf = attribute_filter(gdf, cfg)
    gdf["prop_class_norm"] = norm(gdf[cols["prop_class"]])
    gdf["pin"] = gdf[cols["pin"]]
    if cols["address"]:
        gdf["address"] = gdf[cols["address"]]
    gdf.attrs["cols"] = cols

    if gdf.empty:
        sys.exit("[fatal] nothing survived stage 1 — check property class codes")

    log("STAGE 2 — lookups and zoning")
    gdf = join_lookups(gdf, cfg)
    gdf.attrs["cols"] = cols
    gdf = attach_zoning(gdf, cfg)
    gdf.attrs["cols"] = cols

    if gdf.empty:
        sys.exit("[fatal] nothing survived stage 2 — loosen schools or zoning filters")

    log("STAGE 3 — geometry and regulatory screen")
    g = geometry_screen(gdf, cfg)
    g.attrs["cols"] = cols

    log("STAGE 4 — tracks and scoring")
    g = evaluate(g, cfg)

    geojson = write_outputs(g, cfg)

    if not args.no_map:
        from make_map import build_map
        build_map(geojson, cfg)

    log("done.")


if __name__ == "__main__":
    main()
