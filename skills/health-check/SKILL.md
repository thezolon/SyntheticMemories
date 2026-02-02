# health-check

Monitor OpenClaw Gateway health and detect common issues.

## Overview

This skill performs comprehensive health checks on the OpenClaw Gateway:
- Detects duplicate/conflicting gateway processes
- Monitors memory usage with configurable thresholds
- Identifies zombie/defunct processes
- Verifies gateway responsiveness
- Scans recent logs for errors

## Usage

### Manual Check

```bash
cd ~/.openclaw/workspace/skills/health-check
./check.sh
```

### From Agent

Use the `exec` tool to run the check script:

```javascript
exec({ command: "~/.openclaw/workspace/skills/health-check/check.sh" })
```

### Periodic Monitoring (Heartbeat)

Add to `HEARTBEAT.md`:

```markdown
## Health Checks

Every 4-6 hours, run the health-check skill:
- `~/.openclaw/workspace/skills/health-check/check.sh`
- If status is WARNING or ERROR, alert the user
- Track last check in `memory/heartbeat-state.json`
```

## Exit Codes

- `0` - OK: All checks passed
- `1` - WARNING: Minor issues detected (e.g., high memory usage)
- `2` - ERROR: Critical issues detected (e.g., duplicate processes, gateway unresponsive)

## Output Format

Status summary with details:
```
[OK|WARNING|ERROR] OpenClaw Gateway Health Check
---
Process Check: ✓ Single gateway process running (PID 12345)
Memory Usage: ⚠ 1.2GB (threshold: 1GB warning, 2GB error)
Zombie Check: ✓ No zombie processes
Gateway Response: ✓ Gateway responding
Log Check: ✓ No recent errors
```

## Thresholds

Configure in `check.sh`:
- **Memory Warning**: 1GB (1048576 KB)
- **Memory Error**: 2GB (2097152 KB)
- **Log lookback**: Last 100 lines
- **Process patterns**: `openclaw-gateway`, `python3 app.py` (gateway context)

## Files

- `SKILL.md` - This documentation
- `check.sh` - Health check script (executable)

## Troubleshooting

### Duplicate Processes
```bash
# List all gateway processes
ps aux | grep -E 'openclaw-gateway|python3 app.py'

# Stop gateway cleanly
openclaw gateway stop

# Force kill if needed
pkill -f openclaw-gateway
```

### High Memory Usage
```bash
# Restart gateway to clear memory
openclaw gateway restart
```

### Gateway Not Responding
```bash
# Check status
openclaw gateway status

# View logs
tail -100 ~/.openclaw/logs/gateway.log

# Restart
openclaw gateway restart
```

## Notes

- Requires `openclaw` CLI to be in PATH
- Assumes logs at `~/.openclaw/logs/gateway.log` (adjust if different)
- Safe to run frequently (minimal overhead)
- Non-destructive (only reads system state)
