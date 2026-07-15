"""Social + reel generator — P2.7 (EXPRESSION layer).

From the same genome + QA-gate decision that drives the listing, produce:
  * SocialPost   — caption (encyclopedia voice) + hashtags + ordered REAL
                   photos, per channel.
  * VideoReel    — a shot-list storyboard built from the REAL genome
                   photos (hero → angle → stamping → detail → close), with
                   text overlays. This is a spec a renderer executes where
                   the image files live; it invents no imagery.

Two laws inherited from the visual addendum (V1) and the copy rules:
  * PLACEMENT LAW — reels/posts are corpus surfaces (social/email), never a
    listing slot. They may show the real object; they never carry synthetic
    imagery. A VideoReel here references only genome `media` (is_synthetic
    is impossible by construction).
  * ASSERT-VS-HEDGE — brand/era are stated as fact only when the gate
    cleared them; otherwise hedged or omitted. Same lock as the listing.

Posting FREQUENCY is not decided here — `control.yaml`
(social.max_posts_per_group_per_day) is enforced by the scheduler that
consumes these posts. This module only generates content.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..genome.gate import GateDecision
from ..genome.schema import ProductGenome
from ..genome.vocab import EraBasis, MediaRole

# channels and their caption ceilings (chars). 0 = generous.
_CAPTION_MAX = {
    "instagram": 2200, "tiktok": 2200, "facebook": 2000,
    "x": 280, "reddit": 0, "email": 0,
}
# channels where hashtags drive discovery (TikTok + IG are the reel engines)
_HASHTAG_CHANNELS = {"instagram", "tiktok", "x"}


@dataclass
class SocialPost:
    sku: str
    channel: str
    caption: str
    hashtags: list[str] = field(default_factory=list)
    image_order: list[str] = field(default_factory=list)
    alt_texts: dict[str, str] = field(default_factory=dict)
    eligibility_note: Optional[str] = None      # from compliance facts
    gaps: list[str] = field(default_factory=list)


@dataclass
class ReelShot:
    image_url: Optional[str]     # a REAL genome photo (None = photo pending)
    seconds: float
    overlay: str
    motion: str                  # "ken_burns" | "cut"
    role: str


@dataclass
class VideoReel:
    sku: str
    orientation: str = "9:16"
    shots: list[ReelShot] = field(default_factory=list)
    duration_s: float = 0.0
    pacing: str = "slow, documentary — no on-screen smoking, no person"
    notes: list[str] = field(default_factory=list)


# --- shared assert/hedge helpers (mirror the listing generator) ------------

def _brand(genome: ProductGenome, decision: GateDecision) -> tuple[Optional[str], bool]:
    if not genome.brand:
        return None, False
    if "brand" in decision.assertable_tier_a:
        return genome.brand, True
    return f"attributed to {genome.brand}", False


def _era(genome: ProductGenome, decision: GateDecision) -> Optional[str]:
    up = genome.unique_physical
    if up is None or up.era is None:
        return None
    era = up.era
    hard = era.basis in (EraBasis.STAMPING, EraBasis.HALLMARK, EraBasis.CATALOG, EraBasis.DOCUMENTATION)
    if "unique_physical.era" in decision.assertable_tier_a and hard:
        return f"circa {era.min_year}" if era.min_year == era.max_year else f"circa {era.min_year}–{era.max_year}"
    return f"{(era.min_year // 10) * 10}s"


# --- social post -----------------------------------------------------------

_BASE_TAGS = ["estatepipe", "briar", "pipesmoking", "tobacciana", "pipecollector", "gentlemansaccessories"]


def generate_social(
    genome: ProductGenome,
    decision: GateDecision,
    *,
    channel: str = "instagram",
) -> SocialPost:
    brand_text, asserted = _brand(genome, decision)
    era_text = _era(genome, decision)

    # caption — encyclopedia voice: lead with the hook, then the facts, then CTA
    lines: list[str] = []
    if genome.why_special:
        lines.append(genome.why_special.rstrip("."))
    subject = (brand_text or "An estate pipe")
    subject = subject[0].upper() + subject[1:]
    facts = subject
    if genome.model_line:
        facts += f" — {genome.model_line}"
    if era_text:
        facts += f", {era_text}"
    lines.append(facts + ".")
    price = genome.economics.list_price
    if price is not None:
        cur = genome.economics.currency or "USD"
        sym = "$" if cur == "USD" else ("£" if cur == "GBP" else "")
        lines.append(f"{sym}{price:.0f} — on the shelf now at faridunhill.com.")
    caption = "\n\n".join(lines)
    limit = _CAPTION_MAX.get(channel, 0)
    if limit and len(caption) > limit:
        caption = caption[:limit].rsplit(" ", 1)[0]

    # hashtags — only where the channel uses them; never tag an unasserted maker
    tags: list[str] = []
    if channel in _HASHTAG_CHANNELS:
        tags = list(_BASE_TAGS)
        if asserted and genome.brand:
            tags.insert(0, genome.brand.lower().replace(" ", "").replace("&", "and"))
        if genome.model_line:
            first = genome.model_line.split()[0].lower()
            if first.isalpha():
                tags.append(first)

    # images — the same real photos as the listing, hero first
    order = sorted(
        genome.media,
        key=lambda m: (0 if m.role is MediaRole.HERO else 1, m.seq),
    )
    image_order = [m.url for m in order]
    alt = {m.url: f"{genome.brand or 'estate pipe'} — {m.role.value}" for m in order}

    # compliance-derived eligibility note (facts -> note; verdicts stay in the rules engine)
    note = None
    if genome.compliance.smoking_related or genome.compliance.age_restricted:
        note = ("age-restricted / tobacco-adjacent — some platforms limit reach or "
                "forbid paid promotion; post organically, never depict consumption")

    gaps = []
    if not genome.media:
        gaps.append("real photos (needed for the post/reel) — from C:\\FaridunhillPipes")
    if not genome.why_special:
        gaps.append("the why-special hook")

    return SocialPost(
        sku=genome.sku, channel=channel, caption=caption, hashtags=tags,
        image_order=image_order, alt_texts=alt, eligibility_note=note, gaps=gaps,
    )


# --- video reel (storyboard over REAL photos) ------------------------------

_REEL_SEQUENCE = [
    (MediaRole.HERO, 2.5, "ken_burns"),
    (MediaRole.ANGLE, 1.5, "cut"),
    (MediaRole.STAMPING, 2.5, "ken_burns"),
    (MediaRole.FLAW, 1.5, "cut"),
    (MediaRole.SCALE, 1.5, "cut"),
]


def generate_reel(
    genome: ProductGenome,
    decision: GateDecision,
) -> VideoReel:
    brand_text, asserted = _brand(genome, decision)
    era_text = _era(genome, decision)
    by_role: dict[MediaRole, list[str]] = {}
    for m in sorted(genome.media, key=lambda m: m.seq):
        by_role.setdefault(m.role, []).append(m.url)

    reel = VideoReel(sku=genome.sku)
    # opening overlay: keep it short — brand + a brief shape cue (the full
    # model line lives in the caption/listing, not burned onto the video).
    title_overlay = brand_text or "Estate pipe"
    if genome.model_line:
        short = " ".join(genome.model_line.split()[:3]).rstrip(",.")
        title_overlay = f"{title_overlay} · {short}"

    used_any_photo = False
    for role, secs, motion in _REEL_SEQUENCE:
        urls = by_role.get(role)
        if not urls:
            if role is MediaRole.HERO:
                # hero is mandatory; if absent, note the pending photo
                reel.shots.append(ReelShot(None, secs, title_overlay, motion, role.value))
            continue
        used_any_photo = True
        for i, url in enumerate(urls[:1 if role is not MediaRole.ANGLE else 2]):
            if role is MediaRole.HERO:
                overlay = title_overlay
            elif role is MediaRole.STAMPING:
                overlay = era_text or "the marks"
            elif role is MediaRole.FLAW:
                overlay = "honestly shown"
            elif role is MediaRole.SCALE:
                overlay = "true to size"
            else:
                overlay = ""
            reel.shots.append(ReelShot(url, secs, overlay, motion, role.value))

    # closing shot — price + CTA over the hero
    price = genome.economics.list_price
    hero = by_role.get(MediaRole.HERO, [None])[0]
    cur = genome.economics.currency or "USD"
    sym = "$" if cur == "USD" else ("£" if cur == "GBP" else "")
    close = f"{sym}{price:.0f} · faridunhill.com" if price is not None else "faridunhill.com"
    reel.shots.append(ReelShot(hero, 2.0, close, "ken_burns", "close"))

    reel.duration_s = round(sum(s.seconds for s in reel.shots), 1)
    if not used_any_photo:
        reel.notes.append("no real photos in the record yet — storyboard only; "
                          "render when photos arrive from C:\\FaridunhillPipes")
    reel.notes.append("PLACEMENT LAW: social/email only — a reel is never a listing image.")
    return reel
