# 🌱 Plant Watering Reminder System

An intelligent plant care reminder system that sends personalized watering notifications via Telegram using GitHub Actions. Track different plant types with customized schedules that adapt to seasons!

## ✨ Features

- **Smart Scheduling**: Different watering schedules for each plant type
- **Seasonal Adjustments**: Automatically adjusts watering frequency based on seasons
- **Telegram Notifications**: Sends beautiful, organized reminders via Telegram
- **Plant Status Tracking**: Monitors overdue, due today, and upcoming watering needs
- **Care Tips**: Includes helpful plant care advice in notifications
- **Automated Logging**: Tracks all notifications and plant care history
- **GitHub Actions Integration**: Runs automatically twice daily

## 🪴 Supported Plant Types

The system comes pre-configured with 5 popular houseplants:

1. **🕷️🌱 Spider Plant** - Weekly watering (5-14 days based on season)
2. **💎🌿 Jade Plant** - Bi-weekly watering (7-21 days based on season)  
3. **🐍🌿 Snake Plant** - Monthly watering (10-30 days based on season)
4. **🍃✨ Golden Pothos** - Weekly watering (4-10 days based on season)
5. **☮️🌸 Peace Lily** - Frequent watering (3-7 days based on season)

## 📁 Configuration Files

### `plant_config.json`
Contains plant definitions, care schedules, and settings

### `watering_history.json` 
Tracks when each plant was last watered

## 🤖 GitHub Actions Workflow

The system runs automatically twice daily at:
- **9:00 AM UTC** - Morning reminder
- **6:00 PM UTC** - Evening check

You can also trigger it manually from the GitHub Actions tab.

## 🔧 Setup Instructions

1. **Fork this repository** to your GitHub account

2. **Set up Telegram Bot**:
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot with `/newbot`
   - Save your bot token

3. **Get your Chat ID**:
   - Message your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

4. **Configure GitHub Secrets**:
   - Go to your repository Settings → Secrets and variables → Actions
   - Add these secrets:
     - `TELEGRAM_BOT_TOKEN`: Your bot token
     - `TELEGRAM_CHAT_ID`: Your chat ID

5. **Customize your plants**:
   - Edit `plant_config.json` to match your actual plants
   - Update `watering_history.json` with last watering dates

6. **Enable GitHub Actions**:
   - Go to the Actions tab in your repository
   - Enable workflows if prompted

## 📱 Notification Examples

**When plants need water:**
```
🌱 Plant Watering Reminders

🚨 URGENT - Overdue:
🐍🌿 Snake Plant (Bedroom Corner)
   💡 Very drought tolerant. Water sparingly.

📅 Due Today:  
🕷️🌱 Spider Plant (Living Room Window)
   💡 Water when top inch of soil is dry.

⏰ Coming Up (Next 2 Days):
💎🌿 Jade Plant (Office Desk)

🌍 Current Season: 🌸 Spring

💡 Tip of the day: 💧 Water in the morning for best absorption
```

**When all plants are happy:**
```
🌱 Plant Care Update

All your plants are happy and well-watered! 🎉

Next check: Tomorrow
```

## 🌿 Adding New Plants

To add a new plant, edit `plant_config.json` and add a new plant object with:
- Unique `id`
- Descriptive `name` and `location`
- `watering_schedule` with seasonal adjustments
- `care_notes` for helpful tips
- Fun `emoji` for visual appeal
- Set `active: true`

Then add a corresponding entry to `watering_history.json` with the last watering date.

## 🔄 Seasonal Adjustments

The system automatically adjusts watering schedules based on seasons:
- **Spring** (Mar-May): Moderate growth period
- **Summer** (Jun-Aug): High growth, more frequent watering  
- **Autumn** (Sep-Nov): Slowing growth, less frequent watering
- **Winter** (Dec-Feb): Dormant period, least frequent watering

## 📊 Logging & History

All notifications are logged to `notifications_log.json` with:
- Timestamp and plant status summary
- Message content and delivery status
- Seasonal information
- Error tracking

## 🛠️ Technical Details

- **Language**: Python 3.9+
- **Dependencies**: `requests` for Telegram API calls
- **Automation**: GitHub Actions with cron scheduling
- **Data Storage**: JSON files for configuration and history
- **Notifications**: Telegram Bot API with Markdown formatting

---

🌱 Happy plant parenting! Your green friends will thank you. 🌿