# setup.ps1 - Windows PowerShell setup for multi-agent-brief-workflow
# Run: powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
# Or:  .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== multi-agent-brief-workflow setup ===" -ForegroundColor Cyan

# --- Find Python ---
# Check multiple locations, skip Windows Store placeholder (exit code 49)
function Find-Python {
    # 1. Try py launcher (Python.org installer adds this)
    foreach ($cmd in @("py -3", "py")) {
        try {
            $ver = & cmd /c "$cmd --version 2>&1"
            if ($ver -match "Python 3\.\d+") { return $cmd }
        } catch {}
    }

    # 2. Try python from PATH (may be Windows Store stub)
    foreach ($cmd in @("python3", "python")) {
        try {
            $proc = Start-Process -FilePath $cmd -ArgumentList "--version" -NoNewWindow -Wait -PassThru -RedirectStandardOutput "NUL" -RedirectStandardError "NUL"
            if ($proc.ExitCode -eq 0) {
                $ver = & $cmd --version 2>&1
                if ($ver -match "Python 3\.\d+") { return $cmd }
            }
        } catch {}
    }

    # 3. Search common install locations
    $searchPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe",
        "C:\Python3*\python.exe",
        "C:\Program Files\Python3*\python.exe",
        "$env:USERPROFILE\.cache\codex-runtimes\*\dependencies\python\python.exe",
        "$env:USERPROFILE\.codex\runtimes\*\python.exe"
    )
    foreach ($pattern in $searchPaths) {
        $found = Get-Item $pattern -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
        if ($found) {
            try {
                $ver = & $found.FullName --version 2>&1
                if ($ver -match "Python 3\.\d+") { return $found.FullName }
            } catch {}
        }
    }

    return $null
}

$python = Find-Python

if (-not $python) {
    Write-Host ""
    Write-Host "ERROR: Python 3.9+ not found on this system." -ForegroundColor Red
    Write-Host ""
    Write-Host "The 'python' command may be a Windows Store placeholder." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To fix this, install real Python:" -ForegroundColor Yellow
    Write-Host "  1. Download from https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "  2. During install, CHECK 'Add Python to PATH'" -ForegroundColor White
    Write-Host "  3. Restart your terminal after install" -ForegroundColor White
    Write-Host ""
    Write-Host "Or use winget:" -ForegroundColor Yellow
    Write-Host "  winget install Python.Python.3.12" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Resolve full path for display
$pythonDisplay = $python
try { $pythonDisplay = "$python ($( & $python --version 2>&1 ))" } catch {}
Write-Host "[1/3] Found Python: $pythonDisplay" -ForegroundColor Green

# --- Create venv ---
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvDir = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path $venvDir)) {
    Write-Host "[2/3] Creating virtual environment..." -ForegroundColor Yellow
    & $python -m venv $venvDir
} else {
    Write-Host "[2/3] Virtual environment already exists." -ForegroundColor Green
}

# --- Install package ---
Write-Host "[3/3] Installing package..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip -q
& $venvPython -m pip install -e ".[dev]" -q

# --- Verify ---
& $venvPython -c "from multi_agent_brief.cli.main import main; print('OK: multi-agent-brief is ready')"

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  cd $projectRoot"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  multi-agent-brief init my-workspace --language zh-CN"
Write-Host "  # Add source files to my-workspace\input\"
Write-Host "  multi-agent-brief run --config my-workspace\config.yaml"
