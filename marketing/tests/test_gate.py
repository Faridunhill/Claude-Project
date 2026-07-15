"""P2.4 QA-gate tests — one guarantee per test (Round 2 F2)."""

from __future__ import annotations

from marketing.genome.gate import (
    CONFIDENCE_FLOOR,
    GateOutcome,
    RoutingRule,
    evaluate,
)
from marketing.genome.intake import IntakeInput, build_genome
from marketing.genome.adapter_itemassets import ItemAssets, MediaAsset, VisionClaim
from marketing.genome.vocab import MediaRole


def _never_audit(sku):  # deterministic: audit rule off for most tests
    return False


def _always_audit(sku):
    return True


def _assets(brand_conf=0.97, brand="Peterson", stamping="PETERSON'S DUBLIN MADE IN IRELAND 106", era_conf=0.95):
    claims = [
        VisionClaim(field_path="brand", value=brand, confidence=brand_conf, model_version="eye-v3"),
        VisionClaim(
            field_path="unique_physical.era",
            value={"min_year": 1950, "max_year": 1970, "basis": "hallmark"},
            confidence=era_conf,
        ),
    ]
    return ItemAssets(
        sku="FH-1",
        media=[MediaAsset(url="https://c/h.jpg", role=MediaRole.HERO)],
        vision_claims=claims,
        stamping_ocr=stamping,
    )


def _genome(economics=None, **assets_kw):
    intake = IntakeInput(sku="FH-1", economics=economics)
    genome, _ = build_genome(intake, assets=_assets(**assets_kw))
    return genome


# -- rule 1: confidence -----------------------------------------------------

def test_high_confidence_corroborated_claim_passes():
    d = evaluate(_genome(), audit_sampler=_never_audit)
    assert d.outcome is GateOutcome.PASS
    assert "brand" in d.assertable_tier_a
    assert d.lists is True


def test_low_confidence_tier_a_routes_to_review():
    d = evaluate(_genome(era_conf=0.60), audit_sampler=_never_audit)
    assert d.outcome is GateOutcome.REVIEW
    assert "unique_physical.era" in d.hedge_tier_a
    assert any(r.rule is RoutingRule.CONFIDENCE for r in d.routed)
    # the item still lists — the era just hedges
    assert d.lists is True


# -- rule 2: corroboration --------------------------------------------------

def test_brand_not_in_stamping_routes_regardless_of_confidence():
    # confident vision brand that the stamping does not support
    d = evaluate(
        _genome(brand="Dunhill", brand_conf=0.99,
                stamping="PETERSON'S DUBLIN MADE IN IRELAND"),
        audit_sampler=_never_audit,
    )
    assert d.outcome is GateOutcome.REVIEW
    assert any(r.rule is RoutingRule.CORROBORATION and r.field_path == "brand" for r in d.routed)


def test_no_stamping_witness_does_not_fail_corroboration():
    # absence of OCR is not a contradiction — falls back to confidence only
    d = evaluate(_genome(stamping=None), audit_sampler=_never_audit)
    assert d.outcome is GateOutcome.PASS


# -- rule 3: price ----------------------------------------------------------

def test_high_price_routes_all_tier_a_even_when_confident():
    d = evaluate(_genome(economics={"list_price": 200.0}), audit_sampler=_never_audit)
    assert d.outcome is GateOutcome.REVIEW
    assert "brand" in d.hedge_tier_a and "unique_physical.era" in d.hedge_tier_a
    assert any(r.rule is RoutingRule.PRICE for r in d.routed)


def test_price_under_threshold_passes():
    d = evaluate(_genome(economics={"list_price": 120.0}), audit_sampler=_never_audit)
    assert d.outcome is GateOutcome.PASS


# -- rule 4: audit ----------------------------------------------------------

def test_audit_flags_queue_without_blocking_listing():
    d = evaluate(_genome(), audit_sampler=_always_audit)
    assert d.outcome is GateOutcome.PASS
    assert d.is_audit is True
    assert d.lists is True


# -- human facts are never gated --------------------------------------------

def test_human_asserted_brand_is_never_gated():
    intake = IntakeInput(sku="FH-1", human_facts={"brand": "Kapp & Peterson"},
                         economics={"list_price": 500.0})
    genome, _ = build_genome(intake, assets=_assets(stamping="ILLEGIBLE"))
    d = evaluate(genome, audit_sampler=_never_audit)
    # even at £500 with no corroboration, a human-typed brand is assertable
    assert "brand" in d.assertable_tier_a
    assert all(r.field_path != "brand" for r in d.routed)


# -- research-later ---------------------------------------------------------

def test_high_value_unverified_attribution_is_held_for_research():
    d = evaluate(
        _genome(brand="Dunhill", stamping="NO MATCH HERE"),  # brand routed by corroboration
        attribution_uplift=120.0,
        audit_sampler=_never_audit,
    )
    assert d.outcome is GateOutcome.RESEARCH_LATER
    assert d.lists is False


def test_small_uplift_still_lists_hedged():
    d = evaluate(
        _genome(brand="Dunhill", stamping="NO MATCH HERE"),
        attribution_uplift=20.0,
        audit_sampler=_never_audit,
    )
    assert d.outcome is GateOutcome.REVIEW
    assert d.lists is True
