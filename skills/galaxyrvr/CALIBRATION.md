# GalaxyRVR Movement Calibration

**Date:** 2026-02-01  
**Surface:** Indoor carpet (medium pile)  
**Reference:** Xbox game case (190mm width)  
**Camera setup:** Foscam external + ESP32-CAM onboard

## Speed-to-Distance Mapping

### Speed 100 (Recommended)
- **Linear speed:** ~23 cm/second
- **Reliable on carpet:** ✅ Yes
- **Consistency:** Good (±5cm over 2-3 seconds)

### Speed 70 (Not Recommended)
- **Linear speed:** ~2 cm/second (inconsistent)
- **Reliable on carpet:** ❌ No - insufficient torque to overcome static friction
- **Use case:** Fine positioning only (if any)

## Distance Formulas

### Forward/Backward Movement
```python
# Speed 100
distance_cm = duration_seconds * 23

# Example: Move 50cm forward
duration = 50 / 23  # = 2.17 seconds
rover.forward(speed=100)
await asyncio.sleep(duration)
rover.stop()
```

## Test Results

| Speed | Duration (s) | Distance (cm) | Notes |
|-------|-------------|---------------|-------|
| 70 | 1.0 | ~2 | Too low, unreliable |
| 100 | 3.0 | ~70 | Good |
| 100 | 2.0 | ~47 | Backward, good |

## Notes

- **Carpet friction:** High - requires speed ≥90 for consistent movement
- **Ramp-up time:** ~0.1-0.2s to reach full speed
- **Drift:** Minimal (<5cm over 3 seconds)
- **Measurement method:** Visual estimation using Xbox case (190mm) in dual-camera setup

## Rotation Calibration

*TODO: Test turn_left() and turn_right() for degrees-to-duration mapping*

## Surface Variations

- **Carpet (tested):** Speed 100 = 23 cm/s
- **Hard floor:** *Not yet tested - expect faster*
- **Tile:** *Not yet tested*

## Recommendations

1. **Default speed:** 100 for reliable movement
2. **Minimum duration:** 0.5s (accounts for ramp-up)
3. **Safety margin:** Add 10% to calculated duration for accuracy
4. **Surface check:** Re-calibrate if moving to different floor types
