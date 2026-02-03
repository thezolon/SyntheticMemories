#!/usr/bin/env python3
"""
GalaxyRVR Simple Remote Control
Keyboard control for manual driving and testing
"""

import asyncio
import sys
import termios
import tty
from rover_control import GalaxyRVR

class KeyboardControl:
    def __init__(self):
        self.rover = GalaxyRVR()
        self.speed = 50
        self.servo_angle = 90
        self.running = False
        
    def get_key(self):
        """Get single keypress without Enter"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    async def run(self):
        """Main control loop"""
        if not await self.rover.connect():
            print("❌ Failed to connect to rover")
            return
        
        print("\n🎮 GalaxyRVR Keyboard Control")
        print("=" * 60)
        print("Controls:")
        print("  W/S     - Forward/Backward")
        print("  A/D     - Turn Left/Right")
        print("  Q/E     - Camera Up/Down")
        print("  L       - Toggle Lamp")
        print("  +/-     - Speed Up/Down")
        print("  SPACE   - Stop")
        print("  X       - Exit")
        print("=" * 60)
        print(f"Speed: {self.speed}% | Camera: {self.servo_angle}° | Ready!")
        print()
        
        self.running = True
        
        try:
            while self.running:
                key = self.get_key().lower()
                
                if key == 'w':
                    self.rover.forward(self.speed)
                    print(f"↑ Forward {self.speed}%", end='\r')
                    
                elif key == 's':
                    self.rover.backward(self.speed)
                    print(f"↓ Backward {self.speed}%", end='\r')
                    
                elif key == 'a':
                    self.rover.turn_left(self.speed)
                    print(f"← Left {self.speed}%", end='\r')
                    
                elif key == 'd':
                    self.rover.turn_right(self.speed)
                    print(f"→ Right {self.speed}%", end='\r')
                    
                elif key == 'q':
                    self.servo_angle = min(180, self.servo_angle + 15)
                    self.rover.set_servo(self.servo_angle)
                    print(f"📷 Camera: {self.servo_angle}°", end='\r')
                    
                elif key == 'e':
                    self.servo_angle = max(0, self.servo_angle - 15)
                    self.rover.set_servo(self.servo_angle)
                    print(f"📷 Camera: {self.servo_angle}°", end='\r')
                    
                elif key == 'l':
                    # Toggle lamp (crude - just alternate)
                    self.rover.set_lamp(1)
                    await asyncio.sleep(0.1)
                    self.rover.set_lamp(0)
                    print(f"💡 Lamp toggled", end='\r')
                    
                elif key == '+' or key == '=':
                    self.speed = min(100, self.speed + 10)
                    print(f"⚡ Speed: {self.speed}%", end='\r')
                    
                elif key == '-' or key == '_':
                    self.speed = max(10, self.speed - 10)
                    print(f"🐌 Speed: {self.speed}%", end='\r')
                    
                elif key == ' ':
                    self.rover.stop()
                    print(f"⏸️  Stopped", end='\r')
                    
                elif key == 'x':
                    print("\n👋 Exiting...")
                    break
                
                # Show sensors
                sensors = self.rover.get_sensors()
                status = f"  | Battery: {sensors['battery_voltage']:.2f}V | Distance: {sensors['ultrasonic_cm']:.0f}cm"
                print(status, end='')
                
                await asyncio.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n\n⏸️  Interrupted")
        finally:
            self.rover.stop()
            await self.rover.disconnect()
            print("\n✅ Disconnected")

async def main():
    controller = KeyboardControl()
    await controller.run()

if __name__ == "__main__":
    asyncio.run(main())
