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

    def test_pipes_allows_marketplace_promotion(self):
        """v1.0 said all paid channels were closed for Faridunhill. Farid's own
        sales disproved it on 2026-08-01 — three of five came through eBay
        Promoted Listings. Ratified by Farid: on-platform promotion is open,
        Meta and Google stay closed."""
        from monster.judge import PAID_SCOPE
        self.assertEqual(Judge(self.root).channel_flag(), "paid_allowed")
        self.assertIn("Meta and Google remain closed", PAID_SCOPE["pipes"])


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


class T14_ManySourcesOneWell(MonsterCase):
    """The sales history lives across eBay and Etsy, in CSV and JSONL. One
    Well holds all of it, and loading the same file twice adds nothing."""

    CSV = ("Date,Item Id,Listing Title,Price,Quantity,Shipping Fee,Currency\n"
           "2026-07-02,123,Dunhill Shell Billiard,340.00,1,12.00,USD\n"
           "2026-07-09,124,Charatan Dublin,210.00,1,10.00,USD\n")
    JSONL = ('{"listing_id": 900, "title": "Peterson System", '
             '"price": {"amount": 95.0, "currency": "USD"}, "date": "2026-07-20"}\n'
             '{"listing_id": 901, "title": "Comoy Bulldog", '
             '"price": {"amount": 130.0, "currency": "USD"}, "date": "2026-07-22"}\n')

    def test_plain_date_column_maps(self):
        """A file whose only date column is called 'Date' must still load —
        the specific aliases win, 'date' is the last resort."""
        from monster.well import propose_mapping
        mapping = propose_mapping(["Date", "Item Id", "Listing Title", "Price"])
        self.assertEqual(mapping["sold_at"], "Date")
        self.assertEqual(mapping["item_id"], "Item Id")
        self.assertEqual(mapping["title"], "Listing Title")

    def test_jsonl_with_nested_price(self):
        path = self.base / "etsy_sold_manifest.jsonl"
        path.write_text(self.JSONL, encoding="utf-8")
        well = Well(self.root)
        stats = well.load(path)
        self.assertEqual(stats["transactions"], 2)
        self.assertEqual(stats["channel"], "etsy")
        prices = sorted(r["price"] for r in well.transactions())
        self.assertEqual(prices, [95.0, 130.0])

    def test_append_merges_channels_and_skips_duplicates(self):
        csv_path = self.base / "ebay_sales.csv"
        csv_path.write_text(self.CSV, encoding="utf-8")
        jsonl_path = self.base / "etsy_sold.jsonl"
        jsonl_path.write_text(self.JSONL, encoding="utf-8")

        well = Well(self.root)
        well.load(csv_path)
        stats = well.load(jsonl_path, append=True)
        self.assertEqual(stats["transactions"], 4)
        self.assertEqual({r["channel"] for r in well.transactions()}, {"ebay", "etsy"})

        again = well.load(jsonl_path, append=True)
        self.assertEqual(again["added"], 0)
        self.assertEqual(again["duplicates_skipped"], 2)
        self.assertEqual(again["transactions"], 4)

    def test_load_without_append_replaces(self):
        csv_path = self.base / "ebay_sales.csv"
        csv_path.write_text(self.CSV, encoding="utf-8")
        well = Well(self.root)
        well.load(csv_path)
        jsonl_path = self.base / "etsy_sold.jsonl"
        jsonl_path.write_text(self.JSONL, encoding="utf-8")
        stats = well.load(jsonl_path)
        self.assertEqual(stats["transactions"], 2)


class T15_ProductTitlesAreNotAddresses(MonsterCase):
    """The M4 guard must not refuse the catalogue. Pipe titles are full of
    address-shaped noise — '4 Star Dr Grabow', '2 Ring St' — and blocking on
    them stops the whole load while protecting nothing: a listing title is our
    own marketing copy, not customer data."""

    TRICKY = [
        "Vintage 4 Star Dr Grabow Duke Billiard Estate Pipe",
        "Dunhill 2 Ring St Shell Briar Group 4",
        "Peterson 999 Sterling Way Rustic Bent",
        "Charatan 3 Oak Lane Selected Dublin",
    ]

    def test_titles_load(self):
        rows = "".join(f"{i},{t},100.00,2026-07-0{i}\n"
                       for i, t in enumerate(self.TRICKY, 1))
        path = self.base / "ebay_sales.csv"
        path.write_text("Item Id,Listing Title,Price,Date\n" + rows, encoding="utf-8")
        stats = Well(self.root).load(path)
        self.assertEqual(stats["transactions"], len(self.TRICKY))

    def test_a_real_address_field_is_still_refused(self):
        with self.assertRaises(LedgerError):
            Well(self.root).assert_clean({"note": "ships to 12 Oak Street"})

    def test_email_still_refused_even_in_a_title(self):
        with self.assertRaises(LedgerError) as ctx:
            Well(self.root).assert_clean({"title": "Pipe lot, contact me at a@b.com"})
        self.assertIn("a@b.com", str(ctx.exception))


class T16_ProposalsRankByEvidenceNotEffect(MonsterCase):
    """The real dig exposed this: ranking candidates by lift and taking the
    top three hands every slot to the noisiest finding. A +176% effect seen in
    2 brands beat a +30% effect seen in 11, because small groups swing harder.
    Breadth first, volume second, size last."""

    def setUp(self):
        super().setUp()
        rows, n = [], 0
        # 'broad' appears across 6 brands with a modest, consistent +25%.
        # 'narrow' appears in 2 brands with a wild +150%.
        brands = ["Dunhill", "Peterson", "Stanwell", "Comoy", "GBD", "Savinelli"]
        for i, brand in enumerate(brands):
            for j in range(30):
                broad = j % 2 == 0
                narrow = i < 2 and j % 3 == 0
                price = 100 * (1.25 if broad else 1.0) * (2.5 if narrow else 1.0)
                words = " ".join(w for w, on in
                                 (("broadword", broad), ("narrowword", narrow)) if on)
                n += 1
                rows.append(f"{n},{brand} Billiard {words},{price:.2f},2026-01-0{j % 9 + 1}\n")
        path = self.base / "ebay_sales.csv"
        path.write_text("Item Id,Listing Title,Price,Date\n" + "".join(rows),
                        encoding="utf-8")
        Well(self.root).load(path)
        from monster.dig import Dig
        self.dig = Dig(self.root)

    def test_the_broad_finding_is_proposed_first(self):
        lines = self.dig.proposals()
        self.assertTrue(lines, "expected at least one proposal")
        self.assertIn("broadword", lines[0])

    def test_a_two_brand_spike_never_outranks_a_six_brand_pattern(self):
        lines = self.dig.proposals()
        broad = next((i for i, x in enumerate(lines) if "broadword" in x), None)
        narrow = next((i for i, x in enumerate(lines) if "narrowword" in x), None)
        self.assertIsNotNone(broad)
        if narrow is not None:
            self.assertLess(broad, narrow)


class T17_TwinObeysTheLaws(MonsterCase):
    """Twinning a sold listing is a translation, not an embellishment, and it
    goes to owned ground before borrowed."""

    TITLE = "Savinelli 920 KS Bent Dublin Estate Pipe, Burgundy Finish"

    def _twin(self, title=None, price=125.0):
        from monster.twin import Twin
        return Twin(self.root).build(title or self.TITLE, price,
                                     "savinelli-920-ks-d4b01",
                                     decision_id="D-001", sold_on="2026-08-01")

    def test_requires_a_judge_decision(self):
        from monster.twin import Twin
        with self.assertRaises(LedgerError):
            Twin(self.root).build(self.TITLE, 125.0, "sku", decision_id="",
                                  sold_on="2026-08-01")

    def test_never_invents_a_date(self):
        result = self._twin()
        body = (result["out_dir"] / "site.md").read_text()
        self.assertIn("UNDATED", body)
        for invented in ("1960s", "1970s", "circa", "c.19"):
            self.assertNotIn(invented, body)

    def test_reads_only_what_the_title_says(self):
        result = self._twin()
        self.assertEqual(result["facts"]["brand"], "savinelli")
        self.assertEqual(result["facts"]["shape"], "dublin")
        self.assertFalse(result["facts"]["unsmoked"])   # the title does not say so

    def test_etsy_limits_are_respected(self):
        from monster.twin import (ETSY_TAG_COUNT, ETSY_TAG_MAX_CHARS,
                                  ETSY_TITLE_MAX, etsy_tags, etsy_title, classify)
        long_title = ("Savinelli 920 KS Bent Dublin Estate Pipe Burgundy Finish "
                      "9mm Filter Unsmoked Italian Handmade Briar Collectible " * 3)
        title = etsy_title(long_title)
        self.assertLessEqual(len(title), ETSY_TITLE_MAX)
        self.assertFalse(title.endswith(" "))
        tags = etsy_tags(long_title, classify(long_title))
        self.assertLessEqual(len(tags), ETSY_TAG_COUNT)
        for tag in tags:
            self.assertLessEqual(len(tag), ETSY_TAG_MAX_CHARS)

    def test_output_is_stamped_and_sold_entry_stays_live(self):
        result = self._twin()
        self.assertTrue(result["asset_version"].startswith("pb-"))
        body = (result["out_dir"] / "site.md").read_text()
        self.assertIn("status: sold", body)
        self.assertIn("current", body.lower())     # points at current stock


class T18_DigFeedsThePlaybook(MonsterCase):
    """The loop was broken here: the dig printed candidate lessons and nothing
    carried them into the playbook, so Scale -> playbook -> Maker never closed.
    A lesson nobody records is a lesson nobody learns."""

    def setUp(self):
        super().setUp()
        rows, n = [], 0
        for brand in ("Dunhill", "Peterson", "Stanwell", "Comoy"):
            for j in range(30):
                boxed = j % 2 == 0
                n += 1
                rows.append(f"{n},{brand} Billiard {'Boxed' if boxed else ''},"
                            f"{100 * (1.3 if boxed else 1):.2f},2026-01-0{j % 9 + 1}\n")
        path = self.base / "ebay_sales.csv"
        path.write_text("Item Id,Listing Title,Price,Date\n" + "".join(rows),
                        encoding="utf-8")
        Well(self.root).load(path)
        from monster.dig import Dig
        self.dig = Dig(self.root)
        self.book = Playbook(self.root)

    def test_proposals_land_in_the_playbook_as_proposed(self):
        for line in self.dig.proposals():
            self.book.add_line(line)
        lines = self.book.lines()
        self.assertTrue(lines)
        self.assertTrue(all(x.status == "PROPOSED" for x in lines))
        self.assertEqual(self.book.for_maker(), [])      # Maker reads none of it yet

    def test_rerunning_a_dig_does_not_stack_duplicates(self):
        for _ in range(3):
            for line in self.dig.proposals():
                self.book.add_line(line)
        claims = [x.claim for x in self.book.lines()]
        self.assertEqual(len(claims), len(set(claims)))


class T19_TheMouth(MonsterCase):
    """Owned ground first, borrowed second — enforced, not remembered."""

    def test_ebay_before_owned_ground_is_refused(self):
        from monster.cli import main
        code = main(["--base", str(self.base), "publish", "pipes", "sku-1",
                     "--where", "ebay"])
        self.assertEqual(code, 2)
        self.assertEqual(Scale(self.root).rows(), [])

    def test_admin_records_site_and_etsy_in_one_step(self):
        """Farid's admin holds faridunhill and pushes Etsy automatically, so
        those are one act. Making him record two would be paperwork."""
        from monster.cli import main
        self.assertEqual(
            main(["--base", str(self.base), "publish", "pipes", "sku-1",
                  "--where", "admin"]), 0)
        surfaces = [r["surface"] for r in Scale(self.root).rows()
                    if r["event"] == "published"]
        self.assertEqual(surfaces, ["site", "etsy"])

    def test_ebay_allowed_once_owned_ground_is_live(self):
        from monster.cli import main
        main(["--base", str(self.base), "publish", "pipes", "sku-1", "--where", "admin"])
        self.assertEqual(
            main(["--base", str(self.base), "publish", "pipes", "sku-1",
                  "--where", "ebay"]), 0)
        surfaces = [r["surface"] for r in Scale(self.root).rows()
                    if r["event"] == "published"]
        self.assertEqual(surfaces, ["site", "etsy", "ebay"])

    def test_ebay_csv_marks_what_it_cannot_know(self):
        """Inventing a category id would produce a file that uploads wrong.
        Refusing to guess produces one that visibly needs a value."""
        from monster.twin import Twin
        result = Twin(self.root).build("Peterson System 307", 95.0, "pete-307",
                                       decision_id="D-001", sold_on="2026-08-01")
        body = (result["out_dir"] / "ebay.csv").read_text()
        self.assertIn("FILL_CATEGORY_ID", body)
        self.assertEqual(len(result["needs_filling"]), 3)

    def test_ebay_title_is_cut_to_80(self):
        from monster.twin import EBAY_TITLE_MAX, ebay_title
        long = "Savinelli Roma 626 Sandblast Bent Apple Vulcanite Stem Estate Pipe Italy Briar Collectible"
        self.assertLessEqual(len(ebay_title(long)), EBAY_TITLE_MAX)
        self.assertTrue(ebay_title(long))


class T20_NoCryingWolf(MonsterCase):
    """A warning that fires while the organ is working teaches people to
    ignore warnings — worse than no warning at all. The Digger was judged only
    by sources.jsonl, which records OUTSIDE sources, so it read as dead while
    it was digging the Well and proposing lessons."""

    def test_a_written_dig_counts_as_digger_activity(self):
        from monster.report import ledger_health
        digs = self.root / "digger" / "digs"
        digs.mkdir(parents=True)
        (digs / "DIG_001_2026-08-01_pipes.md").write_text("# dig", encoding="utf-8")
        digger = next(h for h in ledger_health(self.root) if h["organ"] == "DIGGER")
        self.assertEqual(digger["state"], "ok")
        self.assertEqual(digger["this_week"], 1)

    def test_a_truly_idle_digger_is_still_flagged(self):
        from monster.report import ledger_health
        digger = next(h for h in ledger_health(self.root) if h["organ"] == "DIGGER")
        self.assertEqual(digger["state"], "not_started")
