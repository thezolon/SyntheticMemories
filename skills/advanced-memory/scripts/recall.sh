#!/bin/bash
# Recall memories via semantic search

MEMORY_SERVICE="http://localhost:8768"

# Parse arguments
QUERY=""
TIER=""
USER_ID=""
LIMIT=5
MIN_IMPORTANCE=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --tier)
            TIER="$2"
            shift 2
            ;;
        --user)
            USER_ID="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --min-importance)
            MIN_IMPORTANCE="$2"
            shift 2
            ;;
        *)
            QUERY="$1"
            shift
            ;;
    esac
done

if [ -z "$QUERY" ]; then
    echo "Usage: advanced-memory recall <query> [--tier global|user|session] [--user <id>] [--limit N] [--min-importance N]"
    exit 1
fi

# Build query params
PARAMS="query=$(echo "$QUERY" | jq -sRr @uri)"
[ -n "$TIER" ] && PARAMS="$PARAMS&tier=$TIER"
[ -n "$USER_ID" ] && PARAMS="$PARAMS&user_id=$USER_ID"
PARAMS="$PARAMS&limit=$LIMIT&min_importance=$MIN_IMPORTANCE"

# GET from service
curl -s "$MEMORY_SERVICE/recall?$PARAMS" | jq .
