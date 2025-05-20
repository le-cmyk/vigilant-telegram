# Plant Watering Scheduler

Automated plant watering scheduler using GitHub Pages and Actions with Telegram notifications.

Supports:
- Adding a plant (via Issue Form)
- Removing a plant (via Issue Form)
- Daily Telegram reminders
- Manual triggering of add, remove, and reminder actions

## Setup

1. **Telegram Bot**: Create a bot via BotFather. Note down your `TELEGRAM_BOT_TOKEN` and your chat's `TELEGRAM_CHAT_ID`.
2. **GitHub Secrets**: In your repo Settings → Secrets & variables → Actions, add:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. **Issue Templates (Recommended)**: To use the "Add Plant" and "Remove Plant" issue forms as described in the "Managing Plants" section:
   - Create a folder named `.github/ISSUE_TEMPLATE` in your repository.
   - Inside this folder, create Markdown files for your issue templates. For example:
     - `add_plant.md` (for adding plants)
     - `remove_plant.md` (for removing plants)
   - These files should define the structure of your issues (e.g., using YAML frontmatter for forms or Markdown for basic templates). GitHub will then offer these as templates when you click "New issue".
4. **Push to `main`**: GitHub Pages will build the site, and Actions will handle additions, removals & notifications automatically.

## Managing Plants

### Adding a Plant

1. Go to the "Issues" tab in your GitHub repository.
2. Click on "New issue".
3. Choose the "Add Plant" issue template.
4. Fill in the plant's name, start date (when you last watered it or want to start tracking), and watering frequency in days.
5. Submit the issue. The GitHub Action will automatically add the plant to your schedule.

### Removing a Plant

1. Go to the "Issues" tab in your GitHub repository.
2. Click on "New issue".
3. Choose the "Remove Plant" issue template.
4. Fill in the exact name of the plant you want to remove.
5. Submit the issue. The GitHub Action will automatically remove the plant from your schedule.

## Manual Actions

You can manually trigger the workflows for adding plants, removing plants, and sending watering reminders.

1. Go to the "Actions" tab in your GitHub repository.
2. In the left sidebar, you will see the available workflows (e.g., "Add Plant", "Remove Plant", "Send Watering Reminders").
3. Click on the workflow you want to run.
4. Click the "Run workflow" dropdown button, usually on the right side.
5. You may need to input information depending on the workflow (e.g., plant details for adding a plant).
6. Click the "Run workflow" button.
