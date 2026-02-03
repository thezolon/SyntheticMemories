#!/usr/bin/env python3
"""
GalaxyRVR Map Viewer
View saved exploration maps
"""

import sys
import json
from typing import Optional

sys.path.insert(0, '/home/zolon/.openclaw/workspace/skills/galaxyrvr')
from mapping import RoverMap

def view_map(map_file: str, show_wifi: bool = False):
    """Load and display a saved map"""
    
    try:
        rover_map = RoverMap.load_map(map_file)
    except Exception as e:
        print(f"❌ Failed to load map: {e}")
        return
    
    print(f"\n🗺️  Map: {map_file}")
    print("=" * 60)
    
    # Show statistics
    stats = rover_map.get_statistics()
    print(f"Rover Position: ({rover_map.rover_x:.0f}, {rover_map.rover_y:.0f})cm")
    print(f"Heading: {rover_map.rover_heading:.0f}°")
    print(f"Distance Traveled: {stats['distance_traveled_m']:.1f}m")
    print(f"Explored: {stats['explored_percent']:.1f}%")
    print(f"Scans: {stats['scan_count']}")
    print()
    
    # Show map
    if show_wifi:
        print("📡 WiFi Signal Heatmap:")
        print("   █ = Excellent  ▓ = Good  ▒ = Fair  ░ = Weak  · = Very Weak")
        print()
        print(rover_map.get_map_ascii(width=50, show_wifi=True))
        
        # Best WiFi location
        best = rover_map.find_best_wifi_location()
        if best:
            wx, wy, signal = best
            print(f"\n📶 Best signal: ({wx:.0f}, {wy:.0f})cm at {signal}dBm")
    else:
        print("🗺️  Occupancy Grid:")
        print("   ^ = Rover  # = Obstacle  . = Free  ? = Unknown")
        print()
        print(rover_map.get_map_ascii(width=50, show_wifi=False))
    
    print("\n" + "=" * 60)

def list_maps(directory: str = "/tmp"):
    """List available map files"""
    import os
    import glob
    
    maps = glob.glob(f"{directory}/rover_map_*.json")
    
    if not maps:
        print(f"No maps found in {directory}")
        return
    
    print(f"\n📂 Available Maps in {directory}:")
    print("=" * 60)
    
    for map_file in sorted(maps, reverse=True):
        try:
            with open(map_file) as f:
                data = json.load(f)
            
            stats = data.get('statistics', {})
            timestamp = os.path.basename(map_file).replace('rover_map_', '').replace('.json', '')
            
            print(f"  {timestamp}")
            print(f"    Distance: {stats.get('distance_traveled_m', 0):.1f}m")
            print(f"    Explored: {stats.get('explored_percent', 0):.1f}%")
            print(f"    Scans: {stats.get('scan_count', 0)}")
            print()
        except:
            print(f"  {map_file} (error reading)")
    
    print("=" * 60)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='View GalaxyRVR exploration maps')
    parser.add_argument('map_file', nargs='?', help='Map file to view')
    parser.add_argument('--wifi', action='store_true', help='Show WiFi heatmap instead of occupancy')
    parser.add_argument('--list', action='store_true', help='List available maps')
    parser.add_argument('--dir', default='/tmp', help='Directory to search for maps')
    
    args = parser.parse_args()
    
    if args.list:
        list_maps(args.dir)
    elif args.map_file:
        view_map(args.map_file, show_wifi=args.wifi)
    else:
        # Show most recent map
        import glob
        maps = glob.glob(f"{args.dir}/rover_map_*.json")
        if maps:
            latest = max(maps, key=lambda f: os.path.getmtime(f))
            print("Showing most recent map:")
            view_map(latest, show_wifi=args.wifi)
        else:
            print("No maps found. Use --list to search or specify a map file.")
            print("\nUsage:")
            print("  python3 map_viewer.py                    # View latest map")
            print("  python3 map_viewer.py --list             # List all maps")
            print("  python3 map_viewer.py --wifi             # Show WiFi heatmap")
            print("  python3 map_viewer.py my_map.json        # View specific map")

if __name__ == "__main__":
    import os
    main()
