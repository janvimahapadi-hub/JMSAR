@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1"
if errorlevel 1 (
  echo Setup failed. Read the message above.
  pause
  exit /b 1
)
echo.
echo Setup complete. Run START_JMSAR.cmd next.
pause
