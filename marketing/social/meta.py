"""Meta Graph API — live Tier 1 publishing, and the diagnostic that
explains why a channel refuses.

WHY THIS FILE EXISTS. Instagram publishing already works; Facebook
refuses. That asymmetry is diagnosable, because the two surfaces need
DIFFERENT permissions and different token types:

    Instagram publishing : instagram_basic, instagram_content_publish,
                           pages_show_list, pages_read_engagement
    Facebook Page posting: pages_manage_posts, pages_read_engagement,
                           pages_show_list   <-- pages_manage_posts is
                           the one IG never needed

So a token that publishes to Instagram perfectly can be missing exactly
the one permission Facebook requires, and Meta reports that as a generic
error. `diagnose()` asks the Graph API directly which permissions the
token actually holds and which Page tokens it can mint, and prints the
answer instead of a guess.

THE TOKEN TRAP. Facebook Page publishing must use a PAGE access token,
not the User token — a User token returns an error that reads like a
permissions problem but is not one. This module always exchanges for the
Page token via /me/accounts before posting, and the diagnostic reports
whether that exchange works.

THE PUBLIC-URL CONSTRAINT (the one that surprises people). The Instagram
Content Publishing API does not accept file uploads. It takes a
`video_url` that Meta's servers fetch themselves, so a video sitting on
the PC cannot be posted until it is reachable over the public internet.
Facebook can take a local upload, but this module uses `file_url` for
both so there is one hosting story, not two. Set MEDIA_BASE_URL to
wherever `marketing/out/` is served from.

Credentials come from environment variables ONLY — never the repo, never
shared with another business (LAW 06).

    META_ACCESS_TOKEN    long-lived user token
    META_PAGE_ID         the Facebook Page id
    META_IG_USER_ID      the Instagram Business account id (optional:
                         discovered from the Page when omitted)
    MEDIA_BASE_URL       public base url serving marketing/out/
    META_API_VERSION     defaults below
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from .publisher import PostRequest, Tier1Publisher

DEFAULT_API_VERSION = "v21.0"
GRAPH_HOST = "https://graph.facebook.com"

#: Permissions each surface needs. The difference between these two sets
#: is the whole reason Instagram can work while Facebook refuses.
IG_PERMISSIONS = ("instagram_basic", "instagram_content_publish", "pages_show_list")
FB_PERMISSIONS = ("pages_manage_posts", "pages_read_engagement", "pages_show_list")


class MetaError(Exception):
    """A Graph API error, with the fields Meta actually returns."""

    def __init__(self, message: str, code: Optional[int] = None,
                 subcode: Optional[int] = None, user_msg: Optional[str] = None):
        self.code = code
        self.subcode = subcode
        self.user_msg = user_msg
        detail = f"{message} (code={code}"
        if subcode:
            detail += f", subcode={subcode}"
        detail += ")"
        if user_msg:
            detail += f" — {user_msg}"
        super().__init__(detail)


class NotConfigured(Exception):
    """Raised when required env vars are missing — loudly, never silently
    falling back to a no-op that looks like success."""


# ── transport ────────────────────────────────────────────────────────

Transport = Callable[[str, str, dict], dict]
"""(method, url, params) -> parsed json. Injected in tests."""


def http_transport(method: str, url: str, params: dict) -> dict:
    data = urllib.parse.urlencode(params).encode() if method == "POST" else None
    if method == "GET" and params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    request = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Meta puts the useful detail in the error BODY, not the status
        # line. Losing it here is what makes these failures feel opaque.
        try:
            payload = json.loads(exc.read().decode("utf-8"))
            error = payload.get("error") or {}
            raise MetaError(
                error.get("message", str(exc)),
                error.get("code"),
                error.get("error_subcode"),
                error.get("error_user_msg"),
            ) from exc
        except (ValueError, KeyError):
            raise MetaError(f"HTTP {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise MetaError(f"network error: {exc.reason}") from exc


# ── configuration ────────────────────────────────────────────────────

@dataclass(frozen=True)
class MetaConfig:
    access_token: str
    page_id: Optional[str] = None
    ig_user_id: Optional[str] = None
    media_base_url: Optional[str] = None
    api_version: str = DEFAULT_API_VERSION

    @classmethod
    def from_env(cls, env: Optional[dict] = None) -> "MetaConfig":
        env = env if env is not None else os.environ
        token = env.get("META_ACCESS_TOKEN", "").strip()
        if not token:
            raise NotConfigured(
                "META_ACCESS_TOKEN is not set. Publishing stays in dry run "
                "until it is. Set it in the environment, never in the repo."
            )
        return cls(
            access_token=token,
            page_id=(env.get("META_PAGE_ID") or "").strip() or None,
            ig_user_id=(env.get("META_IG_USER_ID") or "").strip() or None,
            media_base_url=(env.get("MEDIA_BASE_URL") or "").strip().rstrip("/") or None,
            api_version=(env.get("META_API_VERSION") or DEFAULT_API_VERSION).strip(),
        )

    @classmethod
    def from_env_or_none(cls, env: Optional[dict] = None) -> Optional["MetaConfig"]:
        try:
            return cls.from_env(env)
        except NotConfigured:
            return None

    def url(self, path: str) -> str:
        return f"{GRAPH_HOST}/{self.api_version}/{path.lstrip('/')}"


def public_url_for(video_path: str, out_root: str | Path, base_url: str) -> str:
    """Local render path -> the public url Meta will fetch.

    `marketing/out/2026-09-12/FH-TP-110-vertical.mp4` with base
    `https://example.com/media` becomes
    `https://example.com/media/2026-09-12/FH-TP-110-vertical.mp4`.
    """
    relative = Path(video_path).resolve().relative_to(Path(out_root).resolve())
    return f"{base_url.rstrip('/')}/{relative.as_posix()}"


# ── the client ───────────────────────────────────────────────────────

class MetaClient:
    def __init__(self, config: MetaConfig, transport: Transport = http_transport,
                 sleeper: Callable[[float], None] = time.sleep):
        self._config = config
        self._transport = transport
        self._sleep = sleeper
        self._page_token: Optional[str] = None

    # -- identity / permissions ---------------------------------------

    def me(self) -> dict:
        return self._transport("GET", self._config.url("me"),
                               {"access_token": self._config.access_token,
                                "fields": "id,name"})

    def granted_permissions(self) -> set[str]:
        payload = self._transport("GET", self._config.url("me/permissions"),
                                  {"access_token": self._config.access_token})
        return {
            row["permission"] for row in payload.get("data", [])
            if row.get("status") == "granted"
        }

    def accounts(self) -> list[dict]:
        """Pages this token can act for, each with its own Page token."""
        payload = self._transport("GET", self._config.url("me/accounts"),
                                  {"access_token": self._config.access_token,
                                   "fields": "id,name,access_token,tasks"})
        return payload.get("data", [])

    def page_token(self) -> str:
        """The Page access token — required for Facebook publishing.

        Posting to a Page with the User token fails in a way that reads
        like a missing permission but is not one.
        """
        if self._page_token:
            return self._page_token
        if not self._config.page_id:
            raise NotConfigured("META_PAGE_ID is not set")
        for account in self.accounts():
            if str(account.get("id")) == str(self._config.page_id):
                token = account.get("access_token")
                if not token:
                    raise MetaError(
                        f"Page {self._config.page_id} returned no access token — "
                        "the token holder is probably not an admin of this Page."
                    )
                self._page_token = token
                return token
        raise MetaError(
            f"Page {self._config.page_id} is not in this token's /me/accounts. "
            "Either the id is wrong or the token holder does not administer it."
        )

    def instagram_account_id(self) -> Optional[str]:
        if self._config.ig_user_id:
            return self._config.ig_user_id
        if not self._config.page_id:
            return None
        payload = self._transport(
            "GET", self._config.url(self._config.page_id),
            {"access_token": self._config.access_token,
             "fields": "instagram_business_account"},
        )
        account = payload.get("instagram_business_account") or {}
        return account.get("id")

    # -- publishing ----------------------------------------------------

    def publish_facebook_video(self, video_url: str, caption: str) -> str:
        """POST /{page-id}/videos with the PAGE token."""
        payload = self._transport(
            "POST", self._config.url(f"{self._config.page_id}/videos"),
            {"access_token": self.page_token(),
             "file_url": video_url, "description": caption},
        )
        post_id = payload.get("id")
        if not post_id:
            raise MetaError(f"Facebook accepted the call but returned no id: {payload}")
        return f"https://www.facebook.com/{post_id}"

    def publish_instagram_reel(self, video_url: str, caption: str,
                               max_status_checks: int = 30,
                               poll_seconds: float = 5.0) -> str:
        """Three steps: create container, wait for Meta to finish
        transcoding it, then publish. Skipping the wait is the usual
        cause of a container that publishes as an error."""
        ig_id = self.instagram_account_id()
        if not ig_id:
            raise NotConfigured(
                "No Instagram Business account found. Set META_IG_USER_ID, or "
                "link the Instagram account to the Facebook Page."
            )
        token = self.page_token() if self._config.page_id else self._config.access_token

        container = self._transport(
            "POST", self._config.url(f"{ig_id}/media"),
            {"access_token": token, "media_type": "REELS",
             "video_url": video_url, "caption": caption},
        )
        creation_id = container.get("id")
        if not creation_id:
            raise MetaError(f"Instagram returned no container id: {container}")

        for _ in range(max_status_checks):
            status = self._transport(
                "GET", self._config.url(creation_id),
                {"access_token": token, "fields": "status_code,status"},
            )
            code = status.get("status_code")
            if code == "FINISHED":
                break
            if code == "ERROR":
                raise MetaError(f"Instagram could not process the video: {status.get('status')}")
            self._sleep(poll_seconds)
        else:
            raise MetaError(
                f"Instagram container {creation_id} was still processing after "
                f"{max_status_checks} checks. Not published; nothing was lost."
            )

        published = self._transport(
            "POST", self._config.url(f"{ig_id}/media_publish"),
            {"access_token": token, "creation_id": creation_id},
        )
        media_id = published.get("id")
        if not media_id:
            raise MetaError(f"Instagram publish returned no id: {published}")
        return f"https://www.instagram.com/p/{media_id}"


# ── the publisher the runner uses ────────────────────────────────────

class MetaPublisher(Tier1Publisher):
    """Live Tier 1 publisher. Page and Instagram only — profiles and
    groups stay Tier 2 (human one-tap), which is a ToS wall."""

    def __init__(self, config: MetaConfig, out_root: str | Path,
                 transport: Transport = http_transport,
                 sleeper: Callable[[float], None] = time.sleep):
        self._config = config
        self._out_root = Path(out_root)
        self._client = MetaClient(config, transport, sleeper)

    def _video_url(self, video_path: str) -> str:
        if not video_path:
            raise MetaError("No video to post.")
        if video_path.startswith(("http://", "https://")):
            return video_path
        if not self._config.media_base_url:
            raise NotConfigured(
                "MEDIA_BASE_URL is not set, so there is no public url for "
                f"{video_path}. Instagram cannot accept a file upload — Meta "
                "fetches the video itself, so it must be reachable on the "
                "public internet before it can be posted."
            )
        return public_url_for(video_path, self._out_root, self._config.media_base_url)

    def post(self, request: PostRequest) -> str:
        video_url = self._video_url(request.video_path)
        if request.target == "page":
            return self._client.publish_facebook_video(video_url, request.caption)
        if request.target == "ig":
            return self._client.publish_instagram_reel(video_url, request.caption)
        raise ValueError(f"MetaPublisher handles page and ig only, not {request.target!r}")


# ── the diagnostic ───────────────────────────────────────────────────

def diagnose(config: MetaConfig, transport: Transport = http_transport
             ) -> list[tuple[str, str, str]]:
    """Ask the Graph API what this token can actually do.

    Returns (status, subject, detail) rows, same shape as `run doctor`.
    Every check degrades to a FAIL row rather than raising, so one broken
    check never hides the rest of the report.
    """
    client = MetaClient(config, transport)
    checks: list[tuple[str, str, str]] = []

    def check(subject: str, fn):
        try:
            return fn()
        except (MetaError, NotConfigured) as exc:
            checks.append(("FAIL", subject, str(exc)))
            return None

    identity = check("Token", lambda: client.me())
    if identity:
        checks.append(("OK", "Token",
                       f"valid - {identity.get('name')} (id {identity.get('id')})"))

    granted = check("Permissions", lambda: client.granted_permissions())
    if granted is not None:
        missing_fb = [p for p in FB_PERMISSIONS if p not in granted]
        missing_ig = [p for p in IG_PERMISSIONS if p not in granted]

        checks.append((
            "OK" if not missing_ig else "FAIL",
            "Instagram permissions",
            "all present" if not missing_ig else f"MISSING: {', '.join(missing_ig)}",
        ))
        checks.append((
            "OK" if not missing_fb else "FAIL",
            "Facebook permissions",
            "all present" if not missing_fb
            else f"MISSING: {', '.join(missing_fb)}."
                 + (" `pages_manage_posts` is the permission Instagram never "
                    "needed and Facebook cannot post without — this alone "
                    "explains IG working while Facebook refuses."
                    if "pages_manage_posts" in missing_fb else ""),
        ))
        checks.append(("OK", "Granted scopes", ", ".join(sorted(granted)) or "none"))

    accounts = check("Pages", lambda: client.accounts())
    if accounts is not None:
        if not accounts:
            checks.append((
                "FAIL", "Pages",
                "This token administers no Pages. Facebook publishing needs a "
                "Page token, which is minted from /me/accounts.",
            ))
        else:
            listed = ", ".join(f"{a.get('name')} ({a.get('id')})" for a in accounts)
            checks.append(("OK", "Pages", listed))
            if config.page_id:
                match = [a for a in accounts if str(a.get("id")) == str(config.page_id)]
                if match:
                    tasks = ", ".join(match[0].get("tasks") or []) or "none reported"
                    has_create = "CREATE_CONTENT" in (match[0].get("tasks") or [])
                    checks.append((
                        "OK" if has_create else "FAIL",
                        "Page token",
                        f"obtainable for META_PAGE_ID. Tasks: {tasks}."
                        + ("" if has_create else
                           " CREATE_CONTENT is absent — this token cannot post "
                           "to the Page even with the right scopes."),
                    ))
                else:
                    checks.append((
                        "FAIL", "Page token",
                        f"META_PAGE_ID={config.page_id} is not among the Pages "
                        "this token administers. Wrong id, or not an admin.",
                    ))
            else:
                checks.append(("WARN", "Page token",
                               "META_PAGE_ID is not set, so Facebook posting is off."))

    ig_id = check("Instagram account", lambda: client.instagram_account_id())
    if ig_id:
        checks.append(("OK", "Instagram account", f"id {ig_id}"))
    elif ig_id is None and not any(c[1] == "Instagram account" for c in checks):
        checks.append((
            "FAIL", "Instagram account",
            "No Instagram Business account linked to the Page, and "
            "META_IG_USER_ID is not set.",
        ))

    checks.append((
        "OK" if config.media_base_url else "FAIL",
        "Public media url",
        f"MEDIA_BASE_URL={config.media_base_url}" if config.media_base_url
        else "NOT SET. Instagram does not accept file uploads - Meta fetches "
             "the video from a url you host. Videos on the PC cannot be "
             "posted to Instagram until marketing/out/ is served publicly.",
    ))

    return checks
