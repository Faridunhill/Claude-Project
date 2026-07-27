"""Standing-wall loader — the single place code reads `control.yaml`.

Before this module the walls in `control.yaml` were DECLARED but never
enforced: no module read the file, so a "ceiling" was a comment, not a
wall. Every spend/post decision now routes through here.

The hardest wall (POLICY-META-ADS-001): Meta prohibits PAID advertising
for tobacco products and smoking paraphernalia. Estate pipes fall under
it. So paid Meta promotion is not a budget set to zero — it is a
capability that does not exist. Organic posting to our own Page, IG and
groups is unaffected and remains the whole distribution strategy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

CONTROL_PATH = Path(__file__).resolve().parent / "control.yaml"


class PaidPromotionProhibited(Exception):
    """Raised on any attempt to spend money promoting on Meta.

    This is a platform-policy wall, not a preference and not a budget.
    Raising it is the correct outcome; there is no config that makes a
    boost succeed while `meta_paid_ads.enabled` is false.
    """


class SpendCeiling(Exception):
    """Raised when a spend would cross a ceiling in control.yaml."""


@dataclass(frozen=True)
class Walls:
    """The numbers and switches machines never cross."""

    currency: str
    max_posts_per_group_per_day: int
    meta_paid_ads_enabled: bool
    meta_paid_ads_reason: str
    marketplace_promotion_enabled: bool
    marketplace_monthly_ceiling: float
    visual_vendor: str
    visual_paid_vendors_enabled: bool
    visual_max_cost_per_asset: float
    visual_monthly_ceiling: float
    visual_max_attempts_per_asset: int

    # -- the walls, as callable guards --------------------------------

    def assert_meta_paid_promotion_allowed(self) -> None:
        """Choke point for every paid-Meta path. Always raises while the
        wall stands — by design."""
        if not self.meta_paid_ads_enabled:
            raise PaidPromotionProhibited(self.meta_paid_ads_reason)

    def assert_visual_spend_allowed(self, cost: float, month_to_date: float = 0.0) -> None:
        """Guard before paying a visual-generation vendor. With the free
        local renderer (cost 0.0) this always passes."""
        if cost > 0 and not self.visual_paid_vendors_enabled:
            raise SpendCeiling(
                f"paid visual vendors are disabled (vendor={self.visual_vendor}); "
                f"refused a {self.currency} {cost:.2f} charge"
            )
        if cost > self.visual_max_cost_per_asset:
            raise SpendCeiling(
                f"{self.currency} {cost:.2f} exceeds max_cost_per_asset "
                f"({self.currency} {self.visual_max_cost_per_asset:.2f})"
            )
        if month_to_date + cost > self.visual_monthly_ceiling:
            raise SpendCeiling(
                f"{self.currency} {month_to_date + cost:.2f} would cross the monthly "
                f"ceiling ({self.currency} {self.visual_monthly_ceiling:.2f})"
            )


def load_walls(control_path: Optional[str | Path] = None) -> Walls:
    with open(control_path or CONTROL_PATH, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    ads = cfg.get("meta_paid_ads", {})
    mkt = cfg.get("marketplace_promotion", {})
    vis = cfg.get("visual_generation", {})
    soc = cfg.get("social", {})

    return Walls(
        currency=cfg.get("currency", "GBP"),
        max_posts_per_group_per_day=int(soc.get("max_posts_per_group_per_day", 1)),
        # Absent key => prohibited. The safe default is always "no spend".
        meta_paid_ads_enabled=bool(ads.get("enabled", False)),
        meta_paid_ads_reason=str(ads.get("reason", "Meta paid promotion is prohibited.")).strip(),
        marketplace_promotion_enabled=bool(mkt.get("enabled", False)),
        marketplace_monthly_ceiling=float(mkt.get("monthly_ceiling", 0.0)),
        visual_vendor=str(vis.get("vendor", "local_ffmpeg")),
        visual_paid_vendors_enabled=bool(vis.get("paid_vendors_enabled", False)),
        visual_max_cost_per_asset=float(vis.get("max_cost_per_asset", 0.0)),
        visual_monthly_ceiling=float(vis.get("monthly_ceiling", 0.0)),
        visual_max_attempts_per_asset=int(vis.get("max_attempts_per_asset", 3)),
    )
