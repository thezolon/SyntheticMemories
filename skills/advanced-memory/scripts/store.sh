#!/bin/bash
# Store a memory via CLI

MEMORY_SERVICE="http://localhost:8768"

# Parse arguments
CONTENT=""
TIER="user"
USER_ID="default"
IMPORTANCE=""

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
        --importance)
            IMPORTANCE="$2"
            shift 2
            ;;
        *)
            CONTENT="$1"
            shift
            ;;
    esac
done

if [ -z "$CONTENT" ]; then
    echo "Usage: advanced-memory store <content> [--tier global|user|session] [--user <id>] [--importance 0-10]"
    exit 1
fi

# Build JSON payload
if [ -n "$IMPORTANCE" ]; then
    PAYLOAD=$(jq -n \
        --arg content "$CONTENT" \
        --arg tier "$TIER" \
        --arg user "$USER_ID" \
        --argjson importance "$IMPORTANCE" \
        '{content: $content, tier: $tier, user_id: $user, importance: $importance}')
else
    PAYLOAD=$(jq -n \
        --arg content "$CONTENT" \
        --arg tier "$TIER" \
        --arg user "$USER_ID" \
        '{content: $content, tier: $tier, user_id: $user}')
fi

# POST to service
curl -s -X POST "$MEMORY_SERVICE/store" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" | jq .
