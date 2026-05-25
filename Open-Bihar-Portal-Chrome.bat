@echo off
setlocal

set "URL=http://127.0.0.1:8001/portal/"

REM Tries to open Google Chrome in "app mode" (standalone window).
REM If Chrome isn't found in PATH, falls back to default browser.

where chrome >nul 2>nul
if %errorlevel%==0 (
  start "" chrome --app="%URL%" --new-window
  exit /b 0
)

if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
  start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" --app="%URL%" --new-window
  exit /b 0
)

if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
  start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" --app="%URL%" --new-window
  exit /b 0
)

REM Registry lookup (covers non-standard installs)
for /f "tokens=2,*" %%A in ('reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" /ve 2^>nul ^| find /i "REG_SZ"') do set "CHROME=%%B"
if defined CHROME if exist "%CHROME%" (
  start "" "%CHROME%" --app="%URL%" --new-window
  exit /b 0
)
for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" /ve 2^>nul ^| find /i "REG_SZ"') do set "CHROME=%%B"
if defined CHROME if exist "%CHROME%" (
  start "" "%CHROME%" --app="%URL%" --new-window
  exit /b 0
)

REM Fallback: default browser
start "" "%URL%"
