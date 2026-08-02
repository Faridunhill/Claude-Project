"""THE DIGGER, inward — the pipes dig (v1.0 DIG ORDER §1).

"What sold fastest, at what price, which title words, who bought twice."

The whole difficulty of this dig is honesty at low N. Every number here comes
with its evidence count and a confidence label, and the thresholds refuse to
call three sales a pattern (B2). A dig produces PROPOSED playbook lines only —
nothing reaches CONFIRMED without two cohorts, and this is one look at one
dataset, which is one cohort by definition.

Written to survive being wrong: findings state what would falsify them.
"""
from __future__ import annotations

import pathlib
import re
import statistics
from collections import Counter, defaultdict
from datetime import date

from .ledger import now_iso
from .well import Well

# --- evidence thresholds (B2) -------------------------------------------
NOT_EVIDENCE = 12      # below this, an observation, never a finding
WEAK = 40              # below this, weak; at or above, worth a PROPOSED line

# --- title tokenising ----------------------------------------------------
# Words carrying no information about the pipe. Condition and provenance
# words — unsmoked, estate, patent, boxed — are deliberately NOT here: in this
# market they are the description, and dropping them hides real effects.
STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "for", "with", "in", "on", "no",
    "nice", "very", "good", "beautiful", "great", "wow", "look", "must", "see",
    "pipe", "pipes", "smoking", "tobacco", "briar", "lot", "free", "shipping",
    "l", "k", "s", "x", "mm", "cm", "inch", "inches",
}
BRANDS = [
    "dunhill", "charatan", "upshall", "peterson", "castello", "sasieni",
    "comoy", "gbd", "barling", "stanwell", "savinelli", "chacom", "radice",
    "ser jacopo", "ashton", "ferndown", "northern briars", "rattray", "parker",
    "bbb", "loewe", "butz-choquin", "nording", "winslow", "bang", "ivarsson",
    "chonowitsch", "tsuge", "kaywoodie", "yello-bole", "missouri meerschaum",
    "falcon", "hardcastle", "orlik", "ropp", "vauen", "meerschaum", "dr grabow",
    "brebbia", "caminetto", "il ceppo", "mastro de paja", "becker", "former",
]
SHAPES = ["billiard", "bulldog", "rhodesian", "dublin", "apple", "bent",
          "canadian", "lovat", "prince", "pot", "author", "poker", "zulu",
          "calabash", "churchwarden", "freehand", "blowfish", "cutty", "egg"]

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'\-]{1,}")


def confidence(n: int) -> str:
    if n < NOT_EVIDENCE:
        return "OBSERVATION (n too low to be evidence)"
    if n < WEAK:
        return "WEAK"
    return "WORTH PROPOSING"


def tokens(title: str) -> list[str]:
    low = title.lower()
    words = [w for w in TOKEN_RE.findall(low) if w not in STOPWORDS and not w.isdigit()]
    return words


def find_in(title: str, vocabulary: list[str]) -> str | None:
    low = title.lower()
    return next((v for v in vocabulary if v in low), None)


def _median(values: list[float]) -> float | None:
    clean = [v for v in values if v is not None]
    return statistics.median(clean) if clean else None


class Dig:
    def __init__(self, clone_root: str | pathlib.Path):
        self.root = pathlib.Path(clone_root)
        self.well = Well(self.root)
        self.rows = self.well.transactions()

    # -- the four questions ------------------------------------------------
    def overview(self) -> dict:
        prices = [r["price"] for r in self.rows if r.get("price")]
        dates = sorted(r["sold_at"] for r in self.rows if r.get("sold_at"))
        speeds = [r["days_to_sale"] for r in self.rows if r.get("days_to_sale") is not None]
        return {
            "n": len(self.rows),
            "span": (dates[0], dates[-1]) if dates else (None, None),
            "revenue": round(sum(prices), 2) if prices else 0.0,
            "median_price": _median(prices),
            "with_speed": len(speeds),
            "median_days": _median(speeds),
        }

    def speed(self) -> list[dict]:
        """What sold fastest — only answerable where a listing date exists."""
        bands = [(0, 75), (75, 150), (150, 300), (300, 600), (600, 10 ** 9)]
        out = []
        for lo, hi in bands:
            group = [r for r in self.rows
                     if r.get("price") and lo <= r["price"] < hi
                     and r.get("days_to_sale") is not None]
            if not group:
                continue
            out.append({"band": f"{lo}-{hi if hi < 10**9 else '+'}",
                        "n": len(group),
                        "median_days": _median([r["days_to_sale"] for r in group]),
                        "confidence": confidence(len(group))})
        return out

    def by_vocabulary(self, vocabulary: list[str], label: str) -> list[dict]:
        groups: dict[str, list[dict]] = defaultdict(list)
        for r in self.rows:
            key = find_in(r.get("title", ""), vocabulary) or "(unclassified)"
            groups[key].append(r)
        overall = _median([r["price"] for r in self.rows if r.get("price")]) or 0
        out = []
        for key, group in groups.items():
            prices = [r["price"] for r in group if r.get("price")]
            med = _median(prices)
            out.append({
                label: key, "n": len(group), "median_price": med,
                "lift": (med / overall - 1) if med and overall else None,
                "median_days": _median([r["days_to_sale"] for r in group
                                        if r.get("days_to_sale") is not None]),
                "revenue": round(sum(prices), 2) if prices else 0.0,
                "confidence": confidence(len(group)),
            })
        return sorted(out, key=lambda d: -d["n"])

    def title_words(self, min_n: int = NOT_EVIDENCE, min_stratum: int = 5) -> list[dict]:
        """Which title words travel with better outcomes — WITHIN BRAND.

        The naive version of this analysis is worthless and dangerous: compare
        every word against the overall median and the brand names win, because
        a Castello costs more than a Stanwell no matter how it is described.
        That produces "lessons" like *use the word Castello*, which cannot be
        acted on — you cannot rename a pipe.

        So each word is compared only against listings OF THE SAME BRAND that
        lack it, and a word must show its effect in at least two independent
        brands to appear at all. Brand and shape words are excluded outright;
        they have their own sections.

        Still correlation, not cause. A word describing a better pipe still
        travels with a better price. This can only ever produce a STRUCT-tier
        PROPOSED line, to be tested deliberately later.
        """
        excluded = {w for name in BRANDS + SHAPES for w in name.split()}
        counts = Counter()
        for r in self.rows:
            counts.update(set(tokens(r.get("title", ""))) - excluded)

        by_brand: dict[str, list[dict]] = defaultdict(list)
        for r in self.rows:
            by_brand[find_in(r.get("title", ""), BRANDS) or "(unclassified)"].append(r)

        out = []
        for word, n in counts.items():
            if n < min_n:
                continue
            ratios, day_deltas = [], []
            for brand, group in by_brand.items():
                if brand == "(unclassified)":
                    continue
                has = [r for r in group if word in tokens(r.get("title", ""))]
                lacks = [r for r in group if word not in tokens(r.get("title", ""))]
                if len(has) < min_stratum or len(lacks) < min_stratum:
                    continue
                a = _median([r["price"] for r in has if r.get("price")])
                b = _median([r["price"] for r in lacks if r.get("price")])
                if a and b:
                    ratios.append(a / b)
                da = _median([r["days_to_sale"] for r in has if r.get("days_to_sale") is not None])
                db = _median([r["days_to_sale"] for r in lacks if r.get("days_to_sale") is not None])
                if da is not None and db is not None:
                    day_deltas.append(da - db)
            if len(ratios) < 2:      # one brand is an anecdote, not a pattern
                continue
            out.append({
                "word": word, "n": n, "brands": len(ratios),
                "price_lift": statistics.median(ratios) - 1,
                "days_delta": statistics.median(day_deltas) if day_deltas else None,
                "median_price": _median([r["price"] for r in self.rows
                                         if word in tokens(r.get("title", "")) and r.get("price")]),
                "confidence": confidence(n) if len(ratios) >= 3 else "WEAK (few brands)",
            })
        return sorted(out, key=lambda d: -(d["price_lift"] or -9))

    def repeat_buyers(self) -> dict:
        import json
        path = self.well.root / "derived" / "buyers.jsonl"
        buyers = ([json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
                  if path.exists() else [])
        repeat = [b for b in buyers if b.get("repeat")]
        total_value = sum(b.get("total_value", 0) for b in buyers)
        return {
            "buyers": len(buyers), "repeat": len(repeat),
            "repeat_share": (len(repeat) / len(buyers)) if buyers else None,
            "revenue_share": (sum(b["total_value"] for b in repeat) / total_value)
                             if total_value else None,
            "top": sorted(repeat, key=lambda b: -b.get("purchases", 0))[:10],
            "confidence": confidence(len(repeat)),
        }

    # -- the written dig ---------------------------------------------------
    def report(self) -> str:
        o = self.overview()
        if not self.rows:
            return ("DIG — pipes\n\nThe Well is empty. Run `monster load pipes <export.csv>` "
                    "first.\nNothing was inferred, because there is nothing to infer from.")

        L = [
            "# DIG 001 — PIPES · face the Well",
            f"*Generated {now_iso()} by the Digger, inward pass.*",
            "",
            "## Provenance (N4)",
            f"- Read: `well/derived/transactions.jsonl` ({o['n']} rows) and `buyers.jsonl`.",
            "- Not read: anything outside this Well. No public data, no competitor data.",
            f"- Speed analysis covers {o['with_speed']} of {o['n']} rows — only those where a "
            "listing date survived the export. Where it is missing, absence does not date.",
            "- Every figure below carries its n. Below "
            f"{NOT_EVIDENCE} it is an observation, not evidence.",
            "",
            "## The shape of the Well",
            f"- {o['n']} transactions, {o['span'][0]} → {o['span'][1]}",
            f"- revenue recorded: {o['revenue']:,.2f}",
            f"- median price: {o['median_price']:,.2f}" if o["median_price"] else "- median price: n/a",
            (f"- median days to sale: {o['median_days']:.0f} (n={o['with_speed']})"
             if o["median_days"] is not None else
             "- days to sale: not computable — no listing dates in this export"),
            "",
        ]

        speed = self.speed()
        L += ["## Q1 · What sold fastest"]
        if speed:
            L += ["| price band | n | median days | confidence |", "|---|---|---|---|"]
            L += [f"| {s['band']} | {s['n']} | {s['median_days']:.0f} | {s['confidence']} |"
                  for s in speed]
        else:
            L += ["Not answerable from this export — no listing dates, so no time-to-sale.",
                  "**What would fix it:** an export including the listing/start date."]
        L += [""]

        L += ["## Q2 · At what price — by brand"]
        brands = [b for b in self.by_vocabulary(BRANDS, "brand") if b["n"] >= 3][:15]
        L += ["| brand | n | median | lift vs all | median days | confidence |", "|---|---|---|---|---|---|"]
        for b in brands:
            lift = f"{b['lift']*100:+.0f}%" if b["lift"] is not None else "—"
            days = f"{b['median_days']:.0f}" if b["median_days"] is not None else "—"
            med = f"{b['median_price']:,.0f}" if b["median_price"] else "—"
            L += [f"| {b['brand']} | {b['n']} | {med} | {lift} | {days} | {b['confidence']} |"]
        L += [""]

        shapes = [s for s in self.by_vocabulary(SHAPES, "shape")
                  if s["shape"] != "(unclassified)" and s["n"] >= 3][:10]
        if shapes:
            L += ["## Q2b · By shape"]
            L += ["| shape | n | median | lift | confidence |", "|---|---|---|---|---|"]
            for s in shapes:
                lift = f"{s['lift']*100:+.0f}%" if s["lift"] is not None else "—"
                med = f"{s['median_price']:,.0f}" if s["median_price"] else "—"
                L += [f"| {s['shape']} | {s['n']} | {med} | {lift} | {s['confidence']} |"]
            L += [""]

        words = [w for w in self.title_words()
                 if not w["confidence"].startswith("OBSERVATION")][:20]
        L += ["## Q3 · Which title words travel with better outcomes",
              "*Compared within brand only — a Castello outsells a Stanwell however it is "
              "described, so comparing words against the overall median just re-discovers "
              "the brands. Brand and shape words are excluded; a word must show up in at "
              "least two independent brands. Still correlation, not cause: a word "
              "describing a better pipe travels with a better price either way.*", ""]
        if words:
            L += ["| word | n | brands | price lift (within brand) | days vs same brand | confidence |",
                  "|---|---|---|---|---|---|"]
            for w in words:
                lift = f"{w['price_lift']*100:+.0f}%" if w["price_lift"] is not None else "—"
                delta = f"{w['days_delta']:+.0f}d" if w["days_delta"] is not None else "—"
                L += [f"| {w['word']} | {w['n']} | {w['brands']} | {lift} | {delta} | {w['confidence']} |"]
        else:
            L += [f"No word clears the bar (seen {NOT_EVIDENCE}+ times, in 2+ brands, with "
                  "enough same-brand listings to compare against). That is the honest "
                  "answer — this Well is not yet big enough to read title effects."]
        L += [""]

        rb = self.repeat_buyers()
        L += ["## Q4 · Who bought twice"]
        if rb["buyers"]:
            share = f"{rb['repeat_share']*100:.0f}%" if rb["repeat_share"] is not None else "—"
            rev = f"{rb['revenue_share']*100:.0f}%" if rb["revenue_share"] is not None else "—"
            L += [f"- {rb['repeat']} repeat buyers out of {rb['buyers']} ({share})",
                  f"- they account for {rev} of recorded revenue",
                  f"- confidence: {rb['confidence']}", ""]
            if rb["top"]:
                L += ["| buyer key | purchases | total | first → last |", "|---|---|---|---|"]
                L += [f"| `{b['buyer_key']}` | {b['purchases']} | {b['total_value']:,.0f} | "
                      f"{b['first_seen']} → {b['last_seen']} |" for b in rb["top"]]
                L += ["", "*Keys, not people. The Well holds no names (M4).*", ""]
        else:
            L += ["No buyer identifier survived the export, so repeat purchase is not "
                  "computable. **What would fix it:** an export including the buyer "
                  "username column — it is hashed on the way in and never stored raw.", ""]

        L += ["## What this dig does NOT show",
              "- Cause. Nothing here is an experiment; every number is what happened, "
              "not why.",
              "- Anything about listings that never sold — unsold inventory is invisible "
              "in a sold-item export, so 'what sells' here means 'what sold', and the "
              "denominator is missing.",
              "- Anything outside this Well.", ""]

        L += ["## Proposed playbook lines (PROPOSED only — B2)"]
        proposals = self.proposals()
        if proposals:
            L += [f"- `{p}`" for p in proposals]
            L += ["", "*None of these is CONFIRMED. Each needs a second, non-overlapping "
                  "cohort before the Maker may read it.*"]
        else:
            L += ["None. Nothing in this Well clears the evidence threshold yet, and "
                  "inventing a lesson to have one is exactly the failure mode the "
                  "playbook rules exist to prevent."]
        return "\n".join(L)

    def proposals(self) -> list[str]:
        """Candidate lines — evidence attached, status PROPOSED, expiry set."""
        today = date.today()
        out = []
        for w in self.title_words(min_n=WEAK)[:3]:
            if w["price_lift"] and w["price_lift"] > 0.15 and w["brands"] >= 3:
                out.append(
                    f"[STRUCT][PROPOSED] Test '{w['word']}' in listing titles where it is "
                    f"true of the pipe. :: n={w['n']} listings across {w['brands']} brands :: "
                    f"effect={w['price_lift']*100:+.0f}% median price within brand (correlational) :: "
                    f"born={today} :: review={today.replace(year=today.year + 1)} :: src=dig-001"
                )
        rb = self.repeat_buyers()
        if rb["repeat"] >= NOT_EVIDENCE and (rb["revenue_share"] or 0) > 0.2:
            out.append(
                f"[OUTCOME][PROPOSED] Treat repeat buyers as a segment worth its own "
                f"contact path. :: n={rb['repeat']} repeat buyers :: "
                f"effect={rb['revenue_share']*100:.0f}% of recorded revenue :: "
                f"born={today} :: review={today.replace(year=today.year + 1)} :: src=dig-001"
            )
        return out

    def write(self) -> pathlib.Path:
        out = self.root / "digger" / "digs"
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"DIG_001_{date.today().isoformat()}_pipes.md"
        path.write_text(self.report() + "\n", encoding="utf-8")
        return path
