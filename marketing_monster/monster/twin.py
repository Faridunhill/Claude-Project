"""THE MAKER + THE MOUTH — twin a proven eBay listing onto the other ground.

A pipe that sold on eBay is gone; the *listing* is not. Its title, its
photographs and the words that worked are proven assets, and they currently
live only on borrowed ground. Twinning moves them:

  1. OWNED GROUND FIRST (v1.0's Mouth law) — faridunhill.com. Farid's admin
     already holds the live listing and pushes it to Etsy automatically, so
     what this file writes for the site is the SOLD entry: the permanent
     record that stays up after the pipe is gone and points at current stock,
     exactly as the encyclopedia law requires.
  2. BORROWED GROUND SECOND — the Etsy copy (reference; the admin push is
     automatic) and the eBay File Exchange CSV, which is the one artifact
     Farid actually uploads by hand.

Two honesty laws bind this file:
  · It never invents a date. The dating engine owns that verdict; a twin says
    UNDATED and waits for the cabinet, exactly as a Passport does.
  · It never claims a condition or a fact the source listing did not state.
    Twinning is a translation, not an embellishment.
"""
from __future__ import annotations

import pathlib
import re

from .dig import BRANDS, MATERIALS, SHAPES, find_in
from .ledger import LedgerError, now_iso
from .playbook import Playbook

# Platform limits. Real constraints, not preferences.
EBAY_TITLE_MAX = 80          # eBay truncates hard at 80
ETSY_TITLE_MAX = 140
ETSY_TAG_MAX_CHARS = 20
ETSY_TAG_COUNT = 13

STOP_TAGS = {"pipe", "pipes", "estate", "the", "and", "for", "with"}


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def classify(title: str) -> dict:
    """What the title itself says. Nothing inferred beyond its own words."""
    return {
        "brand": find_in(title, BRANDS),
        "shape": find_in(title, SHAPES),
        "material": find_in(title, MATERIALS),
        "filter_9mm": bool(re.search(r"\b9\s?mm\b", title, re.I)),
        "unsmoked": bool(re.search(r"\bunsmoked\b", title, re.I)),
    }


def etsy_tags(title: str, facts: dict) -> list[str]:
    """13 tags, 20 characters each — Etsy's limits, not ours. Multi-word tags
    beat single words on Etsy search, so pairs are built where they are true."""
    candidates: list[str] = []
    brand, shape, material = facts["brand"], facts["shape"], facts["material"]
    if brand:
        candidates += [brand, f"{brand} pipe"]
        if shape:
            candidates.append(f"{brand} {shape}")
    if shape:
        candidates += [f"{shape} pipe", f"estate {shape}"]
    if material:
        candidates.append(f"{material} pipe")
    if facts["filter_9mm"]:
        candidates += ["9mm filter pipe", "filter pipe"]
    if facts["unsmoked"]:
        candidates += ["unsmoked pipe", "new old stock"]
    candidates += ["estate pipe", "smoking pipe", "tobacco pipe",
                   "collectible pipe", "gift for smoker", "vintage pipe"]

    out: list[str] = []
    for tag in candidates:
        tag = tag.strip().lower()
        if len(tag) <= ETSY_TAG_MAX_CHARS and tag not in out and tag not in STOP_TAGS:
            out.append(tag)
        if len(out) == ETSY_TAG_COUNT:
            break
    return out


def etsy_title(source_title: str) -> str:
    """Etsy truncates at 140 characters. Cut at a word, never mid-word, and
    never pad with keywords the pipe does not have."""
    title = " ".join(source_title.split())
    if len(title) <= ETSY_TITLE_MAX:
        return title
    cut = title[:ETSY_TITLE_MAX].rsplit(" ", 1)[0]
    return cut.rstrip(" -,|")


def site_entry(title: str, facts: dict, price: float, sku: str,
               sold_on: str, channel: str) -> str:
    """The owned-ground twin. Stays live after the sale and points at stock."""
    brand = (facts["brand"] or "unattributed").title()
    return f"""---
title: "{title}"
sku: {sku}
brand: {brand}
shape: {facts['shape'] or 'unclassified'}
material: {facts['material'] or 'briar (assumed — not stated in the listing)'}
status: sold
sold_on: {sold_on}
sold_channel: {channel}
realised_price_usd: {price}
dating: UNDATED — pending the cabinet engine's verdict
generated: {now_iso()}
---

# {title}

**Sold {sold_on} · {channel} · ${price:,.2f}**

This piece has found its collector. The entry stays for the record — what it
was, what it made, and what it tells the next buyer about pieces like it.

## What the piece is

{('A ' + brand + ' ' + (facts['shape'] or 'pipe').title()).strip()}{
    ', 9mm filter' if facts['filter_9mm'] else ''}{
    ', unsmoked' if facts['unsmoked'] else ''}.

## Dating

**UNDATED.** No date is claimed here. The stamps on this piece have not been
run through the dating cabinets, and a bracket invented for a sold listing
would be a guess wearing a fact's clothes. When the cabinet verdict exists it
replaces this section, with its sources and its honest bracket.

## Looking for one like it

This exact piece is sold. Current stock in the same house and shape is the
place to look → [current {brand} stock](/stock/{slugify(brand)})
"""


def etsy_description(title: str, facts: dict, price: float) -> str:
    brand = (facts["brand"] or "").title()
    lines = [title, "", f"${price:,.2f}", ""]
    lines += ["What this is", ""]
    described = ", ".join(x.title() if x else x for x in
                          (brand, facts["shape"], facts["material"]) if x)
    lines += [f"{described or 'A collected estate pipe'}"
              f"{', with a 9mm filter' if facts['filter_9mm'] else ''}"
              f"{', unsmoked' if facts['unsmoked'] else ''}.", ""]
    lines += [
        "Condition is described from the piece in hand and shown in the "
        "photographs — what you see is what ships.", "",
        "About the dating", "",
        "Where a date can be established from the stamps, it is given as an "
        "honest bracket with its evidence. Where it cannot, this listing says "
        "so rather than guessing. That policy is the whole reason collectors "
        "buy here twice.", "",
        "Shipping", "",
        "Packed to survive the journey and dispatched promptly.",
    ]
    return "\n".join(lines)


# eBay File Exchange — the same upload format Farid already uses (his own
# EBAY_END_SOLD files carry this header). FILL markers are deliberate: the
# category id, the location and the photo URLs are his, and inventing them
# would produce a file that uploads wrong rather than one that refuses.
EBAY_ACTION = "Add"
EBAY_HEADER = [
    "*Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8)",
    "CustomLabel", "*Category", "*Title", "*Description", "*ConditionID",
    "PicURL", "*Quantity", "*StartPrice", "*Format", "*Duration", "*Location",
]


def ebay_title(source_title: str) -> str:
    title = " ".join(source_title.split())
    if len(title) <= EBAY_TITLE_MAX:
        return title
    return title[:EBAY_TITLE_MAX].rsplit(" ", 1)[0].rstrip(" -,|")


def ebay_row(title: str, facts: dict, price: float, sku: str, *,
             category: str = "", location: str = "", pic_url: str = "",
             condition_id: str = "3000", quantity: int = 1) -> list[str]:
    """One File Exchange line. Condition 3000 = Used, eBay's own code."""
    return [
        EBAY_ACTION, sku, category or "FILL_CATEGORY_ID",
        ebay_title(title),
        etsy_description(title, facts, price).replace("\n", "<br>"),
        condition_id, pic_url or "FILL_PHOTO_URLS", str(quantity),
        f"{price:.2f}", "FixedPrice", "GTC", location or "FILL_LOCATION",
    ]


class Twin:
    def __init__(self, clone_root: str | pathlib.Path):
        self.root = pathlib.Path(clone_root)
        self.playbook = Playbook(self.root)

    def build(self, title: str, price: float, sku: str, *, decision_id: str,
              sold_on: str, source_channel: str = "ebay",
              ebay_category: str = "", ebay_location: str = "") -> dict:
        if not decision_id.strip():
            raise LedgerError(
                "the Maker only produces what the Judge ordered — supply decision_id"
            )
        facts = classify(title)
        version = self.playbook.version()
        out_dir = self.root / "maker" / "out" / slugify(sku or title)[:60]
        out_dir.mkdir(parents=True, exist_ok=True)

        import csv, io
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(EBAY_HEADER)
        writer.writerow(ebay_row(title, facts, price, sku, category=ebay_category,
                                 location=ebay_location))

        artifacts = {
            "ebay.csv": buffer.getvalue(),
            "site.md": site_entry(title, facts, price, sku, sold_on, source_channel),
            "etsy.txt": (
                f"TITLE ({len(etsy_title(title))}/{ETSY_TITLE_MAX} chars)\n"
                f"{etsy_title(title)}\n\n"
                f"TAGS ({len(etsy_tags(title, facts))}/{ETSY_TAG_COUNT})\n"
                + "\n".join(f"  {t}" for t in etsy_tags(title, facts))
                + "\n\nDESCRIPTION\n"
                + etsy_description(title, facts, price)
                + f"\n\n---\nplaybook: {version}\ndecision: {decision_id}\n"
            ),
        }
        for name, body in artifacts.items():
            (out_dir / name).write_text(body, encoding="utf-8")

        needs_filling = [f for f in ("FILL_CATEGORY_ID", "FILL_PHOTO_URLS", "FILL_LOCATION")
                         if f in artifacts["ebay.csv"]]
        return {"sku": sku, "facts": facts, "out_dir": out_dir,
                "needs_filling": needs_filling,
                "asset_version": version, "decision_id": decision_id,
                "lessons_applied": [x.claim for x in self.playbook.for_maker()],
                "files": sorted(artifacts)}
