#!/usr/bin/env python3
"""
GalaxyRVR Battery Alert System
Monitors battery and alerts when low (but not when offline)
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime, timedelta

class BatteryAlert:
    def __init__(self, host="192.168.10.118", port=8765):
        self.host = host
        self.port = port
        self.ws = None
        
        # Alert thresholds
        self.CRITICAL_VOLTAGE = 6.5  # Below this = immediate alert
        self.LOW_VOLTAGE = 7.0       # Below this = warning
        
        # State tracking
        self.last_voltage = None
        self.last_reading_time = None
        self.consecutive_failures = 0
        self.is_online = False
        
    async def check_battery(self, timeout=5):
        """
        Check battery status with network detection
        Returns: (status, voltage, message)
        """
        try:
            # Try to connect with timeout
            uri = f"ws://{self.host}:{self.port}"
            self.ws = await asyncio.wait_for(
                websockets.connect(uri, ping_interval=None),
                timeout=timeout
            )
            
            # Get handshake
            await asyncio.wait_for(self.ws.recv(), timeout=2)
            
            # Send keepalive
            await self.ws.send(json.dumps({"K": 0, "Q": 0, "D": 90}))
            
            # Wait for sensor data
            voltage = None
            attempts = 0
            max_attempts = 10
            
            while attempts < max_attempts and voltage is None:
                try:
                    msg = await asyncio.wait_for(self.ws.recv(), timeout=1)
                    
                    if msg.startswith("pong"):
                        await self.ws.send(json.dumps({"K": 0, "Q": 0, "D": 90}))
                        continue
                    
                    if not msg.startswith("{"):
                        continue
                    
                    data = json.loads(msg)
                    if "BV" in data:
                        voltage = data["BV"]
                        break
                        
                except asyncio.TimeoutError:
                    await self.ws.send(json.dumps({"K": 0, "Q": 0, "D": 90}))
                    attempts += 1
                    
            await self.ws.close()
            
            if voltage is None:
                return ("error", None, "Connected but no sensor data received")
            
            # Update state
            self.last_voltage = voltage
            self.last_reading_time = datetime.now()
            self.consecutive_failures = 0
            self.is_online = True
            
            # Determine status
            if voltage < self.CRITICAL_VOLTAGE:
                return ("critical", voltage, f"🔴 CRITICAL: Battery at {voltage:.2f}V - Charge immediately!")
            elif voltage < self.LOW_VOLTAGE:
                return ("low", voltage, f"🟡 WARNING: Battery low at {voltage:.2f}V - Charge soon")
            else:
                percent = int(max(0, min(100, ((voltage - 6.0) / 2.4) * 100)))
                return ("ok", voltage, f"🟢 Battery healthy: {voltage:.2f}V ({percent}%)")
                
        except asyncio.TimeoutError:
            self.consecutive_failures += 1
            self.is_online = False
            return ("offline", None, f"⚫ Rover offline (connection timeout)")
            
        except ConnectionRefusedError:
            self.consecutive_failures += 1
            self.is_online = False
            return ("offline", None, f"⚫ Rover offline (connection refused)")
            
        except Exception as e:
            self.consecutive_failures += 1
            self.is_online = False
            return ("error", None, f"⚠️ Error: {str(e)}")
    
    async def monitor_loop(self, check_interval_seconds=300, alert_callback=None):
        """
        Continuous monitoring loop
        
        Args:
            check_interval_seconds: Time between checks (default: 5 minutes)
            alert_callback: async function(status, voltage, message) called on alerts
        """
        print(f"🔋 Battery monitoring started (checking every {check_interval_seconds}s)")
        print(f"   Critical threshold: {self.CRITICAL_VOLTAGE}V")
        print(f"   Low threshold: {self.LOW_VOLTAGE}V")
        print(f"   Rover: {self.host}\n")
        
        last_status = None
        
        while True:
            try:
                status, voltage, message = await self.check_battery()
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] {message}")
                
                # Only alert on status changes (except offline)
                should_alert = False
                
                if status in ("critical", "low"):
                    # Always alert on battery issues if online
                    if status != last_status:
                        should_alert = True
                        
                elif status == "offline":
                    # Only mention offline once
                    if last_status != "offline":
                        print(f"   (Rover went offline - not alerting)")
                        
                elif status == "ok":
                    # If recovering from low battery, mention it
                    if last_status in ("critical", "low"):
                        should_alert = True
                        message = f"✅ Battery recovered: {voltage:.2f}V"
                
                # Call alert callback if needed
                if should_alert and alert_callback:
                    await alert_callback(status, voltage, message)
                
                last_status = status
                
                # Wait for next check
                await asyncio.sleep(check_interval_seconds)
                
            except KeyboardInterrupt:
                print("\n⏸️ Monitoring stopped")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                await asyncio.sleep(check_interval_seconds)
    
    def get_status_summary(self):
        """Get current status summary"""
        if not self.is_online:
            return {
                "online": False,
                "consecutive_failures": self.consecutive_failures,
                "last_seen": self.last_reading_time.isoformat() if self.last_reading_time else None
            }
        
        return {
            "online": True,
            "voltage": self.last_voltage,
            "percent": int(max(0, min(100, ((self.last_voltage - 6.0) / 2.4) * 100))) if self.last_voltage else 0,
            "status": "critical" if self.last_voltage < self.CRITICAL_VOLTAGE else
                     "low" if self.last_voltage < self.LOW_VOLTAGE else "healthy",
            "last_check": self.last_reading_time.isoformat() if self.last_reading_time else None
        }


async def alert_to_console(status, voltage, message):
    """Example alert callback - print to console"""
    print(f"\n{'='*60}")
    print(f"⚠️  BATTERY ALERT")
    print(f"{'='*60}")
    print(message)
    print(f"{'='*60}\n")


async def alert_to_file(status, voltage, message, filepath="/tmp/rover_battery_alert.txt"):
    """Alert callback - write to file"""
    timestamp = datetime.now().isoformat()
    with open(filepath, 'a') as f:
        f.write(f"{timestamp} | {status} | {voltage}V | {message}\n")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor GalaxyRVR battery with alerts')
    parser.add_argument('--host', default='192.168.10.118', help='Rover IP')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds (default: 300 = 5min)')
    parser.add_argument('--once', action='store_true', help='Check once and exit')
    parser.add_argument('--critical', type=float, default=6.5, help='Critical voltage threshold (default: 6.5V)')
    parser.add_argument('--low', type=float, default=7.0, help='Low voltage threshold (default: 7.0V)')
    
    args = parser.parse_args()
    
    monitor = BatteryAlert(args.host)
    monitor.CRITICAL_VOLTAGE = args.critical
    monitor.LOW_VOLTAGE = args.low
    
    if args.once:
        # Single check
        status, voltage, message = await monitor.check_battery()
        print(message)
        
        if status == "offline":
            print("   (Rover is offline - this is normal when powered off)")
            return 0
        elif status in ("critical", "low"):
            return 1
        else:
            return 0
    else:
        # Continuous monitoring
        try:
            await monitor.monitor_loop(
                check_interval_seconds=args.interval,
                alert_callback=alert_to_console
            )
        except KeyboardInterrupt:
            print("\n✅ Monitoring stopped")
        
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
