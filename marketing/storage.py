"""Object storage — getting a rendered video somewhere Meta can fetch it.

Instagram does not accept file uploads: the Content Publishing API takes
a `video_url` that Meta's own servers fetch. So a reel rendered on the
PC has to be public before it can be posted, and that upload is the last
link in the chain between "video exists" and "video is live".

The host already exists and is already proven: Cloudflare R2 behind
`https://photos.faridunhill.com`, bucket `pipe-archive`, which the
existing reel publisher has been using in production. This module talks
to that same bucket rather than standing up anything new.

Keys mirror the local layout, so `marketing/out/2026-09-12/FH-TP-110-
vertical.mp4` lands at `<prefix>/2026-09-12/FH-TP-110-vertical.mp4` and
`MEDIA_BASE_URL` + that suffix is the url Meta fetches. One layout, two
places, nothing to reconcile.

Credentials come from the environment only (LAW 06):

    R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY,
    R2_BUCKET (default pipe-archive), R2_KEY_PREFIX (default marketing)
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_BUCKET = "pipe-archive"
DEFAULT_PREFIX = "marketing"

_CONTENT_TYPES = {
    ".mp4": "video/mp4", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".webp": "image/webp",
}


class UploadError(Exception):
    pass


@dataclass(frozen=True)
class UploadResult:
    key: str
    url: Optional[str]
    uploaded: bool          # False when it was already there
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.url is not None


class Uploader(ABC):
    @abstractmethod
    def upload(self, local_path: str | Path, key: str) -> UploadResult:
        """Put the file at `key`; return its public url."""


class NullUploader(Uploader):
    """Default. Records what would be uploaded and touches no network,
    so a dry run still exercises the whole path."""

    def __init__(self, base_url: Optional[str] = None):
        self._base = (base_url or "https://example.invalid").rstrip("/")
        self.uploaded: list[tuple[str, str]] = []

    def upload(self, local_path: str | Path, key: str) -> UploadResult:
        self.uploaded.append((str(local_path), key))
        return UploadResult(key=key, url=f"{self._base}/{key}", uploaded=False)


@dataclass(frozen=True)
class R2Config:
    endpoint_url: str
    access_key_id: str
    secret_access_key: str
    bucket: str = DEFAULT_BUCKET
    key_prefix: str = DEFAULT_PREFIX
    base_url: Optional[str] = None

    @classmethod
    def from_env(cls, env: Optional[dict] = None) -> Optional["R2Config"]:
        """None when not configured — the caller falls back to preparing
        content without publishing it, which is a valid state."""
        env = env if env is not None else os.environ
        endpoint = (env.get("R2_ENDPOINT_URL") or "").strip()
        key_id = (env.get("R2_ACCESS_KEY_ID") or "").strip()
        secret = (env.get("R2_SECRET_ACCESS_KEY") or "").strip()
        if not (endpoint and key_id and secret):
            return None
        return cls(
            endpoint_url=endpoint, access_key_id=key_id, secret_access_key=secret,
            bucket=(env.get("R2_BUCKET") or DEFAULT_BUCKET).strip(),
            key_prefix=(env.get("R2_KEY_PREFIX") or DEFAULT_PREFIX).strip().strip("/"),
            base_url=(env.get("MEDIA_BASE_URL") or "").strip().rstrip("/") or None,
        )


class R2Uploader(Uploader):
    """S3-compatible upload to Cloudflare R2.

    `client` is injected by the tests; in production boto3 is imported
    lazily so the rest of the system does not depend on it.
    """

    def __init__(self, config: R2Config, client=None):
        self._config = config
        self._client = client

    @property
    def client(self):
        if self._client is None:
            try:
                import boto3
            except ImportError as exc:
                raise UploadError(
                    "boto3 is not installed, so nothing can be uploaded to R2. "
                    "`pip install boto3`."
                ) from exc
            self._client = boto3.client(
                "s3",
                endpoint_url=self._config.endpoint_url,
                aws_access_key_id=self._config.access_key_id,
                aws_secret_access_key=self._config.secret_access_key,
            )
        return self._client

    def upload(self, local_path: str | Path, key: str) -> UploadResult:
        path = Path(local_path)
        if not path.exists():
            return UploadResult(key=key, url=None, uploaded=False,
                                error=f"no such file: {path}")

        full_key = f"{self._config.key_prefix}/{key}".lstrip("/") \
            if self._config.key_prefix else key
        content_type = _CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")

        try:
            self.client.upload_file(
                str(path), self._config.bucket, full_key,
                ExtraArgs={"ContentType": content_type},
            )
        except UploadError:
            raise
        except Exception as exc:            # boto3 raises many shapes
            return UploadResult(key=full_key, url=None, uploaded=False,
                                error=f"{type(exc).__name__}: {exc}")

        base = self._config.base_url
        url = f"{base}/{key}" if base else None
        return UploadResult(key=full_key, url=url, uploaded=True)


def key_for(video_path: str | Path, out_root: str | Path) -> str:
    """Local render path -> storage key, preserving the date folder.

    `marketing/out/2026-09-12/FH-TP-110-vertical.mp4` becomes
    `2026-09-12/FH-TP-110-vertical.mp4`, so the public url is exactly
    MEDIA_BASE_URL + "/" + this.
    """
    return Path(video_path).resolve().relative_to(
        Path(out_root).resolve()).as_posix()


def get_uploader(env: Optional[dict] = None) -> Optional[Uploader]:
    """A real uploader when R2 is configured, else None."""
    config = R2Config.from_env(env)
    return R2Uploader(config) if config else None
