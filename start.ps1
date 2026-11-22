# Starts ClaimSaathi on Windows: backend and website in two windows.
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

# Determine backend port: check if port 8000 is occupied by something else
$port = 8000
$conn8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($conn8000) {
    # Check if port 8000 is actually ClaimSaathi
    $isClaimSaathi8000 = $false
    try {
        $res = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($res.status -eq "ok") { $isClaimSaathi8000 = $true }
    } catch {}
    if (-not $isClaimSaathi8000) {
        $port = 8001
        Write-Host "Port 8000 is in use by another app. Using port $port for ClaimSaathi." -ForegroundColor Yellow
    }
}

# Configure frontend/.env with the selected port
$frontendEnv = Join-Path $frontend ".env"
"VITE_BACKEND_URL=http://localhost:$port`nAPI_PORT=$port" | Set-Content -Encoding utf8 $frontendEnv

# Check if backend is already running on $port
$backendRunning = $false
try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
    if ($res.status -eq "ok") { $backendRunning = $true }
} catch {}

if (-not $backendRunning) {
    Start-Process powershell -WorkingDirectory $backend -ArgumentList @(
        "-NoExit", "-Command",
        "`$host.UI.RawUI.WindowTitle = 'ClaimSaathi backend'; & '$venvPython' -m uvicorn app.main:app --port $port"
    )
} else {
    Write-Host "ClaimSaathi backend is already running on port $port." -ForegroundColor Green
}

# Check if frontend is already running
$frontendRunning = $false
try {
    $web = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 1 -ErrorAction SilentlyContinue
    if ($web.StatusCode -eq 200) { $frontendRunning = $true }
} catch {}

if (-not $frontendRunning) {
    Start-Process powershell -WorkingDirectory $frontend -ArgumentList @(
        "-NoExit", "-Command",
        "`$host.UI.RawUI.WindowTitle = 'ClaimSaathi website'; npm run dev"
    )
} else {
    Write-Host "ClaimSaathi website is already running on port 5173." -ForegroundColor Green
}

Write-Host "Waiting for the backend to respond on port $port..."
$up = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://127.0.0.1:$port/api/health" | Out-Null
        $up = $true
        break
    } catch { Start-Sleep -Seconds 1 }
}
if ($up) {
    Write-Host "ClaimSaathi is running! Opening http://localhost:5173" -ForegroundColor Green
    Start-Process "http://localhost:5173"
} else {
    Write-Host "The backend didn't start. Check the 'ClaimSaathi backend' window for the error." -ForegroundColor Red
}
