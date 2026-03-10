"""Tests for the pilot logbook application."""

import pytest
from logbook import FlightEntry, Logbook


def make_entry(**kwargs) -> FlightEntry:
    defaults = dict(
        date="2024-06-15",
        aircraft_type="C172",
        aircraft_registration="N12345",
        departure="KSFO",
        arrival="KOAK",
        departure_time="10:00",
        arrival_time="10:30",
        total_time=0.5,
        pilot_in_command=0.5,
        landings_day=1,
    )
    defaults.update(kwargs)
    return FlightEntry(**defaults)


@pytest.fixture
def logbook():
    lb = Logbook(pilot_name="Jane Doe", certificate_number="1234567")
    lb.add_entry(make_entry(date="2024-01-10", total_time=1.5, pilot_in_command=1.5, night=0.5, landings_day=2))
    lb.add_entry(make_entry(date="2024-03-20", total_time=2.0, pilot_in_command=2.0, instrument=1.0, landings_day=1))
    lb.add_entry(make_entry(date="2024-06-01", total_time=3.0, pilot_in_command=1.0, cross_country=3.0, landings_day=1))
    return lb


def test_total_hours(logbook):
    assert logbook.total_hours() == 6.5


def test_total_pic_hours(logbook):
    assert logbook.total_pic_hours() == 4.5


def test_total_night_hours(logbook):
    assert logbook.total_night_hours() == 0.5


def test_total_instrument_hours(logbook):
    assert logbook.total_instrument_hours() == 1.0


def test_total_cross_country_hours(logbook):
    assert logbook.total_cross_country_hours() == 3.0


def test_total_landings(logbook):
    assert logbook.total_landings() == 4


def test_entries_for_aircraft(logbook):
    assert len(logbook.entries_for_aircraft("N12345")) == 3
    assert len(logbook.entries_for_aircraft("N99999")) == 0


def test_entries_in_date_range(logbook):
    results = logbook.entries_in_date_range("2024-01-01", "2024-04-01")
    assert len(results) == 2


def test_entries_in_date_range_invalid_date():
    lb = Logbook(pilot_name="Test Pilot", certificate_number="0000000")
    lb.add_entry(make_entry())
    with pytest.raises(ValueError):
        lb.entries_in_date_range("not-a-date", "2024-12-31")


def test_summary(logbook):
    s = logbook.summary()
    assert s["total_flights"] == 3
    assert s["total_hours"] == 6.5
    assert s["pilot"] == "Jane Doe"


def test_save_and_load(tmp_path, logbook):
    filepath = str(tmp_path / "logbook.json")
    logbook.save(filepath)
    loaded = Logbook.load(filepath)
    assert loaded.pilot_name == logbook.pilot_name
    assert len(loaded.entries) == len(logbook.entries)
    assert loaded.total_hours() == logbook.total_hours()
