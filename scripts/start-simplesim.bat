@echo off
REM SimpleSim Start Script (No Docker Required)
REM This script starts both backend and frontend servers

echo ===========================================
echo     SimpleSim - Starting Application
echo ===========================================

REM Change to project root
cd /d "%~dp0\.."

REM Start Backend Server
echo Starting Backend Server...
start "SimpleSim Backend" cmd /k "python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to start
timeout /t 5 /nobreak

REM Start Frontend Server  
echo Starting Frontend Server...
start "SimpleSim Frontend" cmd /k "cd frontend && npm install && npm run dev"

REM Wait for frontend to start
timeout /t 3 /nobreak

echo.
echo ===========================================
echo     SimpleSim Started Successfully!
echo ===========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to open frontend in browser...
pause > nul

REM Open frontend in default browser
start http://localhost:3000 