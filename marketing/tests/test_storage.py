"""Object storage tests. No network: the S3 client is injected.

Why this exists: Instagram fetches `video_url` rather than accepting an
upload, so an unhosted render can be prepared but never posted. Getting
the key layout wrong means Meta fetches a 404 and the post silently
fails.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from marketing.storage import (
    DEFAULT_BUCKET,
    NullUploader,
    R2Config,
    R2Uploader,
    UploadError,
    get_uploader,
    key_for,
)

ENV = {
    "R2_ENDPOINT_URL": "https://acc.r2.cloudflarestorage.com",
    "R2_ACCESS_KEY_ID": "key",
    "R2_SECRET_ACCESS_KEY": "secret",
    "MEDIA_BASE_URL": "https://photos.faridunhill.com/marketing",
}


class StubS3:
    def __init__(self, fail: Exception | None = None):
        self.fail = fail
        self.calls: list[tuple] = []

    def upload_file(self, path, bucket, key, ExtraArgs=None):
        if self.fail:
            raise self.fail
        self.calls.append((path, bucket, key, ExtraArgs))


@pytest.fixture
def video(tmp_path: Path) -> tuple[Path, Path]:
    out = tmp_path / "out"
    path = out / "2026-09-12" / "FH-TP-110-vertical.mp4"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"video")
    return out, path


# ── key layout ───────────────────────────────────────────────────────

def test_key_preserves_the_date_folder(video):
    out, path = video
    assert key_for(path, out) == "2026-09-12/FH-TP-110-vertical.mp4"


def test_key_and_base_url_reconstruct_the_public_url(video):
    """The url Meta fetches must be exactly base + "/" + key, or it 404s
    and the post fails with no obvious cause."""
    from marketing.social.meta import public_url_for

    out, path = video
    assert (f"{ENV['MEDIA_BASE_URL']}/{key_for(path, out)}"
            == public_url_for(str(path), out, ENV["MEDIA_BASE_URL"]))


# ── configuration ────────────────────────────────────────────────────

def test_unconfigured_returns_none():
    assert R2Config.from_env({}) is None
    assert get_uploader({}) is None


def test_partial_credentials_are_not_configured():
    assert R2Config.from_env({"R2_ENDPOINT_URL": "https://x"}) is None


def test_defaults_match_the_existing_bucket():
    config = R2Config.from_env(ENV)
    assert config.bucket == DEFAULT_BUCKET == "pipe-archive"
    assert config.key_prefix == "marketing"


def test_prefix_slashes_are_normalised():
    assert R2Config.from_env({**ENV, "R2_KEY_PREFIX": "/reels/"}).key_prefix == "reels"


# ── uploading ────────────────────────────────────────────────────────

def test_upload_writes_under_the_prefix(video):
    out, path = video
    client = StubS3()
    result = R2Uploader(R2Config.from_env(ENV), client).upload(path, key_for(path, out))
    assert result.ok and result.uploaded
    _, bucket, key, extra = client.calls[0]
    assert bucket == "pipe-archive"
    assert key == "marketing/2026-09-12/FH-TP-110-vertical.mp4"
    assert extra["ContentType"] == "video/mp4"


def test_public_url_omits_the_prefix(video):
    """The prefix lives in the key; the base url already includes it.
    Doubling it would produce .../marketing/marketing/..."""
    out, path = video
    result = R2Uploader(R2Config.from_env(ENV), StubS3()).upload(path, key_for(path, out))
    assert result.url == f"{ENV['MEDIA_BASE_URL']}/2026-09-12/FH-TP-110-vertical.mp4"
    assert result.url.count("/marketing/") == 1


def test_missing_file_is_reported_not_raised(tmp_path):
    result = R2Uploader(R2Config.from_env(ENV), StubS3()).upload(tmp_path / "gone.mp4", "k")
    assert not result.ok and "no such file" in result.error


def test_upload_failure_degrades_rather_than_aborting(video):
    """One bad upload must not take down the nightly run."""
    out, path = video
    client = StubS3(fail=RuntimeError("connection reset"))
    result = R2Uploader(R2Config.from_env(ENV), client).upload(path, key_for(path, out))
    assert not result.ok and "connection reset" in result.error


def test_missing_boto3_says_so_plainly():
    config = R2Config.from_env(ENV)
    uploader = R2Uploader(config)
    import builtins

    real_import = builtins.__import__

    def no_boto3(name, *args, **kwargs):
        if name == "boto3":
            raise ImportError("no boto3")
        return real_import(name, *args, **kwargs)

    builtins.__import__ = no_boto3
    try:
        with pytest.raises(UploadError, match="boto3"):
            uploader.upload(__file__, "k")
    finally:
        builtins.__import__ = real_import


# ── the dry-run path ─────────────────────────────────────────────────

def test_null_uploader_records_without_network(video):
    out, path = video
    uploader = NullUploader("https://example.test")
    result = uploader.upload(path, key_for(path, out))
    assert result.ok and not result.uploaded
    assert uploader.uploaded == [(str(path), "2026-09-12/FH-TP-110-vertical.mp4")]
