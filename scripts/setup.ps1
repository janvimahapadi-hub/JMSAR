$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
  if (!(Get-Command git -ErrorAction SilentlyContinue)) { throw "Git is required. Install Git for Windows and reopen the terminal." }
  if (!(Get-Command py -ErrorAction SilentlyContinue)) { throw "Python 3.12 (64-bit) is required. Install it and reopen terminal." }
  & py -3.12 -c "import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize('P')==8"
  if ($LASTEXITCODE -ne 0) { throw "Use 64-bit Python 3.12." }

  $core = Join-Path $root "vendor\SARScope"
  if (!(Test-Path (Join-Path $core "serve.py"))) {
    New-Item -ItemType Directory -Force -Path (Join-Path $root "vendor") | Out-Null
    Write-Host "Cloning the original, credited SARScope core into ignored vendor/SARScope..."
    & git clone --depth 1 https://github.com/keyurck7/SARScope.git $core
    if ($LASTEXITCODE -ne 0) { throw "Could not clone SARScope source." }
  }

  $pyMain = Join-Path $root ".venv\Scripts\python.exe"
  $pyCore = Join-Path $core ".venv\Scripts\python.exe"
  if (!(Test-Path $pyMain)) { & py -3.12 -m venv (Join-Path $root ".venv") }
  if (!(Test-Path $pyCore)) { & py -3.12 -m venv (Join-Path $core ".venv") }
  & $pyMain -m pip install -r (Join-Path $root "requirements.txt")
  if ($LASTEXITCODE -ne 0) { throw "JMSAR dependencies failed." }
  & $pyCore -m pip install -r (Join-Path $core "requirements-viewer.txt")
  if ($LASTEXITCODE -ne 0) { throw "SARScope viewer dependencies failed." }

  Write-Host ""
  Write-Host "Done. No model weights or Earth Engine credentials were installed."
  Write-Host "Run START_JMSAR.cmd to view the genuine saved Mannheim 2021 case."
} finally { Pop-Location }
