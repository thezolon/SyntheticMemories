#!/bin/bash
# Comprehensive Docker Security Scanner
# Part 1: ClamAV filesystem scan (includes Docker volumes)
# Part 2: Trivy container image vulnerability scan

LOG_FILE="/home/zolon/.openclaw/logs/security-scan.log"
TRIVY_LOG="/home/zolon/.openclaw/logs/trivy-scan.log"

mkdir -p "$(dirname "$LOG_FILE")"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "========================================" >> "$LOG_FILE"
echo "[$TIMESTAMP] Starting comprehensive security scan" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

THREATS_FOUND=0

# ============================================
# PART 1: ClamAV Filesystem Scan
# ============================================
echo "" >> "$LOG_FILE"
echo "[$TIMESTAMP] Part 1: ClamAV filesystem scan (including Docker volumes)" >> "$LOG_FILE"

docker run --rm \
    -v /home/zolon:/scan/home:ro \
    -v /bulk:/scan/bulk:ro \
    -v /tmp:/scan/tmp:ro \
    -v /var/lib/docker/volumes:/scan/docker-volumes:ro \
    clamav/clamav:latest \
    bash -c "freshclam && clamscan -r -i --log=/dev/stdout /scan" 2>&1 | tee -a "$LOG_FILE"

CLAM_EXIT_CODE=${PIPESTATUS[0]}
echo "[$TIMESTAMP] ClamAV scan complete (exit code: $CLAM_EXIT_CODE)" >> "$LOG_FILE"

if [ "$CLAM_EXIT_CODE" -eq 1 ]; then
    THREATS_FOUND=1
fi

# ============================================
# PART 2: Trivy Container Image Scan
# ============================================
echo "" >> "$LOG_FILE"
echo "[$TIMESTAMP] Part 2: Trivy container vulnerability scan" >> "$LOG_FILE"

# Get all images
IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>")

if [ -z "$IMAGES" ]; then
    echo "[$TIMESTAMP] No Docker images found to scan" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] Scanning $(echo "$IMAGES" | wc -l) container images..." >> "$LOG_FILE"
    
    # Scan each image with Trivy
    echo "" > "$TRIVY_LOG"
    echo "Trivy Container Vulnerability Scan - $TIMESTAMP" >> "$TRIVY_LOG"
    echo "==========================================" >> "$TRIVY_LOG"
    
    CRITICAL_VULNS=0
    HIGH_VULNS=0
    
    while IFS= read -r image; do
        echo "" >> "$TRIVY_LOG"
        echo "Scanning: $image" >> "$TRIVY_LOG"
        echo "---" >> "$TRIVY_LOG"
        
        docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy:latest image \
            --severity HIGH,CRITICAL \
            --no-progress \
            "$image" 2>&1 | tee -a "$TRIVY_LOG"
        
        # Count vulnerabilities
        CRITICAL=$(grep -c "CRITICAL" "$TRIVY_LOG" || true)
        HIGH=$(grep -c "HIGH" "$TRIVY_LOG" || true)
        
        if [ "$CRITICAL" -gt 0 ] || [ "$HIGH" -gt 0 ]; then
            THREATS_FOUND=1
            CRITICAL_VULNS=$((CRITICAL_VULNS + CRITICAL))
            HIGH_VULNS=$((HIGH_VULNS + HIGH))
        fi
    done <<< "$IMAGES"
    
    echo "" >> "$LOG_FILE"
    echo "[$TIMESTAMP] Trivy scan complete - Found $CRITICAL_VULNS CRITICAL and $HIGH_VULNS HIGH vulnerabilities" >> "$LOG_FILE"
    echo "[$TIMESTAMP] Full Trivy results: $TRIVY_LOG" >> "$LOG_FILE"
fi

# ============================================
# Summary & Exit
# ============================================
echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "[$TIMESTAMP] Scan complete" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

if [ "$CLAM_EXIT_CODE" -eq 1 ]; then
    echo "⚠️ MALWARE DETECTED by ClamAV - Check logs: $LOG_FILE"
    exit 1
elif [ "$CLAM_EXIT_CODE" -eq 2 ]; then
    echo "⚠️ ClamAV scan error - Check logs: $LOG_FILE"
    exit 2
elif [ "$THREATS_FOUND" -eq 1 ]; then
    echo "⚠️ Container vulnerabilities detected - Check logs: $LOG_FILE and $TRIVY_LOG"
    exit 1
else
    echo "✅ Security scan complete - No threats or critical vulnerabilities detected"
    exit 0
fi
