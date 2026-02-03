#!/usr/bin/env python3
"""
GalaxyRVR Web Dashboard
Real-time rover control, monitoring, and map visualization
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
import asyncio
import json
import os
import glob
import base64
from io import BytesIO
from datetime import datetime
import threading
import sys

# Support running locally or in Docker
if os.path.exists('/app'):
    sys.path.insert(0, '/app')
else:
    sys.path.insert(0, os.path.dirname(__file__))

from rover_control import GalaxyRVR
from vision import RoverVision
from mapping import RoverMap
from battery_alert import BatteryAlert
from wifi_monitor import WiFiMonitor

# Configuration from environment
ROVER_IP = os.getenv('ROVER_IP', '192.168.10.118')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', '5050'))
MAP_DIR = os.getenv('MAP_DIR', '/app/maps' if os.path.exists('/app') else '/tmp')
LOG_DIR = os.getenv('LOG_DIR', '/app/logs' if os.path.exists('/app') else '/tmp')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'galaxyrvr-secret-2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global rover state
rover = None
rover_map = None
vision = None
battery = None
wifi = None
control_active = False
rover_loop = None
rover_thread = None

def run_rover_loop():
    """Run rover event loop in background thread"""
    global rover_loop
    rover_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(rover_loop)
    rover_loop.run_forever()

def get_or_create_rover():
    """Get global rover instance"""
    global rover, rover_loop, rover_thread
    if rover is None:
        rover = GalaxyRVR(host=ROVER_IP)
        
        # Start background event loop for rover
        if rover_thread is None:
            rover_thread = threading.Thread(target=run_rover_loop, daemon=True)
            rover_thread.start()
            
    return rover

def get_or_create_map():
    """Get or create global map"""
    global rover_map
    if rover_map is None:
        # Try to load most recent map
        maps = glob.glob(f"{MAP_DIR}/rover_map_*.json")
        if maps:
            latest = max(maps, key=os.path.getmtime)
            rover_map = RoverMap.load_map(latest)
            print(f"Loaded map: {latest}")
        else:
            rover_map = RoverMap(grid_size_meters=5.0, cell_size_cm=10)
            print("Created new map")
    return rover_map

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def status():
    """Get rover status"""
    try:
        r = get_or_create_rover()
        
        # Check if already connected, otherwise connect once
        if not r.connected:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            connected = loop.run_until_complete(r.connect())
            loop.close()
            
            if not connected:
                return jsonify({"connected": False, "error": "Failed to connect"})
        
        sensors = r.get_sensors()
        
        # WiFi
        w = WiFiMonitor()
        wifi_signal = w.get_signal_strength()
        
        # Battery status
        battery_v = sensors['battery_voltage']
        if battery_v > 0:
            battery_pct = int(((battery_v - 6.0) / 2.4) * 100)
            if battery_v < 6.5:
                battery_status = "critical"
            elif battery_v < 7.0:
                battery_status = "low"
            else:
                battery_status = "good"
        else:
            battery_pct = 0
            battery_status = "unknown"
        
        return jsonify({
            "connected": r.connected,
            "battery": {
                "voltage": battery_v,
                "percent": battery_pct,
                "status": battery_status
            },
            "sensors": {
                "ultrasonic_cm": sensors['ultrasonic_cm'],
                "ir_left": sensors['ir_left'],
                "ir_right": sensors['ir_right']
            },
            "wifi": {
                "signal_dbm": wifi_signal,
                "quality": w.get_signal_quality()
            }
        })
    except Exception as e:
        return jsonify({"connected": False, "error": str(e)})

@app.route('/api/camera/snapshot')
def camera_snapshot():
    """Get current camera view"""
    try:
        import requests
        camera_url = f"http://{ROVER_IP}:9000/mjpg"
        response = requests.get(camera_url, stream=True, timeout=5)
        
        # Read one frame from MJPEG stream
        for chunk in response.iter_content(chunk_size=1024):
            if b'\xff\xd8' in chunk:  # JPEG start
                frame_data = b''
                frame_data += chunk.split(b'\xff\xd8')[1]
                
                for chunk2 in response.iter_content(chunk_size=1024):
                    frame_data += chunk2
                    if b'\xff\xd9' in chunk2:  # JPEG end
                        frame_data = frame_data.split(b'\xff\xd9')[0]
                        frame = b'\xff\xd8' + frame_data + b'\xff\xd9'
                        
                        return send_file(
                            BytesIO(frame),
                            mimetype='image/jpeg'
                        )
        
        return jsonify({"error": "No frame"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/maps/list')
def list_maps():
    """List all saved maps"""
    maps = glob.glob(f"{MAP_DIR}/rover_map_*.json")
    map_list = []
    
    for map_file in sorted(maps, reverse=True):
        try:
            with open(map_file) as f:
                data = json.load(f)
            
            stats = data.get('statistics', {})
            timestamp = os.path.basename(map_file).replace('rover_map_', '').replace('.json', '')
            
            map_list.append({
                "filename": map_file,
                "timestamp": timestamp,
                "distance_m": stats.get('distance_traveled_m', 0),
                "explored_pct": stats.get('explored_percent', 0),
                "scans": stats.get('scan_count', 0)
            })
        except:
            pass
    
    return jsonify({"maps": map_list})

@app.route('/api/maps/current')
def current_map():
    """Get current/loaded map data"""
    try:
        m = get_or_create_map()
        stats = m.get_statistics()
        
        # Convert grid to simple format
        grid_data = []
        for y in range(0, m.grid_cells, 2):  # Downsample for web
            row = []
            for x in range(0, m.grid_cells, 2):
                cell_val = m.grid[y][x]
                wifi_val = m.wifi_grid[y][x]
                row.append({
                    "occupancy": cell_val,
                    "wifi": wifi_val
                })
            grid_data.append(row)
        
        return jsonify({
            "rover_position": {
                "x": m.rover_x,
                "y": m.rover_y,
                "heading": m.rover_heading
            },
            "grid": grid_data,
            "stats": stats,
            "grid_size_m": m.grid_size_meters,
            "cell_size_cm": m.cell_size_cm
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/maps/load', methods=['POST'])
def load_map():
    """Load a specific map"""
    global rover_map
    
    data = request.json
    map_file = data.get('filename')
    
    try:
        rover_map = RoverMap.load_map(map_file)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print('Client connected')
    emit('status', {'connected': True})

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print('Client disconnected')
    global control_active
    control_active = False

@socketio.on('control')
def handle_control(data):
    """Handle control commands"""
    global control_active, rover_loop
    
    command = data.get('command')
    speed = data.get('speed', 50)
    
    try:
        r = get_or_create_rover()
        
        # Connect if needed (run in background loop)
        if not control_active or not r.connected:
            future = asyncio.run_coroutine_threadsafe(r.connect(), rover_loop)
            connected = future.result(timeout=5)
            if connected:
                control_active = True
            else:
                emit('control_response', {'success': False, 'error': 'Failed to connect to rover'})
                return
        
        # Execute command (synchronous motor setters)
        if command == 'forward':
            r.forward(speed)
        elif command == 'backward':
            r.backward(speed)
        elif command == 'left':
            r.turn_left(speed)
        elif command == 'right':
            r.turn_right(speed)
        elif command == 'stop':
            r.stop()
        elif command == 'servo':
            angle = data.get('angle', 90)
            r.set_servo(angle)
        elif command == 'lamp':
            state = data.get('state', 0)
            r.set_lamp(state)
        
        emit('control_response', {'success': True, 'command': command})
    except Exception as e:
        emit('control_response', {'success': False, 'error': str(e)})

def run_server(host='0.0.0.0', port=None):
    """Start web server"""
    if port is None:
        port = DASHBOARD_PORT
    
    print(f"\n🌐 GalaxyRVR Web Dashboard")
    print("=" * 60)
    print(f"Rover IP: {ROVER_IP}")
    print(f"Map directory: {MAP_DIR}")
    print(f"Starting server on http://{host}:{port}")
    print()
    print("Open in your browser:")
    print(f"  http://localhost:{port}")
    print(f"  http://192.168.10.X:{port}  (from other devices)")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    run_server()
