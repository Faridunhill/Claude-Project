"""Write the 18 known parcels into farid_os.db.

`farmland_parcels` and `parcel_outcomes` were created in June 2026 and have
never held a row (measured 2026-09-15). Until they do, nothing about this
pipeline is proven end to end. This script fills them from the parcels Farid
actually chose and evaluated.

It does NOT assume a schema. Real column names are read with PRAGMA
table_info and the seed fields are mapped onto whatever is there; anything
unmatched is reported, not silently dropped. Nothing is invented — the seven
parcels that were never GIS-measured go in with NULL geometry fields and a
`geometry_source` of "skill file only".

    py backfill_known_parcels.py --inspect      # print the live schema only
    py backfill_known_parcels.py --dry-run      # show the plan, touch nothing
    py backfill_known_parcels.py                # write
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DB = Path(r"C:\Users\hadid\FaridOS\data\farid_os.db")
SEED = HERE / "seed" / "known_parcels.json"

# Seed field -> candidate column names, in preference order. The first name
# that exists in the live table wins.
FIELD_MAP = {
    "pin":                  ["pin", "pams_pin", "parcel_pin", "apn", "parcel_id"],
    "address":              ["address", "prop_loc", "street_address", "location"],
    "municipality":         ["municipality", "mun_name", "town", "muni"],
    "county":               ["county", "county_name"],
    "zoning":               ["zoning", "zone", "zone_code", "zoning_district"],
    "gross_acres_gdb":      ["gross_acres", "acres", "acreage", "gross_acreage"],
    "listed_acres":         ["listed_acres", "listing_acres"],
    "wetland_acres":        ["wetland_acres", "wetlands_acres"],
    "wetland_pct":          ["wetland_pct", "wetland_percent", "wetlands_pct"],
    "net_buildable_acres":  ["net_buildable_acres", "net_acres", "buildable_acres"],
    "asking_price":         ["asking_price", "price", "list_price"],
    "price_per_gross_acre": ["price_per_gross_acre", "ppa_gross", "price_per_acre"],
    "price_per_net_acre":   ["price_per_net_acre", "ppa_net"],
    "tax_class":            ["tax_class", "prop_class", "property_class"],
    "last_year_tax":        ["last_year_tax", "annual_tax", "taxes"],
    "net_assessed_value":   ["net_assessed_value", "assessed_value", "net_value"],
    "score":                ["score", "composite_score", "suitability_score"],
    "commercial_status":    ["commercial_status", "commercial_track", "verdict"],
    "reason":               ["reason", "notes", "summary", "rationale"],
    "open_items":           ["open_items", "outstanding", "pending_items", "next_steps"],
    "cea_status":           ["cea_status", "contamination_status"],
    "contact":              ["contact", "contacts", "municipal_contact"],
    "geometry_source":      ["geometry_source", "data_source", "source"],
}

OUTCOME_MAP = {
    "pin":      ["pin", "pams_pin", "parcel_pin", "parcel_id"],
    "decision": ["decision", "disposition", "outcome"],
    "reason":   ["reason", "notes", "rationale"],
}


def table_columns(con: sqlite3.Connection, table: str) -> dict[str, dict]:
    rows = con.execute(f"PRAGMA table_info({table})").fetchall()
    if not rows:
        sys.exit(f"[fatal] table '{table}' does not exist in this database")
    return {r[1].lower(): {"name": r[1], "type": r[2], "notnull": r[3], "pk": r[5]}
            for r in rows}


def build_mapping(cols: dict, field_map: dict) -> tuple[dict, list, list]:
    """Return (seed_field -> real column), unmatched seed fields, unused columns."""
    mapping, unmatched = {}, []
    for field, candidates in field_map.items():
        hit = next((cols[c]["name"] for c in candidates if c in cols), None)
        if hit:
            mapping[field] = hit
        else:
            unmatched.append(field)
    used = {v.lower() for v in mapping.values()}
    unused = [c["name"] for k, c in cols.items() if k not in used and not c["pk"]]
    return mapping, unmatched, unused


def report_mapping(label: str, mapping: dict, unmatched: list, unused: list) -> None:
    print(f"\n--- {label} ---")
    for field, col in mapping.items():
        print(f"  {field:22s} -> {col}")
    if unmatched:
        print(f"  ! seed fields with no column (NOT written): {', '.join(unmatched)}")
    if unused:
        print(f"  ! table columns left NULL: {', '.join(unused)}")


def upsert(con, table, mapping, rows, key_field, stamp_col=None, dry=False) -> int:
    key_col = mapping.get(key_field)
    if not key_col:
        sys.exit(f"[fatal] cannot identify a key column for {table}")

    written, skipped = 0, []
    for row in rows:
        if row.get(key_field) in (None, ""):
            skipped.append(row)
            continue

        data = {mapping[f]: row.get(f) for f in mapping if f in row}
        if stamp_col:
            data[stamp_col] = datetime.now(timezone.utc).isoformat(timespec="seconds")

        cols = ", ".join(data)
        marks = ", ".join("?" * len(data))
        updates = ", ".join(f"{c}=excluded.{c}" for c in data if c != key_col)
        sql = (f"INSERT INTO {table} ({cols}) VALUES ({marks}) "
               f"ON CONFLICT({key_col}) DO UPDATE SET {updates}")

        if dry:
            print(f"  would write {row.get('address')} ({row[key_field]})")
        else:
            try:
                con.execute(sql, list(data.values()))
            except sqlite3.OperationalError as exc:
                # No unique constraint on the key: fall back to replace-in-place.
                if "conflict" in str(exc).lower() or "unique" in str(exc).lower():
                    con.execute(f"DELETE FROM {table} WHERE {key_col} = ?",
                                (row[key_field],))
                    con.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})",
                                list(data.values()))
                else:
                    raise
        written += 1
    return written, skipped


def write_pin_worklist(skipped: list[dict], out_dir: Path) -> Path | None:
    """Seven parcels carry a disposition but no PIN, so they cannot be keyed.

    They are not dropped quietly and they are not given a fake key. They go
    into a worklist with everything needed to look the PIN up in MOD-IV.
    """
    if not skipped:
        return None
    import csv

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "parcels_needing_pin.csv"
    fields = ["address", "municipality", "county", "decision", "reason",
              "geometry_source", "pams_pin_TO_FILL", "block_TO_FILL", "lot_TO_FILL"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in skipped:
            w.writerow({k: row.get(k, "") for k in fields})
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--seed", default=str(SEED))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--inspect", action="store_true", help="print schema and exit")
    args = ap.parse_args()

    db = Path(args.db)
    if not db.exists():
        sys.exit(f"[fatal] database not found at {db}\n"
                 f"        pass --db if it lives elsewhere")

    payload = json.loads(Path(args.seed).read_text(encoding="utf-8"))
    parcels = payload["parcels"]
    measured = sum(1 for p in parcels if p["geometry_source"] == "dashboard")
    print(f"seed: {len(parcels)} parcels "
          f"({measured} GIS-measured, {len(parcels) - measured} disposition only)")
    print(f"as of: {payload['_meta']['as_of']}")

    con = sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys = ON")   # required for the parcel_outcomes FK

    pcols = table_columns(con, "farmland_parcels")
    ocols = table_columns(con, "parcel_outcomes")

    if args.inspect:
        for name, cols in (("farmland_parcels", pcols), ("parcel_outcomes", ocols)):
            print(f"\n--- {name} ---")
            for c in cols.values():
                flags = " PK" if c["pk"] else (" NOT NULL" if c["notnull"] else "")
                print(f"  {c['name']:28s} {c['type']}{flags}")
        held = con.execute("SELECT COUNT(*) FROM farmland_parcels").fetchone()[0]
        con.close()
        print(f"\nfarmland_parcels currently holds {held} rows")
        return

    pmap, punmatched, punused = build_mapping(pcols, FIELD_MAP)
    omap, ounmatched, ounused = build_mapping(ocols, OUTCOME_MAP)
    report_mapping("farmland_parcels", pmap, punmatched, punused)
    report_mapping("parcel_outcomes", omap, ounmatched, ounused)

    stamp = next((pcols[c]["name"] for c in
                  ("evaluated_at", "updated_at", "created_at", "last_updated")
                  if c in pcols), None)

    print(f"\n{'DRY RUN — nothing will be written' if args.dry_run else 'WRITING'}\n")
    n_p, skipped = upsert(con, "farmland_parcels", pmap, parcels, "pin", stamp,
                          args.dry_run)
    n_o, _ = upsert(con, "parcel_outcomes", omap, parcels, "pin", None, args.dry_run)

    worklist = write_pin_worklist(skipped, HERE / "out")
    if skipped:
        print(f"\n{len(skipped)} parcels have NO PIN and were not written:")
        for row in skipped:
            print(f"    {row['address']}, {row['municipality']} — {row['reason'][:60]}")
        print(f"  -> worklist written to {worklist}")
        print("     Look each PIN up in MOD-IV, fill the *_TO_FILL columns, paste them")
        print("     back into seed/known_parcels.json, and re-run.")

    if args.dry_run:
        con.close()
        print(f"\nwould write {n_p} parcels, {n_o} outcomes. Re-run without --dry-run.")
        return

    con.commit()
    total = con.execute("SELECT COUNT(*) FROM farmland_parcels").fetchone()[0]
    con.close()
    print(f"\nwrote {n_p} parcels and {n_o} outcomes.")
    print(f"farmland_parcels now holds {total} rows (was 0).")
    print(f"That is {n_p} of the {len(parcels)} written-down parcels. The remaining "
          f"{len(skipped)} need a PIN first.")
    print("\nNOTE: prices and listing status are from June 2026 and are NOT current.")


if __name__ == "__main__":
    main()
