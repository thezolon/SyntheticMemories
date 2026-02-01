#!/usr/bin/env python3
"""
GalaxyRVR Local Mapping System
Build 2D occupancy grid map using sensors + odometry
No cloud costs - all processing local!
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
import math

class RoverMap:
    def __init__(self, 
                 grid_size_meters=5.0,
                 cell_size_cm=10,
                 origin_x=None,
                 origin_y=None):
        """
        Args:
            grid_size_meters: Map size (5m = 5x5 meter area)
            cell_size_cm: Grid cell size in cm (10cm = good balance)
            origin_x/y: Rover starting position (None = center of map)
        """
        # Map parameters
        self.grid_size_meters = grid_size_meters
        self.cell_size_cm = cell_size_cm
        self.cells_per_meter = 100 / cell_size_cm
        self.grid_cells = int(grid_size_meters * self.cells_per_meter)
        
        # Occupancy grid: 0=unknown, 1-50=free, 51-100=occupied
        # Using list of lists instead of numpy for zero dependencies
        self.grid = [[0 for _ in range(self.grid_cells)] for _ in range(self.grid_cells)]
        
        # WiFi signal strength overlay (optional)
        # Stores dBm values (-30 to -90) at each location
        self.wifi_grid = [[None for _ in range(self.grid_cells)] for _ in range(self.grid_cells)]
        
        # Rover pose (x, y in cm, heading in degrees)
        center = self.grid_cells // 2
        self.rover_x = origin_x if origin_x is not None else center
        self.rover_y = origin_y if origin_y is not None else center
        self.rover_heading = 0.0  # 0=north, 90=east, 180=south, 270=west
        
        # Movement history for odometry
        self.movement_history = deque(maxlen=1000)
        self.last_update_time = time.time()
        
        # Statistics
        self.total_distance_cm = 0
        self.scan_count = 0
        
    def world_to_grid(self, x_cm: float, y_cm: float) -> Tuple[int, int]:
        """Convert world coordinates (cm) to grid indices"""
        grid_x = int(x_cm / self.cell_size_cm)
        grid_y = int(y_cm / self.cell_size_cm)
        
        # Clamp to grid bounds
        grid_x = max(0, min(self.grid_cells - 1, grid_x))
        grid_y = max(0, min(self.grid_cells - 1, grid_y))
        
        return (grid_x, grid_y)
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Convert grid indices to world coordinates (cm)"""
        x_cm = grid_x * self.cell_size_cm
        y_cm = grid_y * self.cell_size_cm
        return (x_cm, y_cm)
    
    def update_odometry(self, movement_type: str, duration_sec: float, speed: int):
        """
        Update rover position based on movement command
        
        Args:
            movement_type: "forward", "backward", "turn_left", "turn_right", "stop"
            duration_sec: How long the movement lasted
            speed: Motor speed (0-100)
        """
        # Rough calibration (adjust based on real rover testing)
        CM_PER_SEC_AT_SPEED_100 = 30  # Calibrate this!
        DEGREES_PER_SEC_AT_SPEED_100 = 120  # Calibrate this!
        
        if movement_type == "forward":
            distance_cm = (speed / 100.0) * CM_PER_SEC_AT_SPEED_100 * duration_sec
            self.rover_x += distance_cm * math.sin(math.radians(self.rover_heading))
            self.rover_y += distance_cm * math.cos(math.radians(self.rover_heading))
            self.total_distance_cm += distance_cm
            
        elif movement_type == "backward":
            distance_cm = (speed / 100.0) * CM_PER_SEC_AT_SPEED_100 * duration_sec
            self.rover_x -= distance_cm * math.sin(math.radians(self.rover_heading))
            self.rover_y -= distance_cm * math.cos(math.radians(self.rover_heading))
            self.total_distance_cm += distance_cm
            
        elif movement_type == "turn_left":
            degrees = (speed / 100.0) * DEGREES_PER_SEC_AT_SPEED_100 * duration_sec
            self.rover_heading = (self.rover_heading - degrees) % 360
            
        elif movement_type == "turn_right":
            degrees = (speed / 100.0) * DEGREES_PER_SEC_AT_SPEED_100 * duration_sec
            self.rover_heading = (self.rover_heading + degrees) % 360
        
        # Log movement
        self.movement_history.append({
            "time": time.time(),
            "type": movement_type,
            "duration": duration_sec,
            "speed": speed,
            "position": (self.rover_x, self.rover_y),
            "heading": self.rover_heading
        })
        
        self.last_update_time = time.time()
    
    def add_ultrasonic_reading(self, distance_cm: float, confidence: float = 0.8):
        """
        Add ultrasonic sensor reading to map
        
        Args:
            distance_cm: Distance reading (-1 = no reading)
            confidence: How confident we are (0.0-1.0)
        """
        if distance_cm < 2 or distance_cm > 400:
            return  # Invalid reading
        
        self.scan_count += 1
        
        # Calculate obstacle position
        obstacle_x = self.rover_x + distance_cm * math.sin(math.radians(self.rover_heading))
        obstacle_y = self.rover_y + distance_cm * math.cos(math.radians(self.rover_heading))
        
        # Convert to grid
        obs_gx, obs_gy = self.world_to_grid(obstacle_x, obstacle_y)
        rover_gx, rover_gy = self.world_to_grid(self.rover_x, self.rover_y)
        
        # Mark cells between rover and obstacle as FREE
        self._ray_trace(rover_gx, rover_gy, obs_gx, obs_gy, mark_as_free=True)
        
        # Mark obstacle cell as OCCUPIED
        self._mark_cell(obs_gx, obs_gy, occupied=True, confidence=confidence)
    
    def add_ir_reading(self, ir_left: int, ir_right: int):
        """
        Add IR sensor readings (short-range obstacle detection)
        
        Args:
            ir_left: 0=clear, 1=obstacle
            ir_right: 0=clear, 1=obstacle
        """
        IR_DETECTION_RANGE_CM = 15  # IR sensors detect ~15cm ahead
        
        if ir_left == 1:
            # Obstacle on left front
            angle = (self.rover_heading - 30) % 360
            obs_x = self.rover_x + IR_DETECTION_RANGE_CM * math.sin(math.radians(angle))
            obs_y = self.rover_y + IR_DETECTION_RANGE_CM * math.cos(math.radians(angle))
            gx, gy = self.world_to_grid(obs_x, obs_y)
            self._mark_cell(gx, gy, occupied=True, confidence=0.9)
        
        if ir_right == 1:
            # Obstacle on right front
            angle = (self.rover_heading + 30) % 360
            obs_x = self.rover_x + IR_DETECTION_RANGE_CM * math.sin(math.radians(angle))
            obs_y = self.rover_y + IR_DETECTION_RANGE_CM * math.cos(math.radians(angle))
            gx, gy = self.world_to_grid(obs_x, obs_y)
            self._mark_cell(gx, gy, occupied=True, confidence=0.9)
    
    def add_wifi_reading(self, signal_dbm: int):
        """
        Add WiFi signal strength reading at current location
        
        Args:
            signal_dbm: Signal strength in dBm (-30 to -90)
        """
        gx, gy = self.world_to_grid(self.rover_x, self.rover_y)
        
        # Store or average with existing reading
        if self.wifi_grid[gy][gx] is None:
            self.wifi_grid[gy][gx] = signal_dbm
        else:
            # Moving average for multiple readings
            self.wifi_grid[gy][gx] = int((self.wifi_grid[gy][gx] + signal_dbm) / 2)
    
    def find_best_wifi_location(self) -> Optional[Tuple[float, float, int]]:
        """
        Find location with best WiFi signal in explored areas
        
        Returns:
            (x_cm, y_cm, signal_dbm) or None if no WiFi data
        """
        best_signal = -999
        best_x, best_y = None, None
        
        for y in range(self.grid_cells):
            for x in range(self.grid_cells):
                signal = self.wifi_grid[y][x]
                if signal is not None and signal > best_signal:
                    best_signal = signal
                    best_x, best_y = x, y
        
        if best_x is None:
            return None
        
        x_cm, y_cm = self.grid_to_world(best_x, best_y)
        return (x_cm, y_cm, best_signal)
    
    def _mark_cell(self, grid_x: int, grid_y: int, occupied: bool, confidence: float = 0.5):
        """Mark a single grid cell as occupied or free"""
        if grid_x < 0 or grid_x >= self.grid_cells or grid_y < 0 or grid_y >= self.grid_cells:
            return
        
        if occupied:
            # Increase occupancy (max 100)
            delta = int(confidence * 20)
            self.grid[grid_y][grid_x] = min(100, self.grid[grid_y][grid_x] + delta)
        else:
            # Decrease occupancy (min 1, never fully zero = we've explored it)
            delta = int(confidence * 10)
            self.grid[grid_y][grid_x] = max(1, self.grid[grid_y][grid_x] - delta)
    
    def _ray_trace(self, x0: int, y0: int, x1: int, y1: int, mark_as_free: bool = True):
        """Bresenham's line algorithm - mark cells along ray"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            if mark_as_free:
                self._mark_cell(x, y, occupied=False, confidence=0.3)
            
            if x == x1 and y == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def get_map_ascii(self, width: int = 40, show_wifi: bool = False) -> str:
        """Generate ASCII visualization of map"""
        # Downsample grid to fit terminal
        scale = max(1, self.grid_cells // width)
        
        lines = []
        rover_gx, rover_gy = self.world_to_grid(self.rover_x, self.rover_y)
        
        for y in range(0, self.grid_cells, scale):
            line = ""
            for x in range(0, self.grid_cells, scale):
                # Check if rover is here
                if abs(x - rover_gx) < scale and abs(y - rover_gy) < scale:
                    # Rover direction indicator
                    if 45 <= self.rover_heading < 135:
                        line += ">"
                    elif 135 <= self.rover_heading < 225:
                        line += "v"
                    elif 225 <= self.rover_heading < 315:
                        line += "<"
                    else:
                        line += "^"
                else:
                    if show_wifi:
                        # Show WiFi heatmap
                        wifi = self.wifi_grid[y][x]
                        if wifi is None:
                            line += "?"
                        elif wifi >= -50:
                            line += "█"  # Excellent
                        elif wifi >= -60:
                            line += "▓"  # Good
                        elif wifi >= -70:
                            line += "▒"  # Fair
                        elif wifi >= -80:
                            line += "░"  # Weak
                        else:
                            line += "·"  # Very weak
                    else:
                        # Show occupancy grid
                        val = self.grid[y][x]
                        if val == 0:
                            line += "?"  # Unknown
                        elif val < 30:
                            line += "."  # Free
                        elif val < 60:
                            line += "·"  # Possibly free
                        else:
                            line += "#"  # Obstacle
            lines.append(line)
        
        return "\n".join(lines)
    
    def is_cell_free(self, grid_x: int, grid_y: int) -> bool:
        """Check if a cell is free to navigate through"""
        if grid_x < 0 or grid_x >= self.grid_cells or grid_y < 0 or grid_y >= self.grid_cells:
            return False  # Out of bounds
        
        # Consider free if occupancy < 60 (free or unknown)
        # Unknown is optimistically free (frontier exploration)
        return self.grid[grid_y][grid_x] < 60
    
    def find_path(self, target_x_cm: float, target_y_cm: float) -> Optional[List[Tuple[int, int]]]:
        """
        Find path from current rover position to target using A* algorithm
        
        Args:
            target_x_cm, target_y_cm: Target position in world coordinates
        
        Returns:
            List of (grid_x, grid_y) waypoints, or None if no path found
        """
        # Convert to grid coordinates
        start_gx, start_gy = self.world_to_grid(self.rover_x, self.rover_y)
        goal_gx, goal_gy = self.world_to_grid(target_x_cm, target_y_cm)
        
        # Check if goal is reachable
        if not self.is_cell_free(goal_gx, goal_gy):
            # Try to find nearest free cell
            goal_gx, goal_gy = self._find_nearest_free_cell(goal_gx, goal_gy)
            if goal_gx is None:
                return None  # No free cell nearby
        
        # A* pathfinding
        from collections import deque
        
        # Priority queue: (f_score, (x, y))
        open_set = [(0, (start_gx, start_gy))]
        came_from = {}
        g_score = {(start_gx, start_gy): 0}
        
        def heuristic(x, y):
            # Manhattan distance
            return abs(x - goal_gx) + abs(y - goal_gy)
        
        while open_set:
            # Get node with lowest f_score
            open_set.sort()
            current_f, current = open_set.pop(0)
            cx, cy = current
            
            # Goal reached?
            if cx == goal_gx and cy == goal_gy:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            # Explore neighbors (4-connected)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                
                if not self.is_cell_free(nx, ny):
                    continue
                
                tentative_g = g_score[current] + 1
                
                if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                    came_from[(nx, ny)] = current
                    g_score[(nx, ny)] = tentative_g
                    f_score = tentative_g + heuristic(nx, ny)
                    open_set.append((f_score, (nx, ny)))
        
        return None  # No path found
    
    def _find_nearest_free_cell(self, grid_x: int, grid_y: int, max_radius: int = 10) -> Tuple[Optional[int], Optional[int]]:
        """Find nearest free cell within radius"""
        for radius in range(1, max_radius):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) == radius or abs(dy) == radius:
                        nx, ny = grid_x + dx, grid_y + dy
                        if self.is_cell_free(nx, ny):
                            return (nx, ny)
        return (None, None)
    
    def get_next_waypoint(self, path: List[Tuple[int, int]], lookahead: int = 3) -> Optional[Tuple[float, float]]:
        """
        Get next waypoint from path (with lookahead for smoother navigation)
        
        Args:
            path: Path from find_path()
            lookahead: How many cells ahead to target (reduces wiggling)
        
        Returns:
            (x_cm, y_cm) in world coordinates, or None if path empty
        """
        if not path:
            return None
        
        # Look ahead in path for smoother navigation
        idx = min(lookahead, len(path) - 1)
        grid_x, grid_y = path[idx]
        
        return self.grid_to_world(grid_x, grid_y)
    
    def find_unexplored_frontier(self) -> Optional[Tuple[float, float]]:
        """
        Find nearest unexplored area (frontier-based exploration)
        
        Returns:
            (x_cm, y_cm) of frontier cell, or None if map fully explored
        """
        rover_gx, rover_gy = self.world_to_grid(self.rover_x, self.rover_y)
        
        # Find frontier cells (unknown cells adjacent to explored cells)
        frontiers = []
        
        for y in range(self.grid_cells):
            for x in range(self.grid_cells):
                if self.grid[y][x] == 0:  # Unknown
                    # Check if adjacent to explored area
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < self.grid_cells and 
                            0 <= ny < self.grid_cells and 
                            self.grid[ny][nx] > 0):  # Explored
                            # Calculate distance to rover
                            dist = abs(x - rover_gx) + abs(y - rover_gy)
                            frontiers.append((dist, x, y))
                            break
        
        if not frontiers:
            return None  # Fully explored!
        
        # Return nearest frontier
        frontiers.sort()
        _, fx, fy = frontiers[0]
        return self.grid_to_world(fx, fy)
    
    def navigate_to(self, target_x_cm: float, target_y_cm: float) -> Dict[str, Any]:
        """
        High-level navigation: find path and return next move command
        
        Returns:
            {
                "action": "forward" | "turn_left" | "turn_right" | "arrived" | "blocked",
                "path_found": bool,
                "distance_to_goal_cm": float,
                "waypoint": (x, y) or None
            }
        """
        # Find path
        path = self.find_path(target_x_cm, target_y_cm)
        
        if path is None:
            return {
                "action": "blocked",
                "path_found": False,
                "distance_to_goal_cm": None,
                "waypoint": None
            }
        
        if len(path) == 0:
            return {
                "action": "arrived",
                "path_found": True,
                "distance_to_goal_cm": 0,
                "waypoint": None
            }
        
        # Get next waypoint
        waypoint = self.get_next_waypoint(path, lookahead=3)
        if waypoint is None:
            return {
                "action": "arrived",
                "path_found": True,
                "distance_to_goal_cm": 0,
                "waypoint": None
            }
        
        wx, wy = waypoint
        
        # Calculate bearing to waypoint
        dx = wx - self.rover_x
        dy = wy - self.rover_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Target heading (0=north, 90=east, 180=south, 270=west)
        target_heading = math.degrees(math.atan2(dx, dy)) % 360
        
        # Heading error
        heading_error = (target_heading - self.rover_heading + 180) % 360 - 180
        
        # Decide action
        if abs(heading_error) > 15:  # Not facing waypoint
            action = "turn_left" if heading_error < 0 else "turn_right"
        elif distance < 10:  # Very close
            action = "arrived"
        else:
            action = "forward"
        
        return {
            "action": action,
            "path_found": True,
            "distance_to_goal_cm": distance,
            "waypoint": waypoint,
            "heading_error": heading_error,
            "path_length": len(path)
        }


    def get_statistics(self) -> Dict:
        """Get mapping statistics"""
        explored_cells = sum(1 for row in self.grid for cell in row if cell > 0)
        occupied_cells = sum(1 for row in self.grid for cell in row if cell > 60)
        total_cells = self.grid_cells * self.grid_cells
        
        return {
            "grid_size": f"{self.grid_size_meters}m x {self.grid_size_meters}m",
            "cell_size": f"{self.cell_size_cm}cm",
            "total_cells": total_cells,
            "explored_cells": int(explored_cells),
            "explored_percent": round(explored_cells / total_cells * 100, 1),
            "occupied_cells": int(occupied_cells),
            "rover_position": {
                "x_cm": round(self.rover_x, 1),
                "y_cm": round(self.rover_y, 1),
                "heading_deg": round(self.rover_heading, 1)
            },
            "distance_traveled_cm": round(self.total_distance_cm, 1),
            "distance_traveled_m": round(self.total_distance_cm / 100, 2),
            "scan_count": self.scan_count
        }
    
    def save_map(self, filepath: str):
        """Save map to file (JSON + numpy array)"""
        data = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "grid_size_meters": self.grid_size_meters,
                "cell_size_cm": self.cell_size_cm,
                "grid_cells": self.grid_cells
            },
            "rover_pose": {
                "x": float(self.rover_x),
                "y": float(self.rover_y),
                "heading": float(self.rover_heading)
            },
            "statistics": self.get_statistics(),
            "grid": self.grid  # Already a list
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Map saved to {filepath}")
    
    @classmethod
    def load_map(cls, filepath: str) -> 'RoverMap':
        """Load map from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Create map with same parameters
        rover_map = cls(
            grid_size_meters=data["metadata"]["grid_size_meters"],
            cell_size_cm=data["metadata"]["cell_size_cm"]
        )
        
        # Restore grid (convert back to list of lists)
        loaded_grid = data["grid"]
        rover_map.grid = loaded_grid if isinstance(loaded_grid, list) else loaded_grid.tolist()
        
        # Restore rover pose
        rover_map.rover_x = data["rover_pose"]["x"]
        rover_map.rover_y = data["rover_pose"]["y"]
        rover_map.rover_heading = data["rover_pose"]["heading"]
        
        print(f"✅ Map loaded from {filepath}")
        return rover_map


def demo():
    """Demo the mapping system"""
    print("🗺️  GalaxyRVR Local Mapping Demo")
    print("=" * 60)
    
    # Create map
    rover_map = RoverMap(grid_size_meters=3.0, cell_size_cm=10)
    
    # Simulate some movement and sensor readings
    print("\n📍 Simulating rover exploration...")
    
    # Move forward and scan
    rover_map.update_odometry("forward", duration_sec=2.0, speed=50)
    rover_map.add_ultrasonic_reading(distance_cm=150, confidence=0.8)
    rover_map.add_wifi_reading(signal_dbm=-55)  # Good signal
    
    # Turn right
    rover_map.update_odometry("turn_right", duration_sec=1.0, speed=50)
    
    # Move forward again
    rover_map.update_odometry("forward", duration_sec=1.5, speed=50)
    rover_map.add_ultrasonic_reading(distance_cm=80, confidence=0.8)
    rover_map.add_ir_reading(ir_left=0, ir_right=1)  # Obstacle on right
    rover_map.add_wifi_reading(signal_dbm=-60)  # Still good
    
    # Turn left and continue
    rover_map.update_odometry("turn_left", duration_sec=0.5, speed=50)
    rover_map.update_odometry("forward", duration_sec=1.0, speed=50)
    rover_map.add_ultrasonic_reading(distance_cm=200, confidence=0.7)
    rover_map.add_wifi_reading(signal_dbm=-70)  # Getting weaker
    
    # Show map
    print("\n🗺️  Current Map:")
    print(rover_map.get_map_ascii(width=30))
    
    # Show statistics
    print("\n📊 Statistics:")
    stats = rover_map.get_statistics()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"      {k}: {v}")
        else:
            print(f"   {key}: {value}")
    
    # Test navigation
    print("\n🧭 Testing path planning...")
    
    # Plan path back to start (center of map)
    center_cm = (rover_map.grid_cells // 2) * rover_map.cell_size_cm
    nav_result = rover_map.navigate_to(center_cm, center_cm)
    
    print(f"   Navigate to start (150, 150):")
    print(f"   - Path found: {nav_result['path_found']}")
    print(f"   - Next action: {nav_result['action']}")
    print(f"   - Distance: {nav_result.get('distance_to_goal_cm', 0):.1f}cm")
    if nav_result.get('path_length'):
        print(f"   - Path length: {nav_result['path_length']} waypoints")
    
    # Find unexplored area
    frontier = rover_map.find_unexplored_frontier()
    if frontier:
        fx, fy = frontier
        print(f"\n🔍 Nearest unexplored area: ({fx:.0f}, {fy:.0f})cm")
    else:
        print(f"\n✅ Map fully explored!")
    
    # WiFi heatmap
    print("\n📡 WiFi Signal Heatmap:")
    print(rover_map.get_map_ascii(width=30, show_wifi=True))
    
    best_wifi = rover_map.find_best_wifi_location()
    if best_wifi:
        wx, wy, signal = best_wifi
        print(f"\n📶 Best WiFi location: ({wx:.0f}, {wy:.0f})cm at {signal}dBm")
    
    # Save map
    filepath = "/tmp/rover_map_demo.json"
    rover_map.save_map(filepath)
    
    print("\n" + "=" * 60)
    print("✅ Mapping system ready!")
    print("💰 Cost: $0.00 (all local processing)")
    print("\n💡 Path planning features:")
    print("   - A* pathfinding through explored areas")
    print("   - Obstacle avoidance using map data")
    print("   - Frontier-based exploration")
    print("   - Return to previously visited locations")
    print("   - WiFi signal strength heatmap")
    print("   - Navigate back to strong signal areas")


if __name__ == "__main__":
    demo()
