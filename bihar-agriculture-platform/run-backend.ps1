$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$backendDir = Join-Path $PSScriptRoot "backend"
if (!(Test-Path $backendDir)) {
  throw "backend/ folder not found at $backendDir"
}

Set-Location $backendDir

if (!(Test-Path ".venv")) {
  Write-Host "[backend] Creating venv..." -ForegroundColor Cyan
  python -m venv .venv
}

Write-Host "[backend] Activating venv..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"

Write-Host "[backend] Installing requirements..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "[backend] Starting FastAPI on http://127.0.0.1:8001 ..." -ForegroundColor Green
uvicorn src.main:app --reload --host 127.0.0.1 --port 8001

