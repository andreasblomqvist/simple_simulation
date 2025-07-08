# SimpleSim Server Restart Script (PowerShell)
# Kills old instances and restarts backend and frontend servers cleanly

Write-Host "SimpleSim Server Restart Script (Windows)"
Write-Host "========================================="

# Check if we're in the right directory
Write-Host "Current directory: $(Get-Location)"
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: backend directory not found. Please run this script from the project root."
    exit 1
}

if (-not (Test-Path "frontend")) {
    Write-Host "ERROR: frontend directory not found. Please run this script from the project root."
    exit 1
}

# Step 1: Kill all existing server processes
Write-Host "Killing existing server processes..."
try {
    Get-Process | Where-Object { $_.ProcessName -like "*uvicorn*" -or $_.ProcessName -like "*python*" -or $_.ProcessName -like "*vite*" -or $_.ProcessName -like "*node*" -or $_.ProcessName -like "*npm*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    foreach ($port in 3000,3001,3002,3003,8000,8001) {
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

# Step 2: Clear all caches
Write-Host "Clearing all caches..."
try {
    # Clear Python cache
    Get-ChildItem -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    
    # Clear Vite cache
    if (Test-Path "frontend/node_modules/.vite") {
        Remove-Item -Recurse -Force "frontend/node_modules/.vite" -ErrorAction SilentlyContinue
    }
    if (Test-Path "frontend/dist") {
        Remove-Item -Recurse -Force "frontend/dist" -ErrorAction SilentlyContinue
    }
    
    Write-Host "All caches cleared"
} catch {
    Write-Host "Warning: Error clearing caches: $($_.Exception.Message)"
}

# Step 3: Wait for processes to fully terminate
Write-Host "Waiting for processes to terminate..."
Start-Sleep -Seconds 3

# Step 4: Start backend using the dedicated script
Write-Host "Starting backend server..."
try {
    $backendResult = & ".\scripts\start-backend.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Backend failed to start"
        exit 1
    }
    Write-Host "✅ Backend started successfully"
} catch {
    Write-Host "ERROR: Failed to start backend: $($_.Exception.Message)"
    exit 1
}

# Step 5: Start frontend using the dedicated script
Write-Host "Starting frontend server..."
try {
    $frontendResult = & ".\scripts\start-frontend.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Frontend failed to start"
        exit 1
    }
    Write-Host "✅ Frontend started successfully"
} catch {
    Write-Host "ERROR: Failed to start frontend: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Write-Host "✅ Server restart complete!"
Write-Host "Both servers are now running in separate terminal windows where you can see their output."
Write-Host ""
Write-Host "To stop servers manually:"
Write-Host "   Stop-Process -Name uvicorn,vite,node,npm -Force"
Write-Host ""
Write-Host "To restart servers:"
Write-Host "   .\scripts\restart-servers.ps1" 