$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
Set-Location $RootDir

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
    & .venv\Scripts\python.exe -m pip install -r requirements.txt
}

Write-Host "Starting MORPHE Dashboard at http://localhost:8501"
& .venv\Scripts\python.exe -m streamlit run app.py
