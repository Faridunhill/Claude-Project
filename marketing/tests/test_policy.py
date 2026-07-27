"""Standing-wall tests — POLICY-META-ADS-001 and the free-render vendor.

These tests exist so the walls cannot be silently regressed. If someone
(human or agent) flips `meta_paid_ads.enabled` to true or wires a paid
visual vendor, these fail loudly and say why.
"""

import pytest

from marketing.policy import (
    PaidPromotionProhibited,
    SpendCeiling,
    load_walls,
)
from marketing.social import DryRunPublisher, SocialEngine


# ------------------------------------------------ POLICY-META-ADS-001

def test_meta_paid_ads_are_prohibited_in_shipped_config():
    """The shipped control.yaml must never permit paid Meta promotion."""
    walls = load_walls()
    assert walls.meta_paid_ads_enabled is False
    with pytest.raises(PaidPromotionProhibited):
        walls.assert_meta_paid_promotion_allowed()


def test_boost_request_is_refused_at_the_choke_point(tmp_path):
    eng = SocialEngine(tmp_path / "social.db", DryRunPublisher())
    with pytest.raises(PaidPromotionProhibited):
        eng.request_boost("FH-TP-034", "page", budget=5.00)
    eng.close()


def test_organic_posting_still_works_alongside_the_ad_ban(tmp_path):
    """The ban is on PAID promotion only — organic is the whole strategy."""
    from marketing.social import PostRequest

    eng = SocialEngine(tmp_path / "social.db", DryRunPublisher())
    url = eng.publish_tier1(
        PostRequest(sku="FH-1", target="page", video_path="v.mp4", caption="c")
    )
    assert url.startswith("dryrun://page")
    eng.close()


def test_missing_config_keys_default_to_prohibited(tmp_path):
    """Safe default: an absent key never means 'allowed'."""
    cfg = tmp_path / "control.yaml"
    cfg.write_text("version: 2\ncurrency: GBP\n", encoding="utf-8")
    walls = load_walls(cfg)
    assert walls.meta_paid_ads_enabled is False
    assert walls.marketplace_promotion_enabled is False
    assert walls.visual_paid_vendors_enabled is False


# ------------------------------------------------- free render vendor

def test_visual_vendor_is_the_free_local_renderer():
    walls = load_walls()
    assert walls.visual_vendor == "local_ffmpeg"
    assert walls.visual_paid_vendors_enabled is False
    assert walls.visual_monthly_ceiling == 0.00
    # The free path costs nothing and must pass the guard.
    walls.assert_visual_spend_allowed(cost=0.0)


def test_any_paid_asset_charge_is_refused():
    walls = load_walls()
    with pytest.raises(SpendCeiling):
        walls.assert_visual_spend_allowed(cost=0.50)


def test_ceilings_enforced_when_a_paid_vendor_is_someday_enabled(tmp_path):
    """If Farid ever turns a vendor on, per-asset and monthly ceilings
    must still bite."""
    cfg = tmp_path / "control.yaml"
    cfg.write_text(
        "version: 2\ncurrency: GBP\n"
        "visual_generation:\n"
        "  vendor: some_vendor\n"
        "  paid_vendors_enabled: true\n"
        "  max_cost_per_asset: 2.00\n"
        "  monthly_ceiling: 50.00\n",
        encoding="utf-8",
    )
    walls = load_walls(cfg)
    walls.assert_visual_spend_allowed(cost=1.50, month_to_date=10.00)   # fine
    with pytest.raises(SpendCeiling):
        walls.assert_visual_spend_allowed(cost=2.50)                    # per-asset
    with pytest.raises(SpendCeiling):
        walls.assert_visual_spend_allowed(cost=1.00, month_to_date=49.50)  # monthly


# --------------------------------------------------- marketplace pot

def test_marketplace_promotion_is_separate_from_meta_and_off_by_default():
    """Etsy/eBay promoted listings are a different platform with
    different rules — never conflated with the Meta ad ban."""
    walls = load_walls()
    assert walls.marketplace_promotion_enabled is False
    assert walls.marketplace_monthly_ceiling == 0.00


def test_group_frequency_wall_is_read_from_control_yaml(tmp_path):
    eng = SocialEngine(tmp_path / "social.db", DryRunPublisher())
    assert eng._group_wall == load_walls().max_posts_per_group_per_day
    eng.close()
