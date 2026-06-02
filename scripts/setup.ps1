# setup.ps1 - Windows PowerShell setup for multi-agent-brief-workflow
# Run: powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
# Or:  .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== multi-agent-brief-workflow setup ===" -ForegroundColor Cyan

# 1. Find Python
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $python = $cmd
        break
    }
}
if (-not $python) {
    Write-Host "ERROR: Python not found. Install Python 3.9+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}
Write-Host "[1/3] Found Python: $python" -ForegroundColor Green

# 2. Create venv
if (-not (Test-Path ".venv")) {
    Write-Host "[2/3] Creating virtual environment..." -ForegroundColor Yellow
    & $python -m venv .venv
} else {
    Write-Host "[2/3] Virtual environment already exists." -ForegroundColor Green
}

# 3. Activate and install
Write-Host "[3/3] Installing package..." -ForegroundColor Yellow
& ".\.venv\Scripts\python.exe" -m pip install -e ".[dev]" -q

# 4. Verify
& ".\.venv\Scripts\python.exe" -c "from multi_agent_brief.cli.main import main; print('OK: multi-agent-brief is ready')"

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  multi-agent-brief init my-workspace --language zh-CN"
Write-Host "  # Add source files to my-workspace\input\"
Write-Host "  multi-agent-brief run --config my-workspace\config.yaml"
Write-Host ""
Write-Host "Or run the demo:"
Write-Host "  multi-agent-brief init --demo"
Write-Host "  multi-agent-brief run --config brief-demo\config.yaml"
