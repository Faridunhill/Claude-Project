"""Turn listings into screener input.

The bridge between "what is for sale" and "what is worth buying". Feed it
anything a listing site or a broker gives you — a saved-search alert email, a
CSV export, a block of text pasted out of a results page — and it writes the
normalised CSV that `screen.py --listings` expects.

It parses text you already have. It does not fetch anything and it does not
scrape.

    py intake_listings.py alerts.txt                 # an email or pasted text
    py intake_listings.py export.csv                 # a broker/MLS export
    py intake_listings.py a.txt b.txt --out lots.csv # several, merged
    py intake_listings.py --paste                    # type/paste, end with Ctrl-Z

Then:
    py screen.py --listings out/lots.csv
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_COLS = ["pin", "address", "municipality", "county", "acres", "price",
            "price_per_acre", "url", "source", "raw"]

NJ_COUNTIES = {
    "ATLANTIC", "BERGEN", "BURLINGTON", "CAMDEN", "CAPE MAY", "CUMBERLAND",
    "ESSEX", "GLOUCESTER", "HUDSON", "HUNTERDON", "MERCER", "MIDDLESEX",
    "MONMOUTH", "MORRIS", "OCEAN", "PASSAIC", "SALEM", "SOMERSET", "SUSSEX",
    "UNION", "WARREN",
}

# A listing line usually carries acreage and a price somewhere in it.
RE_ACRES = re.compile(r"(\d[\d,]*\.?\d*)\s*(?:\+/-\s*)?(?:acres?|ac\b)", re.I)
RE_PRICE = re.compile(r"\$\s?([\d,]+(?:\.\d{2})?)")
RE_URL = re.compile(r"https?://[^\s<>\"')]+")
RE_MLS = re.compile(r"\b(?:MLS\s*#?\s*)([A-Z]{2,4}\d{5,})\b", re.I)
RE_PIN = re.compile(r"\b(\d{4}_[\d.]+_[\d.]+(?:_[A-Z0-9]+)?)\b")
# "123 Some Road, Township, NJ 08501" or "Route 524, Allentown, NJ"
RE_ADDR = re.compile(
    r"([0-9]*\s*[A-Z][A-Za-z0-9.\- ]{2,40}(?:Rd|Road|Ln|Lane|Dr|Drive|St|Street|Ave|"
    r"Avenue|Ct|Court|Way|Hwy|Highway|Route|Rt|Pike|Trail|Blvd|Terrace|Place|Pl)\.?)"
    r"\s*,?\s*([A-Z][A-Za-z .\-]{2,30})?,?\s*NJ", re.I)


def num(text: str | None) -> float | None:
    if not text:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def parse_line(line: str, source: str) -> dict | None:
    """Pull a listing out of one line of free text. Returns None if it isn't one."""
    line = line.strip()
    if len(line) < 12:
        return None

    acres = num(m.group(1)) if (m := RE_ACRES.search(line)) else None
    price = num(m.group(1)) if (m := RE_PRICE.search(line)) else None

    # A line with neither acreage nor price is prose, not a listing.
    if acres is None and price is None:
        return None
    # Guard against a stray "$" in a footer picking up a nonsense row.
    if acres is None and (price is None or price < 5000):
        return None

    url = m.group(0) if (m := RE_URL.search(line)) else ""
    mls = m.group(1).upper() if (m := RE_MLS.search(line)) else ""
    pin = m.group(1) if (m := RE_PIN.search(line)) else mls

    # Match the address only after the acreage phrase is removed, or the
    # acreage digits get eaten as a house number ("42.37 acres at Sturbridge
    # Ct" became "37 acres at Sturbridge Ct").
    stripped = RE_ACRES.sub(" ", line)
    address, muni = "", ""
    if m := RE_ADDR.search(stripped):
        address = " ".join(m.group(1).split())
        # "42.37 acres at Sturbridge Ct" leaves a dangling connector word.
        address = re.sub(r"^(?:at|on|in|near)\s+", "", address, flags=re.I)
        muni = (m.group(2) or "").strip().upper()

    # A header like "saved search — NJ Land 3-60 acres" has an acreage and
    # nothing else. A real listing always carries at least one way to find it.
    if not (address or url or pin or price):
        return None

    county = next((c for c in NJ_COUNTIES if c in line.upper()), "")

    return {
        "pin": pin,
        "address": address,
        "municipality": muni,
        "county": county,
        "acres": acres if acres is not None else "",
        "price": price if price is not None else "",
        "price_per_acre": round(price / acres) if (price and acres) else "",
        "url": url,
        "source": source,
        "raw": line[:300],
    }


def from_csv(path: Path) -> list[dict]:
    """A broker or MLS export — map its columns onto ours by name."""
    rows: list[dict] = []
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            return rows
        lower = {c.lower().strip(): c for c in reader.fieldnames}

        def pick(*names):
            return next((lower[n] for n in names if n in lower), None)

        c_pin = pick("pin", "apn", "parcel_id", "pams_pin", "mls", "mls#", "mls number")
        c_addr = pick("address", "street", "property address", "location", "prop_loc")
        c_muni = pick("municipality", "city", "town", "mun_name")
        c_cty = pick("county", "county_name")
        c_ac = pick("acres", "acreage", "lot size acres", "lot_acres")
        c_pr = pick("price", "list price", "asking", "list_price")
        c_url = pick("url", "link", "listing url")

        for r in reader:
            acres = num(r.get(c_ac, "")) if c_ac else None
            price = num(re.sub(r"[^\d.]", "", r.get(c_pr, "") or "")) if c_pr else None
            rows.append({
                "pin": (r.get(c_pin) or "").strip() if c_pin else "",
                "address": (r.get(c_addr) or "").strip() if c_addr else "",
                "municipality": (r.get(c_muni) or "").strip().upper() if c_muni else "",
                "county": (r.get(c_cty) or "").strip().upper() if c_cty else "",
                "acres": acres if acres is not None else "",
                "price": price if price is not None else "",
                "price_per_acre": round(price / acres) if (price and acres) else "",
                "url": (r.get(c_url) or "").strip() if c_url else "",
                "source": path.name,
                "raw": "",
            })
    return rows


def from_text(text: str, source: str) -> list[dict]:
    seen, rows = set(), []
    for line in text.splitlines():
        row = parse_line(line, source)
        if not row:
            continue
        key = (row["pin"], row["address"], row["acres"], row["price"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help=".txt / .csv / email body")
    ap.add_argument("--paste", action="store_true", help="read from stdin")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows: list[dict] = []
    if args.paste or not args.files:
        print("Paste listings, then Ctrl-Z + Enter (Windows) or Ctrl-D (Mac/Linux):",
              file=sys.stderr)
        rows += from_text(sys.stdin.read(), "pasted")
    for name in args.files:
        path = Path(name)
        if not path.exists():
            sys.exit(f"[fatal] {path} not found")
        rows += (from_csv(path) if path.suffix.lower() == ".csv"
                 else from_text(path.read_text(encoding="utf-8", errors="replace"),
                                path.name))

    if not rows:
        sys.exit("[fatal] nothing parsed. Each listing needs an acreage or a price "
                 "on its own line. For an MLS export, use the .csv instead.")

    # Dedupe across sources — the same lot appears on four sites.
    unique, seen = [], set()
    for r in rows:
        key = (r["pin"] or "", (r["address"] or "").upper(), r["acres"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    out = Path(args.out) if args.out else HERE / "out" / "lots.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_COLS)
        w.writeheader()
        w.writerows(unique)

    no_key = sum(1 for r in unique if not r["pin"] and not r["address"])
    print(f"[intake] {len(rows)} parsed, {len(unique)} unique -> {out}")
    if no_key:
        print(f"[intake] ! {no_key} rows have neither a PIN nor an address. "
              f"screen.py cannot match those to a parcel — add the MLS number "
              f"or the street address by hand.")
    print(f"[intake] next: py screen.py --listings {out}")


if __name__ == "__main__":
    main()
