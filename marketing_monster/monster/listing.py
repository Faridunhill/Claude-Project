"""THE MAIN JOB — what happens when Farid lists a new pipe.

Everything built before this reacted to sales. But the moment that decides a
sale is the moment the listing is written, and until now the agent was silent
exactly then. This module is the agent at that moment:

  1. PRICE — what pipes like this one actually fetched, from his own Well.
     A range with its evidence count, never a single confident number, and a
     refusal to advise at all when too few comparables exist.
  2. TITLE — the CONFIRMED playbook lessons applied. When nothing is confirmed
     yet, it says so and changes nothing. An unproven lesson dressed as advice
     is the superstition B2 exists to prevent.
  3. THE TWINS — site entry, Etsy copy, eBay CSV.
  4. THE CLOCK — a `listed` event in the Scale. When the pipe sells, the gap
     between the two rows is the days-to-sale the dig has never been able to
     answer, and the pipes that never sell become visible instead of invisible.
"""
from __future__ import annotations

import pathlib
import statistics

from .dig import BRANDS, MATERIALS, SHAPES, find_in
from .ledger import LedgerError
from .playbook import Playbook
from .scale import Scale
from .well import Well

MIN_COMPARABLES = 5        # below this, a price "range" is just two numbers
GOOD_COMPARABLES = 15


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = fraction * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


class ListingDesk:
    def __init__(self, clone_root: str | pathlib.Path):
        self.root = pathlib.Path(clone_root)
        self.well = Well(self.root)
        self.playbook = Playbook(self.root)
        self.rows = self.well.transactions()

    # -- 1: what did pipes like this actually fetch? ----------------------
    def comparables(self, title: str) -> dict:
        brand = find_in(title, BRANDS)
        shape = find_in(title, SHAPES)
        material = find_in(title, MATERIALS)

        def priced(rows):
            return [r for r in rows if r.get("price")]

        exact = priced([r for r in self.rows
                        if brand and shape
                        and find_in(r.get("title", ""), BRANDS) == brand
                        and find_in(r.get("title", ""), SHAPES) == shape])
        by_brand = priced([r for r in self.rows
                           if brand and find_in(r.get("title", ""), BRANDS) == brand])

        if len(exact) >= MIN_COMPARABLES:
            basis, group = f"{brand} {shape}", exact
        elif len(by_brand) >= MIN_COMPARABLES:
            basis, group = f"{brand} (any shape)", by_brand
        else:
            return {"brand": brand, "shape": shape, "material": material,
                    "n": len(by_brand), "basis": None, "advice": None,
                    "why": (f"only {len(by_brand)} past sales of "
                            f"{brand or 'this kind'} — too few to price from. "
                            "Your judgement beats this number.")}

        prices = [r["price"] for r in group]
        return {
            "brand": brand, "shape": shape, "material": material,
            "basis": basis, "n": len(prices),
            "low": round(_percentile(prices, 0.25), 2),
            "median": round(statistics.median(prices), 2),
            "high": round(_percentile(prices, 0.75), 2),
            "best": round(max(prices), 2),
            "confidence": "solid" if len(prices) >= GOOD_COMPARABLES else "thin",
            "advice": "range",
            "why": (f"{len(prices)} past sales of {basis}. Half of them fell "
                    "between the low and high figures."),
        }

    # -- 2: title, using only what is proven ------------------------------
    def title_advice(self, title: str) -> dict:
        confirmed = self.playbook.for_maker()
        if not confirmed:
            return {"lessons": [], "suggestion": None,
                    "why": ("no lesson is CONFIRMED yet, so the agent changes "
                            "nothing about your title. It will not invent advice "
                            "to look useful.")}
        return {"lessons": [x.claim for x in confirmed], "suggestion": title,
                "why": ("apply the confirmed lessons below where they are TRUE "
                        "of this pipe. Never add a word that is not true.")}

    # -- 3 & 4: publish the twins and start the clock ---------------------
    def open_listing(self, title: str, price: float, sku: str, *,
                     decision_id: str, channel: str = "ebay",
                     ebay_category: str = "", ebay_location: str = "") -> dict:
        from .twin import Twin
        if not sku.strip():
            raise LedgerError("a listing needs a SKU — it is how the sale is "
                              "matched back to it later")
        scale = Scale(self.root)
        already = [r for r in scale.rows()
                   if r["event"] == "published" and r["asset_id"] == sku]
        artifacts = Twin(self.root).build(
            title, price, sku, decision_id=decision_id,
            sold_on="(not sold — listed)", source_channel=channel,
            ebay_category=ebay_category, ebay_location=ebay_location)
        row = None
        if not already:
            row = scale.record("published", sku, surface=channel,
                               asset_version=artifacts["asset_version"],
                               value=price, attribution="direct",
                               reason=f"listed on {channel} at {price:.2f}")
        return {"artifacts": artifacts, "clock_started": row is not None,
                "event": row}

    # -- the answer to "what sold fastest", at last -----------------------
    def days_to_sale(self) -> list[dict]:
        """Pairs each sale with the moment its listing went live. This is the
        question the dig has always had to refuse — it could not be answered
        from a sold-item export, only from watching listings from the start."""
        from datetime import datetime
        scale = Scale(self.root)
        listed: dict[str, str] = {}
        for row in scale.rows():
            if row["event"] == "published" and row["asset_id"] not in listed:
                listed[row["asset_id"]] = row["ts"]
        out = []
        for row in scale.rows():
            if row["event"] != "sale" or row["asset_id"] not in listed:
                continue
            start = datetime.fromisoformat(listed[row["asset_id"]].replace("Z", "+00:00"))
            end = datetime.fromisoformat(row["ts"].replace("Z", "+00:00"))
            days = (end - start).days
            if days >= 0:
                out.append({"sku": row["asset_id"], "days": days,
                            "value": row["value"], "surface": row["surface"]})
        return out

    def still_unsold(self) -> list[dict]:
        """The denominator. A sold-item export can never show these, and
        without them "what sells" only ever meant "what sold"."""
        from datetime import datetime, timezone
        scale = Scale(self.root)
        sold = {r["asset_id"] for r in scale.rows() if r["event"] == "sale"}
        # One pipe published to three channels is one pipe, not three. Count
        # from when it FIRST went live.
        first: dict[str, dict] = {}
        for row in scale.rows():
            if row["event"] != "published" or row["asset_id"] in sold:
                continue
            seen = first.get(row["asset_id"])
            if seen is None or row["ts"] < seen["ts"]:
                first[row["asset_id"]] = row
            elif seen.get("value") is None and row.get("value") is not None:
                seen["value"] = row["value"]
        out = []
        for sku, row in first.items():
            age = (datetime.now(timezone.utc)
                   - datetime.fromisoformat(row["ts"].replace("Z", "+00:00"))).days
            out.append({"sku": sku, "days_live": age,
                        "asked": row.get("value"), "surface": row["surface"],
                        "channels": sum(1 for r in scale.rows()
                                        if r["event"] == "published"
                                        and r["asset_id"] == sku)})
        return sorted(out, key=lambda d: -d["days_live"])
