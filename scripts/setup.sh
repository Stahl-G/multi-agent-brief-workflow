#!/usr/bin/env bash
# Setup script for multi-agent-brief-workflow
# Run this after cloning to get a working environment.
# Windows users: use scripts/setup.ps1 instead, or install Git Bash.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== multi-agent-brief-workflow setup ==="

# Find Python (prefer python3, fall back to python)
PYTHON=python3
command -v python3 >/dev/null 2>&1 || PYTHON=python

# 1. Create venv if missing
if [ ! -d ".venv" ]; then
    echo "[1/3] Creating virtual environment..."
    $PYTHON -m venv .venv
else
    echo "[1/3] Virtual environment already exists."
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
echo ""
echo "Or run the demo:"
echo "  multi-agent-brief init --demo"
echo "  multi-agent-brief run --config brief-demo/config.yaml"
