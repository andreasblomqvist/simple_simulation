# SimpleSim Frontend Start Script (PowerShell)
# Starts the frontend server with proper directory handling

Write-Host "SimpleSim Frontend Start Script (Windows)"
Write-Host "========================================="

# Check if we're in the right directory
Write-Host "Current directory: $(Get-Location)"
if (-not (Test-Path "frontend")) {
    Write-Host "ERROR: frontend directory not found. Please run this script from the project root."
    exit 1
}

# Step 1: Kill any existing frontend processes
Write-Host "Killing existing frontend processes..."
try {
    Get-Process | Where-Object { $_.ProcessName -like "*vite*" -or $_.ProcessName -like "*node*" -or $_.ProcessName -like "*npm*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    foreach ($port in 3000,3001,3002,3003) {
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

# Step 2: Clear Vite cache
Write-Host "Clearing Vite cache..."
try {
    if (Test-Path "frontend/node_modules/.vite") {
        Remove-Item -Recurse -Force "frontend/node_modules/.vite" -ErrorAction SilentlyContinue
    }
    if (Test-Path "frontend/dist") {
        Remove-Item -Recurse -Force "frontend/dist" -ErrorAction SilentlyContinue
    }
    Write-Host "Vite cache cleared"
} catch {
    Write-Host "Warning: Error clearing Vite cache: $($_.Exception.Message)"
}

# Step 3: Wait for processes to fully terminate
Write-Host "Waiting for processes to terminate..."
Start-Sleep -Seconds 3

# Step 4: Check if package.json exists
if (-not (Test-Path "frontend/package.json")) {
    Write-Host "ERROR: package.json not found in frontend directory"
    exit 1
}

# Step 5: Check if dev script exists
$packageJson = Get-Content "frontend/package.json" | ConvertFrom-Json
if (-not $packageJson.scripts.dev) {
    Write-Host "ERROR: 'dev' script not found in package.json"
    exit 1
}

# Step 6: Ensure node_modules exists, otherwise run npm install
if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "node_modules not found, running npm install..."
    Start-Process -FilePath "npm" -ArgumentList @("install") -WorkingDirectory "frontend" -Wait -WindowStyle Normal
}

# Step 7: Start frontend server in visible window
Write-Host "Starting frontend server..."
try {
    $frontend = Start-Process -FilePath "npm" -ArgumentList @("run", "dev") -WorkingDirectory "frontend" -PassThru -WindowStyle Normal
    $frontendPid = $frontend.Id
    Write-Host "Frontend process started with PID: $frontendPid in visible window"
} catch {
    Write-Host "ERROR: Failed to start frontend server: $($_.Exception.Message)"
    exit 1
}

# Step 8: Wait for frontend to start
Write-Host "Waiting for frontend to start (this may take up to 60 seconds)..."
$frontendStarted = $false
$frontendPort = $null
$maxAttempts = 60

for ($i = 0; $i -lt $maxAttempts; $i++) {
    Start-Sleep -Seconds 1
    
    # Check if frontend process is still running
    try {
        $proc = Get-Process -Id $frontendPid -ErrorAction Stop
    } catch {
        Write-Host "ERROR: Frontend process died unexpectedly"
        exit 1
    }
    
    # Try to find which port the frontend is using
    foreach ($port in 3000,3001,3002,3003) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$port" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Frontend server is running on http://localhost:$port"
                $frontendStarted = $true
                $frontendPort = $port
                break
            }
        } catch {}
    }
    
    if ($frontendStarted) {
        break
    }
    
    if (($i + 1) % 10 -eq 0) {
        Write-Host "Still waiting for frontend... ($($i+1)/$maxAttempts)"
    }
}

if (-not $frontendStarted) {
    Write-Host "ERROR: Frontend server failed to start within $maxAttempts seconds"
    Write-Host "Frontend PID: $frontendPid"
    try {
        $proc = Get-Process -Id $frontendPid -ErrorAction Stop
        Write-Host "Frontend process is still running but not responding on expected ports"
        Write-Host "You may need to check the frontend logs manually"
    } catch {
        Write-Host "Frontend process has died"
    }
    exit 1
}

Write-Host ""
Write-Host "✅ Frontend server started successfully!"
Write-Host "Frontend: http://localhost:$frontendPort (PID: $frontendPid) - Running in visible window"
Write-Host ""
Write-Host "To stop frontend manually:"
Write-Host "   Stop-Process -Id $frontendPid"
Write-Host "   Or run: Stop-Process -Name vite,node,npm -Force" 