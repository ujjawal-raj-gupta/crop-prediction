@echo on
setlocal

set "PORT=8001"
set "COM=COM3"
set "URL=http://127.0.0.1:%PORT%/portal/crop.html"
set "HEALTH=http://127.0.0.1:%PORT%/health"
set "ROOT=%~dp0"
set "SENSOR_PS1=%ROOT%bihar-agriculture-platform\run-backend-sensor.ps1"

if not exist "%SENSOR_PS1%" (
  echo [ERROR] Missing %SENSOR_PS1%
  pause
  exit /b 1
)

echo.
echo === Bihar Portal + NPK sensor (COM3) ===
echo  Backend:  port %PORT%
echo  Arduino:  %COM%  (change in run-backend-sensor.ps1 if needed)
echo  Crop UI:  %URL%
echo.
echo  IMPORTANT: Flash hardware\npk_sensor\npk_sensor_web.ino to your Arduino.
echo  Close Arduino Serial Monitor before using Read via server.
echo.

echo [1/3] Starting backend with sensor env...
start "Bihar Portal + Sensor COM3" powershell -NoExit -NoProfile -ExecutionPolicy Bypass -File "%SENSOR_PS1%" -SerialPort %COM%

echo [2/3] Waiting for backend...
powershell -NoProfile -Command ^
  "$u='%HEALTH%'; for($i=0;$i -lt 60;$i++) { try { $r=Invoke-WebRequest $u -UseBasicParsing -TimeoutSec 1; if($r.StatusCode -eq 200){Write-Host '   backend up.' -ForegroundColor Green; exit 0} } catch { Start-Sleep 1 } }; exit 1"

echo [3/3] Opening crop page in Chrome...
where chrome >nul 2>nul && (start "" chrome "%URL%" & goto :done)
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "%URL%" & goto :done
start "" "%URL%"

:done
echo.
echo Use "Read via server" on the crop page, or Connect USB sensor in Chrome.
echo.
endlocal
exit /b 0
