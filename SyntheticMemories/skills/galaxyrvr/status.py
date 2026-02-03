#!/usr/bin/env python3
"""
GalaxyRVR Quick Status
One-line status check for rover health
"""

import asyncio
import sys
sys.path.insert(0, '/home/zolon/.openclaw/workspace/skills/galaxyrvr')

from rover_control import GalaxyRVR
from battery_alert import BatteryAlert
from wifi_monitor import WiFiMonitor

async def quick_status():
    """Quick one-line status"""
    
    # Try to connect
    rover = GalaxyRVR()
    connected = await rover.connect()
    
    if not connected:
        print("🔴 OFFLINE")
        return
    
    # Get sensors
    sensors = rover.get_sensors()
    battery_v = sensors['battery_voltage']
    distance = sensors['ultrasonic_cm']
    
    # Battery status
    if battery_v == 0:
        batt_icon = "❓"
        batt_pct = "??"
    elif battery_v < 6.5:
        batt_icon = "🔴"
        batt_pct = int(((battery_v - 6.0) / 2.4) * 100)
    elif battery_v < 7.0:
        batt_icon = "🟡"
        batt_pct = int(((battery_v - 6.0) / 2.4) * 100)
    else:
        batt_icon = "🟢"
        batt_pct = int(((battery_v - 6.0) / 2.4) * 100)
    
    # WiFi
    wifi = WiFiMonitor()
    signal = wifi.get_signal_strength()
    wifi_bars = wifi.get_signal_bars()
    
    # Obstacle
    if distance > 0 and distance < 30:
        obs_icon = "⚠️"
        obs_text = f"{distance:.0f}cm"
    else:
        obs_icon = "✅"
        obs_text = "clear"
    
    await rover.disconnect()
    
    # One-line status
    print(f"{batt_icon} {battery_v:.2f}V ({batt_pct}%) | {wifi_bars} {signal}dBm | {obs_icon} {obs_text}")

if __name__ == "__main__":
    asyncio.run(quick_status())
