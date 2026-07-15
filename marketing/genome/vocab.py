"""Controlled vocabularies for the Marketing DNA genome (Synthesis §3).

Rule (Round 1 Q4, ratified): if a machine BRANCHES on it, it is an enum
here; if a machine NARRATES from it, it is free text in a designated
narrative field. Adding a value is allowed (governance rule 1: add only);
renaming or deleting a value is forbidden — deprecate instead.
"""

from enum import Enum

VOCAB_VERSION = "1.0.0"


class ProductType(str, Enum):
    UNIQUE_PHYSICAL = "unique_physical"
    REPEATABLE_PHYSICAL = "repeatable_physical"
    DIGITAL = "digital"


class FieldSource(str, Enum):
    """Who asserted a genome fact. Decides assert-vs-hedge in all copy."""

    HUMAN = "human"
    VISION = "vision"
    INFERRED = "inferred"


class MediaRole(str, Enum):
    HERO = "hero"
    ANGLE = "angle"
    STAMPING = "stamping"
    FLAW = "flaw"
    SCALE = "scale"      # item beside ruler, or on scale with readout visible
    GROUP = "group"


class ConditionGrade(str, Enum):
    MINT = "mint"
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    PROJECT = "project"


class EraBasis(str, Enum):
    """What the era claim rests on. Decides whether copy may assert
    ("circa 1955") or must hedge ("mid-century")."""

    STAMPING = "stamping"
    CATALOG = "catalog"
    HALLMARK = "hallmark"
    DOCUMENTATION = "documentation"
    STYLE = "style"
    GUESS = "guess"


class Material(str, Enum):
    BRIAR = "briar"
    MEERSCHAUM = "meerschaum"
    CLAY = "clay"
    CORN_COB = "corn_cob"
    WOOD_OTHER = "wood_other"
    VULCANITE = "vulcanite"
    ACRYLIC = "acrylic"
    BAKELITE = "bakelite"
    AMBER = "amber"            # restricted-material trigger on some channels
    HORN = "horn"              # restricted-material trigger
    BONE = "bone"
    IVORY_LIKE = "ivory_like"  # CITES review REQUIRED before listing
    LEATHER = "leather"
    CERAMIC = "ceramic"
    GLASS = "glass"
    STEEL = "steel"
    BRASS = "brass"
    NICKEL = "nickel"
    SILVER = "silver"
    GOLD_PLATE = "gold_plate"


#: Materials that trigger channel restriction review (compliance engine input).
RESTRICTED_MATERIALS = frozenset(
    {Material.AMBER, Material.HORN, Material.BONE, Material.IVORY_LIKE}
)


class FlawCode(str, Enum):
    """The honesty layer: auto-disclosed in copy, paired with FLAW photos."""

    RIM_DARKENING = "rim_darkening"
    RIM_CHAR = "rim_char"
    TOOTH_MARKS_LIGHT = "tooth_marks_light"
    TOOTH_MARKS_DEEP = "tooth_marks_deep"
    STEM_OXIDATION = "stem_oxidation"
    FILLS = "fills"
    CRACK = "crack"
    CHIP = "chip"
    SCRATCHES = "scratches"
    DENT = "dent"
    FINISH_WEAR = "finish_wear"
    LOOSE_STEM_FIT = "loose_stem_fit"
    TIGHT_STEM_FIT = "tight_stem_fit"
    REPLACEMENT_STEM = "replacement_stem"
    REPLACEMENT_BAND = "replacement_band"
    GHOSTING = "ghosting"          # previous-tobacco aroma
    MISSING_PART = "missing_part"


class RestorationCode(str, Enum):
    CLEANED = "cleaned"
    SANITIZED = "sanitized"
    STEM_REPOLISHED = "stem_repolished"
    STEM_DEOXIDIZED = "stem_deoxidized"
    RIM_TOPPED = "rim_topped"
    REFINISHED = "refinished"
    REWAXED = "rewaxed"
    STEM_REPLACED = "stem_replaced"
    BAND_REPLACED = "band_replaced"
    UNRESTORED = "unrestored"


class AttributionStatus(str, Enum):
    """QA-gate outcome for Tier A claims (Synthesis §5)."""

    VERIFIED = "verified"        # human confirmed (Yes)
    REJECTED = "rejected"        # human refuted (No) — claim must not be used
    UNVERIFIED = "unverified"    # Can't tell → hedge-and-list at no-name floor
    PENDING = "pending"          # in the review queue
