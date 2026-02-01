# 🐳 GalaxyRVR Docker Deployment

**Portable, containerized rover control system**

## Why Docker?

✅ **Portable** - Move between systems (PC, Pi5, server)  
✅ **Isolated** - No dependency conflicts  
✅ **Reproducible** - Same environment everywhere  
✅ **Easy deployment** - One command to start  
✅ **Volume persistence** - Maps survive container restarts  

---

## Quick Start

### 1. Build the Container

```bash
cd ~/.openclaw/workspace/skills/galaxyrvr
docker-compose build
```

### 2. Start the Dashboard

```bash
docker-compose up -d
```

### 3. Access the Dashboard

Open browser to: **http://localhost:5050**

Or from another device: **http://YOUR_IP:5050**

### 4. Stop the Dashboard

```bash
docker-compose down
```

---

## Configuration

Create `.env` file from example:

```bash
cp .env.example .env
```

Edit `.env` to customize:

```bash
# Your rover's IP
ROVER_IP=192.168.10.118

# Ollama for vision (localhost if running on host)
OLLAMA_HOST=http://localhost:11434

# Dashboard web port
DASHBOARD_PORT=5050
```

---

## Deployment Scenarios

### Scenario 1: Local Development (Current)

**Your PC runs everything:**
- Docker container (web dashboard)
- Ollama (on host)
- Rover (physical device)

```bash
# Start dashboard
docker-compose up -d

# View logs
docker-compose logs -f

# Access: http://localhost:5050
```

### Scenario 2: Raspberry Pi 5 Deployment

**Pi5 runs dashboard, connects to rover:**

```bash
# On your PC - build and save image
cd ~/.openclaw/workspace/skills/galaxyrvr
docker build -t galaxyrvr:latest .
docker save galaxyrvr:latest | gzip > galaxyrvr-image.tar.gz

# Transfer to Pi5
scp galaxyrvr-image.tar.gz pi@raspberrypi5:~

# On Pi5 - load and run
docker load < galaxyrvr-image.tar.gz
cd /path/to/galaxyrvr
docker-compose up -d

# Access from any device: http://pi5-ip:5050
```

### Scenario 3: Pi Zero 2W On-Board

**Pi Zero 2W mounted on rover:**

The rover becomes fully autonomous! The Pi:
- Runs the dashboard
- Connects to rover via WiFi (same network or direct)
- Provides GPS, 5G, better vision
- Can host maps and serve dashboard remotely

```bash
# On rover's Pi Zero 2W
docker-compose up -d

# Access from phone: http://rover-ip:5050
```

### Scenario 4: Cloud/Remote Server

**Run dashboard on always-on server:**

```bash
# Deploy to any VPS/server
git clone <your-repo>
cd galaxyrvr
docker-compose up -d

# Access from anywhere: http://server-ip:5050
# (Rover must be network-reachable)
```

---

## Volume Management

Docker mounts persistent directories:

```
./maps/  → Container's /app/maps
./logs/  → Container's /app/logs
```

**Maps survive container restarts!**

```bash
# View maps on host
ls -la ~/.openclaw/workspace/skills/galaxyrvr/maps/

# Backup maps
tar -czf rover-maps-backup.tar.gz maps/

# Restore maps
tar -xzf rover-maps-backup.tar.gz
```

---

## Building for ARM (Raspberry Pi)

### Multi-Architecture Build

```bash
# Enable buildx
docker buildx create --use

# Build for ARM64 (Pi 4/5)
docker buildx build \
  --platform linux/arm64 \
  -t galaxyrvr:arm64 \
  --load .

# Build for ARMv7 (Pi Zero 2W)
docker buildx build \
  --platform linux/arm/v7 \
  -t galaxyrvr:armv7 \
  --load .
```

### Cross-Platform Build

```bash
# Build for both AMD64 and ARM64
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t galaxyrvr:multi \
  --push .  # Push to registry
```

---

## Running Individual Components

The Docker container can run any rover script:

### Web Dashboard (default)
```bash
docker-compose up -d
```

### Autonomous Explorer
```bash
docker run --rm --network host \
  -v $(pwd)/maps:/app/maps \
  galaxyrvr-dashboard \
  python autonomous_explorer.py --duration 30
```

### Battery Monitor
```bash
docker run --rm --network host \
  galaxyrvr-dashboard \
  python battery_alert.py --once
```

### Vision Test
```bash
docker run --rm --network host \
  galaxyrvr-dashboard \
  python vision.py
```

### Map Viewer
```bash
docker run --rm --network host \
  -v $(pwd)/maps:/app/maps \
  galaxyrvr-dashboard \
  python map_viewer.py --list
```

---

## Development Workflow

### Live Development (Mount Code)

```bash
# Override docker-compose for development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Create `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  galaxyrvr:
    volumes:
      - .:/app  # Mount current directory
    environment:
      - FLASK_ENV=development
```

### Rebuild After Changes

```bash
# Rebuild and restart
docker-compose up -d --build

# Or just rebuild
docker-compose build
```

---

## Troubleshooting

### Container can't reach rover

```bash
# Check network mode (should be 'host')
docker-compose ps

# Test connectivity from inside container
docker exec galaxyrvr-dashboard ping 192.168.10.118
```

### Maps not persisting

```bash
# Check volume mounts
docker inspect galaxyrvr-dashboard | grep -A 10 Mounts

# Verify directory exists
ls -la ./maps/
```

### Port already in use

```bash
# Change port in .env
DASHBOARD_PORT=5051

# Restart
docker-compose down && docker-compose up -d
```

### Ollama not reachable

If Ollama runs on host:

```bash
# Use host network mode (already configured)
# Or use host.docker.internal
OLLAMA_HOST=http://host.docker.internal:11434
```

---

## Production Deployment

### Docker Compose with Ollama

Uncomment the Ollama service in `docker-compose.yml`:

```yaml
services:
  galaxyrvr:
    # ... existing config ...
    depends_on:
      - ollama
  
  ollama:
    image: ollama/ollama:latest
    container_name: galaxyrvr-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama-data:
```

Then:

```bash
# Start both services
docker-compose up -d

# Pull vision model
docker exec galaxyrvr-ollama ollama pull llava:7b
```

### Systemd Service (Auto-start on Boot)

Create `/etc/systemd/system/galaxyrvr.service`:

```ini
[Unit]
Description=GalaxyRVR Dashboard
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/pi/galaxyrvr
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl enable galaxyrvr
sudo systemctl start galaxyrvr
```

---

## Docker Hub / Registry

### Tag and Push

```bash
# Tag for Docker Hub
docker tag galaxyrvr:latest username/galaxyrvr:latest

# Push
docker push username/galaxyrvr:latest

# Then on any system:
docker pull username/galaxyrvr:latest
```

---

## System Requirements

**Minimum:**
- Docker 20.10+
- 512MB RAM
- 1GB disk space

**Recommended:**
- Docker 24.0+
- 1GB+ RAM
- 2GB disk space
- ARM64 for Raspberry Pi

---

## What's Inside the Container

```
/app/
├── rover_control.py
├── vision.py
├── mapping.py
├── battery_alert.py
├── wifi_monitor.py
├── autonomous_explorer.py
├── web_dashboard.py
├── templates/
│   └── dashboard.html
├── maps/          (volume mount)
└── logs/          (volume mount)
```

---

## Next Steps

1. **Build and test locally**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

2. **Access dashboard**
   - Open http://localhost:5050
   - Test rover control
   - View live map

3. **Deploy to Pi5** (when ready)
   - Transfer image
   - Run on Pi5
   - Access from any device

4. **Mount Pi Zero 2W on rover** (future)
   - Self-contained autonomous system
   - Dashboard accessible via WiFi
   - Full independence!

---

**You now have a production-ready, portable, containerized rover control system!** 🐳🤖

Move it to any system with Docker and it just works.
