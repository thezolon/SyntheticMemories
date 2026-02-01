#!/usr/bin/env python3
"""
GalaxyRVR Control Skill - Working Version
Continuous command sending at 10Hz to maintain control mode
"""

import asyncio
import websockets
import json
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class GalaxyRVR:
    def __init__(self, host="192.168.10.118", port=8765):
        self.host = host
        self.port = port
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.running = False
        
        # Current command state
        self.motor_left = 0
        self.motor_right = 0
        self.servo_angle = 90
        self.lamp_on = False
        
        # Sensor data
        self.sensors = {
            "battery_voltage": 0.0,
            "ir_left": 0,
            "ir_right": 0,
            "ultrasonic_cm": 0.0
        }
        
        # Background tasks
        self._send_task: Optional[asyncio.Task] = None
        self._receive_task: Optional[asyncio.Task] = None
        
    async def connect(self) -> bool:
        """Connect to rover"""
        try:
            uri = f"ws://{self.host}:{self.port}"
            logger.info(f"Connecting to {uri}...")
            
            self.ws = await websockets.connect(uri, ping_interval=None)
            
            # Wait for handshake
            handshake = await self.ws.recv()
            logger.info(f"Connected! Handshake: {handshake}")
            
            self.connected = True
            self.running = True
            
            # Start background tasks
            self._send_task = asyncio.create_task(self._send_loop())
            self._receive_task = asyncio.create_task(self._receive_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect and stop"""
        self.running = False
        
        # Stop motors first
        self.motor_left = 0
        self.motor_right = 0
        await asyncio.sleep(0.2)
        
        # Cancel tasks
        if self._send_task:
            self._send_task.cancel()
            try:
                await self._send_task
            except asyncio.CancelledError:
                pass
        
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket
        if self.ws:
            await self.ws.close()
            self.ws = None
        
        self.connected = False
        logger.info("Disconnected")
    
    async def _send_loop(self):
        """Send commands continuously at 10Hz"""
        while self.running and self.ws:
            try:
                cmd = {
                    "K": self.motor_left,
                    "Q": self.motor_right,
                    "D": self.servo_angle
                }
                
                # Add lamp if needed
                if hasattr(self, '_lamp_changed'):
                    cmd["M"] = 1 if self.lamp_on else 0
                    delattr(self, '_lamp_changed')
                
                await self.ws.send(json.dumps(cmd))
                await asyncio.sleep(0.1)  # 10Hz
                
            except Exception as e:
                if self.running:
                    logger.error(f"Send error: {e}")
                break
    
    async def _receive_loop(self):
        """Receive sensor data"""
        while self.running and self.ws:
            try:
                msg = await asyncio.wait_for(self.ws.recv(), timeout=0.5)
                
                # Skip pong messages
                if msg.startswith("pong"):
                    continue
                
                # Parse JSON sensor data
                try:
                    data = json.loads(msg)
                    if "BV" in data:
                        self.sensors["battery_voltage"] = data["BV"]
                    if "N" in data:
                        self.sensors["ir_left"] = data["N"]
                    if "P" in data:
                        self.sensors["ir_right"] = data["P"]
                    if "O" in data:
                        self.sensors["ultrasonic_cm"] = data["O"]
                except json.JSONDecodeError:
                    pass
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Receive error: {e}")
                break
    
    # ==================== Movement Commands ====================
    
    def set_motors(self, left: int, right: int):
        """
        Set motor power (-100 to 100)
        Changes take effect on next send cycle (~100ms)
        """
        self.motor_left = max(-100, min(100, left))
        self.motor_right = max(-100, min(100, right))
    
    def forward(self, speed: int = 70):
        """Move forward"""
        self.set_motors(speed, speed)
    
    def backward(self, speed: int = 70):
        """Move backward"""
        self.set_motors(-speed, -speed)
    
    def turn_left(self, speed: int = 70):
        """Turn left (left reverse, right forward)"""
        self.set_motors(-speed, speed)
    
    def turn_right(self, speed: int = 70):
        """Turn right (left forward, right reverse)"""
        self.set_motors(speed, -speed)
    
    def stop(self):
        """Stop all motors"""
        self.set_motors(0, 0)
    
    def set_servo(self, angle: int):
        """Set camera servo angle (0-140)"""
        self.servo_angle = max(0, min(140, angle))
    
    def set_lamp(self, on: bool):
        """Turn camera lamp on/off"""
        self.lamp_on = on
        self._lamp_changed = True
    
    # ==================== Sensor Access ====================
    
    def get_battery(self) -> float:
        """Get battery voltage"""
        return self.sensors["battery_voltage"]
    
    def get_distance(self) -> float:
        """Get ultrasonic distance in cm"""
        return self.sensors["ultrasonic_cm"]
    
    def get_ir_left(self) -> int:
        """Get left IR (0=clear, 1=obstacle)"""
        return self.sensors["ir_left"]
    
    def get_ir_right(self) -> int:
        """Get right IR (0=clear, 1=obstacle)"""
        return self.sensors["ir_right"]
    
    def get_sensors(self) -> dict:
        """Get all sensor data"""
        return self.sensors.copy()


async def demo():
    """Demo of rover control"""
    logging.basicConfig(level=logging.INFO)
    
    rover = GalaxyRVR()
    
    try:
        print("🤖 GalaxyRVR Control Demo")
        print("=" * 50)
        
        # Connect
        if not await rover.connect():
            print("Failed to connect!")
            return
        
        print("✅ Connected!\n")
        
        # Wait for sensors to populate
        await asyncio.sleep(1)
        
        # Show sensors
        print(f"📊 Battery: {rover.get_battery():.1f}V")
        print(f"📏 Distance: {rover.get_distance():.1f}cm")
        print(f"👁️  IR: L={rover.get_ir_left()} R={rover.get_ir_right()}\n")
        
        # Movement demo
        print("🎮 Movement Demo (wheels should be free!)")
        
        print("Forward 50%...")
        rover.forward(50)
        await asyncio.sleep(2)
        
        print("Stop...")
        rover.stop()
        await asyncio.sleep(1)
        
        print("Backward 50%...")
        rover.backward(50)
        await asyncio.sleep(2)
        
        print("Stop...")
        rover.stop()
        await asyncio.sleep(1)
        
        print("Turn right...")
        rover.turn_right(50)
        await asyncio.sleep(2)
        
        print("Turn left...")
        rover.turn_left(50)
        await asyncio.sleep(2)
        
        print("Stop...")
        rover.stop()
        await asyncio.sleep(1)
        
        # Camera demo
        print("\n📹 Camera Servo Demo")
        for angle in [60, 40, 60, 90, 120, 140, 120, 90]:
            print(f"  Servo: {angle}°")
            rover.set_servo(angle)
            await asyncio.sleep(0.8)
        
        # Lamp demo
        print("\n💡 Lamp Demo")
        print("  Lamp ON")
        rover.set_lamp(True)
        await asyncio.sleep(2)
        print("  Lamp OFF")
        rover.set_lamp(False)
        await asyncio.sleep(1)
        
        print("\n✅ Demo complete!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted!")
    finally:
        await rover.disconnect()


if __name__ == "__main__":
    asyncio.run(demo())
