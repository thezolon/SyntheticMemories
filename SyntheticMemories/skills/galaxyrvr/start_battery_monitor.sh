#!/bin/bash
# GalaxyRVR Battery Monitor Service
# Runs in background and monitors battery status

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/battery_alert.py"
LOG_FILE="$HOME/.openclaw/workspace/skills/galaxyrvr/battery_monitor.log"

# Configuration
ROVER_IP="${ROVER_IP:-192.168.10.118}"
CHECK_INTERVAL="${CHECK_INTERVAL:-300}"  # 5 minutes default
CRITICAL_VOLTAGE="${CRITICAL_VOLTAGE:-6.5}"
LOW_VOLTAGE="${LOW_VOLTAGE:-7.0}"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

echo "Starting GalaxyRVR Battery Monitor" | tee -a "$LOG_FILE"
echo "  Rover IP: $ROVER_IP" | tee -a "$LOG_FILE"
echo "  Check interval: ${CHECK_INTERVAL}s" | tee -a "$LOG_FILE"
echo "  Critical: <${CRITICAL_VOLTAGE}V, Low: <${LOW_VOLTAGE}V" | tee -a "$LOG_FILE"
echo "  Log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Run monitor
python3 "$PYTHON_SCRIPT" \
    --host "$ROVER_IP" \
    --interval "$CHECK_INTERVAL" \
    --critical "$CRITICAL_VOLTAGE" \
    --low "$LOW_VOLTAGE" \
    2>&1 | tee -a "$LOG_FILE"
