@echo on
setlocal enabledelayedexpansion

REM ---------------------------------------------------------------
REM One-click launcher: starts the Bihar Agriculture Platform backend
REM and opens the portal in Chrome once the server is ready.
REM ---------------------------------------------------------------

set "PORT=8001"
set "URL=http://127.0.0.1:%PORT%/portal/"
set "HEALTH=http://127.0.0.1:%PORT%/health"
set "ROOT=%~dp0"
set "BACKEND_PS1=%ROOT%bihar-agriculture-platform\run-backend.ps1"

if not exist "%BACKEND_PS1%" (
  echo [ERROR] Cannot find backend script:
  echo         %BACKEND_PS1%
  pause
  exit /b 1
)

echo.
echo === Bihar Agriculture Portal launcher ===
echo  Port:   %PORT%
echo  URL:    %URL%
echo.

echo [1/3] Starting backend in a new window...
start "Bihar Portal Backend (port %PORT%)" powershell -NoExit -NoProfile -ExecutionPolicy Bypass -File "%BACKEND_PS1%"

echo [2/3] Waiting for backend at %HEALTH% (up to ~60s)...
powershell -NoProfile -Command ^
  "$u='%HEALTH%';" ^
  "for($i=0; $i -lt 60; $i++) {" ^
  "  try { $r = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 1;" ^
  "        if ($r.StatusCode -eq 200) { Write-Host '   backend is up.' -ForegroundColor Green; exit 0 } }" ^
  "  catch { Start-Sleep -Milliseconds 1000 } }" ^
  "Write-Host '   backend did not respond in time; opening URL anyway.' -ForegroundColor Yellow;" ^
  "exit 1"

echo [3/3] Opening Chrome...

where chrome >nul 2>nul
if %errorlevel%==0 (
  start "" chrome "%URL%"
  goto :done
)

if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
  start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "%URL%"
  goto :done
)

if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
  start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" "%URL%"
  goto :done
)

REM Registry lookup (covers non-standard Chrome installs)
for /f "tokens=2,*" %%A in ('reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" /ve 2^>nul ^| find /i "REG_SZ"') do set "CHROME=%%B"
if defined CHROME if exist "%CHROME%" (
  start "" "%CHROME%" "%URL%"
  goto :done
)
for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" /ve 2^>nul ^| find /i "REG_SZ"') do set "CHROME=%%B"
if defined CHROME if exist "%CHROME%" (
  start "" "%CHROME%" "%URL%"
  goto :done
)

REM Fallback: default browser
start "" "%URL%"

:done
echo.
echo Done. The backend window will keep running; close it to stop the server.
echo.
endlocal
exit /b 0
