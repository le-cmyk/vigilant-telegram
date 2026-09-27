"""Telegram menus and callback handlers for plant management."""
from __future__ import annotations

import datetime as dt
import uuid


class BotHandlers:
    """Render menus and serialize user actions through validated services."""
    def __init__(self, service, repository, telegram):
        self.service, self.repository, self.telegram = service, repository, telegram
        self.flows = {}

    @staticmethod
    def _button(label, data): return {"text": label, "callback_data": data}

    def main_menu(self, chat_id):
        self.telegram.send(chat_id, "🌱 Plant care", [[self._button("🌿 My plants", "plants"), self._button("➕ Add plant", "add")],
            [self._button("💧 Watering / Status", "status"), self._button("⚙️ Settings", "settings")]])

    def plants_menu(self, chat_id):
        plants = self.service.list_plants()
        if not plants:
            self.telegram.send(chat_id, "No plants yet. Choose Add plant to get started.", [[self._button("➕ Add plant", "add")]])
            return
        for p in plants:
            state = "⏸ Paused" if p.get("paused") else f"Next: {p['next_due']}"
            actions = []
            if not p.get("paused"): actions.append(self._button("💧 Watered", f"water:{p['id']}"))
            actions.append(self._button("⏰ Snooze", f"snooze:{p['id']}"))
            actions.append(self._button("✏️ Edit", f"edit:{p['id']}"))
            actions.append(self._button("▶️ Resume" if p.get("paused") else "⏸ Pause", f"pause:{p['id']}"))
            actions.append(self._button("🗑 Delete", f"delete:{p['id']}"))
            self.telegram.send(chat_id, f"{p['name']} · {p['type']}\n{p['location']}\n{state}", [actions[i:i+2] for i in range(0, len(actions), 2)])

    def settings_menu(self, chat_id):
        s = self.repository.load()["settings"]
        toggle = "Turn reminders OFF" if s["reminders_enabled"] else "Turn reminders ON"
        season = "Seasonal adjustment: ON" if s["seasonal_adjustments"] else "Seasonal adjustment: OFF"
        rows = [[self._button(toggle, "setting:reminders_enabled")],
                [self._button(f"Reminder time: {s['preferred_time']}", "prompt:preferred_time"), self._button(f"Timezone: {s['timezone']}", "prompt:timezone")],
                [self._button(f"Upcoming warning: {s['upcoming_warning_days']} days", "prompt:upcoming_warning_days"), self._button(season, "setting:seasonal_adjustments")]]
        self.telegram.send(chat_id, "⚙️ Reminder settings (reminders start OFF)", rows)

    def status_menu(self, chat_id):
        due = self.service.due_plants()
        if not due:
            self.telegram.send(chat_id, "No plants need attention right now.")
            return
        self.telegram.send(chat_id, "💧 Plants needing attention:\n" + "\n".join(f"• {p['name']}: due {p['next_due']}" for p, _ in due),
                           [[self._button(f"💧 {p['name']} watered", f"water:{p['id']}")] for p, _ in due])

    def start_add(self, chat_id):
        self.flows[str(chat_id)] = {"kind": "add", "step": 0, "values": {}}
        self.telegram.send(chat_id, "Add plant · 1/5\nWhat is the plant name?")

    def start_edit(self, chat_id, plant_id):
        plant = self.service.get(plant_id)
        if not plant: self.telegram.send(chat_id, "This plant is no longer available."); return
        values = {k: plant[k] for k in ("name", "type", "location", "interval_days", "seasonal_intervals")}
        self.flows[str(chat_id)] = {"kind": "edit", "step": 0, "values": values, "plant_id": plant_id}
        self.telegram.send(chat_id, f"Edit plant · 1/5\nName? (current: {plant['name']})")

    def handle_text(self, chat_id, text):
        flow = self.flows.get(str(chat_id))
        if not flow:
            if text.strip().lower() in ("/start", "/menu", "menu"): self.main_menu(chat_id)
            else: self.telegram.send(chat_id, "Use /start to open the plant menu.")
            return
        if flow["kind"] == "setting":
            try:
                key = flow["key"]
                value = int(text.strip()) if key == "upcoming_warning_days" else text.strip()
                self.service.update_settings(**{key: value})
                del self.flows[str(chat_id)]
                self.telegram.send(chat_id, "✅ Setting saved.")
                self.settings_menu(chat_id)
            except ValueError as exc:
                self.telegram.send(chat_id, f"{exc}\nPlease try again.")
            return
        fields = ["name", "type", "location", "interval_days", "seasonal_intervals"]
        prompts = ["Plant name", "Plant type or species", "Room or location", "Watering interval in days", "Seasonal intervals: spring=7, summer=5, autumn=10, winter=14 (or 'same')"]
        key = fields[flow["step"]]
        if text.strip().lower() == "/skip" and flow["kind"] == "edit":
            flow["step"] += 1
            if flow["step"] < len(fields):
                self.telegram.send(chat_id, f"Edit plant · {flow['step']+1}/5\n{prompts[flow['step']]}")
                return
            plant = self.service.edit(flow["plant_id"], flow["values"])
            del self.flows[str(chat_id)]
            self.telegram.send(chat_id, f"✅ Saved {plant['name']}.")
            self.plants_menu(chat_id)
            return
        try:
            if key == "interval_days":
                if text.strip(): flow["values"][key] = int(text.strip())
                if not 1 <= flow["values"][key] <= 365: raise ValueError("Enter a whole number from 1 to 365.")
            elif key == "seasonal_intervals":
                if text.strip().lower() == "same":
                    flow["values"][key] = {}
                else:
                    intervals = {}
                    for part in text.split(","):
                        season, value = part.strip().split("=", 1); intervals[season.lower()] = int(value)
                    flow["values"][key] = intervals
                self.service.validate_plant(flow["values"])
            else:
                if text.strip(): flow["values"][key] = text.strip()
                if not flow["values"].get(key): raise ValueError("This field is required.")
            flow["step"] += 1
            if flow["step"] < len(fields):
                current = flow["values"].get(fields[flow["step"]])
                suffix = f" (current: {current}; send /skip to keep it)" if flow["kind"] == "edit" else ""
                self.telegram.send(chat_id, f"{flow['kind'].title()} plant · {flow['step']+1}/5\n{prompts[flow['step']]}{suffix}")
                return
            if flow["kind"] == "add": plant = self.service.add(flow["values"])
            else: plant = self.service.edit(flow["plant_id"], flow["values"])
            del self.flows[str(chat_id)]
            self.telegram.send(chat_id, f"✅ Saved {plant['name']} · every {plant['interval_days']} days.")
            self.plants_menu(chat_id)
        except (ValueError, KeyError) as exc:
            flow["step"] = max(0, flow["step"] - 1)
            self.telegram.send(chat_id, f"{exc}\n{prompts[flow['step']]}")

    def handle_callback(self, callback):
        data = callback.get("data", "")
        chat_id = callback.get("message", {}).get("chat", {}).get("id")
        callback_query_id = callback.get("id") or uuid.uuid4().hex
        message = callback.get("message", {})
        action_id = f"{chat_id}:{message.get('message_id', callback_query_id)}:{data}"
        first_use = self.repository.update(lambda state: False if action_id in state["processed_actions"] else state["processed_actions"].append(action_id) or True)
        if not first_use:
            try: self.telegram.answer_callback(callback_query_id, "Already handled")
            except Exception: pass  # A scheduled GitHub poll may process the tap after Telegram's spinner expired.
            return
        try:
            if data == "plants": self.plants_menu(chat_id)
            elif data == "add": self.start_add(chat_id)
            elif data == "status": self.status_menu(chat_id)
            elif data == "settings": self.settings_menu(chat_id)
            elif data.startswith("water:"):
                plant_id = data.split(":", 1)[1]; self.service.water(plant_id, action_id); self.telegram.send(chat_id, "✅ Watering recorded. Next date updated.")
            elif data.startswith("snooze:"):
                plant_id = data.split(":", 1)[1]
                self.telegram.send(chat_id, "Snooze until tomorrow?", [[self._button("⏰ Tomorrow", f"snooze1:{plant_id}"), self._button("⏰ 2 days", f"snooze2:{plant_id}"), self._button("⏰ 3 days", f"snooze3:{plant_id}")]])
            elif data.startswith("snooze") and ":" in data:
                days, plant_id = data.removeprefix("snooze").split(":", 1); self.service.snooze(plant_id, int(days), action_id); self.telegram.send(chat_id, f"⏰ Reminder snoozed for {days} day(s).")
            elif data.startswith("edit:"): self.start_edit(chat_id, data.split(":", 1)[1])
            elif data.startswith("pause:"):
                plant = self.service.get(data.split(":", 1)[1]); self.service.set_paused(plant["id"], not plant.get("paused")); self.plants_menu(chat_id)
            elif data.startswith("delete:"):
                plant_id = data.split(":", 1)[1]
                self.telegram.send(chat_id, "Delete this plant and keep its history?", [[self._button("Confirm delete", f"confirmdelete:{plant_id}"), self._button("Cancel", "plants")]])
            elif data.startswith("confirmdelete:"):
                self.service.delete(data.split(":", 1)[1], confirmed=True); self.telegram.send(chat_id, "🗑 Plant deleted."); self.plants_menu(chat_id)
            elif data.startswith("setting:"):
                key = data.split(":", 1)[1]; current = self.repository.load()["settings"][key]; self.service.update_settings(**{key: not current}); self.settings_menu(chat_id)
            elif data.startswith("prompt:"):
                key = data.split(":", 1)[1]; self.flows[str(chat_id)] = {"kind": "setting", "key": key}
                self.telegram.send(chat_id, {"preferred_time":"Enter reminder time in 24-hour HH:MM format.", "timezone":"Enter a timezone, such as Europe/Paris.", "upcoming_warning_days":"How many days ahead should warnings begin? (0–30)"}[key])
        except (ValueError, KeyError) as exc:
            self.telegram.send(chat_id, f"Could not apply that action: {exc}")
        finally:
            try: self.telegram.answer_callback(callback_query_id)
            except Exception: pass  # The action itself is recorded; callback acknowledgements can expire while queued.
