# SimpleSim Server Restart Script (PowerShell)
# Kills old instances and restarts backend and frontend servers cleanly

Write-Host "SimpleSim Server Restart Script (Windows)"
Write-Host "========================================="

# Function to kill processes by name
function Kill-ByName {
    param($name)
    $procs = Get-Process | Where-Object { $_.ProcessName -like $name }
    foreach ($proc in $procs) {
        Write-Host "Killing process: $($proc.ProcessName) (PID $($proc.Id))"
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

# Function to kill processes by port
function Kill-ByPort {
    param($port)
    $conns = netstat -ano | Select-String ":$port"
    foreach ($conn in $conns) {
        $procId = ($conn -split '\s+')[-1]
        if ($procId -match '^\d+$') {
            Write-Host "Killing process on port $port (PID $procId)"
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
}

# Function to check if a port is in use
function Test-Port {
    param($port)
    try {
        $conn = netstat -ano | Select-String ":$port\s"
        return $conn -ne $null
    } catch {
        return $false
    }
}

# Function to test health endpoint
function Test-HealthEndpoint {
    param($url)
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 3 -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Step 1: Kill existing server processes
Write-Host "Killing existing server processes..."
Kill-ByName "uvicorn*"
Kill-ByName "python*"
Kill-ByName "vite*"
Kill-ByName "node*"
Kill-ByName "npm*"

# Kill by specific ports
foreach ($port in 3000,3001,3002,3003,8000,8001) {
    Kill-ByPort $port
}

# Step 2: Clear Python cache
Write-Host "Clearing Python cache..."
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue

# Step 3: Wait for processes to fully terminate
Write-Host "Waiting for processes to terminate..."
Start-Sleep -Seconds 5

# Step 4: Start backend server
Write-Host "Starting backend server..."
$env:PYTHONPATH = "."
$backend = Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000") -RedirectStandardOutput "backend_output.log" -RedirectStandardError "backend_error.log" -PassThru -WindowStyle Hidden
$backendPid = $backend.Id
Write-Host "Backend process started with PID: $backendPid"

# Step 5: Wait for backend to start
Write-Host "Waiting for backend to start..."
$backendStarted = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    
    # Check if process is still running
    try {
        $proc = Get-Process -Id $backendPid -ErrorAction Stop
    } catch {
        Write-Host "ERROR: Backend process died unexpectedly"
        exit 1
    }
    
    # Test health endpoint
    if (Test-HealthEndpoint "http://localhost:8000/health") {
        Write-Host "Backend server is running on http://localhost:8000"
        $backendStarted = $true
        break
    }
    
    Write-Host "Waiting for backend... ($($i+1)/30)"
}

if (-not $backendStarted) {
    Write-Host "ERROR: Backend server failed to start within 30 seconds"
    Write-Host "Backend PID: $backendPid"
    Write-Host "Checking if process is still running..."
    try {
        $proc = Get-Process -Id $backendPid -ErrorAction Stop
        Write-Host "Backend process is running but not responding on health endpoint"
        Write-Host "You may need to check the backend logs manually"
    } catch {
        Write-Host "Backend process has died"
    }
    exit 1
}

# Step 6: Start frontend server
Write-Host "Starting frontend server..."
Push-Location frontend

# Clear Vite cache first
if (Test-Path "node_modules/.vite") {
    Remove-Item -Recurse -Force "node_modules/.vite" -ErrorAction SilentlyContinue
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue
}

# Start frontend with proper error handling
$frontend = Start-Process -FilePath "npm" -ArgumentList @("run", "dev") -PassThru -WindowStyle Hidden
$frontendPid = $frontend.Id
Write-Host "Frontend process started with PID: $frontendPid"
Pop-Location

# Step 7: Wait for frontend to start (longer wait for Vite)
Write-Host "Waiting for frontend to start (this may take up to 60 seconds)..."
$frontendStarted = $false
$frontendPort = $null

for ($i = 0; $i -lt 60; $i++) {
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
            $response = Invoke-WebRequest -Uri "http://localhost:$port" -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                Write-Host "Frontend server is running on http://localhost:$port"
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
        Write-Host "Still waiting for frontend... ($($i+1)/60)"
    }
}

if (-not $frontendStarted) {
    Write-Host "ERROR: Frontend server failed to start within 60 seconds"
    Write-Host "Frontend PID: $frontendPid"
    Write-Host "Checking if process is still running..."
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
Write-Host "✅ Server restart complete!"
Write-Host "Backend: http://localhost:8000 (PID: $backendPid)"
Write-Host "Frontend: http://localhost:$frontendPort (PID: $frontendPid)"
Write-Host ""
Write-Host "To stop servers manually:"
Write-Host "   Backend: Stop-Process -Id $backendPid"
Write-Host "   Frontend: Stop-Process -Id $frontendPid"
Write-Host "   Or run: Stop-Process -Name uvicorn,vite,node,npm -Force" 