# Telegram Plant Care

Manage plant schedules, watering history, and reminders through Telegram. Watering calculations are deterministic; the bot does not use AI.

## Run entirely on GitHub Free

1. Create a Telegram bot with [@BotFather](https://t.me/BotFather) and send it a message.
2. In repository **Settings → Secrets and variables → Actions**, add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. These are the only bot secrets required. Never put either value in a file or commit.
3. Enable GitHub Actions and allow the workflow's `GITHUB_TOKEN` to write repository contents. The **Telegram Plant Bot** workflow polls Telegram once an hour, handles menu actions, and saves non-secret state in `plant_state.json` on the default branch.
4. Send `/start` to the bot. Replies and button actions can take up to an hour because GitHub Actions starts short jobs instead of a continuously running service. You can also start a cycle manually from **Actions → Telegram Plant Bot → Run workflow**.

GitHub-hosted standard runners are free for public repositories. GitHub Free includes 2,000 Actions minutes each month for private repositories; hourly polling uses about 720 one-minute runs per month. This repository is public, so standard runner minutes are free. GitHub may delay scheduled runs during periods of high load and disables scheduled workflows in public repositories after 60 days without repository activity. [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions) · [Scheduled workflow behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)

`plant_state.json` stores plant details, settings, watering and notification history, callback deduplication, and Telegram polling progress. It does not store the bot token or chat ID. **This repository is public, so its state file and plant information are public too.** State writes use atomic replacement, and the Actions workflow serializes bot runs before committing state updates.

## Telegram controls

- **My plants** lists plants with Watered, Snooze, Edit, Pause/Resume, and Delete actions. Delete asks for confirmation.
- **Add plant** and **Edit** guide you through name, type, location, watering interval, and optional seasonal intervals.
- **Watering / Status** lists plants that are due or approaching their due date.
- **Settings** controls reminders, preferred reminder time, timezone, upcoming-warning period, and seasonal adjustments.

Reminders default to **ON**. You can turn them off in Settings. Actionable due and upcoming reminders are sent at or after the configured local time on a bot cycle. Sending a reminder never changes watering history or the next watering date. Only the explicit **Watered** action appends a watering event and advances the date. Replayed button actions do not duplicate watering records.

Snooze changes the next reminder date without recording watering. Paused and deleted plants are excluded from reminder checks. Seasonal intervals are selected using the current season and can be disabled in Settings.

## Existing data

On first run, the bot imports plant definitions from `plant_config.json` into `plant_state.json`. It does **not** import `notifications_log.json` as watering history because the old system treated sent reminders as completed watering. Imported plants have no confirmed watering date and are initially due; review them in Telegram and record watering only when it happened.

## GitHub Actions and tests

GitHub Actions polls Telegram hourly and runs tests on pushes and pull requests. Reminders are enabled by default. No server, database, or paid hosting service is used.

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
```
