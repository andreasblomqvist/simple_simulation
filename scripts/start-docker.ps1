# Docker Desktop Startup Script
# Starts Docker Desktop and builds SimpleSim containers

param(
    [switch]$BuildAfterStart
)

Write-Host "=== Docker Desktop Startup ===" -ForegroundColor Yellow

function Test-IsAdmin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Start-DockerDesktop {
    if (!(Test-IsAdmin)) {
        Write-Host "❌ Administrator privileges required to start Docker Desktop" -ForegroundColor Red
        Write-Host "Please run PowerShell as Administrator and try again" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "Starting Docker Desktop..." -ForegroundColor Green
    
    # Check if Docker Desktop is already running
    $dockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
    if ($dockerProcess) {
        Write-Host "✅ Docker Desktop is already running" -ForegroundColor Green
        return $true
    }
    
    # Start Docker Desktop
    try {
        Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe" -WindowStyle Hidden
        Write-Host "⏳ Waiting for Docker Desktop to start..." -ForegroundColor Yellow
        
        # Wait for Docker Desktop to be ready (max 2 minutes)
        $timeout = 120
        $elapsed = 0
        
        while ($elapsed -lt $timeout) {
            Start-Sleep -Seconds 5
            $elapsed += 5
            
            try {
                docker version | Out-Null
                Write-Host "✅ Docker Desktop is ready!" -ForegroundColor Green
                return $true
            }
            catch {
                Write-Host "⏳ Still waiting... ($elapsed/$timeout seconds)" -ForegroundColor Yellow
            }
        }
        
        Write-Host "❌ Docker Desktop failed to start within $timeout seconds" -ForegroundColor Red
        return $false
    }
    catch {
        Write-Host "❌ Failed to start Docker Desktop: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Show-Instructions {
    Write-Host "`n=== Manual Steps ===" -ForegroundColor Yellow
    Write-Host "1. Right-click Windows Start button → 'Windows PowerShell (Admin)'" -ForegroundColor Cyan
    Write-Host "2. Navigate to project: cd 'C:\Users\andre\Code\SimpleSim'" -ForegroundColor Cyan
    Write-Host "3. Run: .\scripts\start-docker.ps1 -BuildAfterStart" -ForegroundColor Cyan
    Write-Host "`nOr use the working alternative:" -ForegroundColor Yellow
    Write-Host ".\scripts\start-simplesim.bat" -ForegroundColor Green
}

# Main execution
if (Start-DockerDesktop) {
    if ($BuildAfterStart) {
        Write-Host "`nBuilding SimpleSim containers..." -ForegroundColor Green
        & "$PSScriptRoot\docker-build.ps1" -All
    } else {
        Write-Host "`nDocker Desktop is ready! Now you can run:" -ForegroundColor Green
        Write-Host ".\scripts\docker-build.ps1 -All" -ForegroundColor Cyan
    }
} else {
    Show-Instructions
} 