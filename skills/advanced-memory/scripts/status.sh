#!/bin/bash
# Check advanced-memory service status

MEMORY_SERVICE="http://localhost:8768"

echo "🧠 Advanced Memory Status"
echo "=========================="
echo ""

# Service health
HEALTH=$(curl -s "$MEMORY_SERVICE/health" 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Service: Running"
    echo "$HEALTH" | jq .
else
    echo "❌ Service: Not running"
    echo ""
    echo "Start with:"
    echo "  cd ~/.openclaw/workspace/skills/advanced-memory"
    echo "  docker compose up -d"
fi
