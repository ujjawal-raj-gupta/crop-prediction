# Creates a public shareable link for the Bihar portal (requires backend running on port 8001).
# Keep this PowerShell window open — closing it stops the public link.

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$BackendDir = Join-Path $Root "bihar-agriculture-platform\backend"
$Port = 8001

# Refresh PATH so cloudflared is found after winget install
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")

$Cloudflared = "C:\Program Files (x86)\cloudflared\cloudflared.exe"
if (-not (Test-Path $Cloudflared)) {
  $Cloudflared = (Get-Command cloudflared -ErrorAction SilentlyContinue)?.Source
}
if (-not $Cloudflared) {
  Write-Host "cloudflared not installed. Run: winget install Cloudflare.cloudflared" -ForegroundColor Red
  exit 1
}

# LAN IP for same-WiFi sharing
$LanIp = (Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -notmatch '^127\.' -and $_.PrefixOrigin -ne 'WellKnown' } |
  Select-Object -First 1).IPAddress

# Start backend if not listening
$listening = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $listening) {
  Write-Host "Starting backend on port $Port ..." -ForegroundColor Yellow
  Start-Process -FilePath "$BackendDir\.venv\Scripts\python.exe" `
    -ArgumentList "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "$Port" `
    -WorkingDirectory $BackendDir -WindowStyle Minimized
  Start-Sleep -Seconds 4
}

Write-Host ""
Write-Host "=== Bihar Agriculture Portal — shareable links ===" -ForegroundColor Green
Write-Host ""
Write-Host "On your PC:" -ForegroundColor Cyan
Write-Host "  http://127.0.0.1:$Port/portal/"
if ($LanIp) {
  Write-Host ""
  Write-Host "Same Wi-Fi (phone/laptop nearby):" -ForegroundColor Cyan
  Write-Host "  http://${LanIp}:$Port/portal/"
}
Write-Host ""
Write-Host "Public internet link (starting tunnel — wait ~10 sec)..." -ForegroundColor Cyan
Write-Host "  Portal will be: https://XXXX.trycloudflare.com/portal/"
Write-Host ""
Write-Host "Keep this window open. Press Ctrl+C to stop the public link." -ForegroundColor Yellow
Write-Host ""

& $Cloudflared tunnel --url "http://127.0.0.1:$Port"
