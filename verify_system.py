#!/usr/bin/env python3
"""
System Verification Script
Verifies that the updated Plant Watering Notification System v2.0 is working correctly
"""

import json
import os
from pathlib import Path
from plant_watering_notifier import PlantWateringNotifier

def verify_system():
    """Verify the complete system setup."""
    print("🔍 Plant Watering System v2.0 - Verification")
    print("=" * 50)
    
    # Check required files
    required_files = ["plant_config.json", "notifications_log.json"]
    obsolete_files = ["watering_history.json"]
    
    print("📁 Checking file structure...")
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file} - Found")
        else:
            print(f"   ❌ {file} - Missing")
    
    for file in obsolete_files:
        if not Path(file).exists():
            print(f"   ✅ {file} - Correctly removed")
        else:
            print(f"   ⚠️ {file} - Still exists (can be removed)")
    
    # Test system initialization
    print("\n🧪 Testing system initialization...")
    try:
        notifier = PlantWateringNotifier("test_token", "test_chat")
        print("   ✅ PlantWateringNotifier initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return
    
    # Check configuration
    print("\n📋 Checking plant configuration...")
    config = notifier._load_plant_config()
    plants = config.get("plants", [])
    print(f"   ✅ {len(plants)} plants configured")
    
    # Check notification settings
    settings = config.get("notification_settings", {})
    assume_watering = settings.get("assume_watering_on_notification", False)
    print(f"   ✅ Assume watering on notification: {assume_watering}")
    
    # Check log structure
    print("\n📜 Checking notification log structure...")
    try:
        with open("notifications_log.json", 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        version = log_data.get("metadata", {}).get("version", "Unknown")
        events_count = len(log_data.get("watering_events", []))
        print(f"   ✅ Log version: {version}")
        print(f"   ✅ Watering events: {events_count}")
    except Exception as e:
        print(f"   ❌ Error reading log: {e}")
    
    # Test core functionality
    print("\n🌱 Testing core functionality...")
    try:
        due_today, overdue, upcoming = notifier._get_plants_needing_water()
        print(f"   ✅ Plant status analysis working")
        print(f"      - Due today: {len(due_today)}")
        print(f"      - Overdue: {len(overdue)}")
        print(f"      - Upcoming: {len(upcoming)}")
    except Exception as e:
        print(f"   ❌ Error in plant analysis: {e}")
    
    print("\n🎉 System verification complete!")
    print("\nℹ️  System Features:")
    print("   • Uses notifications_log.json as single source of truth")
    print("   • Assumes watering completion when notifications are sent")
    print("   • No manual watering history maintenance required")
    print("   • All scheduling managed through plant_config.json")

if __name__ == "__main__":
    verify_system()
