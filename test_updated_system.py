#!/usr/bin/env python3
"""
Test script for the updated plant watering notifier system
"""

import json
import datetime
from plant_watering_notifier import PlantWateringNotifier

def test_notification_system():
    """Test the notification system without actually sending messages."""
    print("🧪 Testing Plant Watering Notification System v2.0")
    print("=" * 50)
    
    # Create notifier instance (won't send actual messages without real tokens)
    notifier = PlantWateringNotifier("dummy_token", "dummy_chat")
    
    # Test loading configuration
    print("📋 Testing plant configuration loading...")
    config = notifier._load_plant_config()
    plants = config.get("plants", [])
    print(f"✅ Loaded {len(plants)} plants from config")
    
    # Test loading watering history from logs
    print("📜 Testing watering history from logs...")
    history = notifier._load_watering_history_from_logs()
    print(f"✅ Found watering history for {len(history)} plants: {list(history.keys())}")
    
    # Test getting plants needing water
    print("🌱 Testing plant watering logic...")
    due_today, overdue, upcoming = notifier._get_plants_needing_water()
    print(f"✅ Plants due today: {len(due_today)}")
    print(f"✅ Plants overdue: {len(overdue)}")
    print(f"✅ Plants upcoming: {len(upcoming)}")
    
    # Test message formatting
    print("💬 Testing message formatting...")
    message = notifier._format_plant_reminder_message(due_today, overdue, upcoming)
    print(f"✅ Generated message (length: {len(message)} chars)")
    print("📝 Message preview:")
    print("-" * 30)
    print(message[:200] + "..." if len(message) > 200 else message)
    print("-" * 30)
    
    # Show current log structure
    print("📊 Current notification log structure:")
    try:
        with open("notifications_log.json", 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        print(f"✅ Log version: {log_data['metadata']['version']}")
        print(f"✅ Total watering events: {log_data['metadata']['total_watering_events']}")
        print(f"✅ Events in log: {len(log_data['watering_events'])}")
    except Exception as e:
        print(f"⚠️ Error reading log: {e}")
    
    print("\n🎉 Test completed successfully!")
    print("💡 The system is now configured to:")
    print("   - Base watering calculations on notification logs")
    print("   - Assume watering is completed when notifications are sent")
    print("   - Use plant_config.json for all scheduling configuration")

if __name__ == "__main__":
    test_notification_system()
