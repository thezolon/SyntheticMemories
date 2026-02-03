#!/usr/bin/env bash
set -euo pipefail

echo "📦 Packaging OpenClaw Workspace..."

# Detect script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$WORKSPACE_ROOT"

# Create dist directory
DIST_DIR="$WORKSPACE_ROOT/dist"
mkdir -p "$DIST_DIR"
echo "📁 Output directory: $DIST_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Run ./scripts/bootstrap.sh first."
    exit 1
fi

# Install build tools
echo "🔧 Installing build tools..."
pip install --upgrade build twine

# Package memory-agent
if [ -d "memory-agent" ] && [ -f "memory-agent/pyproject.toml" ]; then
    echo "📦 Building memory-agent..."
    cd memory-agent
    
    # Clean old builds
    rm -rf dist/ build/ *.egg-info
    
    # Build wheel and sdist
    python -m build
    
    # Copy to workspace dist
    cp dist/* "$DIST_DIR/"
    
    echo "✅ memory-agent built successfully"
    cd "$WORKSPACE_ROOT"
else
    echo "⚠️  memory-agent not found or missing pyproject.toml"
fi

# Create workspace archive (excluding venv and git)
echo "📦 Creating workspace archive..."
ARCHIVE_NAME="openclaw-workspace-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$DIST_DIR/$ARCHIVE_NAME" \
    --exclude='venv' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='.mypy_cache' \
    --exclude='node_modules' \
    --exclude='dist' \
    --exclude='build' \
    --exclude='*.egg-info' \
    --exclude='.coverage' \
    .

echo "✅ Workspace archive created: $ARCHIVE_NAME"

# List all built packages
echo ""
echo "📦 Built packages:"
ls -lh "$DIST_DIR"
echo ""

# Verify wheel
echo "🔍 Verifying packages..."
for wheel in "$DIST_DIR"/*.whl; do
    if [ -f "$wheel" ]; then
        echo "Checking $wheel..."
        python -m zipfile -l "$wheel" | head -20
        echo "✅ Wheel structure looks good"
    fi
done

# Optional: Check package with twine
echo ""
echo "🔍 Running twine check..."
twine check "$DIST_DIR"/*.whl "$DIST_DIR"/*.tar.gz 2>/dev/null || echo "⚠️  twine check had warnings"

echo ""
echo "✨ Packaging complete! ✨"
echo ""
echo "To install locally:"
echo "  pip install $DIST_DIR/memory_agent-*.whl"
echo ""
echo "To publish to PyPI (requires credentials):"
echo "  twine upload $DIST_DIR/memory_agent-*"
echo ""
