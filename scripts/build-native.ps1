$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
cmake -S native -B native/build -DCMAKE_BUILD_TYPE=Release
if ($LASTEXITCODE -ne 0) { throw "CMake configuration failed." }
cmake --build native/build --config Release
if ($LASTEXITCODE -ne 0) { throw "Native build failed." }
ctest --test-dir native/build -C Release --output-on-failure
if ($LASTEXITCODE -ne 0) { throw "Native tests failed." }