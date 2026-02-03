#!/usr/bin/env python3
"""
GalaxyRVR Calibration Helper
Measure actual movement to calibrate odometry constants
"""

import asyncio
import sys
sys.path.insert(0, '/home/zolon/.openclaw/workspace/skills/galaxyrvr')
from rover_control import GalaxyRVR

async def calibrate_forward():
    """Calibrate forward speed"""
    print("\n📏 Forward Speed Calibration")
    print("=" * 60)
    print("1. Place rover on flat ground")
    print("2. Mark starting position")
    print("3. Rover will drive forward for 3 seconds at 50% speed")
    print("4. Measure actual distance traveled in CM")
    print()
    input("Press ENTER when ready...")
    
    rover = GalaxyRVR()
    if not await rover.connect():
        print("❌ Connection failed")
        return
    
    print("\n🚀 Driving...")
    rover.forward(50)
    await asyncio.sleep(3.0)
    rover.stop()
    
    await rover.disconnect()
    
    print("\n✅ Movement complete!")
    distance = float(input("How many CM did it travel? "))
    
    cm_per_sec = distance / 3.0
    cm_per_sec_100 = cm_per_sec * 2  # Scale to 100% speed
    
    print(f"\n📊 Results:")
    print(f"   At 50% speed: {cm_per_sec:.1f} cm/sec")
    print(f"   At 100% speed (estimated): {cm_per_sec_100:.1f} cm/sec")
    print(f"\n💡 Update mapping.py:")
    print(f"   CM_PER_SEC_AT_SPEED_100 = {cm_per_sec_100:.1f}")

async def calibrate_turn():
    """Calibrate turn rate"""
    print("\n🔄 Turn Rate Calibration")
    print("=" * 60)
    print("1. Place rover on flat ground")
    print("2. Mark starting heading (use compass or wall)")
    print("3. Rover will turn right for 2 seconds at 50% speed")
    print("4. Measure actual degrees rotated")
    print()
    input("Press ENTER when ready...")
    
    rover = GalaxyRVR()
    if not await rover.connect():
        print("❌ Connection failed")
        return
    
    print("\n🔄 Turning...")
    rover.turn_right(50)
    await asyncio.sleep(2.0)
    rover.stop()
    
    await rover.disconnect()
    
    print("\n✅ Rotation complete!")
    degrees = float(input("How many degrees did it rotate? "))
    
    deg_per_sec = degrees / 2.0
    deg_per_sec_100 = deg_per_sec * 2  # Scale to 100% speed
    
    print(f"\n📊 Results:")
    print(f"   At 50% speed: {deg_per_sec:.1f} deg/sec")
    print(f"   At 100% speed (estimated): {deg_per_sec_100:.1f} deg/sec")
    print(f"\n💡 Update mapping.py:")
    print(f"   DEGREES_PER_SEC_AT_SPEED_100 = {deg_per_sec_100:.1f}")

async def main():
    print("\n🔧 GalaxyRVR Odometry Calibration")
    print("=" * 60)
    print("Choose calibration:")
    print("  1. Forward speed")
    print("  2. Turn rate")
    print("  3. Both")
    choice = input("\nChoice (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        await calibrate_forward()
        print()
    
    if choice in ['2', '3']:
        await calibrate_turn()
        print()
    
    print("\n✅ Calibration complete!")
    print("Update the constants in mapping.py for accurate odometry.")

if __name__ == "__main__":
    asyncio.run(main())
