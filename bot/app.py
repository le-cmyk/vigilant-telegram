"""Single-cycle Telegram bot runner for GitHub Actions."""
import datetime as dt
import logging
import os
from zoneinfo import ZoneInfo

from plants.service import PlantService
from storage.repository import Repository
from telegram.client import TelegramClient
from bot.handlers import BotHandlers

LOG = logging.getLogger(__name__)


class BotApp:
    """Poll Telegram once, handle controls, and send actionable reminders."""
    def __init__(self, token, chat_id, repository, client=None, service=None):
        if not chat_id: raise ValueError("TELEGRAM_CHAT_ID is required")
        self.chat_id = str(chat_id)
        self.repository = repository
        self.client = client or TelegramClient(token)
        self.service = service or PlantService(repository)
        self.handlers = BotHandlers(self.service, repository, self.client)
        state = repository.load()
        self.offset = state.get("telegram_offset")
        self.handlers.flows = state.get("conversation_flows", {})

    def _remind(self, now=None):
        settings = self.repository.load()["settings"]
        if not settings.get("reminders_enabled", False): return
        tz = ZoneInfo(settings.get("timezone", "UTC"))
        now = now or dt.datetime.now(tz)
        target = dt.time.fromisoformat(settings.get("preferred_time", "09:00"))
        if now.time().replace(tzinfo=None) < target: return
        due = self.service.due_plants(now.date())
        for plant, days_left in due:
            kind = "upcoming" if days_left > 0 else "due"
            marker = f"{plant['id']}:{plant['next_due']}:{kind}"
            state = self.repository.load()
            previous = next((event for event in reversed(state["notification_events"]) if event.get("dedupe_key") == marker), None)
            if previous and (previous.get("status") == "sent" or (now - dt.datetime.fromisoformat(previous["sent_at"])).total_seconds() < 900): continue
            keyboard = [[self.handlers._button("💧 Watered", f"water:{plant['id']}"), self.handlers._button("⏰ Snooze", f"snooze:{plant['id']}")]]
            when = "due today" if days_left == 0 else f"due in {days_left} day(s)"
            try:
                result = self.client.send(
                    self.chat_id,
                    f"🪴 {plant['name']}\n📍 {plant['location']}\nWatering is {when}.",
                    keyboard,
                )
                self.repository.update(lambda s: s["notification_events"].append({"id": f"telegram:{result.get('message_id', 'unknown')}:{marker}", "plant_id": plant["id"], "dedupe_key": marker, "sent_at": now.isoformat(), "status": "sent"}))
            except Exception as exc:
                LOG.exception("Failed to send reminder for plant %s", plant["id"])
                self.repository.update(lambda s: s["notification_events"].append({"plant_id": plant["id"], "dedupe_key": marker, "sent_at": now.isoformat(), "status": "error", "error": str(exc)}))

    def run_once(self):
        self._remind()
        updates = self.client.updates(self.offset, timeout=20)
        for update in updates:
            next_offset = update["update_id"] + 1
            if "message" in update:
                message = update["message"]
                if str(message.get("chat", {}).get("id")) == self.chat_id:
                    text = message.get("text", "")
                    if text.strip().lower() in ("/start", "/menu", "menu"): self.handlers.main_menu(self.chat_id)
                    else: self.handlers.handle_text(self.chat_id, text)
            elif "callback_query" in update:
                callback = update["callback_query"]
                if str(callback.get("message", {}).get("chat", {}).get("id")) == self.chat_id:
                    self.handlers.handle_callback(callback)
            self.offset = next_offset
            flows = self.handlers.flows.copy()
            self.repository.update(lambda state: state.update({"telegram_offset": next_offset,
                                                                "conversation_flows": flows}))


def main():
    token, chat_id = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id: raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
    repository = Repository(os.getenv("PLANT_STATE_FILE", "plant_state.json"))
    try:
        BotApp(token, chat_id, repository).run_once()
    except Exception:
        LOG.exception("GitHub Actions bot cycle failed")
        raise SystemExit(1)


if __name__ == "__main__": main()
