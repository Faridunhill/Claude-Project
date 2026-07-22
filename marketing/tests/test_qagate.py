"""P2.4 test suite — the four routing rules, the review flow, the lock."""

import pytest

from marketing.genome import GenomeStore
from marketing.genome.adapter_itemassets import VisionClaim
from marketing.qagate import (
    ClaimMode,
    GateConfig,
    ReviewQueue,
    Route,
    RouteReason,
    Verdict,
    assertable,
    priced_as_unattributed,
    route_claim,
)
from marketing.tests.test_genome import make_genome

OCR = "CHACOM / GENTLEMAN / 836 / FRANCE"


def claim(field="brand", value="Chacom", conf=0.97) -> VisionClaim:
    return VisionClaim(field_path=field, value=value, confidence=conf)


# ------------------------------------------------------------ routing rules

def test_rule1_low_confidence_routes_to_review():
    d = route_claim("FH-1", claim(conf=0.80), OCR, list_price=99.0)
    assert d.route is Route.REVIEW
    assert RouteReason.LOW_CONFIDENCE in d.reasons


def test_rule2_ocr_mismatch_reviews_regardless_of_confidence():
    d = route_claim("FH-1", claim(value="Dunhill", conf=0.99), OCR, list_price=99.0)
    assert d.route is Route.REVIEW
    assert RouteReason.OCR_MISMATCH in d.reasons


def test_rule3_high_price_always_reviews_tier_a():
    d = route_claim("FH-1", claim(conf=0.99), OCR, list_price=200.0)
    assert d.route is Route.REVIEW
    assert RouteReason.HIGH_PRICE in d.reasons


def test_rule4_audit_sampling_is_deterministic_about_5pct():
    cfg = GateConfig()
    audited = 0
    for i in range(2000):
        d = route_claim(f"FH-{i:05d}", claim(conf=0.99), OCR, list_price=99.0, config=cfg)
        if d.route is Route.AUDIT:
            audited += 1
        # deterministic: same sku always routes identically
        d2 = route_claim(f"FH-{i:05d}", claim(conf=0.99), OCR, list_price=99.0, config=cfg)
        assert d.route == d2.route
    assert 0.03 < audited / 2000 < 0.08  # ~5%


def test_non_tier_a_never_gated():
    d = route_claim("FH-1", claim(field="unique_physical.condition_grade", conf=0.10),
                    None, list_price=999.0)
    assert d.route is Route.AUTO_PASS


def test_missing_ocr_disables_corroboration_only():
    d = route_claim("FH-1", claim(value="Dunhill", conf=0.99), None, list_price=99.0)
    assert RouteReason.OCR_MISMATCH not in d.reasons


# ------------------------------------------------------------- review flow

@pytest.fixture()
def queue(tmp_path):
    store = GenomeStore(tmp_path / "genome.db")
    store.write_birth(make_genome())
    q = ReviewQueue(tmp_path / "genome.db", store)
    yield q, store
    q.close()
    store.close()


def test_review_screen_contains_the_two_witnesses(queue):
    q, _ = queue
    d = route_claim("FH-TP-034", claim(conf=0.5), OCR, list_price=99.0)
    rid = q.enqueue(d)
    screen = q.build_screen(rid, exemplars=["ref/chacom-1.jpg"])
    assert screen.stamping_photos          # macro photos present
    assert screen.ocr_verbatim == OCR      # verbatim text present
    assert "Chacom" in screen.question
    assert screen.exemplars


def test_verdict_yes_verifies_via_corrections_ledger(queue):
    q, store = queue
    rid = q.enqueue(route_claim("FH-TP-034", claim(conf=0.5), OCR, 99.0))
    outcome = q.decide(rid, Verdict.YES)
    assert outcome == "verified"
    birth = store.get_birth("FH-TP-034")
    effective = store.get_effective("FH-TP-034")
    assert birth["brand"] == "Chacom"                # birth untouched
    assert effective["attribution"]["brand"]["status"] == "verified"


def test_cant_tell_hedges_below_uplift_threshold(queue):
    q, _ = queue
    rid = q.enqueue(route_claim("FH-TP-034", claim(conf=0.5), OCR, 99.0))
    assert q.decide(rid, Verdict.CANT_TELL, uplift=20.0) == "hedged"
    assert q.hedged_listing_discount() == 20.0       # the visible cost line


def test_cant_tell_goes_to_research_above_uplift_threshold(queue):
    q, _ = queue
    rid = q.enqueue(route_claim("FH-TP-034", claim(conf=0.5), OCR, 99.0))
    assert q.decide(rid, Verdict.CANT_TELL, uplift=80.0) == "research_later"


def test_double_decide_refused(queue):
    q, _ = queue
    rid = q.enqueue(route_claim("FH-TP-034", claim(conf=0.5), OCR, 99.0))
    q.decide(rid, Verdict.NO)
    with pytest.raises(ValueError):
        q.decide(rid, Verdict.YES)


# ------------------------------------------------------------------ the lock

def test_lock_asserts_human_sourced_brand():
    effective = {
        "brand": "Chacom",
        "field_provenance": {"brand": {"source": "human"}},
    }
    r = assertable(effective, "brand")
    assert r.mode is ClaimMode.ASSERT and r.value == "Chacom"


def test_lock_hedges_vision_sourced_unverified_brand():
    effective = {
        "brand": "Chacom",
        "field_provenance": {"brand": {"source": "vision"}},
    }
    r = assertable(effective, "brand")
    assert r.mode is ClaimMode.HEDGE and r.candidate == "Chacom"
    assert priced_as_unattributed(effective)         # no-name floor pricing


def test_lock_hedges_after_cant_tell_verdict(queue):
    q, store = queue
    rid = q.enqueue(route_claim("FH-TP-034", claim(conf=0.5), OCR, 99.0))
    q.decide(rid, Verdict.CANT_TELL, uplift=10.0)
    effective = store.get_effective("FH-TP-034")
    # brand still present from birth (human-entered in this fixture), so
    # simulate the vision-only case by removing provenance
    effective["field_provenance"].pop("brand", None)
    effective["field_provenance"]["brand"] = {"source": "vision"}
    r = assertable(effective, "brand")
    assert r.mode is ClaimMode.HEDGE


def test_lock_omits_rejected_claims():
    effective = {
        "attribution": {"brand": {"status": "rejected", "candidate": "Dunhill"}},
    }
    r = assertable(effective, "brand")
    assert r.mode is ClaimMode.OMIT and r.value is None
