"""THE WELL — the business's private truth, walled.

Finding M4: the eBay list is intelligence, not a mailing list — and *storing*
it is a separate exposure from *mailing* it. So the Well never holds a name,
an email or an address. It holds derived features keyed by a salted hash,
which answers every strategic question the Digger will ask ("who bought
twice", "which categories repeat") without holding a personal-data file.

Whitelist, not blacklist: a column is dropped unless it is known to be safe.
"""
from __future__ import annotations

import csv
import hashlib
import hmac
import json
import pathlib
import re
import secrets
from collections import defaultdict

from .ledger import LedgerError

# --- what may be written -------------------------------------------------
TRANSACTION_FIELDS = {
    "item_id", "title", "brand", "shape", "category", "condition", "surface",
    "listed_at", "sold_at", "days_to_sale", "price", "currency", "quantity",
    "buyer_key", "channel",
}
BUYER_FIELDS = {"buyer_key", "purchases", "first_seen", "last_seen",
                "categories", "total_value", "repeat"}

# --- what must never appear ---------------------------------------------
PII_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.\w{2,}"),
    # deliberately narrow: an ISO date is not a phone number
    "phone": re.compile(
        r"(?<!\d)(?:\+\d[\d\s().-]{7,}\d"
        r"|\(\d{3}\)\s*\d{3}[-.\s]?\d{4}"
        r"|\d{3}[-.\s]\d{3}[-.\s]\d{4})(?!\d)"),
    "street": re.compile(r"\b\d{1,6}\s+[A-Za-z][A-Za-z.'-]*\s+"
                         r"(?:st|street|ave|avenue|rd|road|ln|lane|dr|drive|blvd|way|ct|court)\b", re.I),
}
PII_COLUMN_HINTS = ("name", "email", "e-mail", "address", "street", "city", "state",
                    "zip", "postcode", "postal", "phone", "tel", "contact", "buyer")

# Fields that hold OUR OWN listing copy, not customer data. A pipe title is
# full of things that look like addresses — "4 Star Dr Grabow", "2 Ring St
# Charatan" — so the street pattern is not applied to them; it would refuse
# the whole catalogue to guard against a risk that is not there. Email and
# phone patterns are specific enough to keep everywhere.
PRODUCT_TEXT_FIELDS = {"title", "brand", "shape", "category", "condition", "channel"}
ADDRESS_PATTERNS = {"street"}

# --- default column aliases (eBay-ish exports; override with a mapping) ---
ALIASES = {
    "item_id": ("item number", "item id", "itemid", "listing id", "sku"),
    "title": ("item title", "title", "listing title"),
    "price": ("sold for", "sale price", "price", "total price", "sold price"),
    "currency": ("currency", "currency code"),
    "quantity": ("quantity", "qty"),
    # order matters — the specific names win, "date" is the last resort so a
    # file whose only date column is called "Date" still maps
    "sold_at": ("sale date", "sold date", "date sold", "paid on",
                "transaction date", "order date", "date"),
    "listed_at": ("start date", "listed date", "listing date", "created"),
    "category": ("category", "ebay category", "leaf category"),
    "condition": ("condition",),
    "_buyer_raw": ("buyer username", "buyer id", "buyer user id", "username", "buyer"),
}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.strip().lower()).strip()


def _flatten(record: dict, prefix: str = "") -> dict:
    """JSONL records nest. One level of flattening is enough to expose the
    fields that matter (price.amount, listing.title) without inventing a
    schema language."""
    out = {}
    for key, value in record.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            out.update(_flatten(value, f"{name}_"))
        elif isinstance(value, list):
            out[name] = ", ".join(str(v) for v in value if not isinstance(v, (dict, list)))
        else:
            out[name] = value
    return out


def read_rows(path: str | pathlib.Path) -> tuple[list[str], list[dict]]:
    """CSV, TSV or JSONL — one reader, so every command speaks all of them."""
    path = pathlib.Path(path)
    suffix = path.suffix.lower()
    if suffix in (".jsonl", ".ndjson"):
        rows = []
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        rows.append(_flatten(json.loads(line)))
                    except json.JSONDecodeError:
                        continue
        if not rows:
            raise LedgerError(f"{path.name} has no readable JSON records")
        headers, seen = [], set()
        for row in rows[:500]:            # union of the first 500 records
            for key in row:
                if key not in seen:
                    seen.add(key)
                    headers.append(key)
        return headers, rows
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):        # {"items": [...]} or similar
            data = next((v for v in data.values() if isinstance(v, list)), [])
        rows = [_flatten(r) for r in data if isinstance(r, dict)]
        if not rows:
            raise LedgerError(f"{path.name} holds no list of records")
        return list(rows[0]), rows
    delimiter = "\t" if suffix == ".tsv" else ","
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        return list(reader.fieldnames or []), list(reader)


def read_headers(path: str | pathlib.Path) -> list[str]:
    """Header row / record keys only — `inspect` must not pull the whole file
    into memory for a CSV just to show its columns."""
    path = pathlib.Path(path)
    if path.suffix.lower() in (".csv", ".tsv"):
        delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
        with path.open(encoding="utf-8-sig", newline="") as fh:
            return next(csv.reader(fh, delimiter=delimiter), [])
    return read_rows(path)[0]


# Words too generic to match by substring. "date" as a last-resort alias is
# what let an active-listings report's "Start date" be read as a sale date,
# recording hundreds of unsold pipes as sold. Generic aliases must match a
# column name exactly or not at all.
# Only the date aliases. "price" matching "price_amount" is correct and
# needed for Etsy's nested records; "date" matching "start date" is not, because
# a start date and a sale date mean opposite things.
EXACT_ONLY = {"date", "created"}


def propose_mapping(headers: list[str]) -> dict[str, str | None]:
    """Given a real export's headers, propose the mapping. Writes nothing."""
    seen = {_norm(h): h for h in headers}
    out: dict[str, str | None] = {}
    for field, names in ALIASES.items():
        hit = next((seen[_norm(n)] for n in names if _norm(n) in seen), None)
        if hit is None:  # substring fallback, specific aliases only
            hit = next((orig for norm, orig in seen.items()
                        if any(_norm(n) in norm for n in names
                               if _norm(n) not in EXACT_ONLY)), None)
        out[field] = hit
    return out


# Columns that only ever appear in a LIVE-inventory report. A file carrying
# these is not a record of sales, whatever its date columns look like.
ACTIVE_LISTING_MARKERS = ("available quantity", "auction buy it now price",
                          "reserve price", "start price", "watchers",
                          "listing duration", "relist")


def looks_like_active_listings(headers: list[str]) -> str | None:
    """Returns the marker found, or None. Active listings are the DENOMINATOR
    — valuable, but they are not sales and must never be counted as sales."""
    seen = {_norm(h) for h in headers}
    for marker in ACTIVE_LISTING_MARKERS:
        if any(marker in name for name in seen):
            return marker
    return None


def dropped_columns(headers: list[str], mapping: dict) -> list[str]:
    used = {v for v in mapping.values() if v}
    return [h for h in headers if h not in used]


class Well:
    def __init__(self, clone_root: str | pathlib.Path):
        self.root = pathlib.Path(clone_root) / "well"
        (self.root / "raw").mkdir(parents=True, exist_ok=True)
        (self.root / "derived").mkdir(parents=True, exist_ok=True)
        self.salt_path = self.root / ".salt"

    # -- identity without identifiers ------------------------------------
    def salt(self) -> bytes:
        if not self.salt_path.exists():
            self.salt_path.write_text(secrets.token_hex(32), encoding="utf-8")
        return self.salt_path.read_text(encoding="utf-8").strip().encode()

    def buyer_key(self, raw: str) -> str:
        """Stable across exports, useless without the salt (T5)."""
        return hmac.new(self.salt(), _norm(str(raw)).encode(), hashlib.sha256).hexdigest()[:16]

    # -- the guard --------------------------------------------------------
    @staticmethod
    def assert_clean(row: dict) -> None:
        for key, value in row.items():
            if any(h in key.lower() for h in PII_COLUMN_HINTS) and key != "buyer_key":
                raise LedgerError(f"refusing to write column {key!r} — M4: derived features only")
            if not isinstance(value, str):
                continue
            for label, pattern in PII_PATTERNS.items():
                if label in ADDRESS_PATTERNS and key in PRODUCT_TEXT_FIELDS:
                    continue          # our own listing copy — see PRODUCT_TEXT_FIELDS
                hit = pattern.search(value)
                if hit:
                    snippet = hit.group(0)[:60]
                    raise LedgerError(
                        f"refusing to write {label} found in {key!r}: {snippet!r} — "
                        "the Well holds no personal data (M4)"
                    )

    # -- loading ----------------------------------------------------------
    def load(self, source: str | pathlib.Path, mapping: dict | None = None, *,
             append: bool = False, channel: str | None = None) -> dict:
        """Turn a sold-item export into derived features. CSV, TSV or JSONL.
        Anything not whitelisted is dropped on the floor, on purpose.

        `append` merges a second source into the same Well — the sales history
        lives across eBay and Etsy exports, and one Well should hold both.
        """
        source = pathlib.Path(source)
        channel = channel or _guess_channel(source)
        headers, raw_rows = read_rows(source)
        mapping = mapping or propose_mapping(headers)
        missing = [f for f in ("item_id", "price", "sold_at") if not mapping.get(f)]
        if missing:
            raise LedgerError(
                f"cannot map required fields {missing} from {headers!r} — "
                "run `inspect` and supply a mapping.json"
            )

        transactions = list(self.transactions()) if append else []
        before = len(transactions)
        seen = {_dedupe_key(t) for t in transactions}
        skipped = 0

        for raw in raw_rows:
            row = {"channel": channel}
            for field, column in mapping.items():
                if not column or field.startswith("_"):
                    continue
                if field in TRANSACTION_FIELDS:
                    value = raw.get(column)
                    row[field] = str(value).strip() if value is not None else ""
            buyer_col = mapping.get("_buyer_raw")
            buyer_raw = str(raw.get(buyer_col) or "").strip() if buyer_col else ""
            row["buyer_key"] = self.buyer_key(buyer_raw) if buyer_raw else ""
            row["price"] = _to_float(row.get("price"))
            for field in ("sold_at", "listed_at"):
                if row.get(field):
                    row[field] = iso_date(row[field]) or row[field]
            row["days_to_sale"] = _days(row.get("listed_at"), row.get("sold_at"))
            self.assert_clean(row)
            key = _dedupe_key(row)
            if key in seen:                 # same sale, loaded twice
                skipped += 1
                continue
            seen.add(key)
            transactions.append(row)

        out_tx = self.root / "derived" / "transactions.jsonl"
        with out_tx.open("w", encoding="utf-8") as fh:
            for row in transactions:
                fh.write(json.dumps(row, sort_keys=True) + "\n")

        buyers = self._rebuild_buyers(transactions)
        return {"transactions": len(transactions), "added": len(transactions) - before,
                "duplicates_skipped": skipped, "channel": channel,
                "buyers": len(buyers),
                "repeat_buyers": sum(1 for b in buyers.values() if b["purchases"] > 1),
                "dropped_columns": dropped_columns(headers, mapping)}

    # kept so existing callers and tests keep working
    load_csv = load

    def _rebuild_buyers(self, transactions: list[dict]) -> dict:
        buyers = defaultdict(lambda: {"purchases": 0, "total_value": 0.0,
                                      "categories": set(), "first_seen": None,
                                      "last_seen": None})
        for row in transactions:
            if not row.get("buyer_key"):
                continue
            b = buyers[row["buyer_key"]]
            b["purchases"] += 1
            b["total_value"] += row.get("price") or 0.0
            if row.get("category"):
                b["categories"].add(row["category"])
            for key, when in (("first_seen", min), ("last_seen", max)):
                sold = row.get("sold_at") or ""
                b[key] = sold if not b[key] else when(b[key], sold)

        out = self.root / "derived" / "buyers.jsonl"
        with out.open("w", encoding="utf-8") as fh:
            for key, b in buyers.items():
                rec = {"buyer_key": key, "purchases": b["purchases"],
                       "total_value": round(b["total_value"], 2),
                       "categories": sorted(b["categories"]),
                       "first_seen": b["first_seen"], "last_seen": b["last_seen"],
                       "repeat": b["purchases"] > 1}
                self.assert_clean(rec)
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
        return buyers

    def transactions(self) -> list[dict]:
        """Normalised on the way out too, so a Well loaded before this fix
        existed reads correctly without being rebuilt."""
        path = self.root / "derived" / "transactions.jsonl"
        if not path.exists():
            return []
        out = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            for field in ("sold_at", "listed_at"):
                if row.get(field):
                    row[field] = iso_date(row[field]) or ""
            out.append(row)
        return out


def _guess_channel(path: pathlib.Path) -> str:
    blob = str(path).lower()
    for name in ("etsy", "ebay", "shopify", "amazon", "site"):
        if name in blob:
            return name
    return "unknown"


def _dedupe_key(row: dict) -> tuple:
    """Same item, same day, same price, same channel = the same sale."""
    return (row.get("channel"), str(row.get("item_id") or ""),
            str(row.get("sold_at") or "")[:10], row.get("price"))


# Order matters for the ambiguous ones: 03/04/2026 is 4 March on a US eBay
# account and 3 April on a UK one. Farid's account is US, so US patterns win.
DATE_FORMATS = (
    "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%m-%d-%Y",
    "%b-%d-%y", "%b-%d-%Y", "%d-%b-%y", "%d-%b-%Y", "%b %d, %Y", "%d %b %Y",
)


def iso_date(value) -> str | None:
    """Every export writes dates differently — eBay ships "Oct-21-25", Etsy
    ships "2026-07-14". One stored format or nothing works: string comparison,
    cohorts, spans and cutoffs all silently misread mixed formats rather than
    failing, which is the worst way to be wrong."""
    from datetime import datetime
    if not value:
        return None
    text = str(value).strip().replace("T", " ").strip()
    if not text:
        return None
    # try the whole string first — "Oct 21, 2025" must not be cut at the space —
    # then the part before the time, for "2015-09-28 13:15:00"
    candidates = [text]
    if " " in text:
        candidates.append(text.split(" ")[0])
    for candidate, fmt in ((c, f) for c in candidates for f in DATE_FORMATS):
        try:
            parsed = datetime.strptime(candidate, fmt)
        except ValueError:
            continue
        # two-digit years: a pipe sale is not from 2070
        if "%y" in fmt and parsed.year > datetime.now().year + 1:
            parsed = parsed.replace(year=parsed.year - 100)
        return parsed.date().isoformat()
    return None


def _to_float(value) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(re.sub(r"[^\d.\-]", "", str(value)) or 0)
    except ValueError:
        return None


def _days(start: str | None, end: str | None) -> int | None:
    from datetime import datetime
    fmts = ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b-%d-%y", "%Y-%m-%dT%H:%M:%SZ")
    def parse(v):
        for f in fmts:
            try:
                return datetime.strptime(str(v)[:len("2026-07-31T00:00:00Z")], f)
            except (ValueError, TypeError):
                continue
        return None
    a, b = parse(start), parse(end)
    return (b - a).days if a and b else None
