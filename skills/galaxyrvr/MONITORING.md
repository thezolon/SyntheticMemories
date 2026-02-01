# GalaxyRVR Monitoring Tools

Complete monitoring suite for the SunFounder GalaxyRVR Mars rover.

## Tools

### 1. Basic Sensor Monitor (`monitor.py`)
Real-time sensor dashboard showing battery, IR sensors, and ultrasonic distance.

```bash
# Live dashboard
python3 monitor.py

# Quick status check
python3 monitor.py --once
```

### 2. Charge State Monitor (`charge_monitor.py`)
Detects charging state by analyzing battery voltage trends over time.

```bash
# Monitor for 2 minutes
python3 charge_monitor.py --duration 120

# Monitor for 5 minutes (more accurate)
python3 charge_monitor.py --duration 300
```

**Charge States Detected:**
- 🔌 AC adapter charging (bright LED, >+5mV/min)
- ☀️ Solar charging (dim LED, +1-5mV/min)
- ⚡ Idle (stable, ±1mV/min)
- 📉 Light discharge (-1 to -5mV/min)
- 🔋 Active discharge (<-5mV/min)

### 3. Battery Alert System (`battery_alert.py`)
Monitors battery and alerts when low, with smart offline detection.

```bash
# Check once
python3 battery_alert.py --once

# Continuous monitoring (checks every 5 minutes)
python3 battery_alert.py --interval 300

# Custom thresholds
python3 battery_alert.py --critical 6.3 --low 6.8
```

**Features:**
- ✅ Detects low battery (default: <7.0V warning, <6.5V critical)
- ✅ Smart offline detection (won't alert if rover is powered off)
- ✅ Only alerts on status changes (no spam)
- ✅ Tracks last seen time when offline

**Background Service:**
```bash
# Start as background process
./start_battery_monitor.sh &

# Or run in tmux/screen
tmux new -d -s rover-battery "./start_battery_monitor.sh"
```

## Battery Information

**Type:** 2S LiPo (7.4V nominal, 8.4V full, 6.0V empty)

**Voltage Guide:**
- 8.4V - 100% (fully charged)
- 7.4V - 50% (nominal)
- 7.0V - 20% (low, charge soon) ⚠️
- 6.5V - 5% (critical, charge now) 🔴
- 6.0V - 0% (empty, damage risk)

**Current Status (Solar Only):**
- ☀️ Solar panel provides some charge but NOT enough for idle power
- 🔌 Rover needs periodic AC charging to maintain battery
- 📉 Indoor/winter sun: -20 to -80mV/min discharge rate
- ☀️ Bright outdoor sun: May achieve +1-5mV/min (slow charge)

## Future Enhancements (Pi Zero 2W Integration)

When you add the Pi Zero 2W + 5G hotspot:
- More sensors (GPS, IMU, better camera)
- Always-online monitoring (via 5G)
- Remote access anywhere
- Advanced autonomous navigation
- Data logging and telemetry

## Notes

- **ADC Noise:** Battery voltage readings can fluctuate ±150mV due to Arduino's 10-bit ADC
- **Monitoring Duration:** For accurate charge state detection, monitor for 1-2 minutes minimum
- **Offline Detection:** Battery monitor only alerts when rover is online and battery is low
- **Solar Panel:** Helps extend runtime but is not a primary power source in current conditions
