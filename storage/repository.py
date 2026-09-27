"""Atomic JSON persistence for plants, settings, and append-only events."""
from __future__ import annotations

import json
import os
import tempfile
import threading
import datetime as dt
from pathlib import Path
from typing import Any


def dt_today() -> str:
    """Return the local calendar date used for migrated plants."""
    return dt.date.today().isoformat()


class Repository:
    """Persist application state in one atomically replaced JSON document."""

    def __init__(self, path: str | Path, legacy_config: str | Path = "plant_config.json"):
        self.path = Path(path)
        self._lock = threading.RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            state = self._initial_state()
            legacy_path = Path(legacy_config)
            if legacy_path.exists():
                try:
                    with legacy_path.open(encoding="utf-8") as stream: legacy = json.load(stream)
                    for old in legacy.get("plants", []):
                        schedule = old.get("watering_schedule", {})
                        interval = int(schedule.get("frequency_days", 7))
                        state["plants"].append({"id": old["id"], "name": old["name"], "type": old.get("type", "Plant"),
                            "location": old.get("location", ""), "interval_days": interval,
                            "seasonal_intervals": schedule.get("season_adjustments", {}), "active": old.get("active", True),
                            "paused": False, "created_at": dt_today(), "last_watered": None,
                            "next_due": dt_today(), "revision": 0})
                except (OSError, ValueError, TypeError, KeyError):
                    # A broken legacy file must not prevent the new bot from starting.
                    pass
            self._write(state)

    @staticmethod
    def _initial_state() -> dict[str, Any]:
        return {"version": 1, "plants": [], "settings": {
            "reminders_enabled": True, "preferred_time": "09:00",
            "timezone": "UTC", "upcoming_warning_days": 2,
            "seasonal_adjustments": True}, "watering_events": [],
            "notification_events": [], "snoozes": [], "processed_actions": [],
            "telegram_offset": None, "conversation_flows": {}}

    def _write(self, state: dict[str, Any]) -> None:
        fd, temp_name = tempfile.mkstemp(prefix=f".{self.path.name}.", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(state, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def load(self) -> dict[str, Any]:
        with self._lock:
            with self.path.open(encoding="utf-8") as stream:
                state = json.load(stream)
            if not isinstance(state, dict) or not isinstance(state.get("plants"), list):
                raise ValueError("Invalid plant state file")
            state.setdefault("processed_actions", [])
            state.setdefault("watering_events", [])
            state.setdefault("notification_events", [])
            state.setdefault("snoozes", [])
            state.setdefault("settings", self._initial_state()["settings"])
            state["settings"].setdefault("reminders_enabled", True)
            state.setdefault("telegram_offset", None)
            state.setdefault("conversation_flows", {})
            return state

    def update(self, operation):
        """Run an operation while holding the lock, then safely persist state."""
        with self._lock:
            state = self.load()
            result = operation(state)
            self._write(state)
            return result
