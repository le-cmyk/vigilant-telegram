# Plant Watering Scheduler

Automated plant watering scheduler using GitHub Pages and Actions with Telegram notifications.

Supports:
- Adding a plant (via Issue Form or site form)
- Removing a plant (via Issue Form or site form)
- Daily Telegram reminders

## Setup

1. **Telegram Bot**: Create a bot via BotFather. Note down your `TELEGRAM_BOT_TOKEN` and your chat's `TELEGRAM_CHAT_ID`.
2. **GitHub Secrets**: In your repo Settings → Secrets & variables → Actions, add:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. **(Optional) OAuth Form**: If you want an embedded site form:
   - Register a GitHub OAuth App (Homepage: your Pages URL, Callback: `/oauth-callback.html`).
   - Host a token-exchange endpoint.
   - Update `CLIENT_ID` and proxy URL in `index.md` JS.
4. **Push to `main`**: GitHub Pages will build the site, and Actions will handle additions, removals & notifications automatically.
