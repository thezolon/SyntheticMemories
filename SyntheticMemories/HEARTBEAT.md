# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.
# Add tasks below when you want the agent to check something periodically.

## Health Checks (rotate, don't run all every time)

Track last checks in memory/heartbeat-state.json

### Gateway Health (every 30-60 minutes)
Run: `~/.openclaw/workspace/skills/health-check/check.sh`
Alert if: WARNING or ERROR status (duplicate processes, high memory, zombies)
