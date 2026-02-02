# GalaxyRVR Rover - Discovery Notes
*2026-02-01*

## Hardware
- **Model:** SunFounder GalaxyRVR Mars Rover Kit
- **Controller:** Arduino R3 + GalaxyRVR Shield
- **Camera:** ESP32-CAM (firmware v1.4.0)
- **Network:** WiFi (ESP32), currently on 192.168.10.118
- **MAC:** 8c:4f:00:ac:75:20
- **Hostname:** esp32-AC7520

## Current Status
✅ **ONLINE AND OPERATIONAL**

### Active Services
1. **HTTP Web Interface** (Port 80)
   - OTA firmware update page
   - Access: http://192.168.10.118

2. **WebSocket Server** (Port 8765)
   - Real-time control interface
   - Used by SunFounder Controller app
   - Protocol: WS (not raw HTTP)

3. **Video Stream** (Port 9000)
   - Live MJPEG stream from ESP32-CAM
   - URL: http://192.168.10.118:9000/mjpg
   - Format: Motion JPEG (multipart HTTP stream)

## Control Architecture

### SunFounder Controller App
- Mobile app (iOS/Android)
- Connects via WebSocket to port 8765
- Visual widgets map to control regions (A-Q)
- Supports both control (input) and display (output) widgets

### Widget Types Used (from docs)
**Control widgets:**
- Joystick (movement control)
- Throttle (motor power, dual for tank-style steering)
- Slider (servo/tilt control)
- Button (discrete commands)
- Microphone (voice control)

**Display widgets:**
- Number (sensor readings)
- Gauge (speed, distance)
- Graph (data visualization)

### Communication Protocol
- **Inbound:** App sends widget values via WebSocket
- **Outbound:** Rover sends sensor data in JSON (`sendDoc[]` dictionary)
- **Video:** Separate MJPEG stream (port 9000)

## Hardware Components
- ESP32-CAM (camera + WiFi)
- Arduino R3 + GalaxyRVR Shield (motor control, sensors)
- TT Motors (4x for rocker-bogie suspension)
- Servo (camera tilt mechanism, 0-140°)
- Ultrasonic sensor (distance measurement)
- IR obstacle avoidance modules (left/right)
- RGB LED strip (4 LEDs)
- Solar panel (optional charging)
- 18650 batteries

## Code Examples from Docs

### Get widget values (in `onReceive()` callback):
```cpp
int16_t sliderD = aiCam.getSlider(REGION_D);
int throttle_L = aiCam.getThrottle(REGION_K);
int throttle_R = aiCam.getThrottle(REGION_Q);
int buttonA = aiCam.getButton(REGION_A);
```

### Send sensor data to app:
```cpp
aiCam.sendDoc["N"] = leftIRValue;
aiCam.sendDoc["P"] = rightIRValue;
aiCam.sendDoc["O"] = ultrasonicDistance;
```

### Motor control:
```cpp
void carSetMotors(int8_t power_L, int8_t power_R) {
  // power range: -100 to 100
  // negative = reverse, 0 = stop, positive = forward
  // Maps to PWM 0-255 via SoftPWM library
}
```

## Network Modes
The rover supports two WiFi modes (configured at compile time):

1. **AP Mode** (Access Point)
   - Creates hotspot: "GalaxyRVR" / password "12345678"
   - Controller device connects directly to rover
   - No internet access on connected device
   - Unlimited range (within WiFi signal)

2. **STA Mode** (Station)
   - Connects to home WiFi
   - Controller device must be on same network
   - Maintains internet access
   - Range limited to WiFi coverage

## Current Configuration
**Mode:** AP Mode (creates "GalaxyRVR" hotspot, password "12345678")  
**Connected to:** Home WiFi (192.168.10.x subnet in STA mode)

## Source Code Location
✅ **You already have the full source code!**
- **Path:** `/bulk/AnimaNet/galaxy-rvr-main/`
- **Main sketch:** `galaxy-rvr/galaxy-rvr.ino`
- **Version:** 1.1.0 (newer than what's on the rover - 1.4.0 is ESP32 firmware)

### Available Functions (from source)
**Motor Control:**
- `carForward(power)` - move forward (0-100)
- `carBackward(power)` - move backward (0-100) 
- `carTurnLeft(power)` - pivot left
- `carTurnRight(power)` - pivot right
- `carSetMotors(left, right)` - independent control (-100 to 100)
- `carStop()` - halt

**Sensors:**
- `irObstacleRead()` - returns byte (bit 0=right clear, bit 1=left clear)
- `ultrasonicRead()` - returns distance in cm (float)
- `batteryGetVoltage()` - returns battery voltage

**RGB LED:**
- `rgbWrite(color)` - set LED strip color
- `rgbOff()` - turn off LEDs
- Colors: RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE, ORANGE

**Servo:**
- `servo.write(angle)` - tilt camera (0-140°)

### Operating Modes (in source)
1. **MODE_NONE** - idle, stopped
2. **MODE_DISCONNECT** - no WebSocket connection (blinks LED)
3. **MODE_OBSTACLE_FOLLOWING** - follows objects via ultrasonic
4. **MODE_OBSTACLE_AVOIDANCE** - autonomous navigation
5. **MODE_APP_CONTROL** - manual control via SunFounder app
6. **MODE_VOICE_CONTROL** - speech commands

### WebSocket Data Exchange
**Sent to app (in `sendDoc`):**
- `BV` - battery voltage
- `N` - left IR (0=clear, 1=obstacle)
- `P` - right IR (0=clear, 1=obstacle)
- `O` - ultrasonic distance (cm)
- `J` - voice recognition status

**Received from app:**
- Region D - Slider (servo angle 0-140)
- Region E - Switch (obstacle avoidance mode)
- Region F - Switch (obstacle following mode)
- Region I - Button (emergency stop)
- Region J - Speech input
- Region K - Throttle (left motor)
- Region M - Switch (camera LED lamp)
- Region Q - Throttle (right motor)

## Next Steps for OpenClaw Integration

### Option 1: WebSocket Control (Native)
- Reverse-engineer the WebSocket protocol used by SunFounder app
- Send control commands directly via WS to port 8765
- Requires understanding the message format

### Option 2: Arduino Code Modification
- Flash custom firmware with REST API endpoints
- Add HTTP endpoints for:
  - `/move?left=X&right=Y` - motor control
  - `/servo?angle=X` - camera tilt
  - `/led?r=X&g=Y&b=Z` - RGB control
  - `/sensors` - read all sensor values (JSON)
- Keep video stream on 9000

### Option 3: Hybrid
- Keep existing SunFounder firmware for app control
- Add secondary HTTP API for programmatic access
- Use Arduino's multiple client support

## Safety Notes
⚠️ **CURRENTLY ON A SHELF** - DO NOT MOVE MOTORS YET
- Need to place on ground before any movement commands
- Test with low power values first
- Rocker-bogie system is designed for rough terrain but can still fall off edges

## Documentation
- Full docs: https://docs.sunfounder.com/projects/galaxy-rvr/en/latest/
- Widget reference: https://docs.sunfounder.com/projects/sf-controller/en/latest/widgets_list.html
- Library: https://github.com/sunfounder/SunFounder_AI_Camera

## Firmware Update Process
1. Switch toggle to RIGHT (disconnect ESP32 from Arduino RX/TX)
2. Upload code via Arduino IDE
3. Switch toggle to LEFT (reconnect, start ESP32)
4. Check Serial Monitor at 115200 baud for IP address
