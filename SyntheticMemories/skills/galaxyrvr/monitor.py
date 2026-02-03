#!/usr/bin/env python3
"""
GalaxyRVR Monitoring Script
Real-time sensor dashboard for the rover
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

class RoverMonitor:
    def __init__(self, host="192.168.10.118", port=8765):
        self.host = host
        self.port = port
        self.ws = None
        
        # Latest sensor readings
        self.battery_voltage = 0.0
        self.battery_percent = 0
        self.ir_left = 0  # 0=clear, 1=obstacle
        self.ir_right = 0
        self.ultrasonic_cm = -1  # -1 = no reading
        self.voice_active = 0  # J field
        
        # Stats
        self.readings_count = 0
        self.start_time = None
        
    async def connect(self):
        """Connect to rover"""
        uri = f"ws://{self.host}:{self.port}"
        self.ws = await websockets.connect(uri, ping_interval=None)
        
        # Handshake
        await self.ws.recv()
        
        # Send keepalive command
        await self.ws.send(json.dumps({"K": 0, "Q": 0, "D": 90}))
        
        self.start_time = datetime.now()
        print(f"✅ Connected to GalaxyRVR at {self.host}")
        
    async def monitor_loop(self, duration=None):
        """Monitor sensors in real-time"""
        print("\n🤖 GalaxyRVR Live Monitor")
        print("=" * 60)
        print("Press Ctrl+C to stop\n")
        
        start = asyncio.get_event_loop().time()
        
        try:
            while True:
                # Check duration limit
                if duration and (asyncio.get_event_loop().time() - start) > duration:
                    break
                
                try:
                    msg = await asyncio.wait_for(self.ws.recv(), timeout=0.5)
                    
                    # Skip pong messages
                    if msg.startswith("pong"):
                        # Send keepalive
                        await self.ws.send(json.dumps({"K": 0, "Q": 0, "D": 90}))
                        continue
                    
                    # Skip non-JSON (echo messages)
                    if not msg.startswith("{"):
                        continue
                    
                    # Parse sensor data
                    try:
                        data = json.loads(msg)
                        self._update_sensors(data)
                        self.readings_count += 1
                        
                        # Display update every reading
                        self._display_status()
                        
                    except json.JSONDecodeError:
                        pass
                        
                except asyncio.TimeoutError:
                    # Send keepalive on timeout
                    await self.ws.send(json.dumps({"K": 0, "Q": 0, "D": 90}))
                    continue
                    
        except KeyboardInterrupt:
            print("\n\n⏸️  Monitoring stopped")
        finally:
            await self.ws.close()
    
    def _update_sensors(self, data):
        """Update sensor values from JSON data"""
        if "BV" in data:
            self.battery_voltage = data["BV"]
            # Calculate percentage (assuming 2S LiPo: 6.0V empty, 8.4V full)
            self.battery_percent = int(max(0, min(100, 
                ((self.battery_voltage - 6.0) / 2.4) * 100)))
        
        if "N" in data:
            self.ir_left = data["N"]
        
        if "P" in data:
            self.ir_right = data["P"]
        
        if "O" in data:
            self.ultrasonic_cm = data["O"]
        
        if "J" in data:
            self.voice_active = data["J"]
    
    def _display_status(self):
        """Display current sensor status"""
        # Clear previous line (ANSI escape)
        sys.stdout.write('\033[2K\r')
        
        # Battery status with color
        if self.battery_voltage < 6.5:
            batt_icon = "🔴"
        elif self.battery_voltage < 7.0:
            batt_icon = "🟡"
        else:
            batt_icon = "🟢"
        
        # Distance status
        if self.ultrasonic_cm > 0:
            dist_str = f"{self.ultrasonic_cm:5.1f}cm"
            if self.ultrasonic_cm < 30:
                dist_icon = "⚠️ "
            else:
                dist_icon = "📏"
        else:
            dist_str = "  ---  "
            dist_icon = "📏"
        
        # IR status
        ir_left_icon = "🚫" if self.ir_left else "✅"
        ir_right_icon = "🚫" if self.ir_right else "✅"
        
        # Build status line
        status = (
            f"{batt_icon} Battery: {self.battery_voltage:.2f}V ({self.battery_percent}%) | "
            f"{dist_icon} Distance: {dist_str} | "
            f"IR: L{ir_left_icon} R{ir_right_icon} | "
            f"📊 {self.readings_count} readings"
        )
        
        sys.stdout.write(status)
        sys.stdout.flush()
    
    def get_status_dict(self):
        """Get current status as dictionary"""
        return {
            "battery": {
                "voltage": self.battery_voltage,
                "percent": self.battery_percent,
                "status": "critical" if self.battery_voltage < 6.5 else
                         "low" if self.battery_voltage < 7.0 else "good"
            },
            "sensors": {
                "ultrasonic_cm": self.ultrasonic_cm if self.ultrasonic_cm > 0 else None,
                "ir_left_clear": self.ir_left == 0,
                "ir_right_clear": self.ir_right == 0
            },
            "connection": {
                "readings": self.readings_count,
                "uptime": str(datetime.now() - self.start_time) if self.start_time else None
            }
        }
    
    def print_summary(self):
        """Print detailed status summary"""
        print("\n\n" + "=" * 60)
        print("📊 GalaxyRVR Status Summary")
        print("=" * 60)
        
        # Battery
        print(f"\n🔋 Battery:")
        print(f"   Voltage: {self.battery_voltage:.2f}V")
        print(f"   Estimated: {self.battery_percent}%")
        if self.battery_voltage < 6.5:
            print(f"   ⚠️  WARNING: Battery critically low! Charge soon.")
        elif self.battery_voltage < 7.0:
            print(f"   ⚠️  Battery getting low")
        else:
            print(f"   ✅ Battery healthy")
        
        # Sensors
        print(f"\n📡 Sensors:")
        print(f"   Ultrasonic: {self.ultrasonic_cm:.1f}cm" if self.ultrasonic_cm > 0 else "   Ultrasonic: No reading")
        print(f"   IR Left: {'Obstacle' if self.ir_left else 'Clear'}")
        print(f"   IR Right: {'Obstacle' if self.ir_right else 'Clear'}")
        
        # Connection
        print(f"\n📶 Connection:")
        print(f"   Readings: {self.readings_count}")
        if self.start_time:
            uptime = datetime.now() - self.start_time
            print(f"   Uptime: {uptime}")
        
        print("\n" + "=" * 60)


async def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor GalaxyRVR rover sensors')
    parser.add_argument('--host', default='192.168.10.118', help='Rover IP address')
    parser.add_argument('--port', type=int, default=8765, help='WebSocket port')
    parser.add_argument('--duration', type=int, help='Monitor duration in seconds (default: indefinite)')
    parser.add_argument('--once', action='store_true', help='Read sensors once and exit')
    
    args = parser.parse_args()
    
    monitor = RoverMonitor(args.host, args.port)
    
    try:
        await monitor.connect()
        
        if args.once:
            # Just read for a few seconds to get stable values
            await monitor.monitor_loop(duration=3)
            monitor.print_summary()
        else:
            # Continuous monitoring
            await monitor.monitor_loop(duration=args.duration)
            monitor.print_summary()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
