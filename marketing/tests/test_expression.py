"""P2.6 test suite — copy generators + versioned expression store."""

from marketing.expression import (
    GENERATOR_VERSION,
    ExpressionRecord,
    ExpressionStore,
    ascii_safe,
    generate_description,
    generate_title,
    inputs_hash,
)


def effective_verified() -> dict:
    return {
        "sku": "FH-TP-034",
        "product_type": "unique_physical",
        "taxonomy": "pipes/estate/dublin",
        "brand": "Chacom",
        "model_line": "Gentleman 836",
        "country_of_origin": "FR",
        "why_special": "Unsmoked 1950s French shop stock — the sandblast is factory-fresh",
        "provenance_context": ["single-owner Bristol estate"],
        "field_provenance": {"brand": {"source": "human"}},
        "unique_physical": {
            "stampings_verbatim": "CHACOM / GENTLEMAN / 836 / FRANCE",
            "era": {"min_year": 1950, "max_year": 1962, "basis": "stamping"},
            "condition_grade": "very_good",
            "flaws": ["rim_darkening", "tooth_marks_light"],
            "restoration": ["cleaned", "sanitized"],
            "measurements": {"length_mm": 148, "weight_g": 41},
        },
    }


def effective_hedged() -> dict:
    e = effective_verified()
    e["field_provenance"]["brand"] = {"source": "vision"}   # unverified vision claim
    return e


# ------------------------------------------------------------------- titles

def test_verified_brand_asserted_in_title():
    title = generate_title(effective_verified())
    assert "Chacom" in title and "Gentleman 836" in title
    assert "circa 1950s" in title
    assert len(title) <= 80


def test_hedged_brand_never_appears_in_title():
    title = generate_title(effective_hedged())
    assert "Chacom" not in title          # the lock, visible
    assert "French" in title              # origin descriptor instead
    assert "Dublin" in title


def test_guessed_era_says_nothing():
    e = effective_verified()
    e["unique_physical"]["era"]["basis"] = "guess"
    assert "circa" not in generate_title(e)


def test_style_era_hedges_loosely():
    e = effective_verified()
    e["unique_physical"]["era"]["basis"] = "style"
    assert "mid-century" in generate_title(e)


# ------------------------------------------------------------- descriptions

def test_hedged_description_uses_attributed_language():
    desc = generate_description(effective_hedged())
    assert "consistent with Chacom" in desc
    assert "not verified" in desc


def test_every_flaw_is_disclosed():
    desc = generate_description(effective_verified())
    assert "rim darkening" in desc
    assert "tooth marks light" in desc
    assert "disclosed in full" in desc


def test_description_carries_hook_stampings_provenance_measurements():
    desc = generate_description(effective_verified())
    assert desc.startswith("Unsmoked 1950s")
    assert 'Stamped: "CHACOM / GENTLEMAN / 836 / FRANCE"' in desc
    assert "Provenance: single-owner Bristol estate." in desc
    assert "length 148 mm" in desc and "weight 41 g" in desc
    assert "exact item you will receive" in desc


def test_output_is_ascii_safe():
    title = generate_title(effective_verified())
    desc = generate_description(effective_verified())
    title.encode("ascii")   # raises if not ASCII
    desc.encode("ascii")
    assert ascii_safe("£99 — “fine”") == 'GBP 99 - "fine"'


# ---------------------------------------------------------- expression store

def test_store_versions_and_staleness(tmp_path):
    store = ExpressionStore(tmp_path / "expr.db")
    e = effective_verified()
    h = inputs_hash(e)

    assert store.is_stale("FH-TP-034", "title", e, GENERATOR_VERSION)
    store.put(ExpressionRecord("FH-TP-034", "title", "core",
                               generate_title(e), GENERATOR_VERSION, h))
    assert not store.is_stale("FH-TP-034", "title", e, GENERATOR_VERSION)

    # a correction changes the effective genome -> stale
    e2 = dict(e, brand="Chapuis-Comoy")
    assert store.is_stale("FH-TP-034", "title", e2, GENERATOR_VERSION)

    # generator upgrade -> stale
    assert store.is_stale("FH-TP-034", "title", e, "copy-2.0.0")

    # regeneration appends; latest wins; history preserved
    store.put(ExpressionRecord("FH-TP-034", "title", "core",
                               "new title", "copy-2.0.0", inputs_hash(e)))
    assert store.latest("FH-TP-034", "title").generator_version == "copy-2.0.0"
    store.close()


def test_store_has_no_edit_api(tmp_path):
    assert not hasattr(ExpressionStore, "update")
    assert not hasattr(ExpressionStore, "edit")
