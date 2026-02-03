#!/bin/bash
# Curate memories from a markdown file

MEMORY_SERVICE="http://localhost:8768"

# Parse arguments
SOURCE_FILE=""
THRESHOLD=7
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --from)
            SOURCE_FILE="$2"
            shift 2
            ;;
        --threshold)
            THRESHOLD="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: advanced-memory curate --from <file> [--threshold 7] [--dry-run]"
            exit 1
            ;;
    esac
done

if [ -z "$SOURCE_FILE" ]; then
    echo "Usage: advanced-memory curate --from <file> [--threshold 7] [--dry-run]"
    exit 1
fi

# Build JSON payload
PAYLOAD=$(jq -n \
    --arg source "$SOURCE_FILE" \
    --argjson threshold "$THRESHOLD" \
    --argjson dry_run "$([ "$DRY_RUN" = true ] && echo true || echo false)" \
    '{source_file: $source, threshold: $threshold, dry_run: $dry_run}')

# POST to service
curl -s -X POST "$MEMORY_SERVICE/curate" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" | jq .
