$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$frontendDir = Join-Path $PSScriptRoot "frontend"
if (!(Test-Path $frontendDir)) {
  throw "frontend/ folder not found at $frontendDir"
}

Set-Location $frontendDir

function Require-Command($cmd) {
  $c = Get-Command $cmd -ErrorAction SilentlyContinue
  if (-not $c) {
    throw "Missing '$cmd'. Install Node.js LTS from https://nodejs.org/ (includes npm). Then reopen PowerShell."
  }
}

Require-Command "node"
Require-Command "npm"

if (!(Test-Path "node_modules")) {
  Write-Host "[frontend] Installing npm dependencies..." -ForegroundColor Cyan
  npm install
}

Write-Host "[frontend] Starting Vite dev server on http://127.0.0.1:5173 ..." -ForegroundColor Green
npm run dev -- --host 127.0.0.1 --port 5173

