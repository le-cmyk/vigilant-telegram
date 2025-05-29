#!/usr/bin/env python3
"""
Test script for the Plant Watering Notifier
Tests the core functionality without requiring Telegram credentials
"""

import json
import datetime
from pathlib import Path
from plant_watering_notifier import PlantWateringNotifier

def test_plant_system():
    """Test the plant watering system without sending messages."""
    print("🧪 Testing Plant Watering Reminder System")
    print("=" * 50)
    
    # Create a mock notifier (without real credentials)
    notifier = PlantWateringNotifier("test_token", "test_chat_id")
    
    print("✅ Plant Watering Notifier initialized successfully")
    
    # Test loading plant config
    config = notifier._load_plant_config()
    plants = config.get("plants", [])
    print(f"✅ Loaded {len(plants)} plants from configuration")
    
    for plant in plants[:3]:  # Show first 3 plants
        emoji = plant.get("emoji", "🌿")
        name = plant.get("name", "Unknown")
        location = plant.get("location", "Unknown")
        print(f"   {emoji} {name} ({location})")
      # Test loading watering history from logs
    history = notifier._load_watering_history_from_logs()
    print(f"✅ Loaded watering history for {len(history)} plants: {list(history.keys())}")
    
    # Test getting plants needing water
    due_today, overdue, upcoming = notifier._get_plants_needing_water()
    
    print(f"\\n📊 Plant Status Summary:")
    print(f"   🚨 Overdue: {len(overdue)} plants")
    print(f"   📅 Due today: {len(due_today)} plants") 
    print(f"   ⏰ Upcoming (2 days): {len(upcoming)} plants")
    
    # Test message formatting
    message = notifier._format_plant_reminder_message(due_today, overdue, upcoming)
    print(f"\\n📱 Sample notification message:")
    print("-" * 40)
    print(message) # Removed .replace("\\\\n", "\\\\n")
    print("-" * 40)
    
    # Test season detection
    season = notifier._get_current_season()
    print(f"\\n🌍 Current season: {season.title()}")
    
    print("\\n🎉 All tests completed successfully!")
    print("💡 To test with real Telegram notifications, set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")

if __name__ == "__main__":
    test_plant_system()
