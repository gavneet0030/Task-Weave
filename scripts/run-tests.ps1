$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
& ".\.venv\Scripts\python.exe" -m pytest
if ($LASTEXITCODE -ne 0) { throw "Python tests failed." }