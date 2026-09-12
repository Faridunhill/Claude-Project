"""Meta Graph API tests. No network: the transport is injected.

The headline case is the one Farid is actually hitting — Instagram
publishes fine, Facebook refuses — and the test proves the diagnostic
names the cause instead of reporting a generic failure.
"""

from __future__ import annotations

import json
import time

import pytest

from marketing.social.meta import (
    FB_PERMISSIONS,
    IG_PERMISSIONS,
    MetaClient,
    MetaConfig,
    MetaError,
    MetaPublisher,
    NotConfigured,
    diagnose,
    public_url_for,
)
from marketing.social.publisher import PostRequest

CONFIG = MetaConfig(
    access_token="tok", page_id="111", ig_user_id="222",
    media_base_url="https://media.example.com",
)


class StubTransport:
    """Scripted Graph API. Routes on the path tail so tests read as
    'this is what Meta said', not 'this is what urllib did'."""

    def __init__(self, permissions=None, accounts=None, fail=None, ig_status="FINISHED",
                 expires_in_days=None):
        self.permissions = permissions if permissions is not None else \
            list(IG_PERMISSIONS) + list(FB_PERMISSIONS)
        self.accounts = accounts if accounts is not None else [
            {"id": "111", "name": "Faridunhill", "access_token": "page-tok",
             "tasks": ["CREATE_CONTENT", "MANAGE"]}
        ]
        self.fail = fail or {}
        self.ig_status = ig_status
        self.expires_in_days = expires_in_days
        self.calls: list[tuple[str, str, dict]] = []

    def __call__(self, method: str, url: str, params: dict) -> dict:
        self.calls.append((method, url, params))
        for needle, error in self.fail.items():
            if needle in url:
                raise error
        if "debug_token" in url:
            if self.expires_in_days is None:
                return {"data": {"expires_at": 0}}       # never expires
            return {"data": {"expires_at": int(time.time() + self.expires_in_days * 86400)}}
        if url.endswith("/me"):
            return {"id": "9", "name": "Farid"}
        if url.endswith("/me/permissions"):
            return {"data": [{"permission": p, "status": "granted"} for p in self.permissions]}
        if url.endswith("/me/accounts"):
            return {"data": self.accounts}
        if url.endswith("/videos"):
            return {"id": "fb-post-1"}
        if url.endswith("/media"):
            return {"id": "container-1"}
        if url.endswith("/media_publish"):
            return {"id": "ig-post-1"}
        if url.endswith("/container-1"):
            return {"status_code": self.ig_status, "status": "detail"}
        if url.endswith("/111"):
            return {"instagram_business_account": {"id": "222"}}
        return {}


def _statuses(checks):
    return {subject: status for status, subject, _ in checks}


def _detail(checks, subject):
    return next(d for _, s, d in checks if s == subject)


# ── configuration ────────────────────────────────────────────────────

def test_missing_token_fails_loudly():
    with pytest.raises(NotConfigured):
        MetaConfig.from_env({})


def test_missing_token_degrades_to_none_for_the_runner():
    assert MetaConfig.from_env_or_none({}) is None


def test_config_reads_the_environment():
    config = MetaConfig.from_env({
        "META_ACCESS_TOKEN": "t", "META_PAGE_ID": "1",
        "MEDIA_BASE_URL": "https://x.example/", "META_API_VERSION": "v20.0",
    })
    assert config.page_id == "1"
    assert config.media_base_url == "https://x.example"   # trailing slash trimmed
    assert "v20.0" in config.url("me")


# ── the diagnostic: the case that matters ────────────────────────────

def test_instagram_works_facebook_refuses_is_explained():
    """The exact live symptom. A token holding every Instagram scope but
    not pages_manage_posts publishes to IG and is refused by Facebook."""
    transport = StubTransport(permissions=list(IG_PERMISSIONS) + ["pages_read_engagement"])
    checks = diagnose(CONFIG, transport)
    status = _statuses(checks)

    assert status["Instagram permissions"] == "OK"
    assert status["Facebook permissions"] == "FAIL"

    detail = _detail(checks, "Facebook permissions")
    assert "pages_manage_posts" in detail
    assert "Instagram never needed" in detail


def test_healthy_token_passes_every_check():
    checks = diagnose(CONFIG, StubTransport())
    assert "FAIL" not in {s for s, _, _ in checks}


def test_page_not_administered_is_named():
    transport = StubTransport(accounts=[{"id": "999", "name": "Other", "access_token": "t"}])
    assert _statuses(diagnose(CONFIG, transport))["Page token"] == "FAIL"
    assert "not among the Pages" in _detail(diagnose(CONFIG, transport), "Page token")


def test_page_without_create_content_is_flagged():
    """Right scopes, wrong role: an Analyst can read but never post."""
    transport = StubTransport(accounts=[
        {"id": "111", "name": "Faridunhill", "access_token": "p", "tasks": ["ANALYZE"]}
    ])
    checks = diagnose(CONFIG, transport)
    assert _statuses(checks)["Page token"] == "FAIL"
    assert "CREATE_CONTENT" in _detail(checks, "Page token")


def test_missing_media_base_url_is_a_failure():
    config = MetaConfig(access_token="t", page_id="111", ig_user_id="222")
    checks = diagnose(config, StubTransport())
    assert _statuses(checks)["Public media url"] == "FAIL"
    assert "does not accept file uploads" in _detail(checks, "Public media url")


def test_one_broken_check_does_not_hide_the_others():
    transport = StubTransport(fail={"me/accounts": MetaError("boom", code=190)})
    checks = diagnose(CONFIG, transport)
    assert _statuses(checks)["Pages"] == "FAIL"
    assert _statuses(checks)["Token"] == "OK"          # the rest still ran


def test_expired_token_reports_its_code():
    transport = StubTransport(fail={"/me": MetaError("Session expired", code=190)})
    assert "code=190" in _detail(diagnose(CONFIG, transport), "Token")


# ── page token: the trap ─────────────────────────────────────────────

def test_facebook_posts_with_the_page_token_not_the_user_token():
    """Posting to a Page with the User token fails in a way that reads
    like a permissions problem but is not one."""
    transport = StubTransport()
    MetaClient(CONFIG, transport).publish_facebook_video("https://v/x.mp4", "hello")
    post = [c for c in transport.calls if c[1].endswith("/videos")][0]
    assert post[2]["access_token"] == "page-tok"


def test_page_token_is_fetched_once_and_reused():
    transport = StubTransport()
    client = MetaClient(CONFIG, transport)
    client.page_token()
    client.page_token()
    assert sum(1 for c in transport.calls if c[1].endswith("/me/accounts")) == 1


# ── instagram publishing ─────────────────────────────────────────────

def test_instagram_creates_waits_then_publishes():
    transport = StubTransport()
    url = MetaClient(CONFIG, transport, sleeper=lambda s: None).publish_instagram_reel(
        "https://v/x.mp4", "caption")
    paths = [c[1] for c in transport.calls]
    assert any(p.endswith("/media") for p in paths)
    assert any(p.endswith("/container-1") for p in paths)      # waited for transcode
    assert any(p.endswith("/media_publish") for p in paths)
    assert "ig-post-1" in url


def test_instagram_error_status_does_not_publish():
    transport = StubTransport(ig_status="ERROR")
    with pytest.raises(MetaError, match="could not process"):
        MetaClient(CONFIG, transport, sleeper=lambda s: None).publish_instagram_reel(
            "https://v/x.mp4", "c")
    assert not any(c[1].endswith("/media_publish") for c in transport.calls)


def test_instagram_gives_up_rather_than_publishing_an_unfinished_video():
    transport = StubTransport(ig_status="IN_PROGRESS")
    with pytest.raises(MetaError, match="still processing"):
        MetaClient(CONFIG, transport, sleeper=lambda s: None).publish_instagram_reel(
            "https://v/x.mp4", "c", max_status_checks=3)


# ── the publisher ────────────────────────────────────────────────────

def test_local_path_becomes_a_public_url(tmp_path):
    out = tmp_path / "out"
    video = out / "2026-09-12" / "FH-TP-110-vertical.mp4"
    video.parent.mkdir(parents=True)
    video.write_bytes(b"x")
    assert public_url_for(str(video), out, "https://media.example.com") == \
        "https://media.example.com/2026-09-12/FH-TP-110-vertical.mp4"


def test_publisher_refuses_local_file_without_hosting(tmp_path):
    config = MetaConfig(access_token="t", page_id="111", ig_user_id="222")
    publisher = MetaPublisher(config, tmp_path, StubTransport())
    with pytest.raises(NotConfigured, match="MEDIA_BASE_URL"):
        publisher.post(PostRequest(sku="S", target="ig",
                                   video_path=str(tmp_path / "a.mp4"), caption="c"))


def test_publisher_refuses_profiles_and_groups(tmp_path):
    """Tier 2 is a ToS wall, enforced here as well as in SocialEngine."""
    publisher = MetaPublisher(CONFIG, tmp_path, StubTransport())
    for target in ("profile", "group:Pipe Collectors"):
        with pytest.raises(ValueError, match="page and ig only"):
            publisher.post(PostRequest(sku="S", target=target,
                                       video_path="https://v/x.mp4", caption="c"))


def test_publisher_routes_each_target(tmp_path):
    transport = StubTransport()
    publisher = MetaPublisher(CONFIG, tmp_path, transport, sleeper=lambda s: None)
    assert "facebook.com" in publisher.post(
        PostRequest(sku="S", target="page", video_path="https://v/x.mp4", caption="c"))
    assert "instagram.com" in publisher.post(
        PostRequest(sku="S", target="ig", video_path="https://v/x.mp4", caption="c"))


# ── config precedence: never ask for a pasted secret ─────────────────

def test_ids_come_from_meta_json(tmp_path):
    """The working setup already stores these; re-asking invites typos."""
    meta = tmp_path / "meta.json"
    meta.write_text(json.dumps({
        "page_id": "111774180543965", "ig_user_id": "17841426740134023",
        "ig_username": "faridunhill",
    }))
    config = MetaConfig.from_env({
        "META_ACCESS_TOKEN": "tok", "META_CONFIG_FILE": str(meta)})
    assert config.page_id == "111774180543965"
    assert config.ig_user_id == "17841426740134023"
    assert config.source == str(meta)


def test_environment_overrides_the_file(tmp_path):
    meta = tmp_path / "meta.json"
    meta.write_text(json.dumps({"page_id": "from-file"}))
    config = MetaConfig.from_env({
        "META_ACCESS_TOKEN": "tok", "META_CONFIG_FILE": str(meta),
        "META_PAGE_ID": "from-env"})
    assert config.page_id == "from-env"


def test_token_command_keeps_the_secret_off_the_screen():
    """The vault hook: a command prints the token, nobody pastes it."""
    config = MetaConfig.from_env({"META_TOKEN_COMMAND": "printf secret-value"})
    assert config.access_token == "secret-value"


def test_failing_token_command_is_reported_not_swallowed():
    with pytest.raises(NotConfigured, match="exited"):
        MetaConfig.from_env({"META_TOKEN_COMMAND": "exit 3"})


def test_empty_token_command_is_rejected():
    with pytest.raises(NotConfigured, match="printed nothing"):
        MetaConfig.from_env({"META_TOKEN_COMMAND": "true"})


def test_missing_token_names_the_vault_route_first():
    with pytest.raises(NotConfigured) as exc:
        MetaConfig.from_env({"META_CONFIG_FILE": "/nonexistent.json"})
    assert "META_TOKEN_COMMAND" in str(exc.value)


def test_corrupt_meta_json_does_not_crash(tmp_path):
    meta = tmp_path / "meta.json"
    meta.write_text("{not json")
    assert MetaConfig.from_env({
        "META_ACCESS_TOKEN": "t", "META_CONFIG_FILE": str(meta)}).page_id is None


# ── token expiry: the scheduled outage ───────────────────────────────

def _expiring_in(days: float) -> StubTransport:
    """Python resolves __call__ on the TYPE, so patching the instance
    does nothing — the stub has to know about expiry itself."""
    return StubTransport(expires_in_days=days)


def test_token_expiring_inside_two_weeks_is_a_failure():
    """A ~60-day token with no never-expiring Page token behind it is a
    scheduled outage; 14 days out it stops being a warning."""
    checks = diagnose(CONFIG, _expiring_in(14))
    assert _statuses(checks)["Token expiry"] == "FAIL"
    assert "never-expiring" in _detail(checks, "Token expiry")


def test_token_expiring_next_month_only_warns():
    assert _statuses(diagnose(CONFIG, _expiring_in(25)))["Token expiry"] == "WARN"


def test_healthy_expiry_passes():
    assert _statuses(diagnose(CONFIG, _expiring_in(90)))["Token expiry"] == "OK"


def test_never_expiring_token_passes():
    checks = diagnose(CONFIG, StubTransport())
    assert _statuses(checks)["Token expiry"] == "OK"
    assert "does not expire" in _detail(checks, "Token expiry")


# ── the confirmed live symptom ───────────────────────────────────────

def test_no_pages_names_business_management_and_the_crosspost_route():
    """/me/accounts returns nothing despite pages_show_list. Confirmed
    on the PC, and no amount of retrying fixes it."""
    checks = diagnose(CONFIG, StubTransport(accounts=[]))
    detail = _detail(checks, "Pages")
    assert "business_management" in detail
    assert "Share to Facebook" in detail


def test_unofferable_permission_points_at_the_app_use_case():
    transport = StubTransport(permissions=list(IG_PERMISSIONS) + ["pages_read_engagement"])
    detail = _detail(diagnose(CONFIG, transport), "Facebook permissions")
    assert "use case" in detail and "no code change" in detail
