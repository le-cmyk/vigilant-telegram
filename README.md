# 🌱 Telegram Watering Plants Notifier

[![GitHub Actions](https://img.shields.io/github/workflow/status/username/repo/Send%20Time%20Notification)](https://github.com/username/repo/actions)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)

Un système automatisé de notifications Telegram pour rappeler l'arrosage des plantes, avec journalisation complète des envois.

## 🎯 Fonctionnalités

### ✅ Implémentées (Version 1.1)
- 🕐 **Notifications automatiques** : Envoi de l'heure actuelle via Telegram
- 📝 **Journalisation JSON** : Enregistrement de toutes les notifications avec métadonnées complètes
- 🔄 **Push automatique** : Synchronisation automatique du fichier de log vers GitHub
- 🧪 **Tests robustes** : Couverture de test complète pour la fiabilité
- ⚡ **GitHub Actions** : Exécution automatique toutes les 3 heures + notification quotidienne

### 🚀 À venir
- 🌱 Gestion personnalisée des plantes avec fréquences d'arrosage
- 💬 Interface de commandes Telegram interactives
- 🗄️ Base de données pour le suivi des plantes
- 🧠 Notifications intelligentes basées sur les besoins des plantes

## Setup

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Chat ID

1. Start a conversation with your bot
2. Send any message to your bot
3. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find your chat ID in the response (usually a number like `123456789`)

### 3. Configure GitHub Secrets

1. Go to your repository settings
2. Navigate to **Secrets and variables** → **Actions**
3. Add the following repository secrets:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from step 1
   - `TELEGRAM_CHAT_ID`: Your chat ID from step 2

## Usage

### Automated Notifications

The service runs automatically via GitHub Actions:

- **Every 3 hours**: Sends current time
- **Daily at 9:00 AM UTC**: Sends a daily summary

### Manual Testing

1. Go to the **Actions** tab in your repository
2. Select either workflow:
   - "Time Notification (Every 3 Hours)"
   - "Daily Time Notification"
3. Click **Run workflow** to test manually

### Local Testing (Optional)

To test the setup locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"

# Test configuration
python test_setup.py

# Send a test notification
python time_notifier.py
```

## File Structure

```
├── .github/workflows/
│   ├── time-notification.yml    # Every 3 hours workflow
│   └── daily-time.yml          # Daily notification workflow
├── time_notifier.py            # Main notification script
├── test_setup.py              # Configuration test script
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Configuration

The service uses environment variables for configuration:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID

These should be set as GitHub repository secrets for security.

## Troubleshooting

### Common Issues

1. **Bot not responding**: Ensure you've started a conversation with your bot
2. **Permission errors**: Make sure the bot token and chat ID are correct
3. **Workflow not running**: Check that GitHub Actions are enabled for your repository

### Testing Your Setup

Run the test script to verify your configuration:

```bash
python test_setup.py
```

This will check:
- Environment variables are set
- Bot token is valid
- Chat ID is accessible
- Test message can be sent

## GitHub Actions Workflows

### Every 3 Hours Notification
- **File**: `.github/workflows/time-notification.yml`
- **Schedule**: `0 */3 * * *` (every 3 hours)
- **Manual trigger**: Supported

### Daily Notification
- **File**: `.github/workflows/daily-time.yml`
- **Schedule**: `0 9 * * *` (daily at 9:00 AM UTC)
- **Manual trigger**: Supported

## Security

- Bot tokens and chat IDs are stored as encrypted GitHub secrets
- No sensitive information is exposed in the code
- All communication uses HTTPS

## License

This project is open source and available under the [MIT License](LICENSE).