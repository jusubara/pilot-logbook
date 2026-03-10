"""Pilot logbook application for tracking flight hours and entries."""

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import List, Optional


@dataclass
class FlightEntry:
    date: str
    aircraft_type: str
    aircraft_registration: str
    departure: str
    arrival: str
    departure_time: str
    arrival_time: str
    total_time: float
    pilot_in_command: float = 0.0
    second_in_command: float = 0.0
    dual_received: float = 0.0
    night: float = 0.0
    instrument: float = 0.0
    cross_country: float = 0.0
    landings_day: int = 0
    landings_night: int = 0
    remarks: str = ""


@dataclass
class Logbook:
    pilot_name: str
    certificate_number: str
    entries: List[FlightEntry] = field(default_factory=list)

    def add_entry(self, entry: FlightEntry) -> None:
        self.entries.append(entry)

    def total_hours(self) -> float:
        return sum(e.total_time for e in self.entries)

    def total_pic_hours(self) -> float:
        return sum(e.pilot_in_command for e in self.entries)

    def total_night_hours(self) -> float:
        return sum(e.night for e in self.entries)

    def total_instrument_hours(self) -> float:
        return sum(e.instrument for e in self.entries)

    def total_cross_country_hours(self) -> float:
        return sum(e.cross_country for e in self.entries)

    def total_landings(self) -> int:
        return sum(e.landings_day + e.landings_night for e in self.entries)

    def entries_for_aircraft(self, registration: str) -> List[FlightEntry]:
        return [e for e in self.entries if e.aircraft_registration == registration]

    def entries_in_date_range(self, start: str, end: str) -> List[FlightEntry]:
        for label, value in (("start", start), ("end", end)):
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"Invalid {label} date {value!r}: expected YYYY-MM-DD format"
                )
        return [e for e in self.entries if start <= e.date <= end]

    def recent_experience(self, days: int = 90) -> List[FlightEntry]:
        """Return entries from the last `days` days."""
        # TODO: Replace string-based date comparison with proper datetime arithmetic
        # so that `days` is computed relative to today rather than a hardcoded cutoff.
        cutoff = "2000-01-01"  # placeholder; replace with real cutoff logic
        return [e for e in self.entries if e.date >= cutoff]

    def currency_check(self) -> dict:
        """Check FAR 61.57 currency requirements."""
        # TODO: Implement FAR 61.57 passenger-carrying currency check:
        # Return a dict with 'day_current' and 'night_current' booleans indicating
        # whether the pilot has made 3 takeoffs/landings in the last 90 days (day)
        # and 3 night takeoffs/landings in the last 90 days (night).
        return {"day_current": False, "night_current": False}

    def summary(self) -> dict:
        return {
            "pilot": self.pilot_name,
            "certificate": self.certificate_number,
            "total_flights": len(self.entries),
            "total_hours": round(self.total_hours(), 1),
            "pic_hours": round(self.total_pic_hours(), 1),
            "night_hours": round(self.total_night_hours(), 1),
            "instrument_hours": round(self.total_instrument_hours(), 1),
            "cross_country_hours": round(self.total_cross_country_hours(), 1),
            "total_landings": self.total_landings(),
        }

    def save(self, filepath: str) -> None:
        data = {
            "pilot_name": self.pilot_name,
            "certificate_number": self.certificate_number,
            "entries": [asdict(e) for e in self.entries],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "Logbook":
        with open(filepath) as f:
            data = json.load(f)
        entries = [FlightEntry(**e) for e in data["entries"]]
        logbook = cls(
            pilot_name=data["pilot_name"],
            certificate_number=data["certificate_number"],
        )
        logbook.entries = entries
        return logbook
