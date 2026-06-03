# Start FastAPI with NPK sensor on USB serial (default COM3).
param(
  [string]$SerialPort = "COM3",
  [int]$HttpPort = 8001,
  [string]$ListenHost = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
$backendDir = Join-Path $PSScriptRoot "backend"
Set-Location $backendDir

if (!(Test-Path ".venv")) {
  Write-Host "[sensor] Creating venv..." -ForegroundColor Cyan
  python -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt -q

$env:NPK_SERIAL_PORT = $SerialPort
$env:NPK_SERIAL_BAUD = "9600"
if (-not $env:NPK_MGKG_TO_KGHA) { $env:NPK_MGKG_TO_KGHA = "2.0" }

Write-Host "[sensor] NPK_SERIAL_PORT=$SerialPort  NPK_MGKG_TO_KGHA=$($env:NPK_MGKG_TO_KGHA)" -ForegroundColor Cyan
Write-Host "[sensor] API: http://${ListenHost}:${HttpPort}/api/v1/sensor/read" -ForegroundColor Cyan
Write-Host "[sensor] Portal crop page: http://${ListenHost}:${HttpPort}/portal/crop.html" -ForegroundColor Green
Write-Host "[sensor] Firmware required: hardware/npk_sensor/npk_sensor_web.ino" -ForegroundColor Yellow

uvicorn src.main:app --host $ListenHost --port $HttpPort
