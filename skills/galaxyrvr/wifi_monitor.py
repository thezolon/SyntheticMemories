#!/usr/bin/env python3
"""
GalaxyRVR WiFi Signal Monitor
Monitor WiFi signal strength during rover exploration
Useful for creating signal strength heatmaps!
"""

import subprocess
import re
import time
from typing import Optional

class WiFiMonitor:
    def __init__(self, target_ip="192.168.10.118"):
        self.target_ip = target_ip
        self.interface = None
        self._detect_interface()
    
    def _detect_interface(self):
        """Detect active WiFi interface"""
        try:
            # Try common WiFi interface names
            result = subprocess.run(['ip', 'link', 'show'], 
                                  capture_output=True, text=True, timeout=2)
            
            # Look for wlan, wlp, wifi interfaces
            for line in result.stdout.split('\n'):
                if 'wlan' in line or 'wlp' in line or 'wifi' in line:
                    match = re.search(r'\d+: (\w+):', line)
                    if match:
                        self.interface = match.group(1)
                        break
            
            if not self.interface:
                # Fallback to iwconfig
                result = subprocess.run(['iwconfig'], 
                                      capture_output=True, text=True, timeout=2)
                for line in result.stdout.split('\n'):
                    if 'IEEE 802.11' in line or 'ESSID' in line:
                        self.interface = line.split()[0]
                        break
                        
        except Exception as e:
            print(f"Warning: Could not detect WiFi interface: {e}")
            self.interface = "wlan0"  # Default fallback
    
    def get_signal_strength(self) -> Optional[int]:
        """
        Get WiFi signal strength in dBm (or estimated from ping)
        
        Returns:
            Signal strength in dBm (typically -30 to -90)
            -30 = excellent, -50 = good, -70 = weak, -90 = very weak
            None if unable to measure
        """
        if not self.interface:
            # Try ping-based estimation as fallback
            return self._estimate_from_ping()
        
        try:
            # Try iw first (modern tool)
            result = subprocess.run(['iw', 'dev', self.interface, 'link'],
                                  capture_output=True, text=True, timeout=2)
            match = re.search(r'signal: (-?\d+) dBm', result.stdout)
            if match:
                return int(match.group(1))
            
            # Try iwconfig (older tool)
            result = subprocess.run(['iwconfig', self.interface],
                                  capture_output=True, text=True, timeout=2)
            
            # Parse signal level
            match = re.search(r'Signal level[=:](-?\d+)', result.stdout)
            if match:
                return int(match.group(1))
            
            # Alternative: parse link quality
            match = re.search(r'Link Quality[=:](\d+)/(\d+)', result.stdout)
            if match:
                quality = int(match.group(1))
                max_quality = int(match.group(2))
                # Convert to approximate dBm (-90 to -30 range)
                dbm = int(-90 + (quality / max_quality) * 60)
                return dbm
            
        except FileNotFoundError:
            pass  # Tool not installed
        except Exception as e:
            pass  # Other errors
        
        # Fallback: estimate from ping latency
        return self._estimate_from_ping()
    
    def _estimate_from_ping(self) -> Optional[int]:
        """Estimate signal strength from ping latency (when tools unavailable)"""
        latency = self.ping_test()
        if latency is None:
            return -90  # No response = very weak
        
        # Rough estimation: 
        # <10ms = excellent (-40dBm)
        # 10-50ms = good (-55dBm)
        # 50-100ms = fair (-65dBm)
        # 100-200ms = weak (-75dBm)
        # >200ms = very weak (-85dBm)
        
        if latency < 10:
            return -40
        elif latency < 50:
            return -55
        elif latency < 100:
            return -65
        elif latency < 200:
            return -75
        else:
            return -85
    
    def get_signal_quality(self) -> str:
        """Get human-readable signal quality"""
        dbm = self.get_signal_strength()
        
        if dbm is None:
            return "Unknown"
        elif dbm >= -50:
            return "Excellent"
        elif dbm >= -60:
            return "Good"
        elif dbm >= -70:
            return "Fair"
        elif dbm >= -80:
            return "Weak"
        else:
            return "Very Weak"
    
    def get_signal_bars(self) -> str:
        """Get signal strength as bars (like phone signal)"""
        dbm = self.get_signal_strength()
        
        if dbm is None:
            return "❓"
        elif dbm >= -50:
            return "📶" * 4  # Excellent
        elif dbm >= -60:
            return "📶" * 3  # Good
        elif dbm >= -70:
            return "📶" * 2  # Fair
        elif dbm >= -80:
            return "📶"      # Weak
        else:
            return "📵"      # Very weak
    
    def is_signal_safe(self, threshold_dbm: int = -75) -> bool:
        """Check if signal is strong enough for reliable operation"""
        dbm = self.get_signal_strength()
        if dbm is None:
            return False  # Unknown = assume unsafe
        return dbm >= threshold_dbm
    
    def ping_test(self) -> Optional[float]:
        """
        Ping rover to test connection latency
        
        Returns:
            Latency in milliseconds, or None if failed
        """
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '2', self.target_ip],
                                  capture_output=True, text=True, timeout=3)
            
            # Parse ping time
            match = re.search(r'time=([\d.]+) ms', result.stdout)
            if match:
                return float(match.group(1))
            
            return None
            
        except Exception:
            return None


def demo():
    """Demo WiFi monitoring"""
    print("📡 GalaxyRVR WiFi Monitor Demo")
    print("=" * 60)
    
    monitor = WiFiMonitor(target_ip="192.168.10.118")
    
    print(f"Interface: {monitor.interface or 'Not detected'}")
    print()
    
    print("📊 Real-time signal monitoring (5 seconds)...")
    print()
    
    for i in range(5):
        dbm = monitor.get_signal_strength()
        quality = monitor.get_signal_quality()
        bars = monitor.get_signal_bars()
        safe = monitor.is_signal_safe()
        ping = monitor.ping_test()
        
        print(f"[{i+1}/5] {bars} Signal: {dbm}dBm ({quality}) "
              f"| Safe: {'✅' if safe else '⚠️ '} "
              f"| Ping: {ping:.1f}ms" if ping else "| Ping: timeout")
        
        if i < 4:
            time.sleep(1)
    
    print()
    print("=" * 60)
    print("✅ WiFi monitoring ready!")
    print()
    print("💡 Use cases:")
    print("   - Create WiFi signal strength heatmap")
    print("   - Know when approaching connection limits")
    print("   - Navigate back to strong signal areas")
    print("   - Set 'safe zone' boundaries based on signal")


if __name__ == "__main__":
    demo()
