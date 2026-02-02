# 🎮 GalaxyRVR Quick Reference

## One-Line Commands

```bash
cd ~/.openclaw/workspace/skills/galaxyrvr

# Quick health check
python3 status.py

# System test (safe on tissue box)
./test_all_systems.sh

# Manual keyboard driving (WASD)
python3 keyboard_control.py

# What does rover see?
python3 vision.py

# Check battery
python3 battery_alert.py --once

# View latest map
python3 map_viewer.py

# List all saved maps  
python3 map_viewer.py --list

# Autonomous exploration (GROUND ONLY!)
python3 autonomous_explorer.py --duration 30
```

## File Purposes

| File | Purpose | Safe on Tissue Box? |
|------|---------|---------------------|
| `status.py` | Quick health check | ✅ Yes |
| `test_all_systems.sh` | Full system test | ✅ Yes |
| `keyboard_control.py` | Manual WASD driving | ⚠️ No - drives motors |
| `rover_control.py` | Control demo | ⚠️ No - drives motors |
| `vision.py` | Vision test | ✅ Yes |
| `battery_alert.py` | Battery check | ✅ Yes |
| `monitor.py` | Live sensor dashboard | ✅ Yes |
| `calibrate.py` | Odometry calibration | ⚠️ No - drives motors |
| `mapping.py` | Mapping demo | ✅ Yes (simulation) |
| `map_viewer.py` | View saved maps | ✅ Yes |
| `autonomous_explorer.py` | Full autonomy | ⚠️ No - drives motors |

## Keyboard Control Keys

```
W/S     - Forward/Backward
A/D     - Turn Left/Right  
Q/E     - Camera Up/Down
L       - Toggle Lamp
+/-     - Speed Up/Down
SPACE   - Stop
X       - Exit
```

## Current Status

- **Rover**: GalaxyRVR at 192.168.10.118
- **Camera**: http://192.168.10.118:9000/mjpg
- **Location**: Tissue box (charging)
- **Battery**: Check with `python3 status.py`
- **WiFi**: Usually -55dBm to -65dBm (good)

## Safety Reminders

🔴 **DO NOT RUN ON TISSUE BOX:**
- `keyboard_control.py`
- `autonomous_explorer.py`
- `calibrate.py`
- Any script that drives motors

✅ **SAFE ON TISSUE BOX:**
- All read-only scripts
- Vision tests
- Battery checks
- Map viewing
- System tests

## When Ready for Ground Testing

1. Clear Samoyed-free zone
2. Place rover on flat floor
3. Start with short duration:
   ```bash
   python3 autonomous_explorer.py --duration 10
   ```
4. Observe behavior
5. Increase duration as confidence builds

## Emergency Stop

- **Keyboard control**: Press SPACE or X
- **Autonomous**: Press Ctrl+C
- **Physical**: Power off rover

## Troubleshooting

**"Failed to connect"**
- Check rover is powered on
- Verify on same WiFi network
- Ping 192.168.10.118

**"Battery 0.00V"**
- Rover might be charging (sensor unreliable during charge)
- Wait 30 seconds after unplugging to get accurate reading

**"Vision timeout"**
- Ollama might be slow (~7s is normal)
- Check `ollama list` shows llava:7b

**"Map not found"**
- Maps saved to /tmp/rover_map_*.json
- Use `python3 map_viewer.py --list` to find them

## Cost Tracking

**Total spent on this project:** $0.00  
**Ongoing API costs:** $0.00  
**Value created:** Priceless 🤖

---

**Quick help:** `cat README.md`  
**Full summary:** `cat PROJECT_SUMMARY.md`
