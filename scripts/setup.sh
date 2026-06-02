#!/usr/bin/env bash
# Setup script for multi-agent-brief-workflow
# Run this after cloning to get a working environment.
# Windows users: use scripts\setup.ps1 instead.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== multi-agent-brief-workflow setup ==="

# Find Python: try python3, python, py -3
PYTHON=""
for cmd in python3 python "py -3"; do
    if command -v $cmd >/dev/null 2>&1 || $cmd --version >/dev/null 2>&1; then
        ver=$($cmd --version 2>&1 || true)
        if echo "$ver" | grep -q "Python 3"; then
            PYTHON=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.9+ not found."
    echo ""
    echo "Install Python from https://www.python.org/downloads/"
    echo "Or on macOS: brew install python@3.12"
    echo "Or on Ubuntu: sudo apt install python3 python3-venv"
    exit 1
fi

echo "[1/3] Found Python: $PYTHON ($($PYTHON --version 2>&1))"

# 1. Create venv if missing
if [ ! -d ".venv" ]; then
    echo "[2/3] Creating virtual environment..."
    $PYTHON -m venv .venv
else
    echo "[2/3] Virtual environment already exists."
fi

# 2. Activate
source .venv/bin/activate

# 3. Install package in editable mode with dev dependencies
echo "[2/3] Installing package..."
pip install -e ".[dev]" -q

# 4. Verify
echo "[3/3] Verifying installation..."
$PYTHON -c "from multi_agent_brief.cli.main import main; print('OK: multi-agent-brief is ready')"

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  source .venv/bin/activate"
echo "  multi-agent-brief init my-workspace --language zh-CN"
echo "  # Add source files to my-workspace/input/"
echo "  multi-agent-brief run --config my-workspace/config.yaml"
