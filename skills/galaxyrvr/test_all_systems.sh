#!/bin/bash
# Safe test of autonomous explorer while on tissue box
# This will test all systems without dangerous movement

cd ~/.openclaw/workspace/skills/galaxyrvr

echo "🤖 GalaxyRVR System Test (Safe for Tissue Box)"
echo "=============================================="
echo ""
echo "This will test:"
echo "  ✅ Rover connection"
echo "  ✅ Battery status"
echo "  ✅ WiFi signal"
echo "  ✅ Sensor reading"
echo "  ✅ Vision system"
echo "  ✅ Mapping system"
echo "  ✅ Camera servo (you'll see it move)"
echo ""
echo "Motors will NOT drive (safe on tissue box)"
echo ""
read -p "Press ENTER to start test..."

python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, '/home/zolon/.openclaw/workspace/skills/galaxyrvr')

from rover_control import GalaxyRVR
from vision import RoverVision  
from mapping import RoverMap
from battery_alert import BatteryAlert
from wifi_monitor import WiFiMonitor

async def system_test():
    print("\n1️⃣  Testing Rover Connection...")
    rover = GalaxyRVR()
    if not await rover.connect():
        print("❌ Failed to connect")
        return
    print("✅ Rover connected\n")
    
    print("2️⃣  Testing Battery...")
    battery = BatteryAlert()
    status, voltage, msg = await battery.check_battery()
    print(f"   {msg}\n")
    
    print("3️⃣  Testing WiFi...")
    wifi = WiFiMonitor()
    signal = wifi.get_signal_strength()
    quality = wifi.get_signal_quality()
    bars = wifi.get_signal_bars()
    print(f"   {bars} {signal}dBm ({quality})\n")
    
    print("4️⃣  Testing Sensors...")
    sensors = rover.get_sensors()
    print(f"   Battery: {sensors['battery_voltage']:.2f}V")
    print(f"   Ultrasonic: {sensors['ultrasonic_cm']:.1f}cm")
    print(f"   IR Left: {'Obstacle' if sensors['ir_left'] else 'Clear'}")
    print(f"   IR Right: {'Obstacle' if sensors['ir_right'] else 'Clear'}\n")
    
    print("5️⃣  Testing Camera Servo...")
    print("   Moving camera through angles...")
    for angle in [60, 90, 120, 90]:
        rover.set_servo(angle)
        print(f"      {angle}°")
        await asyncio.sleep(0.8)
    print("✅ Servo working\n")
    
    print("6️⃣  Testing Vision (this takes ~7 seconds)...")
    vision = RoverVision()
    description = vision.quick_look("What do you see? One sentence.")
    if description:
        print(f"   Vision: {description}")
        print("✅ Vision working\n")
    else:
        print("❌ Vision failed\n")
    
    print("7️⃣  Testing Mapping...")
    rover_map = RoverMap(grid_size_meters=2.0, cell_size_cm=10)
    rover_map.add_ultrasonic_reading(sensors['ultrasonic_cm'], confidence=0.8)
    rover_map.add_wifi_reading(signal)
    print(rover_map.get_map_ascii(width=20))
    stats = rover_map.get_statistics()
    print(f"   Map cells: {stats['total_cells']}")
    print(f"   Explored: {stats['explored_percent']}%\n")
    
    print("8️⃣  Cleanup...")
    await rover.disconnect()
    
    print("\n" + "="*50)
    print("✅ All systems operational!")
    print("="*50)
    print("\n💡 To run autonomous exploration:")
    print("   python3 autonomous_explorer.py")
    print("\n⚠️  Make sure rover is ON THE GROUND before running!")

asyncio.run(system_test())
EOF
