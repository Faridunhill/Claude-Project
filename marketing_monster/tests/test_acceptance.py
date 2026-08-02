"""T1–T10 — the honesty laws expressed as code that fails.

These are the wave-1 acceptance tests from doc 004 §6. Each one names the
finding it enforces, so a future refactor that quietly removes a law breaks a
test with the law's name on it. Same job the 324 dating tests do for the
cabinets.

    python -m unittest discover -s marketing_monster/tests -v
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from monster.judge import Judge                       # noqa: E402
from monster.ledger import LedgerError                # noqa: E402
from monster.maker import Maker                       # noqa: E402
from monster.playbook import Playbook                 # noqa: E402
from monster.report import weekly_report              # noqa: E402
from monster.scale import Scale                       # noqa: E402
from monster.wall import Cookbook, admission_test     # noqa: E402
from monster.well import Well                         # noqa: E402


class MonsterCase(unittest.TestCase):
    def setUp(self):
        self.base = pathlib.Path(tempfile.mkdtemp(prefix="monster-"))
        self.root = self.base / "clones" / "pipes"
        self.root.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)


class T1_AttributionDefaults(MonsterCase):
    """B1 — the Scale never guesses a cause."""

    def test_missing_attribution_stores_unattributable(self):
        row = Scale(self.root).record("sale", "listing/a", value=340)
        self.assertEqual(row["attribution"], "unattributable")


class T2_AttributionUpgradeNeedsReason(MonsterCase):
    """B1 — an upgrade above unattributable must justify itself in the row."""

    def test_upgrade_without_reason_is_rejected(self):
        with self.assertRaises(LedgerError) as ctx:
            Scale(self.root).record("sale", "listing/a", attribution="direct")
        self.assertIn("reason", str(ctx.exception))

    def test_upgrade_with_reason_is_allowed(self):
        row = Scale(self.root).record("sale", "listing/a", attribution="assumed",
                                      reason="buyer quoted the hub page title")
        self.assertEqual(row["attribution"], "assumed")


class T3_AppendOnly(MonsterCase):
    """Truth is append-only; an edit made outside the API is detectable."""

    def test_edit_breaks_the_chain(self):
        scale = Scale(self.root)
        scale.record("impression", "listing/a")
        scale.record("sale", "listing/a", value=100)
        self.assertTrue(scale.log.verify()[0])

        path = scale.log.path
        rows = [json.loads(x) for x in path.read_text().splitlines()]
        rows[1]["value"] = 999_999                       # tamper
        path.write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n")

        ok, msg = scale.log.verify()
        self.assertFalse(ok)
        self.assertIn("edited", msg)

    def test_correction_is_a_new_row(self):
        scale = Scale(self.root)
        first = scale.record("sale", "listing/a", value=100)
        scale.correct(first["id"], reason="price was net of shipping", value=120)
        live = scale.rows()
        self.assertEqual(len(live), 1)
        self.assertEqual(live[0]["value"], 120)
        self.assertEqual(len(scale.log.rows()), 2)       # history kept


class T4_NoPersonalDataInTheWell(MonsterCase):
    """M4 — derived features only. No names, no emails, no addresses."""

    EXPORT = ("Item number,Item title,Sold for,Sale date,Buyer username,"
              "Buyer email,Buyer name,Ship to address\n"
              "123,Dunhill Shell 1961,340.00,2026-07-02,collector_x,"
              "x@example.com,John Smith,12 Oak Street\n"
              "124,Charatan Belvedere,210.00,2026-07-09,collector_x,"
              "x@example.com,John Smith,12 Oak Street\n")

    def test_loader_writes_zero_personal_rows(self):
        csv_path = self.base / "export.csv"
        csv_path.write_text(self.EXPORT, encoding="utf-8")
        well = Well(self.root)
        stats = well.load_csv(csv_path)
        self.assertEqual(stats["transactions"], 2)

        blob = (well.root / "derived" / "transactions.jsonl").read_text() + \
               (well.root / "derived" / "buyers.jsonl").read_text()
        for forbidden in ("x@example.com", "John Smith", "Oak Street", "collector_x"):
            self.assertNotIn(forbidden, blob, f"personal data leaked into the Well: {forbidden}")

    def test_writer_refuses_a_personal_field(self):
        with self.assertRaises(LedgerError):
            Well(self.root).assert_clean({"item_id": "1", "note": "reach me at a@b.com"})


class T5_StableUnreversibleIdentity(MonsterCase):
    """M4 — the same customer resolves the same way twice, and not at all
    without the salt."""

    def test_same_buyer_same_key_across_exports(self):
        well = Well(self.root)
        self.assertEqual(well.buyer_key("collector_x"), well.buyer_key("Collector_X "))

    def test_different_salt_different_key(self):
        a = Well(self.root).buyer_key("collector_x")
        other = self.base / "clones" / "other"
        other.mkdir(parents=True)
        b = Well(other).buyer_key("collector_x")
        self.assertNotEqual(a, b, "keys must not be reproducible without this Well's salt")


class T6_PlaybookLineNeedsEvidence(MonsterCase):
    """B2 — a lesson without its evidence is a superstition."""

    def test_missing_fields_rejected(self):
        with self.assertRaises(LedgerError):
            Playbook(self.root).propose("STRUCT", "Put the shape name first.",
                                        n="", effect="+18% impressions", src="q-07")

    def test_unparseable_line_rejected(self):
        book = Playbook(self.root)
        book.path.write_text("[STRUCT][CONFIRMED] shape name first, trust me\n")
        with self.assertRaises(LedgerError):
            book.lines()


class T7_NoConfirmationOnOneCohort(MonsterCase):
    """B2 — nothing is confirmed on a single cohort, unless Farid says so and
    the line records that it was his call."""

    def setUp(self):
        super().setUp()
        self.book = Playbook(self.root)
        self.claim = "Put the shape name before the finish in listing titles."
        self.book.propose("STRUCT", self.claim, n="412 impressions",
                          effect="+18% search impressions", src="q-titles-07")

    def test_single_cohort_rejected(self):
        with self.assertRaises(LedgerError) as ctx:
            self.book.promote(self.claim, ["2026-W32"])
        self.assertIn("two non-overlapping cohorts", str(ctx.exception))

    def test_two_cohorts_confirm(self):
        line = self.book.promote(self.claim, ["2026-W32", "2026-W35"])
        self.assertEqual(line.status, "CONFIRMED")

    def test_farid_override_is_recorded_honestly(self):
        line = self.book.promote(self.claim, ["2026-W32"], src="farid")
        self.assertEqual(line.status, "CONFIRMED")
        self.assertEqual(line.src, "farid")

    def test_expired_line_stops_being_read(self):
        self.book.promote(self.claim, ["2026-W32", "2026-W35"])
        later = date.today() + timedelta(days=400)
        self.assertEqual(len(self.book.for_maker(later)), 0)
        self.assertEqual(len(self.book.expire_due(later)), 1)


class T8_MakerOutputIsStamped(MonsterCase):
    """N1 — the rollback key. An unstamped asset cannot be published."""

    def test_publish_requires_a_decision(self):
        with self.assertRaises(LedgerError):
            Maker(self.root).publish("listing/a", "body", decision_id="")

    def test_publish_stamps_and_rollback_query_works(self):
        maker = Maker(self.root)
        asset = maker.publish("listing/a", "body", decision_id="D-014")
        self.assertTrue(asset["asset_version"].startswith("pb-"))
        self.assertEqual(maker.written_under(asset["asset_version"]), ["listing/a"])


class T9_ReportPrintsItsOwnBlindSpots(MonsterCase):
    """B1 + §2.3 — the unattributable share and ledger silence are printed
    even when both look bad."""

    def test_report_shows_share_and_silence(self):
        scale = Scale(self.root)
        for _ in range(3):
            scale.record("sale", "listing/a", value=100)
        scale.record("sale", "listing/b", value=100,
                     attribution="direct", reason="buyer said so")

        body = weekly_report(self.root)
        self.assertIn("75% of outcomes", body)          # 3 of 4 unknown, stated plainly
        self.assertIn("DIGGER NOT STARTED", body)       # never wrote a row
        self.assertIn("LEDGER HEALTH", body)

    def test_silence_outranks_performance_in_the_headline(self):
        Scale(self.root).record("sale", "listing/a", value=5_000)
        body = weekly_report(self.root)
        headline = body.split("HEADLINE")[1]
        self.assertIn("not writing rows", headline)


class T10_TheWall(MonsterCase):
    """B3 — a cookbook line with no admission-log entry fails the build, and
    data wearing a method's coat cannot cross."""

    def setUp(self):
        super().setUp()
        self.cook = Cookbook(self.base / "cookbook")

    def test_method_crosses(self):
        claim = "Photograph the maker's mark at an angle that shows wear."
        self.assertTrue(admission_test(claim)["passes"])
        self.cook.admit(claim, verdict="yes", decided_by="farid", from_clone="pipes")
        self.assertTrue(self.cook.verify()[0])

    def test_data_in_a_methods_coat_is_refused(self):
        claim = "Pre-1970 Dunhills clear at $340+ within nine days."
        self.assertFalse(admission_test(claim, proper_nouns=["Dunhill"])["passes"])
        with self.assertRaises(LedgerError):
            self.cook.admit(claim, verdict="yes", decided_by="farid",
                            from_clone="pipes", proper_nouns=["Dunhill"])

    def test_refusal_is_still_recorded(self):
        claim = "Photograph the maker's mark at an angle that shows wear."
        self.cook.admit(claim, verdict="no", decided_by="farid", from_clone="pipes")
        self.assertEqual(len(self.cook.log.rows()), 1)
        self.assertNotIn(claim, self.cook.book.read_text() if self.cook.book.exists() else "")

    def test_smuggled_line_fails_the_build(self):
        self.cook.book.write_text("# COOKBOOK\n\n- Dunhill buyers pay $340 in nine days.\n")
        ok, msg = self.cook.verify()
        self.assertFalse(ok)
        self.assertIn("admission-log", msg)


class T11_JudgeRemembersRejections(MonsterCase):
    """M2 — dead categories stay dead until something changes."""

    def test_reproposal_requires_stating_the_change(self):
        judge = Judge(self.root)
        judge.decide("Generic lighters", edge="NONE", verdict="REJECT",
                     reason="no edge; knife-fight with Amazon")
        with self.assertRaises(LedgerError) as ctx:
            judge.decide("Generic lighters", edge="NONE", verdict="DO", reason="feels right")
        self.assertIn("what changed", str(ctx.exception))

    def test_edge_none_cannot_be_a_do(self):
        with self.assertRaises(LedgerError):
            Judge(self.root).decide("Handy tools", edge="NONE", verdict="DO", reason="cheap")

    def test_pipes_is_organic_only(self):
        self.assertEqual(Judge(self.root).channel_flag(), "organic_only")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class T12_DigDoesNotInventPatterns(MonsterCase):
    """B2 at the analysis layer: the dig must recover real effects, refuse to
    report absent ones, and never propose a lesson that cannot be acted on."""

    HEADER = ("Item number,Item title,Start date,Sale date,Sold for,"
              "Buyer username\n")

    def _write_well(self, rows):
        csv_path = self.base / "export.csv"
        csv_path.write_text(self.HEADER + "".join(rows), encoding="utf-8")
        Well(self.root).load_csv(csv_path)

    def _synthetic(self):
        """Two brands at very different price levels. Inside each brand,
        'boxed' adds 20%; 'restored' does nothing."""
        rows, n = [], 0
        for brand, base in (("Dunhill", 300), ("Stanwell", 60)):
            for i in range(40):
                boxed = i % 2 == 0
                restored = i % 3 == 0
                price = base * (1.2 if boxed else 1.0)
                words = " ".join(w for w, on in
                                 (("Boxed", boxed), ("Restored", restored)) if on)
                n += 1
                rows.append(f"{n},{brand} Billiard {words},2026-01-01,2026-03-01,"
                            f"${price:.2f},buyer_{i % 7}\n")
        return rows

    def setUp(self):
        super().setUp()
        self._write_well(self._synthetic())
        from monster.dig import Dig
        self.dig = Dig(self.root)
        self.words = {w["word"]: w for w in self.dig.title_words(min_n=10)}

    def test_recovers_a_planted_effect(self):
        self.assertIn("boxed", self.words)
        self.assertAlmostEqual(self.words["boxed"]["price_lift"], 0.20, delta=0.05)

    def test_reports_no_effect_where_none_exists(self):
        self.assertAlmostEqual(self.words.get("restored", {}).get("price_lift", 0),
                               0.0, delta=0.05)

    def test_brand_names_are_never_title_word_findings(self):
        """The confound that makes the naive version of this analysis useless:
        a Dunhill outsells a Stanwell however it is described. 'Use the word
        Dunhill' is not a lesson — you cannot rename a pipe."""
        for brand in ("dunhill", "stanwell"):
            self.assertNotIn(brand, self.words)

    def test_proposals_are_never_confirmed(self):
        for line in self.dig.proposals():
            self.assertIn("[PROPOSED]", line)
            self.assertNotIn("[CONFIRMED]", line)

    def test_empty_well_proposes_nothing(self):
        from monster.dig import Dig
        empty = self.base / "clones" / "empty"
        empty.mkdir(parents=True)
        dig = Dig(empty)
        self.assertEqual(dig.proposals(), [])
        self.assertIn("Well is empty", dig.report())


class T13_LocateReadsNoRecords(MonsterCase):
    """`locate` answers "where does the data live?" without opening the data."""

    def test_header_only(self):
        from monster.locate import header_of, scan
        path = self.base / "sold_items.csv"
        path.write_text("Item number,Sold for\n1,340.00\nSECRET_ROW,999\n",
                        encoding="utf-8")
        head = header_of(path)
        self.assertIn("Item number", head)
        self.assertNotIn("SECRET_ROW", head)
        self.assertNotIn("340.00", head)

    def test_ranks_likely_data_first(self):
        from monster.locate import scan
        (self.base / "notes.txt").write_text("hello", encoding="utf-8")
        (self.base / "ebay_sold_orders.csv").write_text(
            "Item number,Sold for\n" + "1,2\n" * 500, encoding="utf-8")
        hits = scan(self.base)
        self.assertTrue(hits)
        self.assertEqual(hits[0]["path"].name, "ebay_sold_orders.csv")
