"""Validated plant management and deterministic watering calculations."""
from __future__ import annotations

import datetime as dt
import uuid
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def season_for(date: dt.date) -> str:
    """Return the northern hemisphere season for a date."""
    return {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring",
            5: "spring", 6: "summer", 7: "summer", 8: "summer", 9: "autumn",
            10: "autumn", 11: "autumn"}[date.month]


class PlantService:
    """Business rules for plant lifecycle and reminder decisions."""

    def __init__(self, repository, today=None):
        self.repository = repository
        self._today_override = today

    def _today(self):
        """Read today's date in the user's configured timezone."""
        if self._today_override:
            return self._today_override()
        timezone = self.repository.load()["settings"].get("timezone", "UTC")
        return dt.datetime.now(ZoneInfo(timezone)).date()

    @staticmethod
    def validate_plant(data):
        name = str(data.get("name", "")).strip()
        kind = str(data.get("type", "")).strip()
        location = str(data.get("location", "")).strip()
        try:
            interval = int(data.get("interval_days", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError("Watering interval must be a whole number of days") from exc
        if not name or len(name) > 80: raise ValueError("Name must contain 1–80 characters")
        if not kind or len(kind) > 80: raise ValueError("Plant type must contain 1–80 characters")
        if not location or len(location) > 120: raise ValueError("Location must contain 1–120 characters")
        if not 1 <= interval <= 365: raise ValueError("Watering interval must be between 1 and 365 days")
        seasonal = data.get("seasonal_intervals", {}) or {}
        clean_seasonal = {}
        for season, value in seasonal.items():
            if season not in {"spring", "summer", "autumn", "winter"}: raise ValueError("Invalid season")
            try: days = int(value)
            except (TypeError, ValueError) as exc: raise ValueError("Season interval must be a whole number") from exc
            if not 1 <= days <= 365: raise ValueError("Season interval must be between 1 and 365 days")
            clean_seasonal[season] = days
        return {"name": name, "type": kind, "location": location,
                "interval_days": interval, "seasonal_intervals": clean_seasonal}

    def add(self, data):
        plant = self.validate_plant(data)
        today = self._today()
        plant.update(id=uuid.uuid4().hex[:12], active=True, paused=False,
                     created_at=today.isoformat(), next_due=today.isoformat(),
                     last_watered=None, revision=0)
        self.repository.update(lambda state: state["plants"].append(plant))
        return plant

    def list_plants(self, include_paused=True):
        plants = self.repository.load()["plants"]
        return [p for p in plants if p.get("active", True) and (include_paused or not p.get("paused"))]

    def get(self, plant_id):
        return next((p for p in self.repository.load()["plants"] if p["id"] == plant_id and p.get("active", True)), None)

    def edit(self, plant_id, data):
        values = self.validate_plant(data)
        def op(state):
            plant = next((p for p in state["plants"] if p["id"] == plant_id and p.get("active", True)), None)
            if plant is None: raise KeyError(plant_id)
            plant.update(values); plant["revision"] = plant.get("revision", 0) + 1
        self.repository.update(op)
        return self.get(plant_id)

    def water(self, plant_id, action_id=None):
        today = self._today()
        def op(state):
            if action_id and any(e.get("action_id") == action_id for e in state["watering_events"]):
                return False
            if any(e.get("plant_id") == plant_id and e.get("watered_at") == today.isoformat() for e in state["watering_events"]):
                return False
            plant = next((p for p in state["plants"] if p["id"] == plant_id and p.get("active", True)), None)
            if plant is None: raise KeyError(plant_id)
            if plant.get("paused"): raise ValueError("Plant is paused")
            due_season = season_for(today)
            seasonal_on = state["settings"].get("seasonal_adjustments", True)
            interval = plant.get("seasonal_intervals", {}).get(due_season, plant["interval_days"]) if seasonal_on else plant["interval_days"]
            plant["last_watered"] = today.isoformat()
            plant["next_due"] = (today + dt.timedelta(days=interval)).isoformat()
            plant["snoozed_until"] = None
            plant["revision"] = plant.get("revision", 0) + 1
            state["watering_events"].append({"id": uuid.uuid4().hex, "action_id": action_id,
                "plant_id": plant_id, "watered_at": today.isoformat(), "next_due": plant["next_due"]})
            return True
        return self.repository.update(op)

    def snooze(self, plant_id, days=1, action_id=None):
        if not 1 <= int(days) <= 30: raise ValueError("Snooze must be between 1 and 30 days")
        today = self._today()
        def op(state):
            if action_id and any(e.get("action_id") == action_id for e in state["snoozes"]): return False
            plant = next((p for p in state["plants"] if p["id"] == plant_id and p.get("active", True)), None)
            if plant is None: raise KeyError(plant_id)
            if plant.get("last_watered"):
                last = dt.date.fromisoformat(plant["last_watered"])
                settings = state["settings"]
                interval = plant.get("seasonal_intervals", {}).get(season_for(today), plant["interval_days"]) if settings.get("seasonal_adjustments", True) else plant["interval_days"]
                plant["next_due"] = (last + dt.timedelta(days=interval)).isoformat()
            plant["next_due"] = (max(dt.date.fromisoformat(plant["next_due"]), today) + dt.timedelta(days=int(days))).isoformat()
            plant["snoozed_until"] = plant["next_due"]
            state["snoozes"].append({"action_id": action_id, "plant_id": plant_id, "days": int(days), "date": today.isoformat()})
            return True
        return self.repository.update(op)

    def set_paused(self, plant_id, paused):
        def op(state):
            plant = next((p for p in state["plants"] if p["id"] == plant_id and p.get("active", True)), None)
            if plant is None: raise KeyError(plant_id)
            plant["paused"] = bool(paused); plant["revision"] = plant.get("revision", 0) + 1
        self.repository.update(op)

    def delete(self, plant_id, confirmed=False):
        if not confirmed: raise ValueError("Deletion requires confirmation")
        def op(state):
            plant = next((p for p in state["plants"] if p["id"] == plant_id and p.get("active", True)), None)
            if plant is None: raise KeyError(plant_id)
            plant["active"] = False
        self.repository.update(op)

    def due_plants(self, today=None):
        now = today or self._today()
        state = self.repository.load()
        warning = int(state["settings"].get("upcoming_warning_days", 2))
        result = []
        for plant in state["plants"]:
            if not plant.get("active", True) or plant.get("paused"): continue
            due = dt.date.fromisoformat(plant["next_due"])
            if plant.get("last_watered"):
                last = dt.date.fromisoformat(plant["last_watered"])
                season = season_for(now)
                interval = plant.get("seasonal_intervals", {}).get(season, plant["interval_days"]) if state["settings"].get("seasonal_adjustments", True) else plant["interval_days"]
                due = last + dt.timedelta(days=interval)
                if plant.get("snoozed_until"):
                    due = max(due, dt.date.fromisoformat(plant["snoozed_until"]))
                plant["next_due"] = due.isoformat()
            if due <= now + dt.timedelta(days=warning): result.append((plant, max(0, (due-now).days)))
        return result

    def update_settings(self, **changes):
        allowed = {"reminders_enabled", "preferred_time", "timezone", "upcoming_warning_days", "seasonal_adjustments"}
        if set(changes) - allowed: raise ValueError("Unknown setting")
        if "preferred_time" in changes:
            try: dt.datetime.strptime(changes["preferred_time"], "%H:%M")
            except ValueError as exc: raise ValueError("Time must use HH:MM") from exc
        if "timezone" in changes:
            try: ZoneInfo(changes["timezone"])
            except (ZoneInfoNotFoundError, TypeError) as exc: raise ValueError("Unknown timezone") from exc
        if "upcoming_warning_days" in changes and not 0 <= int(changes["upcoming_warning_days"]) <= 30:
            raise ValueError("Upcoming warning period must be 0–30 days")
        self.repository.update(lambda state: state["settings"].update(changes))
