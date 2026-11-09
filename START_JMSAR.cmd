@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo First run SETUP_WINDOWS.cmd
  pause
  exit /b 1
)
if not exist "vendor\SARScope\serve.py" (
  echo Original SARScope core is missing. Run SETUP_WINDOWS.cmd first.
  pause
  exit /b 1
)
if not exist "vendor\SARScope\.venv\Scripts\python.exe" (
  echo SARScope core environment is missing. Run SETUP_WINDOWS.cmd first.
  pause
  exit /b 1
)
start "SARScope Core - Local 8765" /D "%~dp0vendor\SARScope" "%~dp0vendor\SARScope\.venv\Scripts\python.exe" serve.py --port 8765 --strictPort
echo Starting JMSAR Research Workspace at http://127.0.0.1:8899
".venv\Scripts\python.exe" app.py
pause
