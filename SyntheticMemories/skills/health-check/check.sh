#!/bin/bash
# OpenClaw Gateway Health Check
# Returns: 0=OK, 1=WARNING, 2=ERROR

set -euo pipefail

# Thresholds (in KB)
MEMORY_WARN_KB=1048576  # 1GB
MEMORY_ERROR_KB=2097152 # 2GB

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Status tracking
STATUS="OK"
EXIT_CODE=0
DETAILS=""

# Helper functions
log_ok() {
    DETAILS="${DETAILS}✓ $1\n"
}

log_warn() {
    DETAILS="${DETAILS}⚠ $1\n"
    if [ "$STATUS" = "OK" ]; then
        STATUS="WARNING"
        EXIT_CODE=1
    fi
}

log_error() {
    DETAILS="${DETAILS}✗ $1\n"
    STATUS="ERROR"
    EXIT_CODE=2
}

# 1. Check for duplicate gateway processes
check_processes() {
    # Look for openclaw-gateway or python3 processes running app.py in gateway context
    GATEWAY_PIDS=$(pgrep -f "openclaw-gateway" || true)
    PYTHON_GATEWAY_PIDS=$(pgrep -f "python3.*app\.py" | while read pid; do
        # Check if this python process is in a gateway-related directory
        if ps -p "$pid" -o args= | grep -q "openclaw.*gateway\|gateway.*openclaw"; then
            echo "$pid"
        fi
    done || true)
    
    ALL_PIDS=$(echo -e "${GATEWAY_PIDS}\n${PYTHON_GATEWAY_PIDS}" | sort -u | grep -v '^$' || true)
    PID_COUNT=$(echo "$ALL_PIDS" | grep -v '^$' | wc -l || echo 0)
    
    if [ "$PID_COUNT" -eq 0 ]; then
        log_error "Process Check: No gateway process found"
    elif [ "$PID_COUNT" -eq 1 ]; then
        MAIN_PID=$(echo "$ALL_PIDS" | head -1)
        log_ok "Process Check: Single gateway process running (PID $MAIN_PID)"
    else
        PIDS_LIST=$(echo "$ALL_PIDS" | tr '\n' ' ')
        log_error "Process Check: Multiple gateway processes detected (PIDs: $PIDS_LIST)"
    fi
    
    # Store main PID for memory check
    MAIN_PID=$(echo "$ALL_PIDS" | head -1 || echo "")
}

# 2. Monitor memory usage
check_memory() {
    if [ -z "$MAIN_PID" ]; then
        log_error "Memory Usage: Cannot check (no process found)"
        return
    fi
    
    # Get RSS memory in KB
    MEMORY_KB=$(ps -p "$MAIN_PID" -o rss= 2>/dev/null | tr -d ' ' || echo "0")
    
    if [ "$MEMORY_KB" -eq 0 ]; then
        log_error "Memory Usage: Cannot read memory for PID $MAIN_PID"
        return
    fi
    
    # Convert to MB for display
    MEMORY_MB=$((MEMORY_KB / 1024))
    
    if [ "$MEMORY_KB" -ge "$MEMORY_ERROR_KB" ]; then
        log_error "Memory Usage: ${MEMORY_MB}MB (critical: >2GB)"
    elif [ "$MEMORY_KB" -ge "$MEMORY_WARN_KB" ]; then
        log_warn "Memory Usage: ${MEMORY_MB}MB (warning: >1GB)"
    else
        log_ok "Memory Usage: ${MEMORY_MB}MB (healthy)"
    fi
}

# 3. Check for zombie/defunct processes
check_zombies() {
    ZOMBIE_COUNT=$(ps aux | awk '{print $8}' | grep -c '^Z' || true)
    
    if [ "$ZOMBIE_COUNT" -gt 0 ]; then
        log_warn "Zombie Check: $ZOMBIE_COUNT zombie/defunct process(es) found"
    else
        log_ok "Zombie Check: No zombie processes"
    fi
}

# 4. Verify gateway is responding
check_gateway_response() {
    # Try to get gateway status
    if command -v openclaw &>/dev/null; then
        if timeout 5 openclaw gateway status &>/dev/null; then
            log_ok "Gateway Response: Gateway responding to status command"
        else
            log_error "Gateway Response: Gateway not responding (timeout or error)"
        fi
    else
        log_warn "Gateway Response: Cannot verify (openclaw CLI not found in PATH)"
    fi
}

# 5. Check log files for errors
check_logs() {
    LOG_FILE="$HOME/.openclaw/logs/gateway.log"
    
    if [ ! -f "$LOG_FILE" ]; then
        log_warn "Log Check: Log file not found ($LOG_FILE)"
        return
    fi
    
    # Check last 100 lines for ERROR or CRITICAL
    ERROR_COUNT=$(tail -100 "$LOG_FILE" 2>/dev/null | grep -ciE 'ERROR|CRITICAL' || true)
    
    if [ "$ERROR_COUNT" -gt 10 ]; then
        log_error "Log Check: $ERROR_COUNT errors in last 100 lines"
    elif [ "$ERROR_COUNT" -gt 0 ]; then
        log_warn "Log Check: $ERROR_COUNT error(s) in last 100 lines"
    else
        log_ok "Log Check: No recent errors in logs"
    fi
}

# Run all checks
MAIN_PID=""
check_processes
check_memory
check_zombies
check_gateway_response
check_logs

# Output results
echo -e "\n${STATUS} OpenClaw Gateway Health Check"
echo "---"
echo -e "$DETAILS"

# Color the status
case $STATUS in
    OK)
        echo -e "${GREEN}Status: OK${NC}"
        ;;
    WARNING)
        echo -e "${YELLOW}Status: WARNING${NC}"
        ;;
    ERROR)
        echo -e "${RED}Status: ERROR${NC}"
        ;;
esac

exit $EXIT_CODE
