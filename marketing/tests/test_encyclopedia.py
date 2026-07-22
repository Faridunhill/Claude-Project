"""P2.8 test suite — the sold-archive flywheel."""

from marketing.encyclopedia import build_archive_entry, on_sold, slugify
from marketing.tests.test_expression import effective_hedged, effective_verified

SOLD = {"sold_price": 88.0, "channel": "ebay", "ts": "2026-07-20T14:00:00+00:00"}


def test_slugify_stable_and_url_safe():
    assert slugify("Chacom Gentleman 836 — circa 1950s | Estate") == \
        "chacom-gentleman-836-circa-1950s-estate"


def test_archive_entry_contains_record_and_price():
    entry = build_archive_entry(effective_verified(), SOLD)
    assert entry.slug.startswith("fh-tp-034-chacom")
    assert "soldPrice: 88.0" in entry.markdown
    assert 'Stamped: "CHACOM / GENTLEMAN / 836 / FRANCE"' in entry.markdown
    assert "disclosed in full" in entry.markdown        # honesty survives into archive
    assert "permanent reference" in entry.markdown
    assert "From the archive" in entry.caption.text


def test_price_can_be_withheld():
    entry = build_archive_entry(effective_verified(), SOLD, show_price=False)
    assert "soldPrice: 88" not in entry.markdown


def test_hedged_item_stays_hedged_in_archive():
    entry = build_archive_entry(effective_hedged(), SOLD)
    assert "not verified" in entry.markdown             # hedge language persists
    first_line = entry.markdown.splitlines()[1]         # title frontmatter
    assert "Chacom" not in first_line                   # no asserted brand in title


def test_permanent_slug_on_regeneration():
    e = effective_verified()
    entry1 = build_archive_entry(e, SOLD)
    e2 = dict(e, why_special="Updated hook after generator upgrade")
    entry2 = build_archive_entry(e2, SOLD, existing_slug=entry1.slug)
    assert entry2.slug == entry1.slug                   # URL never changes
    assert "Updated hook" in entry2.markdown


def test_on_sold_writes_page_and_returns_caption(tmp_path):
    path, caption = on_sold(effective_verified(), SOLD, tmp_path / "archive")
    assert path.exists() and path.suffix == ".md"
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---")
    assert "encyclopedia" in caption.text
