"""Encyclopedia flywheel (P2.8) — sold event -> permanent SEO page -> archive post."""

from .flywheel import (
    FLYWHEEL_VERSION,
    ArchiveEntry,
    build_archive_entry,
    on_sold,
    slugify,
    write_archive_entry,
)

__all__ = [
    "FLYWHEEL_VERSION",
    "ArchiveEntry",
    "build_archive_entry",
    "on_sold",
    "slugify",
    "write_archive_entry",
]
