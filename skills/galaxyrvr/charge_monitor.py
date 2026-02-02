#!/usr/bin/env python3
"""
GalaxyRVR Charge Monitor
Detects charging state by monitoring battery voltage trends
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime
from collections import deque

class ChargeMonitor:
    def __init__(self, host="192.168.10.118", port=8765):
        self.host = host
        self.port = port
        self.ws = None
        
        # Voltage history (last N readings)
        self.voltage_history = deque(maxlen=30)  # ~30 seconds of data
        self.timestamps = deque(maxlen=30)
        
        # Current state
        self.current_voltage = 0.0
        self.charging_state = "unknown"
        self.charge_rate_mv_min = 0.0
        
    async def connect(self):
        """Connect to rover"""
        uri = f"ws://{self.host}:{self.port}"
        self.ws = await websockets.connect(uri, ping_interval=None)
        await self.ws.recv()  # handshake
        await self.ws.send(json.dumps({"K": 0, "Q": 0, "D": 90}))
        print(f"✅ Connected to GalaxyRVR")
        
    async def monitor_charging(self, duration=60):
        """Monitor charging state for specified duration"""
        print("\n🔋 GalaxyRVR Charge Monitor")
        print("=" * 70)
        print("Collecting baseline data (wait 30 seconds for accurate detection)...\n")
        
        start = asyncio.get_event_loop().time()
        last_analysis = start
        
        try:
            while (asyncio.get_event_loop().time() - start) < duration:
                try:
                    msg = await asyncio.wait_for(self.ws.recv(), timeout=0.5)
                    
                    if msg.startswith("pong"):
                        await self.ws.send(json.dumps({"K": 0, "Q": 0, "D": 90}))
                        continue
                    
                    if not msg.startswith("{"):
                        continue
                    
                    try:
                        data = json.loads(msg)
                        if "BV" in data:
                            voltage = data["BV"]
                            now = datetime.now()
                            
                            self.voltage_history.append(voltage)
                            self.timestamps.append(now)
                            self.current_voltage = voltage
                            
                            # Analyze every 2 seconds
                            if asyncio.get_event_loop().time() - last_analysis > 2:
                                self._analyze_trend()
                                self._display_status()
                                last_analysis = asyncio.get_event_loop().time()
                            
                    except json.JSONDecodeError:
                        pass
                        
                except asyncio.TimeoutError:
                    await self.ws.send(json.dumps({"K": 0, "Q": 0, "D": 90}))
                    continue
                    
        except KeyboardInterrupt:
            print("\n\n⏸️  Monitoring stopped")
        finally:
            await self.ws.close()
            self._print_summary()
    
    def _analyze_trend(self):
        """Analyze voltage trend to detect charging (with smoothing)"""
        if len(self.voltage_history) < 10:
            self.charging_state = "collecting data..."
            return
        
        # Calculate voltage change over time
        voltages = list(self.voltage_history)
        times = list(self.timestamps)
        
        # Use moving average to reduce ADC noise
        if len(voltages) >= 20:
            # Average first 10 and last 10 readings
            start_avg = sum(voltages[:10]) / 10
            end_avg = sum(voltages[-10:]) / 10
            
            time_span = (times[-1] - times[-10]).total_seconds() / 60.0  # minutes
            voltage_change = end_avg - start_avg
            
            if time_span > 0:
                self.charge_rate_mv_min = (voltage_change * 1000) / time_span
                
                # Classify charging state (looser thresholds due to ADC noise)
                if self.charge_rate_mv_min > 5.0:
                    # Gaining >5mV/min = likely plugged in charging
                    self.charging_state = "🔌 CHARGING (AC adapter)"
                elif self.charge_rate_mv_min > 1.0:
                    # Gaining 1-5mV/min = likely solar charging
                    self.charging_state = "☀️  SOLAR CHARGING"
                elif self.charge_rate_mv_min > -1.0:
                    # Stable within ±1mV/min = idle/trickle
                    self.charging_state = "⚡ IDLE (no load)"
                elif self.charge_rate_mv_min > -5.0:
                    # Losing 1-5mV/min = light usage
                    self.charging_state = "📉 LIGHT DISCHARGE"
                else:
                    # Losing >5mV/min = active discharge
                    self.charging_state = "🔋 ACTIVE DISCHARGE"
        else:
            self.charging_state = "📊 Analyzing..."
    
    def _display_status(self):
        """Display current status"""
        sys.stdout.write('\033[2K\r')
        
        # Voltage with color
        if self.current_voltage < 6.5:
            v_icon = "🔴"
        elif self.current_voltage < 7.0:
            v_icon = "🟡"
        else:
            v_icon = "🟢"
        
        # Build status
        status = (
            f"{v_icon} {self.current_voltage:.2f}V | "
            f"{self.charging_state} | "
            f"Rate: {self.charge_rate_mv_min:+.1f}mV/min | "
            f"Samples: {len(self.voltage_history)}"
        )
        
        sys.stdout.write(status)
        sys.stdout.flush()
    
    def _print_summary(self):
        """Print detailed summary"""
        print("\n\n" + "=" * 70)
        print("📊 Charge Monitoring Summary")
        print("=" * 70)
        
        if len(self.voltage_history) < 2:
            print("Insufficient data collected")
            return
        
        voltages = list(self.voltage_history)
        times = list(self.timestamps)
        
        print(f"\n🔋 Battery Status:")
        print(f"   Current Voltage: {self.current_voltage:.2f}V")
        print(f"   Starting Voltage: {voltages[0]:.2f}V")
        print(f"   Change: {(self.current_voltage - voltages[0])*1000:+.1f}mV")
        
        print(f"\n⚡ Charging Analysis:")
        print(f"   State: {self.charging_state}")
        print(f"   Rate: {self.charge_rate_mv_min:+.1f}mV/min")
        
        time_span = (times[-1] - times[0]).total_seconds()
        print(f"\n📊 Monitoring Stats:")
        print(f"   Duration: {time_span:.0f} seconds")
        print(f"   Samples: {len(voltages)}")
        print(f"   Sample Rate: {len(voltages)/time_span*60:.1f} per minute")
        
        # Voltage graph
        print(f"\n📈 Voltage History (last {len(voltages)} readings):")
        min_v = min(voltages)
        max_v = max(voltages)
        range_v = max_v - min_v if max_v > min_v else 0.01
        
        for i in range(0, len(voltages), max(1, len(voltages)//10)):
            v = voltages[i]
            bar_len = int(((v - min_v) / range_v) * 40)
            bar = "█" * bar_len
            print(f"   {v:.2f}V |{bar}")
        
        print("\n" + "=" * 70)
        
        # Interpretation guide
        print("\n💡 What the numbers mean:")
        print("   >+5mV/min   = AC adapter charging (bright LED)")
        print("   +1-5mV/min  = Solar charging (dim LED)")
        print("   ±1mV/min    = Idle/trickle")
        print("   <-1mV/min   = Discharging (in use)")
        print("\n⚠️  Note: ADC noise can cause ±150mV jumps in readings.")
        print("   Monitor for 1-2 minutes for accurate charge detection.")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor GalaxyRVR charging state')
    parser.add_argument('--host', default='192.168.10.118', help='Rover IP')
    parser.add_argument('--duration', type=int, default=60, help='Monitor duration in seconds (default: 60)')
    
    args = parser.parse_args()
    
    monitor = ChargeMonitor(args.host)
    
    try:
        await monitor.connect()
        await monitor.monitor_charging(duration=args.duration)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
