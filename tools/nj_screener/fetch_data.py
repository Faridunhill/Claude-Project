"""Download the statewide layers the screener needs.

Run once, then re-run whenever NJGIN publishes a refresh. Everything here is
free and public. The two layers already on the PC (NJDEP wetlands 2020, NJ
groundwater CEA) are not re-downloaded — copy them into data/ yourself.

    py fetch_data.py                 # everything missing
    py fetch_data.py --only parcels  # just one layer
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

from common import HERE, log

# ArcGIS FeatureServer query endpoints. NJGIN republishes these periodically;
# if one 404s, open the NJGIN Open Data portal, find the layer, and paste its
# FeatureServer URL here.
SOURCES = {
    "parcels": {
        "desc": "NJ MOD-IV parcels — all property classes",
        "portal": "https://njogis-newjersey.opendata.arcgis.com/",
        # This service is ALREADY CONNECTED on the PC — the farm-class pull
        # (3A + 3B, 32,257 rows) came from here. What has never been pulled is
        # everything else: class 1 vacant, 2 residential, 4A commercial. Those
        # are what make "R zoning that accepts commercial" answerable statewide.
        "url": "https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/NJ_MOD4_Parcels/FeatureServer/0",
        "where_field": "PROP_CLASS",
        "note": (
            "~1.9M polygons statewide. Pull by property class so each request "
            "set stays manageable; --classes controls which. The bulk county "
            "downloads + --merge-counties are the faster route for a full set."
        ),
        "out": "data/nj_parcels_modiv.gpkg",
    },
    "zoning": {
        "desc": "Municipal Zoning (NJDCA)",
        "url": "https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/Municipal_Zoning/FeatureServer/0",
        "out": "data/municipal_zoning.gpkg",
    },
    "highlands": {
        "desc": "Highlands Preservation / Planning Area boundary",
        "portal": "https://www.highlands.state.nj.us/njhighlands/maps/",
        "url": "https://mapsdep.nj.gov/arcgis/rest/services/Features/Land_use/MapServer/12",
        "out": "data/highlands.gpkg",
    },
    "pinelands": {
        "desc": "Pinelands management areas",
        "url": "https://mapsdep.nj.gov/arcgis/rest/services/Features/Land_use/MapServer/9",
        "out": "data/pinelands.gpkg",
    },
}


def fetch_featureserver(url: str, out: Path, page: int = 1000,
                        where: str = "1=1") -> None:
    import geopandas as gpd
    import pandas as pd

    frames, offset = [], 0
    while True:
        params = {
            "where": where,
            "outFields": "*",
            "outSR": "4326",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page,
        }
        resp = requests.get(f"{url}/query", params=params, timeout=180)
        resp.raise_for_status()
        payload = resp.json()
        feats = payload.get("features", [])
        if not feats:
            break
        frames.append(gpd.GeoDataFrame.from_features(feats, crs="EPSG:4326"))
        offset += len(feats)
        log(f"  … {offset} features")
        if len(feats) < page:
            break

    if not frames:
        raise RuntimeError(f"no features returned from {url}")

    gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:4326")
    out.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out, driver="GPKG")
    log(f"  wrote {len(gdf):,} features -> {out}")


def merge_counties(folder: Path, out: Path) -> None:
    """Merge per-county parcel downloads (shp or gdb) into one GeoPackage."""
    import geopandas as gpd
    import pandas as pd

    parts = sorted(
        [p for p in folder.iterdir() if p.suffix.lower() in {".shp", ".gdb", ".gpkg"}]
    )
    if not parts:
        sys.exit(f"[fatal] no .shp/.gdb/.gpkg found in {folder}")

    frames = []
    for part in parts:
        log(f"reading {part.name}")
        gdf = gpd.read_file(part)
        gdf["SRC_FILE"] = part.name
        frames.append(gdf)

    merged = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=frames[0].crs)
    out.parent.mkdir(parents=True, exist_ok=True)
    merged.to_file(out, layer="parcels", driver="GPKG")
    log(f"merged {len(merged):,} parcels from {len(parts)} files -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="fetch a single layer by key")
    ap.add_argument("--classes", default=None,
                    help="parcels only: MOD-IV classes to pull, e.g. 1,2,3A,3B,4A")
    ap.add_argument("--merge-counties", metavar="FOLDER",
                    help="merge per-county parcel downloads into one GeoPackage")
    args = ap.parse_args()

    if args.merge_counties:
        merge_counties(Path(args.merge_counties), HERE / SOURCES["parcels"]["out"])
        return

    keys = [args.only] if args.only else list(SOURCES)
    for key in keys:
        spec = SOURCES.get(key)
        if not spec:
            sys.exit(f"[fatal] unknown layer '{key}'. Known: {', '.join(SOURCES)}")

        out = HERE / spec["out"]
        if out.exists():
            log(f"{key}: already present at {out} — skipping")
            continue

        log(f"{key}: {spec['desc']}")
        if spec.get("note"):
            log(f"  {spec['note']}")

        where = "1=1"
        if key == "parcels" and args.classes:
            wanted = [c.strip().upper() for c in args.classes.split(",")]
            quoted = ",".join(f"'{c}'" for c in wanted)
            where = f"{spec['where_field']} IN ({quoted})"
            log(f"  where: {where}")

        fetch_featureserver(spec["url"], out, where=where)

    log("done. Copy Wetlands_(2020).shp and NJ_Groundwater_CEA.geojson into data/ by hand.")


if __name__ == "__main__":
    main()
