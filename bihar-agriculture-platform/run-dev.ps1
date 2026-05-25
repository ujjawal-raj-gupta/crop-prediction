$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$backend = Join-Path $PSScriptRoot "run-backend.ps1"
$frontend = Join-Path $PSScriptRoot "run-frontend.ps1"

if (!(Test-Path $backend)) { throw "Missing run-backend.ps1" }
if (!(Test-Path $frontend)) { throw "Missing run-frontend.ps1" }

Write-Host "Starting Bihar Agriculture Platform (dev)..." -ForegroundColor Green
Write-Host "- Backend:  http://127.0.0.1:8001 (FastAPI)" -ForegroundColor Gray
Write-Host "- Frontend: http://127.0.0.1:5173 (Vite/React)" -ForegroundColor Gray

# Start backend in a new PowerShell window
Start-Process powershell -ArgumentList @(
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-File", $backend
)

Start-Sleep -Seconds 2

# Start frontend in a new PowerShell window
Start-Process powershell -ArgumentList @(
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-File", $frontend
)

Start-Sleep -Seconds 2

# Open the frontend in default browser
Start-Process "http://127.0.0.1:5173/"

Write-Host "Launched dev servers. If the frontend says API error, confirm backend window is running." -ForegroundColor Cyan

