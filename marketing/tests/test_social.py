"""P2.7 test suite — captions, video command, tiers, walls, placements."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from marketing.social import (
    ChannelPaused,
    DryRunPublisher,
    FrequencyWall,
    PostRequest,
    SocialEngine,
    VideoSpec,
    build_command,
    build_video,
    generate_caption,
    load_style,
)
from marketing.tests.test_expression import effective_hedged, effective_verified

STYLE_PATH = Path(__file__).resolve().parents[1] / "social" / "style_faridunhill.yaml"
NOW = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)


# ----------------------------------------------------------------- captions

def test_caption_asserts_verified_brand():
    cap = generate_caption(effective_verified())
    assert "Chacom Gentleman 836" in cap.text
    assert "chacom" in cap.hashtags
    cap.full().encode("ascii")  # ASCII-safe


def test_caption_never_asserts_hedged_brand():
    cap = generate_caption(effective_hedged())
    assert "Chacom" not in cap.text
    assert "chacom" not in cap.hashtags
    assert "Dublin" in cap.text


def test_sold_archive_caption_kind():
    cap = generate_caption(effective_verified(), kind="sold_archive")
    assert "From the archive" in cap.text and "encyclopedia" in cap.text


# -------------------------------------------------------------------- video

def test_video_command_built_with_style_and_overlays(tmp_path):
    style = load_style(STYLE_PATH)
    spec = VideoSpec(
        sku="FH-TP-034",
        photos=["p/01.jpg", "p/02.jpg", "p/03.jpg"],
        title_overlay="Chacom Gentleman 836",
        fmt="vertical",
        music_path="music/track1.mp3",
    )
    cmd, out = build_command(spec, style, tmp_path)
    joined = " ".join(cmd)
    assert "1080x1920" in joined            # vertical format
    assert "FARIDUNHILL" in joined          # brand overlay
    assert "Chacom Gentleman 836" in joined # name overlay
    assert "music/track1.mp3" in cmd        # house music input
    assert out.name == "FH-TP-034-vertical.mp4"


def test_video_manifest_logs_license_and_is_not_synthetic(tmp_path):
    style = load_style(STYLE_PATH)
    spec = VideoSpec(sku="FH-1", photos=["a.jpg"], title_overlay="X", fmt="square")
    result = build_video(spec, style, tmp_path)   # no ffmpeg here -> not rendered
    assert result.manifest["music_license_source"] == "meta_sound_collection"
    assert result.manifest["is_synthetic"] is False   # real photos, placement-law safe
    assert result.rendered is False and result.command


# ------------------------------------------------------------ tiers + walls

@pytest.fixture()
def engine(tmp_path):
    pub = DryRunPublisher()
    eng = SocialEngine(tmp_path / "social.db", pub, max_posts_per_group_per_day=1)
    yield eng, pub
    eng.close()


def req(target: str, sku: str = "FH-TP-034") -> PostRequest:
    return PostRequest(sku=sku, target=target, video_path="v.mp4", caption="cap")


def test_tier1_only_page_and_ig(engine):
    eng, pub = engine
    url = eng.publish_tier1(req("page"), now=NOW)
    assert url.startswith("dryrun://page")
    with pytest.raises(ValueError):
        eng.publish_tier1(req("group:pipe-collectors"), now=NOW)  # ToS wall
    with pytest.raises(ValueError):
        eng.publish_tier1(req("profile"), now=NOW)


def test_group_frequency_wall(engine):
    eng, _ = engine
    pid = eng.queue_tier2(req("group:pipe-collectors"), now=NOW)
    eng.mark_posted(pid, "https://fb/1", now=NOW)
    with pytest.raises(FrequencyWall):                 # second same-day queue refused
        eng.queue_tier2(req("group:pipe-collectors", sku="FH-2"), now=NOW)
    # different group, same day: fine
    eng.queue_tier2(req("group:estate-pipes", sku="FH-2"), now=NOW)


def test_meta_warning_pauses_channel_one_email_no_retries(engine):
    eng, _ = engine
    email = eng.pause_channel("meta", "account warning received")
    assert "PAUSED" in email["subject"]
    with pytest.raises(ChannelPaused):
        eng.publish_tier1(req("page"), now=NOW)
    with pytest.raises(ChannelPaused):
        eng.queue_tier2(req("group:x"), now=NOW)
    eng.unpause_channel("meta")
    assert eng.publish_tier1(req("page"), now=NOW)     # resumes only after Farid


def test_placements_index(engine):
    eng, _ = engine
    eng.publish_tier1(req("page"), now=NOW)
    pid = eng.queue_tier2(req("group:pipe-collectors"), now=NOW)
    eng.mark_posted(pid, "https://fb/post/9", now=NOW)
    places = eng.placements_for("FH-TP-034")
    assert len(places) == 2
    assert {p["target"] for p in places} == {"page", "group:pipe-collectors"}
    assert all(p["license_source"] for p in places)    # license logged per video


def test_ready_package_queue_flow(engine):
    eng, _ = engine
    pid = eng.queue_tier2(req("group:pipe-collectors"), now=NOW)
    ready = eng.ready_packages()
    assert ready and ready[0]["package_id"] == pid
    eng.mark_posted(pid, "https://fb/1", now=NOW)
    assert eng.ready_packages() == []
    with pytest.raises(KeyError):
        eng.mark_posted(pid, "again", now=NOW)         # no double-posting
