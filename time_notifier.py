#!/usr/bin/env python3
"""
Telegram Time Notifier
A simple script that sends the current time via Telegram using GitHub Actions.
"""

import requests
import datetime
import os
from typing import Optional

class TelegramTimeNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize the Telegram Time Notifier.
        
        Args:
            bot_token (str): Your Telegram bot token
            chat_id (str): Your Telegram chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_time_message(self) -> bool:
        """
        Send the current time to Telegram.
        
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            day_name = current_time.strftime("%A")
            
            message = f"🕐 **Current Time**\n\n" \
                     f"📅 {day_name}\n" \
                     f"⏰ {formatted_time}"
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Time message sent successfully at {formatted_time}")
                return True
            else:
                print(f"❌ Failed to send message. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test the Telegram bot connection.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                print(f"✅ Bot connection successful!")
                print(f"Bot name: {bot_info['result']['first_name']}")
                return True
            else:
                print(f"❌ Bot connection failed. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

def load_config() -> tuple[Optional[str], Optional[str]]:
    """
    Load configuration from environment variables.
    
    Returns:
        tuple: (bot_token, chat_id) or (None, None) if not found
    """
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    return bot_token, chat_id

def main():
    """Send time message once and exit."""
    print("🤖 Telegram Time Notifier")
    print("=" * 30)
    
    bot_token, chat_id = load_config()
    
    if not bot_token or not chat_id:
        print("❌ Missing configuration!")
        print("💡 Make sure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID secrets are set in GitHub.")
        return
    
    notifier = TelegramTimeNotifier(bot_token, chat_id)
    
    # Test connection first
    if not notifier.test_connection():
        print("❌ Cannot connect to Telegram. Please check your configuration.")
        return
    
    # Send the message
    success = notifier.send_time_message()
    if success:
        print("🎉 Time notification sent successfully via GitHub Actions!")
    else:
        print("❌ Failed to send time notification.")

if __name__ == "__main__":
    main()
