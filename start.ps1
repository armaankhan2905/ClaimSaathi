# Starts ClaimSaathi on Windows: backend (port 8000) and website (port 5173) in two windows.
#   powershell -ExecutionPolicy Bypass -File .\start.ps1
# Run setup.ps1 once first. Close the two windows to stop the app.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$venvPython = Join-Path $backend ".venv\Scripts\python.exe"

$ok = $false
if (Test-Path $venvPython) {
    try { & $venvPython -c "import uvicorn" 2>$null; $ok = ($LASTEXITCODE -eq 0) } catch { $ok = $false }
}
if (-not $ok -or -not (Test-Path (Join-Path $frontend "node_modules"))) {
    Write-Host "The app isn't set up on this computer yet. Running setup.ps1 first..." -ForegroundColor Yellow
    & (Join-Path $root "setup.ps1")
}

Start-Process powershell -WorkingDirectory $backend -ArgumentList @(
    "-NoExit", "-Command",
    "`$host.UI.RawUI.WindowTitle = 'ClaimSaathi backend'; & '$venvPython' -m uvicorn app.main:app --port 8000"
)
Start-Process powershell -WorkingDirectory $frontend -ArgumentList @(
    "-NoExit", "-Command",
    "`$host.UI.RawUI.WindowTitle = 'ClaimSaathi website'; npm run dev"
)

Write-Host "Waiting for the backend to start..."
$up = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://127.0.0.1:8000/api/health" | Out-Null
        $up = $true
        break
    } catch { Start-Sleep -Seconds 1 }
}
if ($up) {
    Write-Host "Running. Opening http://localhost:5173" -ForegroundColor Green
    Start-Process "http://localhost:5173"
} else {
    Write-Host "The backend didn't start. Check the 'ClaimSaathi backend' window for the error." -ForegroundColor Red
}
