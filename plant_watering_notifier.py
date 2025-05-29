#!/usr/bin/env python3
"""
Plant Watering Reminder System
A smart system that sends plant watering reminders via Telegram using GitHub Actions.
Tracks different plant types with customized watering schedules.
"""

import requests
import datetime
import os
import json
import uuid
import random
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

class PlantWateringNotifier:
    def __init__(self, bot_token: str, chat_id: str, 
                 config_file: str = "plant_config.json",
                 log_file: str = "notifications_log.json"):
        """
        Initialize the Plant Watering Notifier.
        
        Args:
            bot_token (str): Your Telegram bot token
            chat_id (str): Your Telegram chat ID
            config_file (str): Path to the plant configuration JSON file
            log_file (str): Path to the notifications log JSON file
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.config_file = Path(config_file)
        self.log_file = Path(log_file)
        self._ensure_files_exist()
    
    def _ensure_files_exist(self) -> None:
        """Ensure all required files exist and initialize them if they don't."""
        if not self.log_file.exists():
            initial_log_data = {
                "metadata": {
                    "created_at": datetime.datetime.now().isoformat(),
                    "project": "Watering Plants Telegram Notifier",
                    "version": "2.0",
                    "total_watering_events": 0,
                    "description": "Notification log that tracks when watering reminders are sent and assumes watering is completed when notification is sent"
                },
                "watering_events": []
            }
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(initial_log_data, f, indent=2, ensure_ascii=False)
    
    def _get_current_season(self) -> str:
        """Determine the current season based on the month."""
        month = datetime.datetime.now().month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        else:
            return "winter"
    
    def _load_plant_config(self) -> Dict[str, Any]:
        """Load plant configuration from JSON file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Plant config file not found: {self.config_file}")
            return {"plants": [], "notification_settings": {}}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing plant config: {e}")
            return {"plants": [], "notification_settings": {}}
    
    def _load_watering_history_from_logs(self) -> Dict[str, str]:
        """
        Load the last watering dates from notification logs.
        Returns a dictionary mapping plant_id to last_watered_date.
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            last_watered = {}
            
            # Go through watering events and find the most recent watering for each plant
            for event in data.get("watering_events", []):
                if event.get("status") == "success" and event.get("plants_watered"):
                    for plant in event["plants_watered"]:
                        plant_id = plant.get("plant_id")
                        watered_date = plant.get("watered_date")
                        if plant_id and watered_date:
                            # Keep the most recent date for each plant
                            if plant_id not in last_watered or watered_date > last_watered[plant_id]:
                                last_watered[plant_id] = watered_date
            
            return last_watered
        except FileNotFoundError:
            print(f"❌ Notification log file not found: {self.log_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing notification log: {e}")
            return {}
    
    def _calculate_next_watering_date(self, plant: Dict[str, Any], last_watered: str) -> datetime.date:
        """Calculate the next watering date for a plant based on its schedule and season."""
        last_date = datetime.datetime.strptime(last_watered, "%Y-%m-%d").date()
        current_season = self._get_current_season()
        
        # Get frequency for current season, fallback to default frequency
        schedule = plant.get("watering_schedule", {})
        season_adjustments = schedule.get("season_adjustments", {})
        frequency_days = season_adjustments.get(current_season, schedule.get("frequency_days", 7))
        
        return last_date + datetime.timedelta(days=frequency_days)
    
    def _get_plants_needing_water(self) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Get plants that need watering today, are overdue, or are due soon.
        Based on notifications log instead of separate watering history.
        
        Returns:
            Tuple of (due_today, overdue, upcoming_in_2_days)
        """
        config = self._load_plant_config()
        last_watered_dates = self._load_watering_history_from_logs()
        
        due_today = []
        overdue = []
        upcoming_in_2_days = []
        today = datetime.date.today()
        
        for plant in config.get("plants", []):
            if not plant.get("active", True):
                continue
                
            plant_id = plant["id"]
            last_watered = last_watered_dates.get(plant_id)
            
            if not last_watered:
                # If no watering history, assume it needs watering today
                due_today.append(plant)
                continue
            
            next_due = self._calculate_next_watering_date(plant, last_watered)
            days_until_due = (next_due - today).days
            
            if days_until_due < 0:
                overdue.append(plant)
            elif days_until_due == 0:
                due_today.append(plant)
            elif days_until_due <= 2:
                upcoming_in_2_days.append(plant)
        
        return due_today, overdue, upcoming_in_2_days
    
    def _format_plant_reminder_message(self, due_today: List[Dict], overdue: List[Dict], upcoming: List[Dict]) -> str:
        """Format the plant watering reminder message."""
        if not due_today and not overdue and not upcoming:
            return "🌱 **Plant Care Update**\\n\\nAll your plants are happy and well-watered! 🎉\\n\\nNext check: Tomorrow"
        
        message_parts = ["🌱 **Plant Watering Reminders**\\n"]
        
        if overdue:
            message_parts.append("🚨 **URGENT - Overdue:**")
            for plant in overdue:
                emoji = plant.get("emoji", "🌿")
                message_parts.append(f"{emoji} *{plant['name']}* ({plant['location']})")
                if plant.get("care_notes"):
                    message_parts.append(f"   💡 {plant['care_notes']}")
            message_parts.append("")
        
        if due_today:
            message_parts.append("\\n📅 **Due Today:**")
            for plant in due_today:
                emoji = plant.get("emoji", "🌿")
                message_parts.append(f"{emoji} *{plant['name']}* ({plant['location']})")
                if plant.get("care_notes"):
                    message_parts.append(f"   💡 {plant['care_notes']}")
            message_parts.append("")
        
        if upcoming:
            message_parts.append("\\n⏰ **Coming Up (Next 2 Days):**")
            for plant in upcoming:
                emoji = plant.get("emoji", "🌿")
                message_parts.append(f"{emoji} *{plant['name']}* ({plant['location']})")
            message_parts.append("")
        
        # Add current season info
        current_season = self._get_current_season()
        season_emoji = {"spring": "🌸", "summer": "☀️", "autumn": "🍂", "winter": "❄️"}
        message_parts.append(f"\\n🌍 Current Season: {season_emoji.get(current_season, '🌿')} {current_season.title()}")
        
        # Add care tip
        tips = [
            "💧 Water in the morning for best absorption",
            "☀️ Check soil moisture before watering",
            "🌡️ Room temperature water is best",
            "💚 Happy plants = happy home!",
            "🍃 Don't forget to check the drainage"
        ]
        message_parts.append(f"\\n💡 **Tip of the day:** {random.choice(tips)}")
        
        return "\\n".join(message_parts)
    
    def _log_watering_notification(self, message: str, status: str, plants_watered: List[Dict], 
                                  response_data: Optional[Dict] = None, error: Optional[str] = None) -> None:
        """Log a watering notification to the JSON file."""
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
                "season": self._get_current_season(),
                "notification_type": "watering_reminder",
                "message": message,
                "status": status,
                "chat_id": self.chat_id,
                "bot_token_last_4": self.bot_token[-4:] if len(self.bot_token) > 4 else "****",
                "plants_watered": plants_watered
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
            
            # Append to watering events
            data["watering_events"].append(notification_entry)
            
            # Update metadata
            data["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
            data["metadata"]["total_watering_events"] = len(data["watering_events"])
            
            # Write back to file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"📝 Watering notification logged to {self.log_file}")
            
        except Exception as e:
            print(f"⚠️ Failed to log watering notification: {e}")
    
    def send_watering_reminder(self) -> bool:
        """
        Send plant watering reminders to Telegram and log the notification.
        Assumes watering is completed when notification is sent.
        
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            due_today, overdue, upcoming = self._get_plants_needing_water()
            
            # Prepare plants that will be "watered" when notification is sent
            plants_to_water = []
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            
            # All overdue and due today plants will be considered watered
            for plant in overdue:
                plants_to_water.append({
                    "plant_id": plant["id"],
                    "name": plant["name"],
                    "watered_date": today_str,
                    "was_overdue": True
                })
            
            for plant in due_today:
                plants_to_water.append({
                    "plant_id": plant["id"],
                    "name": plant["name"],
                    "watered_date": today_str,
                    "was_overdue": False
                })
            
            message = self._format_plant_reminder_message(due_today, overdue, upcoming)
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                total_plants = len(due_today) + len(overdue)
                print(f"✅ Plant watering reminder sent successfully! ({total_plants} plants watered)")
                
                # Log successful notification with plants watered
                self._log_watering_notification(
                    message=message,
                    status="success",
                    plants_watered=plants_to_water,
                    response_data=response.json()
                )
                return True
            else:
                error_msg = f"Status code: {response.status_code}, Response: {response.text}"
                print(f"❌ Failed to send message. {error_msg}")
                
                # Log failed notification
                self._log_watering_notification(
                    message=message,
                    status="error",
                    plants_watered=[],
                    error=error_msg
                )
                return False
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {e}"
            print(f"❌ {error_msg}")
            
            # Log network error
            self._log_watering_notification(
                message="Failed to send plant reminder due to network error",
                status="error",
                plants_watered=[],
                error=error_msg
            )
            return False
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"❌ {error_msg}")
            
            # Log unexpected error
            self._log_watering_notification(
                message="Failed to send plant reminder due to unexpected error",
                status="error",
                plants_watered=[],
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
    """Send plant watering reminders and exit."""
    print("🌱 Plant Watering Reminder System v2.0")
    print("=" * 40)
    
    bot_token, chat_id = load_config()
    
    if not bot_token or not chat_id:
        print("❌ Missing configuration!")
        print("💡 Make sure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID secrets are set in GitHub.")
        return
    
    notifier = PlantWateringNotifier(bot_token, chat_id)
    
    # Test connection first
    if not notifier.test_connection():
        print("❌ Cannot connect to Telegram. Please check your configuration.")
        return
    
    # Send the plant watering reminders
    success = notifier.send_watering_reminder()
    if success:
        print("🎉 Plant watering reminders sent successfully via GitHub Actions! 🌿")
        print("💧 Watering assumed completed for all notified plants.")
    else:
        print("❌ Failed to send plant watering reminders.")

if __name__ == "__main__":
    main()
