# SimpleSim Docker Build Script
# Works with Docker CLI without requiring Docker Desktop GUI

param(
    [switch]$Build,
    [switch]$Run,
    [switch]$Stop,
    [switch]$All,
    [string]$Registry = "localhost:5000"
)

$ErrorActionPreference = "Stop"

Write-Host "=== SimpleSim Docker Management ===" -ForegroundColor Yellow

# Get project root directory
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Test-DockerDaemon {
    try {
        docker version | Out-Null
        return $true
    }
    catch {
        Write-Host "❌ Docker daemon is not running. Attempting to start..." -ForegroundColor Red
        
        # Try to start Docker service
        try {
            Start-Service -Name "Docker Desktop Service" -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 10
            docker version | Out-Null
            return $true
        }
        catch {
            Write-Host "❌ Cannot start Docker daemon. Please ensure Docker is installed and running." -ForegroundColor Red
            Write-Host "Alternatives:" -ForegroundColor Yellow
            Write-Host "1. Run: .\scripts\start-simplesim.bat (No Docker required)" -ForegroundColor Cyan
            Write-Host "2. Start Docker Desktop manually" -ForegroundColor Cyan
            return $false
        }
    }
}

function Build-Images {
    Write-Host "Building SimpleSim Docker images..." -ForegroundColor Green
    
    Set-Location $ProjectRoot
    
    # Build backend image
    Write-Host "Building backend image..." -ForegroundColor Yellow
    docker build -f Dockerfile.backend -t simplesim-backend:latest .
    
    # Build frontend image  
    Write-Host "Building frontend image..." -ForegroundColor Yellow
    docker build -f Dockerfile.frontend -t simplesim-frontend:latest .
    
    Write-Host "✅ Images built successfully!" -ForegroundColor Green
    docker images | Select-String "simplesim"
}

function Run-Containers {
    Write-Host "Starting SimpleSim containers..." -ForegroundColor Green
    
    # Stop existing containers
    Stop-Containers
    
    # Create network if it doesn't exist
    try {
        docker network create simplesim-network 2>$null
    } catch {
        Write-Host "Network already exists or error creating network" -ForegroundColor Yellow
    }
    
    # Run backend container
    Write-Host "Starting backend container..." -ForegroundColor Yellow
    docker run -d `
        --name simplesim-backend `
        --network simplesim-network `
        -p 8000:8000 `
        simplesim-backend:latest
    
    # Run frontend container
    Write-Host "Starting frontend container..." -ForegroundColor Yellow
    docker run -d `
        --name simplesim-frontend `
        --network simplesim-network `
        -p 3000:3000 `
        simplesim-frontend:latest
    
    # Wait for services to start
    Start-Sleep -Seconds 10
    
    # Check status
    Show-Status
}

function Stop-Containers {
    Write-Host "Stopping SimpleSim containers..." -ForegroundColor Red
    
    docker stop simplesim-backend 2>$null
    docker stop simplesim-frontend 2>$null  
    docker rm simplesim-backend 2>$null
    docker rm simplesim-frontend 2>$null
    
    Write-Host "✅ Containers stopped and removed" -ForegroundColor Green
}

function Show-Status {
    Write-Host "=== Container Status ===" -ForegroundColor Yellow
    
    $containers = docker ps --filter "name=simplesim" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    if ($containers) {
        $containers
    } else {
        Write-Host "❌ No SimpleSim containers running" -ForegroundColor Red
    }
    
    Write-Host "`nService Health Check:" -ForegroundColor Yellow
    
    # Check backend
    try {
        $backend = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
        Write-Host "✅ Backend: Running (Status: $($backend.StatusCode))" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Backend: Not responding" -ForegroundColor Red
    }
    
    # Check frontend
    try {
        $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        Write-Host "✅ Frontend: Running (Status: $($frontend.StatusCode))" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Frontend: Not responding" -ForegroundColor Red
    }
    
    Write-Host "`nAccess URLs:" -ForegroundColor Yellow
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
}

# Main execution
try {
    if (!(Test-DockerDaemon)) {
        exit 1
    }
    
    if ($Stop) {
        Stop-Containers
    }
    elseif ($Build) {
        Build-Images
    }
    elseif ($Run) {
        Run-Containers
    }
    elseif ($All -or (!$Build -and !$Run -and !$Stop)) {
        Build-Images
        Run-Containers
    }
    else {
        Show-Status
    }
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nFallback option: Use .\scripts\start-simplesim.bat for non-Docker setup" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n=== Docker Operation Complete ===" -ForegroundColor Green 