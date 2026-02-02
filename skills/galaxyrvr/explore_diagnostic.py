#!/usr/bin/env python3
"""
Diagnostic exploration run with sensor logging
"""

import asyncio
import sys
import json
from datetime import datetime
sys.path.insert(0, '.')
from rover_control import GalaxyRVR

async def exploration_with_sensors():
    rover = GalaxyRVR()
    await rover.connect()
    
    log = []
    
    print('=== Starting Diagnostic Exploration ===\n')
    
    # Helper to log current state
    def log_state(label, moving=False):
        sensors = rover.get_sensors()
        entry = {
            'time': datetime.now().isoformat(),
            'label': label,
            'moving': moving,
            'sensors': sensors
        }
        log.append(entry)
        print(f'[{label}] Battery: {sensors.get("battery_voltage", 0):.2f}V, '
              f'Distance: {sensors.get("ultrasonic_cm", 0):.1f}cm, '
              f'IR: L={sensors.get("ir_left", 0)} R={sensors.get("ir_right", 0)}')
        return sensors
    
    # Baseline
    await asyncio.sleep(0.5)
    log_state('BASELINE')
    print()
    
    # Forward exploration
    print('Moving forward (3s)...')
    rover.forward(speed=100)
    for i in range(6):
        await asyncio.sleep(0.5)
        log_state(f'FORWARD_t{i*0.5:.1f}', moving=True)
    rover.stop()
    await asyncio.sleep(0.5)
    sensors = log_state('FORWARD_END')
    print()
    
    # Check what's ahead
    distance_ahead = sensors.get('ultrasonic_cm', 999)
    print(f'Object ahead: {distance_ahead:.1f}cm')
    
    if distance_ahead < 40:
        print('Too close! Backing up...')
        rover.backward(speed=100)
        await asyncio.sleep(1.5)
        rover.stop()
        await asyncio.sleep(0.5)
        log_state('BACKUP_END')
        print()
    
    # Rotate to explore
    print('Rotating right to scan area...')
    rover.turn_right(speed=100)
    await asyncio.sleep(1.2)  # ~90 degree turn
    rover.stop()
    await asyncio.sleep(0.5)
    log_state('ROTATE_90')
    print()
    
    # Another forward exploration
    print('Moving forward in new direction (2s)...')
    rover.forward(speed=100)
    await asyncio.sleep(2.0)
    rover.stop()
    await asyncio.sleep(0.5)
    log_state('EXPLORE2_END')
    print()
    
    # Return to start
    print('Returning to start position...')
    rover.backward(speed=100)
    await asyncio.sleep(2.0)
    rover.stop()
    rover.turn_left(speed=100)
    await asyncio.sleep(1.2)
    rover.stop()
    rover.backward(speed=100)
    await asyncio.sleep(3.0)
    rover.stop()
    await asyncio.sleep(0.5)
    log_state('RETURN_HOME')
    print()
    
    await rover.disconnect()
    
    # Save log
    log_file = f'/tmp/rover_exploration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(log_file, 'w') as f:
        json.dump(log, f, indent=2)
    
    print(f'=== Exploration Complete ===')
    print(f'Log saved to: {log_file}')
    print(f'Total waypoints: {len(log)}')
    
    # Summary
    print('\n=== Sensor Summary ===')
    battery_readings = [e['sensors'].get('battery_voltage', 0) for e in log if e['sensors'].get('battery_voltage')]
    if battery_readings:
        print(f'Battery: {min(battery_readings):.2f}V - {max(battery_readings):.2f}V (avg: {sum(battery_readings)/len(battery_readings):.2f}V)')
    
    distances = [e['sensors'].get('ultrasonic_cm', 0) for e in log if e['sensors'].get('ultrasonic_cm')]
    if distances:
        print(f'Distance range: {min(distances):.1f}cm - {max(distances):.1f}cm')
    
    ir_events = sum(1 for e in log if e['sensors'].get('ir_left', 0) == 1 or e['sensors'].get('ir_right', 0) == 1)
    print(f'IR obstacle detections: {ir_events}')

asyncio.run(exploration_with_sensors())
