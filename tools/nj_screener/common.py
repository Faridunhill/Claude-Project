"""Shared helpers for the NJ statewide land screener.

The NJGIN parcel schema changed in the 2026 refresh and county extracts do not
all agree on column names, so nothing here hardcodes a field name. Every column
is resolved by trying a list of candidates, and a miss raises an error that
prints what the file actually contains.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent

# NJ counties grouped for the region preference. Ocean is split in practice;
# it is filed under Central here because its northern half is where the
# buildable land sits.
REGIONS = {
    "North": {
        "BERGEN", "ESSEX", "HUDSON", "MORRIS", "PASSAIC", "SUSSEX",
        "UNION", "WARREN",
    },
    "Central": {
        "HUNTERDON", "MERCER", "MIDDLESEX", "MONMOUTH", "OCEAN", "SOMERSET",
    },
    "South": {
        "ATLANTIC", "BURLINGTON", "CAMDEN", "CAPE MAY", "CUMBERLAND",
        "GLOUCESTER", "SALEM",
    },
}

SQFT_PER_ACRE = 43560.0
FEET_PER_MILE = 5280.0


def load_config(path: str | Path | None = None) -> dict:
    path = Path(path) if path else HERE / "config.yml"
    with open(path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    cfg["_root"] = HERE
    return cfg


def resolve_path(cfg: dict, key: str) -> Path:
    raw = Path(cfg["paths"][key])
    return raw if raw.is_absolute() else cfg["_root"] / raw


def resolve_column(df, *candidates: str, required: bool = True) -> str | None:
    """Return the real column name matching any candidate, case-insensitively."""
    lookup = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        hit = lookup.get(cand.lower().strip())
        if hit:
            return hit
    if not required:
        return None
    raise KeyError(
        f"None of {candidates} found. Available columns:\n  "
        + "\n  ".join(sorted(df.columns))
    )


def region_for_county(county: str) -> str:
    key = str(county or "").upper().strip().replace(" COUNTY", "")
    for region, members in REGIONS.items():
        if key in members:
            return region
    return "Unknown"


def load_lookup(path: Path, key_cols: list[str], label: str) -> pd.DataFrame:
    """Load one of the maintained CSV lookups, failing loudly if it is missing."""
    if not path.exists():
        sys.exit(
            f"[fatal] {label} not found at {path}.\n"
            f"        A seed template ships in data/. Fill it in and re-run."
        )
    df = pd.read_csv(path, dtype=str).fillna("")
    for col in key_cols:
        if col not in df.columns:
            sys.exit(f"[fatal] {label} is missing required column '{col}'.")
        df[col] = df[col].str.upper().str.strip()
    return df


def norm(series) -> pd.Series:
    """Uppercase + strip a text column for joining on names."""
    return series.astype(str).str.upper().str.strip()


def log(msg: str) -> None:
    print(f"[screener] {msg}", flush=True)
