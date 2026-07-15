"""Marketing DNA — Layer 2 (EXPRESSION).

Generated marketing content — titles, descriptions, tags, ordered images,
alt-text. Disposable and versioned: regenerated at will from the genome,
never hand-edited in place (a hand-edit is a genome correction, not an
expression tweak — Synthesis §3, Round 1 Q1).

Every generator obeys two laws:
  * ASSERT ONLY WHAT THE GATE CLEARED — a Tier A claim is stated as fact
    only if the QA gate (P2.4) marked it assertable; otherwise it hedges
    ("attributed to") or is omitted. A vision guess never ships as fact.
  * DISCLOSE EVERY FLAW — the honesty layer; flaws become sentences and
    pair with FLAW photos. Underclaiming costs margin, overclaiming costs
    the business.
"""

from .listing import ListingDraft, generate_listing

__all__ = ["ListingDraft", "generate_listing"]
