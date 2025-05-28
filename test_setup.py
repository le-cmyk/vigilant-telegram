#!/usr/bin/env python3
"""
Test script to verify Telegram bot configuration
Run this to test your bot setup before deploying to GitHub Actions
"""

from time_notifier import TelegramTimeNotifier, load_config

def main():
    print("🧪 Testing Telegram Bot Configuration")
    print("=" * 40)
      # Load configuration
    bot_token, chat_id = load_config()
    if not bot_token or not chat_id:
        print("❌ Missing configuration!")
        print("💡 Make sure to set environment variables:")
        print("   TELEGRAM_BOT_TOKEN (your bot token from @BotFather)")
        print("   TELEGRAM_CHAT_ID (your chat ID from @userinfobot)")
        return False
    
    print(f"✅ Configuration loaded")
    print(f"🤖 Bot token: {bot_token[:10]}...")
    print(f"💬 Chat ID: {chat_id}")
    
    # Initialize notifier
    notifier = TelegramTimeNotifier(bot_token, chat_id)
    
    # Test connection
    print("\n🔗 Testing bot connection...")
    if not notifier.test_connection():
        print("❌ Connection test failed!")
        return False
    
    # Send test message
    print("\n📤 Sending test message...")
    success = notifier.send_time_message()
    
    if success:
        print("\n🎉 All tests passed!")
        print("✅ Your bot is ready for GitHub Actions deployment")
        return True
    else:
        print("\n❌ Test message failed!")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n📋 Next steps:")
        print("1. Push this repository to GitHub")
        print("2. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID as repository secrets")
        print("3. Enable GitHub Actions")
        print("4. Watch your time notifications arrive every 10 minutes!")
    else:
        print("\n🔧 Please fix the configuration and try again")
