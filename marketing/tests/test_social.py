"""P2.7 social + reel generator tests."""

from __future__ import annotations

from marketing.expression.social import generate_reel, generate_social
from marketing.genome.adapter_itemassets import ItemAssets, MediaAsset, VisionClaim
from marketing.genome.gate import evaluate
from marketing.genome.intake import IntakeInput, build_genome
from marketing.genome.vocab import MediaRole


def _no_audit(sku):
    return False


def _genome(assets=None, **facts):
    economics = facts.pop("economics", None)
    why = facts.pop("why_special", None)
    intake = IntakeInput(sku="FH-1", why_special=why, economics=economics, human_facts=facts)
    g, _ = build_genome(intake, assets=assets)
    return g


def test_instagram_and_tiktok_get_hashtags():
    g = _genome(brand="Peterson", model_line="XL 90S")
    d = evaluate(g, audit_sampler=_no_audit)
    for ch in ("instagram", "tiktok"):
        post = generate_social(g, d, channel=ch)
        assert "peterson" in post.hashtags
        assert "estatepipe" in post.hashtags


def test_x_caption_respects_280():
    g = _genome(brand="Dunhill", why_special="A Cumberland sandblast with its original sterling band, " * 6,
                economics={"list_price": 425.0, "currency": "USD"})
    d = evaluate(g, audit_sampler=_no_audit)
    post = generate_social(g, d, channel="x")
    assert len(post.caption) <= 280


def test_unasserted_brand_is_not_hashtagged():
    assets = ItemAssets(
        sku="FH-1",
        vision_claims=[VisionClaim(field_path="brand", value="Dunhill", confidence=0.99)],
        stamping_ocr="NO MAKER MARK",
    )
    g = _genome(assets=assets)
    d = evaluate(g, audit_sampler=_no_audit)          # corroboration fails
    post = generate_social(g, d, channel="tiktok")
    assert "dunhill" not in post.hashtags
    assert "attributed to dunhill" in post.caption.lower()


def test_caption_includes_price_and_cta():
    g = _genome(brand="Vauen", economics={"list_price": 95.0, "currency": "USD"})
    d = evaluate(g, audit_sampler=_no_audit)
    post = generate_social(g, d, channel="instagram")
    assert "$95" in post.caption
    assert "faridunhill.com" in post.caption


def test_compliance_note_present_for_tobacco_item():
    g = _genome(brand="Stanwell")
    d = evaluate(g, audit_sampler=_no_audit)
    post = generate_social(g, d)
    assert post.eligibility_note is not None


def test_reel_is_vertical_and_built_from_real_photos():
    assets = ItemAssets(
        sku="FH-1",
        media=[
            MediaAsset(url="hero.jpg", role=MediaRole.HERO, seq=0),
            MediaAsset(url="stamp.jpg", role=MediaRole.STAMPING, seq=1),
        ],
    )
    g = _genome(brand="Peterson", economics={"list_price": 110.0, "currency": "USD"}, assets=assets)
    d = evaluate(g, audit_sampler=_no_audit)
    reel = generate_reel(g, d, target_seconds=30.0)
    assert reel.orientation == "9:16"
    urls = [s.image_url for s in reel.shots if s.image_url]
    assert "hero.jpg" in urls and "stamp.jpg" in urls
    # ~30s reel, built by repeating the walk-around across the photos
    assert 27 <= reel.duration_s <= 33
    # the only on-screen caption is the brand name (no price/CTA burned in)
    assert reel.title.startswith("Peterson")
    assert all(s.overlay == reel.title for s in reel.shots)
    # placement law noted
    assert any("PLACEMENT LAW" in n for n in reel.notes)


def test_reel_without_photos_is_storyboard_only():
    g = _genome(brand="GBD", model_line="Cutty")
    d = evaluate(g, audit_sampler=_no_audit)
    reel = generate_reel(g, d)
    assert any("storyboard only" in n for n in reel.notes)
