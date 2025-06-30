# SimpleSim Server Restart Script (PowerShell)
# Kills old instances and restarts backend and frontend servers cleanly

Write-Host "SimpleSim Server Restart Script (Windows)"
Write-Host "========================================="

# Set the correct Python path where packages are installed
$pythonPath = "C:\Users\andre\AppData\Local\Programs\Python\Python313\python.exe"

# Function to kill processes by name with better error handling
function Kill-ByName {
    param($name)
    try {
        $procs = Get-Process | Where-Object { $_.ProcessName -like $name } -ErrorAction SilentlyContinue
        if ($procs) {
            foreach ($proc in $procs) {
                Write-Host "Killing process: $($proc.ProcessName) (PID $($proc.Id))"
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
        } else {
            Write-Host "No processes found matching: $name"
        }
    } catch {
        Write-Host "Error killing processes matching $name : $($_.Exception.Message)"
    }
}

# Function to kill processes by port with better error handling
function Kill-ByPort {
    param($port)
    try {
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
        } else {
            Write-Host "No processes found on port: $port"
        }
    } catch {
        Write-Host "Error checking port $port : $($_.Exception.Message)"
    }
}

# Function to test health endpoint with timeout
function Test-HealthEndpoint {
    param($url, $timeout = 3)
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec $timeout -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Step 1: Kill existing server processes (with better error handling)
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
try {
    Get-ChildItem -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "Python cache cleared"
} catch {
    Write-Host "Error clearing Python cache: $($_.Exception.Message)"
}

# Step 3: Wait for processes to fully terminate
Write-Host "Waiting for processes to terminate..."
Start-Sleep -Seconds 3

# Step 4: Check if we're in the right directory
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: backend directory not found. Please run this script from the project root."
    exit 1
}

if (-not (Test-Path "frontend")) {
    Write-Host "ERROR: frontend directory not found. Please run this script from the project root."
    exit 1
}

# Step 5: Verify Python and uvicorn are available
Write-Host "Verifying Python and uvicorn installation..."
try {
    $uvicornVersion = & $pythonPath -m uvicorn --version 2>&1
    Write-Host "✅ Using Python: $uvicornVersion"
} catch {
    Write-Host "ERROR: uvicorn not found. Please install requirements: pip install -r backend/requirements.txt"
    exit 1
}

# Step 6: Start backend server in visible window
Write-Host "Starting backend server..."
$env:PYTHONPATH = "."

try {
    $backend = Start-Process -FilePath $pythonPath -ArgumentList @("-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000") -PassThru -WindowStyle Normal
    $backendPid = $backend.Id
    Write-Host "Backend process started with PID: $backendPid in visible window"
} catch {
    Write-Host "ERROR: Failed to start backend server: $($_.Exception.Message)"
    exit 1
}

# Step 7: Wait for backend to start (with better timeout handling)
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
    if (Test-HealthEndpoint "http://localhost:8000/health") {
        Write-Host "✅ Backend server is running on http://localhost:8000"
        $backendStarted = $true
        break
    }
    
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

# Step 8: Start frontend server in visible window
Write-Host "Starting frontend server..."
Push-Location frontend

# Check if package.json exists
if (-not (Test-Path "package.json")) {
    Write-Host "ERROR: package.json not found in frontend directory"
    Pop-Location
    exit 1
}

# Check if dev script exists
$packageJson = Get-Content "package.json" | ConvertFrom-Json
if (-not $packageJson.scripts.dev) {
    Write-Host "ERROR: 'dev' script not found in package.json"
    Pop-Location
    exit 1
}

# Clear Vite cache first
if (Test-Path "node_modules/.vite") {
    Remove-Item -Recurse -Force "node_modules/.vite" -ErrorAction SilentlyContinue
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue
}

# Start frontend with proper error handling in visible window
try {
    $frontend = Start-Process -FilePath "npm" -ArgumentList @("run", "dev") -PassThru -WindowStyle Normal
    $frontendPid = $frontend.Id
    Write-Host "Frontend process started with PID: $frontendPid in visible window"
} catch {
    Write-Host "ERROR: Failed to start frontend server: $($_.Exception.Message)"
    Pop-Location
    exit 1
}

Pop-Location

# Step 9: Wait for frontend to start (with better detection)
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
Write-Host "✅ Server restart complete!"
Write-Host "Backend: http://localhost:8000 (PID: $backendPid) - Running in visible window"
Write-Host "Frontend: http://localhost:$frontendPort (PID: $frontendPid) - Running in visible window"
Write-Host ""
Write-Host "Both servers are now running in separate terminal windows where you can see their output."
Write-Host ""
Write-Host "To stop servers manually:"
Write-Host "   Backend: Stop-Process -Id $backendPid"
Write-Host "   Frontend: Stop-Process -Id $frontendPid"
Write-Host "   Or run: Stop-Process -Name uvicorn,vite,node,npm -Force" 