"""Encyclopedia flywheel (P2.8, SOCIAL-ENGINE-001 §sold):

    sold event -> permanent SEO archive page -> archive social post

Every sold item's page persists as a comparable-price reference —
the sold-price database as a public marketing asset (Round 1 Q6).

The flywheel writes `content/archive/<slug>.md` (frontmatter + body)
which the store renders at /archive/<slug>. The page is EXPRESSION —
regenerated from the effective genome whenever generators improve —
but the URL is permanent: slugs never change once published.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..expression.copy import generate_description, generate_title
from ..social.captions import Caption, generate_caption

FLYWHEEL_VERSION = "encyclopedia-1.0.0"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)[:80]


@dataclass(frozen=True)
class ArchiveEntry:
    slug: str
    markdown: str
    caption: Caption


def build_archive_entry(
    effective: dict,
    sold: dict,
    show_price: bool = True,
    existing_slug: Optional[str] = None,
) -> ArchiveEntry:
    """effective: the effective genome. sold: the SOLD phenotype event
    payload ({'sold_price': .., 'channel': .., 'ts': ..}).

    existing_slug: pass when regenerating — the URL is permanent."""
    title = generate_title(effective)
    slug = existing_slug or slugify(f"{effective['sku']}-{title}")
    body = generate_description(effective)

    images = [m["url"] for m in effective.get("media", [])]
    lines = [
        "---",
        f"title: {title!r}",
        f"sku: {effective['sku']}",
        f"brand: {effective.get('brand') or ''!r}",
        f"department: {(effective.get('taxonomy') or '').split('/')[0] or 'pipes'}",
        f"taxonomy: {effective.get('taxonomy') or ''!r}",
        f"soldAt: {sold.get('ts', '')!r}",
        f"soldChannel: {sold.get('channel', '')!r}",
        f"soldPrice: {sold.get('sold_price') if show_price else ''}",
        f"generatorVersion: {FLYWHEEL_VERSION!r}",
        "images:",
        *[f"- {url!r}" for url in images],
        "---",
        "",
        body,
        "",
        "*This piece has found its home. The record remains as part of the "
        "Faridunhill encyclopedia - a permanent reference for collectors "
        "researching this maker, shape, and period.*",
    ]
    caption = generate_caption(effective, kind="sold_archive")
    return ArchiveEntry(slug=slug, markdown="\n".join(lines), caption=caption)


def write_archive_entry(entry: ArchiveEntry, archive_dir: str | Path) -> Path:
    archive_dir = Path(archive_dir)
    archive_dir.mkdir(parents=True, exist_ok=True)
    path = archive_dir / f"{entry.slug}.md"
    path.write_text(entry.markdown, encoding="utf-8")
    return path


def on_sold(
    effective: dict,
    sold_payload: dict,
    archive_dir: str | Path,
    show_price: bool = True,
) -> tuple[Path, Caption]:
    """The flywheel turn: call this from the nightly job when a SOLD
    event lands in the phenotype ledger. Returns (archive page path,
    ready archive caption for the social queue)."""
    entry = build_archive_entry(effective, sold_payload, show_price=show_price)
    path = write_archive_entry(entry, archive_dir)
    return path, entry.caption
