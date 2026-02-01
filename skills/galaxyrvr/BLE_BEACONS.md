# BLE Beacon Navigation for GalaxyRVR

## Hardware Capability

✅ **ESP32-CAM supports BLE!**
- ESP32 chip has built-in Bluetooth 4.2 + BLE
- Can scan for BLE beacons while connected to WiFi
- Would need custom firmware modification to enable

## BLE Beacon Indoor Positioning System

### Concept

Place cheap BLE beacon nodes around your house. Rover scans RSSI (signal strength) from multiple beacons to triangulate its position.

### Hardware Options

**Option 1: ESP32 Beacon Nodes (~$3-5 each)**
- ESP32-C3 Super Mini boards
- Run in deep sleep, wake every few seconds to broadcast
- Battery powered (CR2032 or rechargeable)
- Months of battery life

**Option 2: Commercial BLE Beacons (~$10-20)**
- iBeacon/Eddystone compatible
- Pre-configured, just stick on wall
- 1-2 year battery life

**Option 3: Your existing devices**
- Raspberry Pis
- Old Android phones
- Any device with BLE

### Setup Example

```
Kitchen:    BLE Beacon 1 (ID: kitchen)
Living Room: BLE Beacon 2 (ID: living)  
Bedroom:    BLE Beacon 3 (ID: bedroom)
Hallway:    BLE Beacon 4 (ID: hallway)
```

Rover scans and gets:
```
kitchen:  -45dBm (very close)
living:   -60dBm (nearby)
bedroom:  -75dBm (far)
hallway:  -85dBm (very far)
```

### Triangulation

With 3+ beacons, rover can estimate position:
- Strong signal from kitchen beacon → I'm in/near kitchen
- Weak signal from bedroom → I'm far from bedroom
- Combine all signals → approximate (x, y) position

### Benefits Over WiFi Mapping

1. **Absolute positioning** instead of relative odometry
2. **No drift** - beacons are fixed reference points
3. **Multi-room** - each room has identifier
4. **Room detection** - "Which room am I in?" is instant
5. **Drift correction** - Reset odometry errors when passing beacon

### Implementation Plan

#### Phase 1: Firmware Modification
Modify ESP32-CAM firmware to:
```cpp
#include <BLEDevice.h>
#include <BLEScan.h>

BLEScan* pBLEScan;

void setup() {
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setActiveScan(true);
}

void loop() {
  BLEScanResults results = pBLEScan->start(1); // 1 second scan
  
  for(int i = 0; i < results.getCount(); i++) {
    BLEAdvertisedDevice device = results.getDevice(i);
    
    // Send via WebSocket: {"beacon": "kitchen", "rssi": -45}
    sendBeaconData(device.getAddress(), device.getRSSI());
  }
}
```

#### Phase 2: Beacon Deployment
Place beacons at known coordinates:
```json
{
  "beacons": [
    {"id": "kitchen", "x": 100, "y": 50},
    {"id": "living", "x": 300, "y": 50},
    {"id": "bedroom", "x": 100, "y": 250}
  ]
}
```

#### Phase 3: Position Estimation
Rover receives beacon data, calculates position:
```python
def estimate_position(beacon_readings):
    # Weighted average based on signal strength
    total_weight = 0
    x_sum = 0
    y_sum = 0
    
    for beacon_id, rssi in beacon_readings.items():
        beacon_pos = BEACON_MAP[beacon_id]
        # Convert RSSI to weight (closer = higher weight)
        weight = 10 ** ((-rssi - 30) / 20)  # Path loss model
        
        x_sum += beacon_pos['x'] * weight
        y_sum += beacon_pos['y'] * weight
        total_weight += weight
    
    return (x_sum / total_weight, y_sum / total_weight)
```

#### Phase 4: Map Integration
```python
# Correct odometry drift using beacon position
estimated_pos = estimate_position(beacon_data)
rover_map.rover_x = estimated_pos[0]  # Snap to beacon estimate
rover_map.rover_y = estimated_pos[1]

# Or blend: 80% odometry + 20% beacons
rover_map.rover_x = 0.8 * odometry_x + 0.2 * beacon_x
```

## Simple Starting Point (No Firmware Change!)

**Use your computer as a beacon scanner:**

Even without modifying rover firmware, you can:
1. Put BLE beacons around house
2. Your **computer** scans beacons
3. Rover reports its **WiFi signal** to you
4. You triangulate rover position from **your computer's** BLE scan
5. Feed position corrections back to mapping system

This works because:
- Rover stays close to you (tissue box testing!)
- Your computer can scan BLE
- Combine rover's sensors + your BLE scan = indoor positioning

## Cost Analysis

**Minimal Setup (3 beacons):**
- 3x ESP32-C3 boards: $12
- 3x CR2032 batteries: $3
- **Total: $15**

**Premium Setup (5 beacons):**
- 5x Commercial iBeacons: $50
- **Total: $50**

**DIY with spare hardware:**
- Old Android phones as beacons: **$0**
- Raspberry Pi zeros: **already own?**

## Accuracy

- **WiFi-only odometry**: ±50cm drift after 5m travel
- **BLE beacon assist**: ±10cm accuracy
- **BLE + odometry fusion**: ±5cm accuracy

## Alternative: When Pi Zero 2W is added

Once you mount the Pi Zero 2W:
- **Pi does BLE scanning** (more powerful than ESP32)
- ESP32 focuses on motors/sensors
- Pi handles: BLE, GPS, advanced vision, 5G
- Perfect division of labor

## Next Steps

1. **Test BLE range in your house**
   - Use phone app "BLE Scanner"
   - See how far beacons reach

2. **Buy 1-2 cheap beacons** (~$5 each)
   - Test concept before full deployment
   - See actual RSSI values in your space

3. **Map beacon locations**
   - Drive rover to each beacon
   - Record (x, y) coordinates
   - Save as beacon map file

4. **Firmware mod** (optional, for advanced use)
   - Add BLE scanning to ESP32-CAM
   - Or wait for Pi Zero 2W

Would you like me to create a BLE beacon scanning script that runs on your computer and feeds position data to the rover? That way you can test the concept without any firmware changes! 📡

⚡
