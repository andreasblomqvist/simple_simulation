#!/usr/bin/env python3
"""
SimpleSim Backend Starter
Run this from the project root to start the backend server.
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    # Get the project root directory
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Set PYTHONPATH to include the backend directory
    env = os.environ.copy()
    env['PYTHONPATH'] = str(backend_dir)
    
    print(f"Starting backend from: {backend_dir}")
    print(f"PYTHONPATH: {env['PYTHONPATH']}")
    
    # Start uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]
    
    try:
        subprocess.run(cmd, env=env, check=True)
    except KeyboardInterrupt:
        print("\nBackend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Backend failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 