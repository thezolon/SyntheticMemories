# 🚀 GalaxyRVR Web Dashboard - Quick Start

## What You Get

🌐 **Beautiful web interface** with:
- Live camera feed
- Real-time sensor monitoring
- Interactive rover control (WASD keys + buttons)
- Live map visualization
- WiFi signal heatmap
- Saved map browser

🐳 **Docker containerized** - runs anywhere:
- Your PC
- Raspberry Pi 5
- Cloud server
- **Future: Pi Zero 2W mounted on rover!**

---

## Start in 30 Seconds

```bash
cd ~/.openclaw/workspace/skills/galaxyrvr

# Build (one time)
docker-compose build

# Start
docker-compose up -d

# Open browser
firefox http://localhost:5050
```

**That's it!** 🎉

---

## What You'll See

### Dashboard Homepage

```
┌─────────────────────────────────────────────────┐
│  🤖 GalaxyRVR Dashboard                         │
├─────────────────────────────────────────────────┤
│                                                 │
│  📊 Status      📷 Camera      🎮 Controls      │
│  ┌─────────┐   ┌─────────┐   ┌─────────────┐  │
│  │Connection│   │[Camera  │   │    ⬆️        │  │
│  │ Battery │   │ Feed]   │   │  ⬅️ ⬇️ ➡️     │  │
│  │ Distance│   │         │   │   [STOP]    │  │
│  │ WiFi    │   │         │   │  Speed: 50% │  │
│  │ IR      │   └─────────┘   └─────────────┘  │
│  └─────────┘                                   │
│                                                 │
│  🗺️ Live Map              💾 Saved Maps        │
│  ┌───────────────────┐    ┌──────────────┐    │
│  │ [Interactive Map] │    │ 2026-02-01   │    │
│  │  • = Free         │    │ 150m, 45%    │    │
│  │  # = Obstacle     │    │              │    │
│  │  ^ = Rover        │    │ 2026-01-31   │    │
│  │                   │    │ 89m, 32%     │    │
│  └───────────────────┘    └──────────────┘    │
└─────────────────────────────────────────────────┘
```

### Controls

**Keyboard:**
- `W` - Forward
- `S` - Backward
- `A` - Left
- `D` - Right
- `SPACE` - Stop

**Mouse:**
- Click and hold direction buttons
- Adjust speed slider
- Adjust camera angle slider

---

## Features in Action

### 1. Monitor Rover Health
- Battery voltage and percentage
- Real-time distance sensor
- WiFi signal strength
- IR obstacle sensors

### 2. Drive the Rover
- WASD keyboard control
- On-screen buttons (mobile-friendly)
- Variable speed control
- Camera angle adjustment

### 3. View Live Map
- See explored areas
- Obstacles marked in red
- Rover position and heading
- Toggle between occupancy and WiFi heatmap

### 4. Review Past Explorations
- List all saved maps
- Load any previous map
- See statistics (distance, %, scans)
- Compare WiFi coverage over time

---

## Access from Other Devices

### Same WiFi Network

**From phone/tablet/laptop:**
1. Find your PC's IP: `hostname -I`
2. Open browser to: `http://YOUR_IP:5050`
3. Control rover from anywhere in house!

### Example

```
Your PC IP: 192.168.1.100

Phone browser: http://192.168.1.100:5050
Tablet browser: http://192.168.1.100:5050
Laptop browser: http://192.168.1.100:5050
```

---

## Deploy to Raspberry Pi 5

**Make rover accessible from anywhere in house:**

```bash
# On your PC
cd ~/.openclaw/workspace/skills/galaxyrvr
docker save galaxyrvr-dashboard | gzip > galaxyrvr.tar.gz
scp galaxyrvr.tar.gz pi@raspberrypi5:~

# On Pi5
docker load < galaxyrvr.tar.gz
# Copy docker-compose.yml and .env
docker-compose up -d

# Access from any device
# http://raspberrypi5.local:5050
```

Now the dashboard runs on Pi5 permanently!

---

## Future: On-Board Pi Zero 2W

**Mount Pi Zero 2W on rover:**

The rover becomes completely autonomous:
1. Pi runs dashboard container
2. Connects to rover directly (no PC needed)
3. Creates own WiFi hotspot OR uses 5G
4. Access dashboard from phone: `http://rover-ip:5050`
5. **Control from anywhere with internet!**

---

## Stop the Dashboard

```bash
# Stop container
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

---

## Customization

Edit `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit settings
nano .env
```

Options:
- `ROVER_IP` - Your rover's IP address
- `OLLAMA_HOST` - Ollama vision service
- `DASHBOARD_PORT` - Web interface port

---

## Troubleshooting

**Dashboard won't start:**
```bash
# Check if port is in use
lsof -i :5050

# Try different port
echo "DASHBOARD_PORT=5051" >> .env
docker-compose down && docker-compose up -d
```

**Can't reach rover:**
```bash
# Test from container
docker exec galaxyrvr-dashboard ping 192.168.10.118
```

**Camera not loading:**
- Check rover is powered on
- Verify camera URL: http://192.168.10.118:9000/mjpg

---

## What's Next?

1. ✅ **Test dashboard locally** (you are here!)
2. **Deploy to Pi5** - Permanent installation
3. **Add GPS** - Know rover's real-world position
4. **Mount Pi Zero 2W** - Full autonomy
5. **5G connection** - Control from anywhere
6. **Mobile app** - Native iOS/Android (future)

---

## Full Documentation

- **[README.md](README.md)** - Complete feature guide
- **[DOCKER.md](DOCKER.md)** - Deployment scenarios
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - What we built
- **[QUICK_REF.md](QUICK_REF.md)** - Command cheat sheet

---

**Enjoy your web-controlled Mars rover!** 🤖🌐

Open http://localhost:5050 and drive!
