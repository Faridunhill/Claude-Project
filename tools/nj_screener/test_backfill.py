"""Self-test for backfill_known_parcels.py against a mock farid_os.db.

The real schema is on Farid's PC and was never read here, so the backfill maps
fields onto whatever columns exist. This test proves that mapping works against
two deliberately different schemas — one using the names the evaluation skill
uses, one using shorter names — so a surprise on the real database degrades to
"column left NULL" rather than a crash or a silent wrong write.

    py test_backfill.py
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

SCHEMA_VERBOSE = """
CREATE TABLE farmland_parcels (
  id INTEGER PRIMARY KEY,
  pin TEXT UNIQUE NOT NULL,
  address TEXT, municipality TEXT, county TEXT, zoning TEXT,
  gross_acres REAL, listed_acres REAL, wetland_acres REAL, wetland_pct REAL,
  net_buildable_acres REAL, asking_price REAL, price_per_gross_acre REAL,
  tax_class TEXT, last_year_tax REAL, net_assessed_value REAL,
  score REAL, commercial_status TEXT, reason TEXT, open_items TEXT,
  cea_status TEXT, contact TEXT, geometry_source TEXT,
  evaluated_at TEXT, archived INTEGER DEFAULT 0
);
CREATE TABLE parcel_outcomes (
  id INTEGER PRIMARY KEY,
  pin TEXT UNIQUE NOT NULL,
  decision TEXT CHECK(decision IN ('BUY','PASS','PENDING','HOLD','WATCH')),
  reason TEXT,
  FOREIGN KEY(pin) REFERENCES farmland_parcels(pin)
    ON UPDATE CASCADE ON DELETE RESTRICT
);
"""

SCHEMA_TERSE = """
CREATE TABLE farmland_parcels (
  id INTEGER PRIMARY KEY,
  parcel_id TEXT UNIQUE NOT NULL,
  location TEXT, town TEXT, county_name TEXT, zone TEXT,
  acreage REAL, net_acres REAL, price REAL, composite_score REAL,
  verdict TEXT, notes TEXT, updated_at TEXT
);
CREATE TABLE parcel_outcomes (
  id INTEGER PRIMARY KEY,
  parcel_id TEXT UNIQUE NOT NULL,
  disposition TEXT,
  rationale TEXT
);
"""


def make_db(path: Path, schema: str) -> None:
    con = sqlite3.connect(path)
    con.executescript(schema)
    con.commit()
    con.close()


def run(db: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HERE / "backfill_known_parcels.py"), "--db", str(db), *extra],
        capture_output=True, text=True, cwd=HERE,
    )


def check(label: str, condition: bool, detail: str = "") -> bool:
    print(f"  {'PASS' if condition else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    return condition


def main() -> int:
    seed = json.loads((HERE / "seed" / "known_parcels.json").read_text(encoding="utf-8"))
    expected = sum(1 for p in seed["parcels"] if p.get("pin"))
    total = len(seed["parcels"])
    ok = True

    print(f"seed: {total} parcels, {expected} with a PIN "
          f"({total - expected} have no PIN and must be skipped, not faked)")

    with tempfile.TemporaryDirectory() as tmp:
        for label, schema in (("verbose schema", SCHEMA_VERBOSE),
                              ("terse schema", SCHEMA_TERSE)):
            print(f"\n=== {label} ===")
            db = Path(tmp) / f"{label.replace(' ', '_')}.db"
            make_db(db, schema)

            r = run(db, "--inspect")
            ok &= check("--inspect runs", r.returncode == 0, r.stderr.strip()[:200])
            ok &= check("--inspect reports 0 rows", "holds 0 rows" in r.stdout)

            r = run(db, "--dry-run")
            ok &= check("--dry-run runs", r.returncode == 0, r.stderr.strip()[:200])
            con = sqlite3.connect(db)
            rows = con.execute("SELECT COUNT(*) FROM farmland_parcels").fetchone()[0]
            con.close()
            ok &= check("--dry-run writes nothing", rows == 0, f"found {rows} rows")

            r = run(db)
            ok &= check("write runs", r.returncode == 0, r.stderr.strip()[:300])

            con = sqlite3.connect(db)
            n_p = con.execute("SELECT COUNT(*) FROM farmland_parcels").fetchone()[0]
            n_o = con.execute("SELECT COUNT(*) FROM parcel_outcomes").fetchone()[0]
            ok &= check(f"{expected} parcels written", n_p == expected, f"got {n_p}")
            ok &= check(f"{expected} outcomes written", n_o == expected, f"got {n_o}")

            key = "pin" if label.startswith("verbose") else "parcel_id"
            score = "score" if label.startswith("verbose") else "composite_score"
            top = con.execute(
                f"SELECT {key}, {score} FROM farmland_parcels "
                f"WHERE {score} IS NOT NULL ORDER BY {score} DESC LIMIT 1").fetchone()
            ok &= check("highest score is 28 W Springtown at 93",
                        top is not None and top[0] == "1438_32_2.01" and top[1] == 93,
                        str(top))

            halfway = con.execute(
                f"SELECT {score} FROM farmland_parcels WHERE {key} = ?",
                ("2105_18_1_Q0059",)).fetchone()
            ok &= check("Half Way House scored 72", halfway and halfway[0] == 72,
                        str(halfway))

            # Values that were never measured must stay NULL, never become 0.
            if label.startswith("verbose"):
                nulls = con.execute(
                    "SELECT COUNT(*) FROM farmland_parcels "
                    "WHERE geometry_source = 'skill file only' "
                    "AND gross_acres IS NOT NULL").fetchone()[0]
                ok &= check("unmeasured acreage stays NULL", nulls == 0,
                            f"{nulls} rows got a number they never had")

            # Re-running must update in place, not duplicate.
            run(db)
            con2 = sqlite3.connect(db)
            again = con2.execute("SELECT COUNT(*) FROM farmland_parcels").fetchone()[0]
            con2.close()
            ok &= check("re-run is idempotent", again == expected, f"got {again}")
            con.close()

    print("\n" + ("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
