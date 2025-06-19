# SimpleSim Production Setup Script (No Docker Required)
# This script sets up and runs SimpleSim in production mode

param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$All,
    [switch]$Stop,
    [string]$Host = "0.0.0.0",
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 3000
)

$ErrorActionPreference = "Stop"

Write-Host "=== SimpleSim Production Setup ===" -ForegroundColor Yellow

# Get project root directory
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Start-Backend {
    Write-Host "Starting Backend Server..." -ForegroundColor Green
    
    # Activate virtual environment and start backend
    Set-Location $ProjectRoot
    
    # Check if virtual environment exists
    if (!(Test-Path ".venv")) {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
        python -m venv .venv
    }
    
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
    
    # Install/update dependencies
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Start backend server
    Write-Host "Backend starting on http://${Host}:${BackendPort}" -ForegroundColor Green
    Start-Process -NoNewWindow -FilePath "uvicorn" -ArgumentList "backend.main:app", "--host", $Host, "--port", $BackendPort, "--reload"
}

function Start-Frontend {
    Write-Host "Starting Frontend Server..." -ForegroundColor Green
    
    Set-Location "$ProjectRoot\frontend"
    
    # Install dependencies if needed
    if (!(Test-Path "node_modules")) {
        Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
        npm install
    }
    
    # Build for production
    Write-Host "Building frontend for production..." -ForegroundColor Yellow
    npm run build
    
    # Serve production build
    if (!(Get-Command "serve" -ErrorAction SilentlyContinue)) {
        Write-Host "Installing serve globally..." -ForegroundColor Yellow
        npm install -g serve
    }
    
    Write-Host "Frontend starting on http://${Host}:${FrontendPort}" -ForegroundColor Green
    Start-Process -NoNewWindow -FilePath "serve" -ArgumentList "-s", "dist", "-l", $FrontendPort
}

function Stop-Services {
    Write-Host "Stopping SimpleSim services..." -ForegroundColor Red
    
    # Stop backend (uvicorn processes)
    Get-Process | Where-Object { $_.ProcessName -like "*uvicorn*" -or $_.CommandLine -like "*backend.main:app*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Stop frontend (serve processes)
    Get-Process | Where-Object { $_.ProcessName -like "*serve*" -or $_.CommandLine -like "*serve -s dist*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Stop Node processes serving on port 3000
    $port3000 = netstat -ano | Select-String ":3000.*LISTENING"
    if ($port3000) {
        $pid = ($port3000 -split '\s+')[-1]
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "Services stopped." -ForegroundColor Green
}

function Show-Status {
    Write-Host "=== Service Status ===" -ForegroundColor Yellow
    
    # Check backend
    try {
        $backend = Invoke-WebRequest -Uri "http://localhost:$BackendPort/health" -UseBasicParsing -TimeoutSec 5
        Write-Host "✅ Backend: Running (Status: $($backend.StatusCode))" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Backend: Not running" -ForegroundColor Red
    }
    
    # Check frontend
    try {
        $frontend = Invoke-WebRequest -Uri "http://localhost:$FrontendPort" -UseBasicParsing -TimeoutSec 5
        Write-Host "✅ Frontend: Running (Status: $($frontend.StatusCode))" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Frontend: Not running" -ForegroundColor Red
    }
    
    Write-Host "`nAccess URLs:" -ForegroundColor Yellow
    Write-Host "Frontend: http://localhost:$FrontendPort" -ForegroundColor Cyan
    Write-Host "Backend API: http://localhost:$BackendPort" -ForegroundColor Cyan
    Write-Host "API Docs: http://localhost:$BackendPort/docs" -ForegroundColor Cyan
}

# Main execution
try {
    if ($Stop) {
        Stop-Services
    }
    elseif ($All -or (!$Backend -and !$Frontend)) {
        Stop-Services
        Start-Sleep -Seconds 2
        Start-Backend
        Start-Sleep -Seconds 5
        Start-Frontend
        Start-Sleep -Seconds 3
        Show-Status
    }
    elseif ($Backend) {
        Start-Backend
        Start-Sleep -Seconds 3
        Show-Status
    }
    elseif ($Frontend) {
        Start-Frontend
        Start-Sleep -Seconds 3
        Show-Status
    }
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green 