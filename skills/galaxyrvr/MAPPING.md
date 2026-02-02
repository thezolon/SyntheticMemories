# GalaxyRVR Local Mapping System

**Zero dependencies, zero cloud costs!**

## Features

✅ **2D Occupancy Grid Mapping**
- Build map using ultrasonic + IR sensors
- Track explored/free/occupied areas
- Real-time odometry tracking

✅ **Pure Python (No Dependencies)**
- No numpy, no external libraries
- Runs on any Python 3 system
- Lightweight and fast

✅ **Sensor Fusion**
- Ultrasonic: Long-range obstacle detection (2-400cm)
- IR sensors: Short-range edge detection (~15cm)
- Movement odometry: Track rover position

✅ **ASCII Visualization**
- Real-time map display in terminal
- Rover position and heading shown
- Legend: `?`=unknown, `.`=free, `#`=obstacle, `^v<>`=rover

## How It Works

### Occupancy Grid
- Map divided into cells (default 10cm x 10cm)
- Each cell stores confidence: 0-100
  - 0 = Unknown (not explored)
  - 1-50 = Free space
  - 51-100 = Occupied (obstacle)

### Odometry
Tracks rover movement to estimate position:
- Forward/backward: Updates X,Y coordinates
- Turn left/right: Updates heading angle
- **Needs calibration** for your specific rover

### Sensor Integration
1. **Ultrasonic Reading**: Marks ray from rover to obstacle
   - Cells along ray = free
   - Cell at obstacle = occupied
2. **IR Sensors**: Immediate obstacle detection
   - Left/right sensors detect edges
   - High confidence close-range marking

## Usage

```python
from mapping import RoverMap

# Create map (3m x 3m area, 10cm cells)
rover_map = RoverMap(grid_size_meters=3.0, cell_size_cm=10)

# Update as rover moves
rover_map.update_odometry("forward", duration_sec=2.0, speed=50)
rover_map.add_ultrasonic_reading(distance_cm=150)
rover_map.add_ir_reading(ir_left=0, ir_right=1)

# View map
print(rover_map.get_map_ascii(width=40))

# Save/load
rover_map.save_map("my_map.json")
loaded = RoverMap.load_map("my_map.json")
```

## Calibration Needed

**Important:** You need to calibrate these constants for accurate mapping:

```python
CM_PER_SEC_AT_SPEED_100 = 30  # How fast rover moves
DEGREES_PER_SEC_AT_SPEED_100 = 120  # How fast it turns
```

### To Calibrate:
1. Mark starting position on floor
2. Run: `rover.forward(100)` for 5 seconds
3. Measure distance traveled
4. Calculate: `CM_PER_SEC = distance_cm / 5`

Repeat for turning (measure degrees with protractor).

## Integration with Vision

Combine with `vision.py` for enhanced mapping:
- Use vision to identify specific obstacles
- Label map cells with object types
- Navigate toward/away from targets

## Future Enhancements

With **Pi Zero 2W + GPS**:
- Absolute positioning (lat/long coordinates)
- SLAM (Simultaneous Localization and Mapping)
- Multi-session map merging
- Cloud map upload for visualization

## Example Output

```
🗺️  Current Map:
??????????????????????????????
?.????????????????????????????
?.?..?????????????????????????
?.??^.????????????????????????  <- Rover here
?.???...??????????????????????
?.?????.??????????????????????
```

Legend:
- `?` = Unknown/unexplored
- `.` = Free space (safe to drive)
- `#` = Obstacle detected
- `^v<>` = Rover (pointing direction)

## Cost

**$0.00** - All processing happens locally on your machine!

No cloud APIs, no external services, pure local computation.
