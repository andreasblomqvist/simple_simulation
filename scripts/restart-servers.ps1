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
Start-Sleep -Seconds 3

# Step 4: Start backend server
Write-Host "Starting backend server..."
$backend = Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000") -PassThru
$backendPid = $backend.Id

# Step 5: Wait a moment for backend to start
Start-Sleep -Seconds 2

# Step 6: Start frontend server
Write-Host "Starting frontend server..."
Push-Location frontend
$frontend = Start-Process -FilePath "npm" -ArgumentList @("run", "dev") -PassThru
$frontendPid = $frontend.Id
Pop-Location

# Step 7: Wait and verify servers are running
Write-Host "Waiting for servers to start..."
Start-Sleep -Seconds 5

# Check if backend is responding
try {
    $backendOk = (Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200
} catch { $backendOk = $false }
if ($backendOk) {
    Write-Host "Backend server is running on http://localhost:8000"
} else {
    Write-Host "Backend server failed to start"
}

# Check if frontend is running (try common ports)
$frontendOk = $false
foreach ($port in 3000,3001,3002,3003) {
    try {
        if ((Invoke-WebRequest -Uri "http://localhost:$port" -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200) {
            Write-Host "Frontend server is running on http://localhost:$port"
            $frontendOk = $true
            break
        }
    } catch {}
}
if (-not $frontendOk) {
    Write-Host "Frontend server failed to start"
}

Write-Host ""
Write-Host "Server restart complete!"
Write-Host "Backend PID: $backendPid"
Write-Host "Frontend PID: $frontendPid"
Write-Host ""
Write-Host "To stop servers manually:"
Write-Host "   Backend: Stop-Process -Id $backendPid"
Write-Host "   Frontend: Stop-Process -Id $frontendPid"
Write-Host "   Or run: Stop-Process -Name uvicorn,vite,node,npm -Force" 