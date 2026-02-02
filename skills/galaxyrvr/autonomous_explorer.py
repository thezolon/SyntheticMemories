#!/usr/bin/env python3
"""
GalaxyRVR Autonomous Explorer
Complete integration: control + vision + mapping + battery monitoring
All local, zero API costs!
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any

# Import our modules
import sys
sys.path.insert(0, '/home/zolon/.openclaw/workspace/skills/galaxyrvr')

from rover_control import GalaxyRVR
from vision import RoverVision
from mapping import RoverMap
from battery_alert import BatteryAlert
from wifi_monitor import WiFiMonitor


class AutonomousExplorer:
    def __init__(self, 
                 rover_ip="192.168.10.118",
                 safe_mode=True,
                 map_file=None):
        """
        Args:
            rover_ip: Rover WebSocket address
            safe_mode: If True, reduced speeds and extra caution
            map_file: Load existing map, or None for new map
        """
        self.rover_ip = rover_ip
        self.safe_mode = safe_mode
        
        # Core systems
        self.rover = GalaxyRVR(host=rover_ip)
        self.vision = RoverVision(camera_url=f"http://{rover_ip}:9000/mjpg")
        self.battery = BatteryAlert(host=rover_ip)
        self.wifi = WiFiMonitor(target_ip=rover_ip)
        
        # Load or create map
        if map_file:
            self.map = RoverMap.load_map(map_file)
            print(f"📂 Loaded existing map from {map_file}")
        else:
            self.map = RoverMap(grid_size_meters=5.0, cell_size_cm=10)
            print(f"🗺️  Created new map (5m x 5m)")
        
        # Exploration state
        self.running = False
        self.exploration_mode = "frontier"  # "frontier" or "manual"
        self.moves_since_vision_check = 0
        self.last_vision_time = 0
        
        # Statistics
        self.stats = {
            "start_time": None,
            "moves_made": 0,
            "obstacles_avoided": 0,
            "vision_checks": 0,
            "battery_checks": 0
        }
    
    async def initialize(self):
        """Connect to rover and prepare systems"""
        print("\n🤖 GalaxyRVR Autonomous Explorer")
        print("=" * 60)
        print(f"Safe mode: {'ON' if self.safe_mode else 'OFF'}")
        print(f"Rover: {self.rover_ip}")
        print()
        
        # Connect rover
        print("Connecting to rover...")
        if not await self.rover.connect():
            raise Exception("Failed to connect to rover!")
        
        print("✅ Rover connected")
        
        # Check battery
        print("Checking battery...")
        status, voltage, msg = await self.battery.check_battery()
        print(f"   {msg}")
        
        if status == "critical":
            raise Exception("Battery too low! Charge before exploring.")
        
        # Check WiFi
        print("Checking WiFi...")
        signal = self.wifi.get_signal_strength()
        quality = self.wifi.get_signal_quality()
        print(f"   Signal: {signal}dBm ({quality})")
        
        # Center camera
        print("Centering camera...")
        self.rover.set_servo(90)
        await asyncio.sleep(0.5)
        
        print("\n✅ All systems ready!")
        self.stats["start_time"] = time.time()
    
    async def check_battery_safe(self) -> bool:
        """Check if battery is safe to continue"""
        self.stats["battery_checks"] += 1
        status, voltage, msg = await self.battery.check_battery()
        
        if status == "critical":
            print(f"\n🔴 {msg}")
            return False
        elif status == "low":
            print(f"\n🟡 {msg}")
            # Continue but log warning
        
        return True
    
    async def sensor_scan(self) -> Dict[str, Any]:
        """Read all sensors and update map"""
        sensors = self.rover.get_sensors()
        
        # Update map with sensor data
        ultrasonic = sensors["ultrasonic_cm"]
        if ultrasonic > 2 and ultrasonic < 400:
            self.map.add_ultrasonic_reading(ultrasonic, confidence=0.8)
        
        self.map.add_ir_reading(sensors["ir_left"], sensors["ir_right"])
        
        # Add WiFi data
        wifi_signal = self.wifi.get_signal_strength()
        if wifi_signal:
            self.map.add_wifi_reading(wifi_signal)
        
        return {
            "ultrasonic_cm": ultrasonic,
            "ir_left": sensors["ir_left"],
            "ir_right": sensors["ir_right"],
            "wifi_dbm": wifi_signal,
            "battery_v": sensors["battery_voltage"]
        }
    
    async def vision_check(self) -> Dict[str, Any]:
        """Use vision to check for obstacles"""
        self.stats["vision_checks"] += 1
        self.last_vision_time = time.time()
        
        print("   👁️  Vision check...")
        result = self.vision.detect_obstacles()
        
        if result["has_obstacle"]:
            print(f"      Obstacle: {result['description']}")
        
        return result
    
    async def safe_move_forward(self, duration: float = 1.0, speed: int = 50):
        """Move forward with safety checks"""
        if self.safe_mode:
            speed = min(speed, 40)  # Limit speed in safe mode
        
        # Pre-move sensor check
        sensors = await self.sensor_scan()
        
        # Check IR sensors (immediate obstacles)
        if sensors["ir_left"] == 1 or sensors["ir_right"] == 1:
            print("   ⚠️  IR obstacle detected - stopping")
            self.stats["obstacles_avoided"] += 1
            return False
        
        # Check ultrasonic (longer range)
        if sensors["ultrasonic_cm"] > 0 and sensors["ultrasonic_cm"] < 30:
            print(f"   ⚠️  Obstacle at {sensors['ultrasonic_cm']:.0f}cm - stopping")
            self.stats["obstacles_avoided"] += 1
            return False
        
        # Vision check every 5 moves or if >10 seconds since last
        time_since_vision = time.time() - self.last_vision_time
        if self.moves_since_vision_check >= 5 or time_since_vision > 10:
            vision = await self.vision_check()
            self.moves_since_vision_check = 0
            
            if vision["has_obstacle"] and not vision["safe_to_move"]:
                print("   ⚠️  Vision obstacle detected - stopping")
                self.stats["obstacles_avoided"] += 1
                return False
        
        # Move forward
        self.rover.forward(speed)
        await asyncio.sleep(duration)
        self.rover.stop()
        
        # Update odometry
        self.map.update_odometry("forward", duration, speed)
        self.stats["moves_made"] += 1
        self.moves_since_vision_check += 1
        
        return True
    
    async def turn(self, direction: str, duration: float = 0.5, speed: int = 50):
        """Turn left or right"""
        if self.safe_mode:
            speed = min(speed, 40)
        
        if direction == "left":
            self.rover.turn_left(speed)
        else:
            self.rover.turn_right(speed)
        
        await asyncio.sleep(duration)
        self.rover.stop()
        
        # Update odometry
        self.map.update_odometry(f"turn_{direction}", duration, speed)
        self.stats["moves_made"] += 1
    
    async def explore_frontier(self):
        """Frontier-based autonomous exploration"""
        print("\n🧭 Starting frontier exploration...")
        
        while self.running:
            # Battery check every 10 moves
            if self.stats["moves_made"] % 10 == 0:
                if not await self.check_battery_safe():
                    print("🔴 Battery critical - stopping exploration")
                    break
            
            # Sensor scan
            print("\n📡 Scanning...")
            sensors = await self.sensor_scan()
            
            # Find nearest unexplored frontier
            frontier = self.map.find_unexplored_frontier()
            
            if frontier is None:
                print("✅ Map fully explored!")
                break
            
            # Navigate toward frontier
            fx, fy = frontier
            nav = self.map.navigate_to(fx, fy)
            
            print(f"   Target: ({fx:.0f}, {fy:.0f}cm)")
            print(f"   Action: {nav['action']}")
            
            if nav["action"] == "forward":
                success = await self.safe_move_forward(duration=1.0, speed=40)
                if not success:
                    # Blocked - turn and try again
                    print("   Obstacle! Turning...")
                    await self.turn("right", duration=1.0)
                    
            elif nav["action"] == "turn_left":
                await self.turn("left", duration=0.5)
                
            elif nav["action"] == "turn_right":
                await self.turn("right", duration=0.5)
                
            elif nav["action"] == "blocked":
                print("   Path blocked - trying alternate route")
                await self.turn("right", duration=1.5)
                
            elif nav["action"] == "arrived":
                print("   ✅ Reached frontier!")
            
            # Show map periodically
            if self.stats["moves_made"] % 5 == 0:
                print("\n🗺️  Current Map:")
                print(self.map.get_map_ascii(width=30))
                stats = self.map.get_statistics()
                print(f"   Explored: {stats['explored_percent']}%")
                print(f"   Distance: {stats['distance_traveled_m']}m")
            
            await asyncio.sleep(0.1)  # Small delay between moves
    
    async def run(self, duration_seconds: Optional[int] = None):
        """Run autonomous exploration"""
        self.running = True
        start_time = time.time()
        
        try:
            if self.exploration_mode == "frontier":
                await self.explore_frontier()
            
        except KeyboardInterrupt:
            print("\n\n⏸️  Exploration interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            await self.shutdown()
    
    async def shutdown(self):
        """Clean shutdown and save map"""
        print("\n\n🛑 Shutting down...")
        
        # Stop rover
        self.rover.stop()
        await asyncio.sleep(0.5)
        await self.rover.disconnect()
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_file = f"/tmp/rover_map_{timestamp}.json"
        self.map.save_map(map_file)
        
        # Show final statistics
        runtime = time.time() - self.stats["start_time"]
        print("\n" + "=" * 60)
        print("📊 Exploration Statistics")
        print("=" * 60)
        print(f"Runtime: {runtime:.0f}s ({runtime/60:.1f}min)")
        print(f"Moves made: {self.stats['moves_made']}")
        print(f"Obstacles avoided: {self.stats['obstacles_avoided']}")
        print(f"Vision checks: {self.stats['vision_checks']}")
        print(f"Battery checks: {self.stats['battery_checks']}")
        
        map_stats = self.map.get_statistics()
        print(f"\nMap explored: {map_stats['explored_percent']}%")
        print(f"Distance traveled: {map_stats['distance_traveled_m']}m")
        print(f"Scans performed: {map_stats['scan_count']}")
        
        print(f"\n💾 Map saved to: {map_file}")
        
        # Final map
        print("\n🗺️  Final Map:")
        print(self.map.get_map_ascii(width=40))
        
        print("\n" + "=" * 60)
        print("✅ Shutdown complete")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='GalaxyRVR Autonomous Explorer')
    parser.add_argument('--ip', default='192.168.10.118', help='Rover IP address')
    parser.add_argument('--load-map', help='Load existing map file')
    parser.add_argument('--duration', type=int, help='Exploration duration (seconds)')
    parser.add_argument('--unsafe', action='store_true', help='Disable safe mode (higher speeds)')
    parser.add_argument('--mode', choices=['frontier', 'manual'], default='frontier', 
                       help='Exploration mode')
    
    args = parser.parse_args()
    
    explorer = AutonomousExplorer(
        rover_ip=args.ip,
        safe_mode=not args.unsafe,
        map_file=args.load_map
    )
    
    explorer.exploration_mode = args.mode
    
    await explorer.initialize()
    await explorer.run(duration_seconds=args.duration)


if __name__ == "__main__":
    asyncio.run(main())
