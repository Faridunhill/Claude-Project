"""P2.6 listing-generator tests — one guarantee per test."""

from __future__ import annotations

from marketing.expression.listing import generate_listing
from marketing.genome.adapter_itemassets import ItemAssets, MediaAsset, VisionClaim
from marketing.genome.gate import evaluate
from marketing.genome.intake import IntakeInput, build_genome
from marketing.genome.vocab import (
    ConditionGrade,
    EraBasis,
    FlawCode,
    MediaRole,
    ProductType,
)


def _no_audit(sku):
    return False


def _genome(**human_facts_and_kw):
    economics = human_facts_and_kw.pop("economics", None)
    why = human_facts_and_kw.pop("why_special", None)
    assets = human_facts_and_kw.pop("assets", None)
    intake = IntakeInput(
        sku="FH-1",
        why_special=why,
        economics=economics,
        human_facts=human_facts_and_kw,
    )
    genome, _ = build_genome(intake, assets=assets)
    return genome


# -- assert path ------------------------------------------------------------

def test_human_brand_is_asserted_in_title_and_tags():
    g = _genome(brand="Dunhill", model_line="Cumberland 41031")
    d = evaluate(g, audit_sampler=_no_audit)
    draft = generate_listing(g, d)
    assert draft.title.startswith("Dunhill")
    assert "dunhill" in draft.tags


# -- hedge path -------------------------------------------------------------

def test_uncorroborated_vision_brand_is_hedged_not_asserted():
    assets = ItemAssets(
        sku="FH-1",
        vision_claims=[VisionClaim(field_path="brand", value="Dunhill", confidence=0.99)],
        stamping_ocr="NO MAKER MARK VISIBLE",
    )
    g = _genome(assets=assets)
    d = evaluate(g, audit_sampler=_no_audit)          # corroboration fails -> hedge
    draft = generate_listing(g, d)
    assert "brand" in draft.hedged
    assert "attributed to dunhill" in draft.description.lower()
    assert "dunhill" not in draft.tags                # never tag an unasserted maker
    assert "attributed" in draft.title.lower()


# -- honesty layer ----------------------------------------------------------

def test_every_flaw_is_disclosed():
    g = _genome(
        **{
            "unique_physical.condition_grade": ConditionGrade.GOOD,
            "unique_physical.flaws": [FlawCode.RIM_DARKENING, FlawCode.TOOTH_MARKS_LIGHT],
        }
    )
    d = evaluate(g, audit_sampler=_no_audit)
    draft = generate_listing(g, d)
    assert "darkening to the rim" in draft.description
    assert "tooth marks" in draft.description
    assert len(draft.disclosures) == 2


# -- era assert vs hedge ----------------------------------------------------

def test_hard_basis_era_is_asserted_as_circa():
    g = _genome(
        **{"unique_physical.era": {"min_year": 1955, "max_year": 1962, "basis": EraBasis.HALLMARK}}
    )
    d = evaluate(g, audit_sampler=_no_audit)
    draft = generate_listing(g, d)
    assert "circa 1955–1962" in draft.description


def test_soft_basis_era_is_hedged_to_a_decade():
    g = _genome(
        **{"unique_physical.era": {"min_year": 1955, "max_year": 1962, "basis": EraBasis.STYLE}}
    )
    d = evaluate(g, audit_sampler=_no_audit)
    draft = generate_listing(g, d)
    assert "1950s" in draft.description
    assert "circa" not in draft.description


# -- graceful degradation ---------------------------------------------------

def test_missing_facts_become_gaps_not_fabrications():
    g = _genome(brand="Peterson")   # no era, no grade, no photos, no price
    d = evaluate(g, audit_sampler=_no_audit)
    draft = generate_listing(g, d)
    assert any("era" in gap for gap in draft.gaps)
    assert any("condition grade" in gap for gap in draft.gaps)
    assert any("photos" in gap for gap in draft.gaps)


# -- media ordering ---------------------------------------------------------

def test_hero_photo_leads_image_order():
    assets = ItemAssets(
        sku="FH-1",
        media=[
            MediaAsset(url="stamp.jpg", role=MediaRole.STAMPING, seq=0),
            MediaAsset(url="hero.jpg", role=MediaRole.HERO, seq=0),
        ],
    )
    g = _genome(brand="Stanwell", assets=assets)
    d = evaluate(g, audit_sampler=_no_audit)
    draft = generate_listing(g, d)
    assert draft.image_order[0] == "hero.jpg"
    assert draft.alt_texts["hero.jpg"].endswith("main view")


# -- channel title limits ---------------------------------------------------

def test_ebay_title_respects_80_char_limit():
    g = _genome(brand="Peterson", model_line="Sterling Silver XL 90S Smooth Bent Billiard Extra Long Descriptor Here")
    d = evaluate(g, audit_sampler=_no_audit)
    draft = generate_listing(g, d, channel="ebay")
    assert len(draft.title) <= 80
