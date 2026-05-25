@echo off
setlocal

set "URL=http://127.0.0.1:8001/portal/"

REM Normal Chrome tab (or default browser if Chrome missing)

where chrome >nul 2>nul
if %errorlevel%==0 (
  start "" chrome "%URL%"
  exit /b 0
)

start "" "%URL%"

