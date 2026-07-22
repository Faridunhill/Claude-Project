"""P2.5 test suite — five-event ledger, cohort stats, inference trigger."""

from datetime import datetime, timedelta, timezone

from marketing.phenotype import Event, PhenotypeLedger, price_band


def test_price_bands_fixed():
    assert price_band(10) == "0-25"
    assert price_band(99) == "50-100"
    assert price_band(150) == "150-300"
    assert price_band(5000) == "300+"
    assert price_band(None) == "unknown"


def test_only_five_events_exist():
    assert {e.value for e in Event} == {
        "listed", "price_changed", "offer_received", "sold", "returned"
    }


def test_ledger_is_append_only():
    assert not hasattr(PhenotypeLedger, "update")
    assert not hasattr(PhenotypeLedger, "delete")


def test_days_to_sale_computed_not_stored(tmp_path):
    led = PhenotypeLedger(tmp_path / "pheno.db")
    t0 = datetime(2026, 7, 1, tzinfo=timezone.utc)
    led.record("FH-1", Event.LISTED, "ebay", taxonomy="pipes/estate/dublin",
               list_price=99.0, ts=t0)
    led.record("FH-1", Event.OFFER_RECEIVED, "ebay", payload={"amount": 80.0},
               ts=t0 + timedelta(days=5))
    led.record("FH-1", Event.SOLD, "ebay", payload={"sold_price": 88.0},
               taxonomy="pipes/estate/dublin", list_price=99.0,
               ts=t0 + timedelta(days=11))
    assert led.days_to_sale("FH-1") == 11.0
    assert led.days_to_sale("FH-NEVER-SOLD") is None
    led.close()


def test_cohort_stats_and_trigger(tmp_path):
    led = PhenotypeLedger(tmp_path / "pheno.db")
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    # 49 sales in one cohort: trigger NOT met
    for i in range(49):
        sku = f"FH-{i:03d}"
        led.record(sku, Event.LISTED, "ebay", taxonomy="pipes/estate/dublin",
                   list_price=80.0, ts=t0 + timedelta(days=i))
        led.record(sku, Event.SOLD, "ebay", payload={"sold_price": 75.0},
                   taxonomy="pipes/estate/dublin", list_price=80.0,
                   ts=t0 + timedelta(days=i + 10))
    now = t0 + timedelta(days=90)
    stats = led.cohort_stats(now=now)
    assert len(stats) == 1
    s = stats[0]
    assert (s.taxonomy, s.band, s.sold_count) == ("pipes/estate/dublin", "50-100", 49)
    assert s.median_days_to_sale == 10.0
    assert s.median_sold_price == 75.0
    assert not s.trigger_met

    # the 50th sale wakes the trigger
    led.record("FH-049", Event.LISTED, "ebay", taxonomy="pipes/estate/dublin",
               list_price=80.0, ts=t0)
    led.record("FH-049", Event.SOLD, "ebay", payload={"sold_price": 70.0},
               taxonomy="pipes/estate/dublin", list_price=80.0,
               ts=t0 + timedelta(days=8))
    assert led.cohort_stats(now=now)[0].trigger_met
    assert led.inference_trigger_met()
    led.close()


def test_old_sales_age_out_of_trigger_window(tmp_path):
    led = PhenotypeLedger(tmp_path / "pheno.db")
    old = datetime(2020, 1, 1, tzinfo=timezone.utc)
    led.record("FH-OLD", Event.SOLD, "ebay", payload={"sold_price": 50.0},
               taxonomy="pipes/estate/dublin", list_price=60.0, ts=old)
    stats = led.cohort_stats(now=datetime(2026, 7, 1, tzinfo=timezone.utc))
    assert stats == []           # outside the rolling 365-day window
    led.close()


def test_event_history_per_sku(tmp_path):
    led = PhenotypeLedger(tmp_path / "pheno.db")
    t0 = datetime(2026, 7, 1, tzinfo=timezone.utc)
    led.record("FH-9", Event.LISTED, "etsy", list_price=120.0, ts=t0)
    led.record("FH-9", Event.PRICE_CHANGED, "etsy",
               payload={"old": 120.0, "new": 105.0, "reason": "stale-60d"},
               ts=t0 + timedelta(days=60))
    led.record("FH-9", Event.RETURNED, "etsy", payload={"reason": "changed_mind"},
               ts=t0 + timedelta(days=80))
    events = led.events_for("FH-9")
    assert [e["event"] for e in events] == ["listed", "price_changed", "returned"]
    assert events[1]["payload"]["new"] == 105.0
    led.close()
