import datetime as dt
import json
from pathlib import Path
import pytest

from bot.app import BotApp
from plants.service import PlantService
from storage.repository import Repository
from telegram.client import TelegramClient


@pytest.fixture
def setup(tmp_path):
    now = [dt.date(2026, 6, 1)]
    repo = Repository(tmp_path / "state.json", legacy_config=tmp_path / "missing.json")
    service = PlantService(repo, today=lambda: now[0])
    return repo, service, now


def draft(**changes):
    data = {"name": "Fern", "type": "Boston fern", "location": "Kitchen", "interval_days": 7,
            "seasonal_intervals": {"summer": 4, "winter": 14}}
    data.update(changes)
    return data


def test_full_lifecycle_and_restart(setup):
    repo, service, now = setup
    plant = service.add(draft())
    assert service.list_plants()[0]["id"] == plant["id"]
    service.edit(plant["id"], draft(name="Fern 2", location="Window"))
    assert service.due_plants()[0][0]["id"] == plant["id"]
    service.snooze(plant["id"], 1, "snooze-1")
    assert service.snooze(plant["id"], 1, "snooze-1") is False
    assert service.get(plant["id"])["next_due"] == "2026-06-02"
    service.water(plant["id"], "water-1")
    assert service.water(plant["id"], "water-1") is False
    assert service.water(plant["id"], "different-button") is False
    assert service.get(plant["id"])["last_watered"] == "2026-06-01"
    assert service.get(plant["id"])["next_due"] == "2026-06-05"
    service.set_paused(plant["id"], True)
    assert not service.due_plants()
    service.set_paused(plant["id"], False)
    reloaded = PlantService(Repository(repo.path, legacy_config=repo.path.parent / "missing"), today=lambda: now[0])
    assert reloaded.get(plant["id"])["next_due"] == "2026-06-05"
    service.delete(plant["id"], confirmed=True)
    assert service.list_plants() == []
    state = repo.load()
    assert len(state["watering_events"]) == 1
    assert state["notification_events"] == []


def test_invalid_input_settings_and_confirm_delete(setup):
    repo, service, _ = setup
    assert repo.load()["settings"]["reminders_enabled"] is True
    with pytest.raises(ValueError): service.add(draft(interval_days=0))
    with pytest.raises(ValueError): service.add(draft(name="  "))
    with pytest.raises(ValueError): service.update_settings(timezone="Not/AZone")
    with pytest.raises(ValueError): service.update_settings(preferred_time="9am")
    with pytest.raises(ValueError): service.update_settings(upcoming_warning_days=99)
    with pytest.raises(ValueError): service.snooze("missing", 0)
    plant = service.add(draft())
    with pytest.raises(ValueError): service.delete(plant["id"])


def test_season_transitions_and_season_toggle(setup):
    _, service, now = setup
    now[0] = dt.date(2026, 3, 1)
    plant = service.add(draft())
    service.water(plant["id"])
    assert service.get(plant["id"])["next_due"] == "2026-03-08"
    now[0] = dt.date(2026, 7, 1)
    assert service.due_plants()[0][0]["next_due"] == "2026-03-05"
    service.update_settings(seasonal_adjustments=False)
    assert service.due_plants()[0][0]["next_due"] == "2026-03-08"


class FakeTelegram:
    def __init__(self, fail=False): self.fail, self.sent = fail, []
    @property
    def pending(self): return getattr(self, "_pending", [])
    @pending.setter
    def pending(self, value): self._pending = value
    def send(self, chat_id, text, keyboard=None):
        if self.fail: raise RuntimeError("API unavailable")
        self.sent.append((chat_id, text, keyboard)); return {"message_id": len(self.sent)}
    def updates(self, *args, **kwargs):
        pending, self._pending = self.pending, []
        return pending
    def answer_callback(self, *_args, **_kwargs): return None


def test_duplicate_callback_does_not_toggle_pause_twice(setup):
    repo, service, _ = setup
    plant = service.add(draft())
    fake = FakeTelegram()
    from bot.handlers import BotHandlers
    handlers = BotHandlers(service, repo, fake)
    callback = {"id": "callback-1", "data": f"pause:{plant['id']}", "message": {"message_id": 19, "chat": {"id": 123}}}
    handlers.handle_callback(callback)
    replay = {**callback, "id": "callback-2"}
    handlers.handle_callback(replay)
    assert service.get(plant["id"])["paused"] is True


def test_github_cycle_persists_telegram_offset_and_guided_flow(setup):
    repo, service, _ = setup
    fake = FakeTelegram()
    fake.pending = [{"update_id": 42, "callback_query": {"id": "add-1", "data": "add", "message": {"chat": {"id": 123}}}}]
    app = BotApp("token", "123", repo, client=fake, service=service)
    app.run_once()
    state = repo.load()
    assert state["telegram_offset"] == 43
    assert state["conversation_flows"]["123"]["kind"] == "add"
    resumed = BotApp("token", "123", repo, client=FakeTelegram(), service=service)
    assert resumed.handlers.flows["123"]["step"] == 0


def test_reminder_never_records_watering_and_deduplicates(setup):
    repo, service, now = setup
    plant = service.add(draft())
    service.update_settings(reminders_enabled=True, preferred_time="09:00", timezone="UTC")
    app = BotApp("token", "123", repo, client=FakeTelegram(), service=service)
    stamp = dt.datetime(2026, 6, 1, 9, 0, tzinfo=dt.timezone.utc)
    app._remind(stamp); app._remind(stamp)
    state = repo.load()
    assert len(state["notification_events"]) == 1
    assert state["watering_events"] == []
    assert service.get(plant["id"])["last_watered"] is None
    service.water(plant["id"], "confirmed")
    assert len(repo.load()["watering_events"]) == 1


def test_requested_end_to_end_sequence(setup):
    repo, service, now = setup
    plant = service.add(draft())
    assert service.list_plants()
    service.edit(plant["id"], draft(name="Fern by window"))
    service.update_settings(reminders_enabled=True, preferred_time="09:00", timezone="UTC")
    fake = FakeTelegram()
    app = BotApp("token", "123", repo, client=fake, service=service)
    morning = dt.datetime(2026, 6, 1, 9, 0, tzinfo=dt.timezone.utc)
    app._remind(morning)
    assert fake.sent and repo.load()["watering_events"] == []
    service.snooze(plant["id"], 1, "snooze-once")
    now[0] = dt.date(2026, 6, 2)
    app._remind(dt.datetime(2026, 6, 2, 9, 0, tzinfo=dt.timezone.utc))
    assert len(fake.sent) == 2
    assert repo.load()["watering_events"] == []
    service.water(plant["id"], "water-once")
    assert service.get(plant["id"])["next_due"] == "2026-06-06"
    service.snooze(plant["id"], 2, "snooze-after-water")
    assert service.get(plant["id"])["next_due"] == "2026-06-08"
    assert service.due_plants() == []
    now[0] = dt.date(2026, 6, 8)
    assert service.due_plants()[0][0]["next_due"] == "2026-06-08"
    service.set_paused(plant["id"], True)
    assert service.due_plants() == []
    service.set_paused(plant["id"], False)
    assert service.get(plant["id"])["paused"] is False
    service.delete(plant["id"], confirmed=True)
    assert service.get(plant["id"]) is None


def test_telegram_failure_logged_but_never_watered(setup):
    repo, service, _ = setup
    service.add(draft())
    service.update_settings(reminders_enabled=True)
    app = BotApp("token", "123", repo, client=FakeTelegram(fail=True), service=service)
    app._remind(dt.datetime(2026, 6, 1, 9, 0, tzinfo=dt.timezone.utc))
    state = repo.load()
    assert state["notification_events"][0]["status"] == "error"
    assert state["watering_events"] == []


def test_missing_secrets_and_api_client_failures(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    with pytest.raises(SystemExit):
        from bot.app import main
        main()
    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
        TelegramClient("")


def test_telegram_api_failure_is_sanitized(monkeypatch):
    import telegram.client as module
    def fail(*_args, **_kwargs): raise OSError("request URL contained token=secret")
    monkeypatch.setattr(module, "urlopen", fail)
    with pytest.raises(RuntimeError, match="request failed") as error:
        TelegramClient("sensitive-token").send("1", "hello")
    assert "sensitive-token" not in str(error.value)


def test_github_actions_only_runs_tests_without_schedule_or_secrets():
    root = Path(__file__).parents[1]
    workflow = (root / ".github/workflows/tests.yml").read_text()
    bot_workflow = (root / ".github/workflows/plant-bot.yml").read_text()
    assert "schedule:" not in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "pytest" in workflow
    assert "TELEGRAM_BOT_TOKEN" not in workflow
    assert "cron: '13 * * * *'" in bot_workflow
    assert "contents: write" in bot_workflow
    assert "git add -f plant_state.json" in bot_workflow
    assert "TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}" in bot_workflow


def test_legacy_seed_does_not_treat_notifications_as_watering(tmp_path):
    legacy = tmp_path / "plants.json"
    legacy.write_text(json.dumps({"plants": [{"id":"p1", "name":"Fern", "type":"Fern", "location":"Room", "watering_schedule":{"frequency_days":8, "season_adjustments":{"winter":12}}}]}))
    (tmp_path / "notifications_log.json").write_text(json.dumps({"watering_events":[{"status":"success", "plants_watered":[{"plant_id":"p1", "watered_date":"2026-05-30"}]}]}))
    repo = Repository(tmp_path / "state.json", legacy_config=legacy)
    plant = repo.load()["plants"][0]
    assert plant["last_watered"] is None
    assert plant["next_due"] == dt.date.today().isoformat()
    assert repo.load()["watering_events"] == []
