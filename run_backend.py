#!/usr/bin/env python3
"""
SimpleSim Backend Entry Point
Run this script from the project root to start the backend server.
"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Now we can import the FastAPI app
from main import app

if __name__ == "__main__":
    import uvicorn
    
    print("Starting SimpleSim Backend Server...")
    print(f"Backend directory: {backend_dir}")
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(backend_dir)]
    ) 