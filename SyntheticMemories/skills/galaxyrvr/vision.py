#!/usr/bin/env python3
"""
GalaxyRVR Local Vision System (Ollama-powered)
Fast, cheap vision processing using local AI - no cloud costs!
"""

import asyncio
import requests
import base64
import time
from typing import Optional, Dict, Any
from datetime import datetime

class RoverVision:
    def __init__(self, 
                 camera_url="http://192.168.10.118:9000/mjpg",
                 ollama_url="http://localhost:11434",
                 model="llava:7b"):
        self.camera_url = camera_url
        self.ollama_url = ollama_url
        self.model = model
        
        # Cache last frame to avoid redundant captures
        self.last_frame = None
        self.last_frame_time = None
        
    def capture_frame(self) -> Optional[bytes]:
        """Capture single JPEG frame from camera stream"""
        try:
            response = requests.get(self.camera_url, stream=True, timeout=3)
            buffer = b''
            
            for chunk in response.iter_content(chunk_size=1024):
                buffer += chunk
                
                # Find JPEG markers
                start = buffer.find(b'\xff\xd8')
                end = buffer.find(b'\xff\xd9')
                
                if start != -1 and end != -1 and end > start:
                    jpeg_data = buffer[start:end+2]
                    self.last_frame = jpeg_data
                    self.last_frame_time = time.time()
                    return jpeg_data
            
            return None
            
        except Exception as e:
            print(f"Camera capture error: {e}")
            return None
    
    def analyze_frame(self, 
                     frame_data: bytes, 
                     prompt: str = "What do you see? Describe briefly.",
                     max_tokens: int = 50) -> Optional[Dict[str, Any]]:
        """
        Analyze frame using local Ollama vision model
        
        Args:
            frame_data: JPEG image bytes
            prompt: Question to ask about the image
            max_tokens: Limit response length (faster)
        
        Returns:
            {"description": str, "time_seconds": float, "model": str}
        """
        try:
            # Encode image
            image_b64 = base64.b64encode(frame_data).decode('utf-8')
            
            start = time.time()
            
            # Call Ollama API (non-streaming for simplicity)
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "images": [image_b64],
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,  # Limit tokens for speed
                        "temperature": 0.3  # Lower = more consistent/faster
                    }
                },
                timeout=30
            )
            
            elapsed = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "description": result["response"].strip(),
                    "time_seconds": elapsed,
                    "model": self.model,
                    "prompt": prompt
                }
            else:
                print(f"Ollama error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Vision analysis error: {e}")
            return None
    
    def quick_look(self, prompt: str = "What do you see? One sentence.") -> Optional[str]:
        """
        Quick vision check - capture + analyze in one call
        Optimized for speed
        """
        frame = self.capture_frame()
        if not frame:
            return None
        
        result = self.analyze_frame(frame, prompt, max_tokens=30)
        if result:
            return result["description"]
        return None
    
    def detect_obstacles(self) -> Dict[str, Any]:
        """
        Optimized obstacle detection
        Returns: {"has_obstacle": bool, "description": str, "safe_to_move": bool}
        """
        prompt = "Is there any obstacle or object blocking the path ahead? Answer yes or no, then briefly describe what you see."
        
        description = self.quick_look(prompt)
        if not description:
            return {"has_obstacle": None, "description": "Camera unavailable", "safe_to_move": False}
        
        desc_lower = description.lower()
        has_obstacle = any(word in desc_lower for word in ["yes", "obstacle", "blocked", "object", "dog", "wall", "furniture"])
        
        return {
            "has_obstacle": has_obstacle,
            "description": description,
            "safe_to_move": not has_obstacle
        }
    
    def find_target(self, target: str = "blue object") -> Dict[str, Any]:
        """
        Look for a specific target
        Returns: {"found": bool, "position": str, "description": str}
        """
        prompt = f"Do you see a {target}? If yes, is it on the left, center, or right? Answer briefly."
        
        description = self.quick_look(prompt)
        if not description:
            return {"found": False, "position": None, "description": "Camera unavailable"}
        
        desc_lower = description.lower()
        found = target.lower() in desc_lower or "yes" in desc_lower
        
        position = None
        if "left" in desc_lower:
            position = "left"
        elif "right" in desc_lower:
            position = "right"
        elif "center" in desc_lower or "middle" in desc_lower:
            position = "center"
        
        return {
            "found": found,
            "position": position,
            "description": description
        }


def demo():
    """Demo the vision system"""
    print("🤖 GalaxyRVR Local Vision Demo")
    print("=" * 60)
    print("Using Ollama (local, free, no API costs!)")
    print()
    
    vision = RoverVision()
    
    # Test 1: What do you see?
    print("📸 Test 1: What does the rover see?")
    start = time.time()
    result = vision.quick_look("Describe what you see in one sentence.")
    elapsed = time.time() - start
    
    if result:
        print(f"   Vision: {result}")
        print(f"   Time: {elapsed:.1f}s")
    else:
        print("   ❌ Vision failed")
    
    print()
    
    # Test 2: Obstacle detection
    print("📸 Test 2: Obstacle detection")
    start = time.time()
    obstacles = vision.detect_obstacles()
    elapsed = time.time() - start
    
    print(f"   Obstacle: {obstacles['has_obstacle']}")
    print(f"   Description: {obstacles['description']}")
    print(f"   Safe to move: {obstacles['safe_to_move']}")
    print(f"   Time: {elapsed:.1f}s")
    
    print()
    
    # Test 3: Find target
    print("📸 Test 3: Look for white fluffy dog")
    start = time.time()
    target = vision.find_target("white fluffy dog")
    elapsed = time.time() - start
    
    print(f"   Found: {target['found']}")
    print(f"   Position: {target['position']}")
    print(f"   Description: {target['description']}")
    print(f"   Time: {elapsed:.1f}s")
    
    print()
    print("=" * 60)
    print("✅ Vision system ready!")
    print("💰 Cost: $0.00 (running locally)")


if __name__ == "__main__":
    demo()
