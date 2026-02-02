# GalaxyRVR Rover - Full Working Control

**Date:** 2026-02-01  
**Status:** ✅ FULLY OPERATIONAL

## Hardware
- **Model:** SunFounder GalaxyRVR Mars Rover
- **IP:** 192.168.10.118
- **Components:** ESP32-CAM (WiFi/camera) + Arduino R3 + GalaxyRVR Shield
- **Source:** `/bulk/AnimaNet/galaxy-rvr-main/`

## Working Control System
**Location:** `~/.openclaw/workspace/skills/galaxyrvr/rover_control.py`

### Key Discovery: Continuous Commands Required
The Arduino firmware uses mode-based control:
- Commands must be sent at **10Hz continuously** to maintain MODE_APP_CONTROL
- Single commands work for servo, but motors need continuous stream
- This mimics how the SunFounder Controller app operates

### Protocol
```
1. Connect: ws://192.168.10.118:8765
2. Receive: "pong [timestamp]"
3. Send JSON at 10Hz: {"K": left, "Q": right, "D": servo}
```

### Python API
```python
from galaxyrvr.rover_control import GalaxyRVR

rover = GalaxyRVR()
await rover.connect()

# Movement (changes take effect within 100ms)
rover.forward(speed=70)
rover.backward(speed=70)
rover.turn_left(speed=70)
rover.turn_right(speed=70)
rover.stop()
rover.set_motors(left, right)  # -100 to 100

# Camera & Accessories
rover.set_servo(angle)  # 0-140 degrees
rover.set_lamp(True)    # ESP32-CAM LED

# Sensors (updated continuously)
battery = rover.get_battery()      # Voltage
distance = rover.get_distance()    # cm
ir_left = rover.get_ir_left()      # 0=clear, 1=obstacle
ir_right = rover.get_ir_right()
sensors = rover.get_sensors()      # All data
```

## AnimaNet Integration
Found working code in `/bulk/AnimaNet/archive/2025-12-20-phase5-deprecated/robot-embodiment/`

Key files:
- `src/hardware/sunfounder_protocol_adapter.py` - Working WebSocket adapter
- `demo_hybrid_navigation.py` - Autonomous navigation example
- Uses same protocol we reverse-engineered

## Next Steps for OpenClaw Skill
1. Wrap Python class in shell scripts for exec() calls
2. Add autonomous modes (obstacle avoid, follow, explore)
3. Integrate camera stream analysis
4. Build safety wrappers (collision avoidance)
5. Create conversational interface ("drive forward", "look around", etc.)

## For Future Reference
**Problem:** Motors didn't move with single commands  
**Solution:** Send commands continuously at 10Hz (Arduino mode system requirement)  
**How we found it:** Examined AnimaNet working code, noticed continuous sending in background loop
