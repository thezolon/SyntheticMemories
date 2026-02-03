# Rover Upgrade Options & Planning

## Mission Statement
Build outdoor patrol rover that can drive around property autonomously and return to charging dock. Multi-hour runtime required. Dog-proof (Samoyeds).

## Development Philosophy
**Iterative approach** - Start small, test cheap, scale up:
1. **Phase 1:** GalaxyRVR (current) - learning platform, prove concepts
2. **Phase 2:** Small tracked chassis - intermediate testing
3. **Phase 3:** Large outdoor rover - final platform

## Current Platform: GalaxyRVR

### Hardware Specs
- **Motors:** 6× TT motors (one per wheel), wired in 2 groups of 3
  - Right side: 3 motors parallel on pins 2 & 3
  - Left side: 3 motors parallel on pins 4 & 5
  - Total draw: ~3-6A under load (6 motors × 0.5-1A each)
- **Suspension:** Rocker-bogie system (NASA Mars rover style)
- **Controller:** Arduino R3 + GalaxyRVR Shield
- **Computer:** Raspberry Pi Zero 2W (0.8A typical, 1.2A peak)
- **Camera:** ESP32-CAM with tilt servo (pin 6)
- **Sensors:** 
  - Ultrasonic (pin 10)
  - IR obstacle avoidance left (pin 8) & right (pin 7)
  - RGB LED strips (pins 11, 12, 13)
- **Battery:** 7.4V 2S LiPo (~2600mAh typical)
- **Shield Features:**
  - Built-in motor drivers (H-bridge)
  - Built-in battery charging (USB-C, 130min charge time)
  - Solar panel input
  - All sensors pre-wired via XH/ZH connectors

### Current Limitations
- No wheel encoders = time-based distance guessing (accumulates error)
- Arduino bottleneck for direct sensor access from Pi
- ~45 minute runtime on single battery

### Control Architecture (Current)
```
Raspberry Pi Zero 2W (powered by USB bank)
    ↓ USB Serial
Arduino R3 (powered by rover battery)
    ↓ Shield
6× TT Motors (3 left, 3 right) + Servo + Sensors
```

## Available Resources

### Batteries (Already Owned)
**ExpertPower LiFePO4 (from ham radio setup):**
- **20Ah (EP1220):** 12.8V, 5 lbs, 7.1×3×6.6", 10A max discharge, 2500-7000 cycles
- **10Ah (EP1210):** 12.8V, 2.7 lbs, 6×2.6×3.7", ~5A max discharge, 2500-7000 cycles
- Both have built-in BMS, safe auto-charging capability
- **Issue:** Too large for small tracked chassis (would need external mount or bigger platform)

**Use case:** Save for Phase 3 (large outdoor rover)

### Flight Controllers (Already Owned)
**30+ FPV drone flight controllers** (F4/F7/H7 including GOKU F411 stacks)

**Advantages over Arduino:**
- Built-in IMU (gyro + accel)
- 5V BEC (powers Pi + sensors)
- Current sensor (battery monitoring)
- Multiple UARTs (GPS, telemetry, ELRS)
- Native encoder support
- ArduRover firmware (ground vehicle optimized)
- Full RC integration (TX16 + ELRS)
- Better motor control (PID loops)

**Integration Options:**
1. **Keep shield, replace Arduino:** FC outputs PWM → Shield drivers → Motors (simplest)
2. **Full FC stack:** Remove shield, FC → 4-in-1 ESC → Motors directly (cleaner but more work)

**Use case:** Future upgrade once basic concepts proven

### Radio Control
- RadioMaster TX16 with ELRS/Crossfire
- Full RC control + telemetry capability
- 1-10km range, <5ms latency

## Immediate Upgrades (Minimal Cost)

### 1. Wheel Encoders (~$8)
**Hardware:** 2× LM393 optical speed sensors with 20-slot encoder discs
- Mount on rear wheels (or front wheels)
- Wire to Pi GPIO or Arduino analog pins
- Real distance measurement vs time-based guessing
- Detect wheel slip/drift

**Shopping:** Amazon search "LM393 speed sensor encoder disc"

**Benefit:** Eliminates dead reckoning error, essential for return-to-home

### 2. Pi Power via USB Bank (~$0-15)
**Solution:** Small 5000mAh USB power bank
- Powers Pi Zero 2W independently (6+ hours runtime)
- Rover battery powers motors/Arduino/sensors (45 min)
- USB cable Pi→Arduino enables OTA firmware updates

**Bonus:** Can SSH to rover and flash Arduino via `arduino-cli`

**Shopping:** Anker PowerCore 5000 or similar (5V 2A output)

### 3. GPS Module (~$30, optional)
**For outdoor navigation:**
- Return-to-home waypoints
- Position logging
- Geo-fencing

**Use case:** Phase 2/3 (outdoor missions)

## Future Chassis Options

### Small: XiaoR Geek Tank Chassis (~$60)
- **Size:** 300×230×124mm (11.8" × 9" × 4.9")
- **Motors:** 2× geared motors with encoders (6-12V)
- **Pros:** Affordable, suspension, encoder motors included
- **Cons:** Too small for LiFePO4 batteries (would need top-mount)
- **Use case:** Phase 2 testing with smaller battery or 18650 pack

### Medium: RC Rock Crawler Conversion (~$200-250)
- **Examples:** Axial SCX10, Traxxas TRX-4 (1/10 scale)
- **Pros:** Built for outdoor abuse, waterproof, fits large batteries, all-terrain
- **Cons:** Need to replace RC electronics with FC + Pi
- **Use case:** Phase 3 (outdoor patrol rover)

### Large: SuperDroid IG52-DB4 (~$600-800)
- **Professional robot platform**
- 4× IG52 motors with encoders
- 10" pneumatic wheels
- Designed for 12V 18-20Ah batteries (perfect for LiFePO4!)
- 50+ lb payload capacity
- **Use case:** If budget allows, ultimate platform

### DIY: Custom 80/20 Aluminum Frame (~$250-300)
- Maximum flexibility
- Built around your specific battery size
- 4× wheelchair/scooter motors
- 10" pneumatic wheels
- **Use case:** If you enjoy fabrication

## Power Architecture Options

### Current (Phase 1)
```
7.4V LiPo → Arduino Shield → Motors
USB Bank → Pi Zero 2W
```
**Runtime:** Pi 6+ hrs, motors 45 min

### Future Small Chassis (Phase 2)
```
10Ah LiFePO4 → Buck (5V) → Pi + Sensors
             → Motor Driver → Motors
```
**Runtime:** 1-1.5 hours

### Future Large Chassis (Phase 3)
```
20Ah LiFePO4 → Buck (5V 5A) → Pi + Peripherals
             → ESC/Motor Driver → Motors
```
**Runtime:** 3+ hours

### Dual Battery (Ultimate)
```
20Ah LiFePO4 #1 ──┐
20Ah LiFePO4 #2 ──┤→ Y-harness → Power Distribution
                  
30Ah combined, 15A discharge, 4+ hour runtime
```

## Auto-Charging Dock Ideas

### Components
- Magnetic pogo pin connectors (auto-align)
- 12V charger with LFP profile (14.4V charge, 13.8V float)
- Vision markers or IR beacons for docking guidance
- Contact sensors to verify connection

### Docking Approach
1. Visual navigation to dock vicinity (camera + markers)
2. Final approach using contact sensors
3. Magnetic alignment (pogo pins snap into place)
4. BMS manages charging automatically

## Software Stack Options

### Current
- Python control script (`rover_control.py`)
- Direct HTTP commands to ESP32-CAM
- 10Hz continuous command loop required

### With Encoders
- Odometry feedback loop
- Dead reckoning with error correction
- Real-time position tracking

### With Flight Controller
- ArduRover firmware (skid-steer mode)
- MAVLink protocol (Pi ↔ FC)
- Waypoint navigation
- GPS integration
- Failsafe modes (return-to-home)

### With Vision
- OpenCV lane following
- AprilTag dock markers
- Visual odometry (camera-based position)
- Obstacle detection via depth perception

## Cost Summary

| Upgrade | Phase | Cost | Benefit |
|---------|-------|------|---------|
| **Wheel encoders** | 1 | ~$8 | Real odometry ✅✅✅ |
| **USB power bank** | 1 | ~$15 | Pi independence ✅ |
| **GPS module** | 2 | ~$30 | Waypoints, RTH ✅ |
| **Small tracked chassis** | 2 | ~$60 | Testing platform ✅ |
| **18650 battery pack (DIY)** | 2 | ~$145 | Internal mount ✅ |
| **RC rock crawler** | 3 | ~$200 | Outdoor capable ✅✅ |
| **Flight controller swap** | 2-3 | $0 | Advanced control ✅✅ |
| **SuperDroid platform** | 3 | ~$700 | Professional grade ✅✅✅ |

## Decision: Current Path Forward

**KEEP IT SIMPLE FOR NOW:**
1. **Use GalaxyRVR as-is** (Arduino + Shield + current motors)
2. **Add wheel encoders only** (~$8) for real odometry
3. **Use USB power bank for Pi** (check existing inventory)
4. **Master the basics:** navigation, obstacle avoidance, sensor fusion
5. **Once software is proven:** Then upgrade hardware

**Why:** Avoid getting overwhelmed. Focus on learning and iterating. Hardware is easy to swap later once you know what works.

## Next Immediate Steps

1. Order LM393 wheel encoder kit (~$8)
2. Find suitable USB power bank in existing inventory
3. Mount encoders on GalaxyRVR wheels
4. Write encoder integration code
5. Test improved odometry on carpet
6. Continue calibration work (rotation, precision movement)

---

**Remember:** The goal is to build incrementally. Each phase teaches lessons for the next. Don't over-engineer before you've proven the fundamentals.
