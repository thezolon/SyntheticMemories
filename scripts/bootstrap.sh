#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Bootstrapping OpenClaw Workspace..."

# Detect script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$WORKSPACE_ROOT"

# Check Python version
echo "📋 Checking Python version..."
PYTHON_CMD=$(command -v python3.12 || command -v python3.11 || command -v python3.10 || command -v python3)
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    echo "❌ Python 3.10+ required, found $PYTHON_VERSION"
    exit 1
fi

echo "✅ Using Python $PYTHON_VERSION ($PYTHON_CMD)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install memory-agent in editable mode
echo "📚 Installing memory-agent..."
if [ -d "memory-agent" ] && [ -f "memory-agent/pyproject.toml" ]; then
    pip install -e "memory-agent[dev]"
    echo "✅ memory-agent installed in editable mode"
else
    echo "⚠️  memory-agent directory not found or missing pyproject.toml"
fi

# Install any additional requirements
if [ -f "requirements.txt" ]; then
    echo "📦 Installing additional requirements..."
    pip install -r requirements.txt
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p memory/backups
mkdir -p CI_RUNS
mkdir -p memory-agent/data
mkdir -p memory-agent/models

# Run basic health check
echo "🏥 Running health check..."
if command -v memory &> /dev/null; then
    echo "✅ 'memory' command is available"
    memory --version || echo "⚠️  Could not get memory version"
else
    echo "⚠️  'memory' command not found in PATH"
fi

# Test imports
echo "🧪 Testing Python imports..."
python -c "import memory_agent; print('✅ memory_agent imports successfully')" || echo "⚠️  memory_agent import failed"

# Run quick tests if pytest is available
if command -v pytest &> /dev/null && [ -d "memory-agent/tests" ]; then
    echo "🧪 Running quick test suite..."
    cd memory-agent
    pytest --tb=short -q || echo "⚠️  Some tests failed"
    cd "$WORKSPACE_ROOT"
else
    echo "⚠️  pytest not available or no tests found"
fi

echo ""
echo "✨ Bootstrap complete! ✨"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run memory-agent CLI:"
echo "  memory --help"
echo ""
echo "To run tests:"
echo "  cd memory-agent && pytest"
echo ""
