"""Generate the three lookup CSVs pre-filled with every municipality and zone
code that actually appears in the data, so only the value columns are left to
fill in.

No ratings, minimum lot sizes or cluster flags are invented — those columns are
emitted blank on purpose. A blank is honest; a guessed number would quietly
decide which land you buy.

    py scaffold_lookups.py             # writes data/*.csv (never overwrites)
    py scaffold_lookups.py --force     # rebuild, keeping values already filled
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd

from common import (
    load_config,
    log,
    norm,
    region_for_county,
    resolve_column,
    resolve_path,
)


def _merge_keep_existing(new: pd.DataFrame, path: Path, keys: list[str]) -> pd.DataFrame:
    """Re-scaffold without losing work already done."""
    if not path.exists():
        return new
    old = pd.read_csv(path, dtype=str).fillna("")
    for k in keys:
        old[k] = old[k].str.upper().str.strip()
    merged = new.merge(old, on=keys, how="left", suffixes=("", "_old"))
    for col in [c for c in merged.columns if c.endswith("_old")]:
        base = col[:-4]
        merged[base] = merged[col].where(merged[col].astype(str) != "", merged[base])
        merged = merged.drop(columns=[col])
    return merged


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    parcels_path = resolve_path(cfg, "parcels")
    if not parcels_path.exists():
        raise SystemExit(f"[fatal] {parcels_path} not found — run fetch_data.py first")

    log("reading parcels (municipality + county only) …")
    gdf = gpd.read_file(parcels_path, layer=cfg["paths"].get("parcels_layer"))
    muni_col = resolve_column(gdf, "MUN_NAME", "MUNICIPALITY", "MUN", "PCL_MUN")
    cty_col = resolve_column(gdf, "COUNTY", "COUNTY_NAME", "CTY_NAME")

    munis = (
        pd.DataFrame({
            "municipality": norm(gdf[muni_col]),
            "county": norm(gdf[cty_col]),
        })
        .drop_duplicates()
        .sort_values(["county", "municipality"])
        .reset_index(drop=True)
    )
    munis["region"] = munis.county.map(region_for_county)
    log(f"  {len(munis):,} municipalities")

    # ---- school_ratings.csv ----
    schools = munis.assign(district="", rating="", source="", checked_on="")
    path = resolve_path(cfg, "school_ratings")
    if path.exists() and not args.force:
        log(f"  {path.name} exists — skipping (use --force to refresh)")
    else:
        schools = _merge_keep_existing(schools, path, ["municipality", "county"])
        path.parent.mkdir(parents=True, exist_ok=True)
        schools.to_csv(path, index=False)
        log(f"  wrote {path} — fill in 'rating' (0-10) and 'district'")

    # ---- municipal_flags.csv ----
    flags = munis.assign(allows_cluster="", allows_subdivision="",
                         ag_permitted_generally="", notes="", source="")
    path = resolve_path(cfg, "muni_flags")
    if path.exists() and not args.force:
        log(f"  {path.name} exists — skipping")
    else:
        flags = _merge_keep_existing(flags, path, ["municipality", "county"])
        flags.to_csv(path, index=False)
        log(f"  wrote {path} — fill in 'allows_cluster' (Y/N/UNKNOWN)")

    # ---- zone_rules.csv ----
    zpath = resolve_path(cfg, "zoning")
    if not zpath.exists():
        log(f"  ! zoning layer missing at {zpath} — zone_rules.csv not scaffolded")
        return

    zoning = gpd.read_file(zpath)
    zcol = resolve_column(zoning, "ZONING", "ZONE", "ZONE_CODE", "ZONECODE", "ZONE_ABBR")
    zmuni = resolve_column(zoning, "MUN_NAME", "MUNICIPALITY", "MUN", required=False)

    zones = pd.DataFrame({
        "municipality": norm(zoning[zmuni]) if zmuni else "",
        "zone_code": norm(zoning[zcol]),
    }).drop_duplicates().sort_values(["municipality", "zone_code"]).reset_index(drop=True)

    # Suggest a category from the code itself. This is a STARTING GUESS to be
    # corrected against the ordinance, not an answer.
    def guess(code: str) -> str:
        c = str(code).upper()
        if c.startswith(("C", "B", "HC", "GB", "VB", "VC", "HB")):
            return "C"
        if c.startswith("R") and not c.startswith("RR-CONS"):
            return "R"
        if c.startswith(("A", "AG", "FP", "FPD")):
            return "AG"
        return "OTHER"

    zones["zone_category_guess"] = zones.zone_code.map(guess)
    zones["zone_category"] = ""        # you confirm
    zones["min_lot_acres"] = ""        # from the ordinance bulk table
    zones["ag_permitted"] = ""         # Y/N — Right to Farm Gate 1
    zones["retail_permitted"] = ""     # Y/N/CONDITIONAL
    zones["ordinance_section"] = ""
    zones["checked_on"] = ""

    path = resolve_path(cfg, "zone_rules")
    if path.exists() and not args.force:
        log(f"  {path.name} exists — skipping")
    else:
        zones = _merge_keep_existing(zones, path, ["municipality", "zone_code"])
        zones.to_csv(path, index=False)
        log(f"  wrote {path} — {len(zones):,} zone codes to confirm")

    log("scaffold done. Fill the blank columns before trusting a run.")


if __name__ == "__main__":
    main()
