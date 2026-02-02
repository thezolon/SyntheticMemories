# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Cameras

### Foscam (External Reference)
- **URL:** `rtsp://zcamz:merfda13@192.168.2.208:88/videoMain`
- **Credentials:** Stored in `~/.openclaw/.env` (FOSCAM_USER, FOSCAM_PASS)
- **Purpose:** Third-person view of rover position for spatial calibration
- **Snapshot command:** 
  ```bash
  ffmpeg -rtsp_transport tcp -i "rtsp://$FOSCAM_USER:$FOSCAM_PASS@192.168.2.208:88/videoMain" \
    -frames:v 1 -q:v 2 -update 1 /tmp/foscam_snapshot.jpg -y
  ```

### GalaxyRVR Onboard Camera
- **URL:** `http://192.168.10.118:9000/mjpg`
- **Purpose:** Rover's first-person view (what the rover sees)
- **Tilt control:** `/servo?angle=X` (0-140°)

---

Add whatever helps you do your job. This is your cheat sheet.
