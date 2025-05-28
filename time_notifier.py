#!/usr/bin/env python3
"""
Telegram Time Notifier
A simple script that sends the current time via Telegram using GitHub Actions.
"""

import requests
import datetime
import os
import json
import uuid
from typing import Optional, Dict, Any
from pathlib import Path

class TelegramTimeNotifier:
    def __init__(self, bot_token: str, chat_id: str, log_file: str = "notifications_log.json"):
        """
        Initialize the Telegram Time Notifier.
        
        Args:
            bot_token (str): Your Telegram bot token
            chat_id (str): Your Telegram chat ID
            log_file (str): Path to the JSON log file
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.log_file = Path(log_file)
        self._ensure_log_file_exists()
    
    def _ensure_log_file_exists(self) -> None:
        """
        Ensure the log file exists and initialize it if it doesn't.
        """
        if not self.log_file.exists():
            initial_data = {
                "metadata": {
                    "created_at": datetime.datetime.now().isoformat(),
                    "project": "Watering Plants Telegram Notifier",
                    "version": "1.0"
                },
                "notifications": []
            }
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def _log_notification(self, message: str, status: str, response_data: Optional[Dict[Any, Any]] = None, error: Optional[str] = None) -> None:
        """
        Log notification details to JSON file.
        
        Args:
            message (str): The message that was sent
            status (str): Status of the notification (success/error)
            response_data (Optional[Dict]): Telegram API response data
            error (Optional[str]): Error message if any
        """
        try:
            # Read existing data
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create notification entry
            notification_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.datetime.now().isoformat(),
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "day_of_week": datetime.datetime.now().strftime("%A"),
                "message": message,
                "status": status,
                "chat_id": self.chat_id,
                "bot_token_last_4": self.bot_token[-4:] if len(self.bot_token) > 4 else "****"
            }
            
            # Add response data if available
            if response_data:
                notification_entry["telegram_response"] = {
                    "message_id": response_data.get("result", {}).get("message_id"),
                    "date": response_data.get("result", {}).get("date"),
                    "success": True
                }
            
            # Add error if any
            if error:
                notification_entry["error"] = error
            
            # Append to notifications
            data["notifications"].append(notification_entry)
            
            # Update metadata
            data["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
            data["metadata"]["total_notifications"] = len(data["notifications"])
            
            # Write back to file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"📝 Notification logged to {self.log_file}")
            
        except Exception as e:
            print(f"⚠️ Failed to log notification: {e}")
    
    def send_time_message(self) -> bool:
        """
        Send the current time to Telegram and log the notification.
        
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
                # Log successful notification
                self._log_notification(
                    message=message,
                    status="success",
                    response_data=response.json()
                )
                return True
            else:
                error_msg = f"Status code: {response.status_code}, Response: {response.text}"
                print(f"❌ Failed to send message. {error_msg}")
                # Log failed notification
                self._log_notification(
                    message=message,
                    status="error",
                    error=error_msg
                )
                return False
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {e}"
            print(f"❌ {error_msg}")
            # Log network error
            self._log_notification(
                message="Failed to send message due to network error",
                status="error",
                error=error_msg
            )
            return False
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"❌ {error_msg}")
            # Log unexpected error
            self._log_notification(
                message="Failed to send message due to unexpected error",
                status="error",
                error=error_msg
            )
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
