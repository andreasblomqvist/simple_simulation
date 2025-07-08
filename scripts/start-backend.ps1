# SimpleSim Backend Start Script (PowerShell)
# Starts the backend server with proper Python path configuration

Write-Host "SimpleSim Backend Start Script (Windows)"
Write-Host "========================================="

# Set the correct Python path where packages are installed
$pythonPath = "C:\Users\andre\AppData\Local\Programs\Python\Python313\python.exe"

# Check if we're in the right directory
Write-Host "Current directory: $(Get-Location)"
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: backend directory not found. Please run this script from the project root."
    exit 1
}

# Verify Python and uvicorn are available
Write-Host "Verifying Python and uvicorn installation..."
try {
    $uvicornVersion = & $pythonPath -m uvicorn --version 2>&1
    Write-Host "✅ Using Python: $uvicornVersion"
} catch {
    Write-Host "ERROR: uvicorn not found. Please install requirements: pip install -r backend/requirements.txt"
    exit 1
}

# Step 1: Kill any existing backend processes
Write-Host "Killing existing backend processes..."
try {
    Get-Process | Where-Object { $_.ProcessName -like "*uvicorn*" -or $_.ProcessName -like "*python*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    foreach ($port in 8000,8001) {
        $conns = netstat -ano 2>$null | Select-String ":$port\s" -ErrorAction SilentlyContinue
        if ($conns) {
            foreach ($conn in $conns) {
                $parts = $conn -split '\s+'
                $procId = $parts[-1]
                if ($procId -match '^\d+$') {
                    Write-Host "Killing process on port $port (PID $procId)"
                    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                }
            }
        }
    }
} catch {
    Write-Host "Warning: Error killing processes: $($_.Exception.Message)"
}

# Step 2: Clear Python cache
Write-Host "Clearing Python cache..."
try {
    Get-ChildItem -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "Python cache cleared"
} catch {
    Write-Host "Warning: Error clearing Python cache: $($_.Exception.Message)"
}

# Step 3: Wait for processes to fully terminate
Write-Host "Waiting for processes to terminate..."
Start-Sleep -Seconds 3

# Step 4: Start backend server with proper PYTHONPATH
Write-Host "Starting backend server with PYTHONPATH=backend..."
try {
    $backend = Start-Process -FilePath "cmd" -ArgumentList @("/c", "set PYTHONPATH=backend & $pythonPath -m uvicorn main:app --reload --host 0.0.0.0 --port 8000") -PassThru -WindowStyle Normal -WorkingDirectory "backend"
    $backendPid = $backend.Id
    Write-Host "Backend process started with PID: $backendPid in visible window"
} catch {
    Write-Host "ERROR: Failed to start backend server: $($_.Exception.Message)"
    exit 1
}

# Step 5: Wait for backend to start
Write-Host "Waiting for backend to start..."
$backendStarted = $false
$maxAttempts = 30

for ($i = 0; $i -lt $maxAttempts; $i++) {
    Start-Sleep -Seconds 1
    
    # Check if process is still running
    try {
        $proc = Get-Process -Id $backendPid -ErrorAction Stop
    } catch {
        Write-Host "ERROR: Backend process died unexpectedly"
        exit 1
    }
    
    # Test health endpoint
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 2 -ErrorAction Stop
        Write-Host "✅ Backend server is running on http://localhost:8000"
        $backendStarted = $true
        break
    } catch {}
    
    if (($i + 1) % 5 -eq 0) {
        Write-Host "Waiting for backend... ($($i+1)/$maxAttempts)"
    }
}

if (-not $backendStarted) {
    Write-Host "ERROR: Backend server failed to start within $maxAttempts seconds"
    Write-Host "Backend PID: $backendPid"
    try {
        $proc = Get-Process -Id $backendPid -ErrorAction Stop
        Write-Host "Backend process is running but not responding on health endpoint"
        Write-Host "You may need to check the backend logs manually"
    } catch {
        Write-Host "Backend process has died"
    }
    exit 1
}

Write-Host ""
Write-Host "✅ Backend server started successfully!"
Write-Host "Backend: http://localhost:8000 (PID: $backendPid) - Running in visible window"
Write-Host ""
Write-Host "To stop backend manually:"
Write-Host "   Stop-Process -Id $backendPid"
Write-Host "   Or run: Stop-Process -Name uvicorn,python -Force" 