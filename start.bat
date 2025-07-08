@echo off
echo Starting SimpleSim Backend...
cd backend
set PYTHONPATH=.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 