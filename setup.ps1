# ClaimSaathi one-time setup for Windows. Run from the project folder:
#   powershell -ExecutionPolicy Bypass -File .\setup.ps1
#
# Safe to run again. It (re)builds backend\.venv for THIS computer, installs packages,
# creates backend\.env if missing, adds the demo account and installs the website packages.
# A .venv copied from another computer points at that computer's Python and won't start,
# which is why sign-in fails with "Can't reach the server" on a copied folder.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$venvPython = Join-Path $backend ".venv\Scripts\python.exe"

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

# ---- find Python 3.12+ ----
Step "Looking for Python 3.12 or newer"
$python = $null
foreach ($candidate in @(@("py", "-3"), @("python"), @("python3"))) {
    $exe = $candidate[0]
    $pre = @($candidate | Select-Object -Skip 1)
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
    try {
        $ver = & $exe @pre -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
    } catch { continue }
    if ($LASTEXITCODE -eq 0 -and $ver -and [version]$ver -ge [version]"3.12") {
        $python = $candidate
        Write-Host "Found Python $ver ($($candidate -join ' '))"
        break
    }
}
if (-not $python) {
    throw "Python 3.12+ not found. Install it from https://www.python.org/downloads/ (tick 'Add python.exe to PATH'), then run this again."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "Node.js not found. Install Node.js 20+ from https://nodejs.org/, then run this again."
}

# ---- backend virtual environment ----
Step "Preparing the backend Python environment"
$venvWorks = $false
if (Test-Path $venvPython) {
    try {
        & $venvPython -c "import sys" 2>$null
        $venvWorks = ($LASTEXITCODE -eq 0)
    } catch { $venvWorks = $false }
}
if ((Test-Path (Join-Path $backend ".venv")) -and -not $venvWorks) {
    Write-Host "Existing backend\.venv doesn't work on this computer (probably copied from another one). Rebuilding it."
    Remove-Item -Recurse -Force (Join-Path $backend ".venv")
}
if (-not $venvWorks) {
    $exe = $python[0]
    $pre = @($python | Select-Object -Skip 1)
    & $exe @pre -m venv (Join-Path $backend ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Couldn't create backend\.venv" }
}

Step "Installing backend packages (first time takes a few minutes)"
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r (Join-Path $backend "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

# ---- settings ----
$envFile = Join-Path $backend ".env"
if (-not (Test-Path $envFile)) {
    Step "Creating backend\.env from .env.example"
    Copy-Item (Join-Path $backend ".env.example") $envFile
    $secret = & $venvPython -c "import secrets; print(secrets.token_urlsafe(48))"
    (Get-Content $envFile) -replace '^JWT_SECRET=.*', "JWT_SECRET=$secret" | Set-Content -Encoding utf8 $envFile
    Write-Host "Add GROQ_API_KEY=... to backend\.env later if you want AI explanations (optional)."
}

Step "Setting up the database and demo account"
Push-Location $backend
try {
    & $venvPython -m app.seed
    if ($LASTEXITCODE -ne 0) { throw "Seeding the database failed" }
} finally { Pop-Location }

# ---- website ----
Step "Installing website packages"
Push-Location $frontend
try {
    npm install
    if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
} finally { Pop-Location }

Write-Host "`nSetup done. Start the app with:  powershell -ExecutionPolicy Bypass -File .\start.ps1" -ForegroundColor Green
