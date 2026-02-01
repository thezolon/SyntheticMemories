#!/bin/bash
# Start GalaxyRVR Web Dashboard

cd ~/.openclaw/workspace/skills/galaxyrvr

echo "🌐 GalaxyRVR Web Dashboard"
echo "=========================="
echo ""

# Check dependencies
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements-web.txt
    echo ""
fi

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "Starting dashboard..."
echo ""
echo "🌐 Access from:"
echo "   This computer: http://localhost:5050"
echo "   Other devices: http://$LOCAL_IP:5050"
echo ""
echo "⚠️  Make sure rover is powered on and connected!"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 web_dashboard.py
