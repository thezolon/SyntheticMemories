#!/bin/bash
# OpenClaw Media Cleanup Script
# Removes inbound media files older than specified retention period

MEDIA_DIR="/bulk/openclaw/media/inbound"
RETENTION_DAYS=7  # Keep files for 7 days by default

# Log file
LOG_FILE="/home/zolon/.openclaw/logs/media-cleanup.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Starting media cleanup (retention: ${RETENTION_DAYS} days)" >> "$LOG_FILE"

# Count files before cleanup
BEFORE_COUNT=$(find "$MEDIA_DIR" -type f | wc -l)
BEFORE_SIZE=$(du -sh "$MEDIA_DIR" 2>/dev/null | cut -f1)

# Remove files older than retention period
DELETED_COUNT=$(find "$MEDIA_DIR" -type f -mtime +${RETENTION_DAYS} -delete -print | tee -a "$LOG_FILE" | wc -l)

# Count files after cleanup
AFTER_COUNT=$(find "$MEDIA_DIR" -type f | wc -l)
AFTER_SIZE=$(du -sh "$MEDIA_DIR" 2>/dev/null | cut -f1)

echo "[$TIMESTAMP] Cleanup complete: $DELETED_COUNT files removed" >> "$LOG_FILE"
echo "[$TIMESTAMP] Before: $BEFORE_COUNT files ($BEFORE_SIZE) | After: $AFTER_COUNT files ($AFTER_SIZE)" >> "$LOG_FILE"

# Only output if files were deleted (for cron notification)
if [ "$DELETED_COUNT" -gt 0 ]; then
    echo "Cleaned up $DELETED_COUNT media files older than ${RETENTION_DAYS} days"
    echo "Storage: $BEFORE_SIZE → $AFTER_SIZE"
fi
