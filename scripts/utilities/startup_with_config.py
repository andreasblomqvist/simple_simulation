#!/usr/bin/env python3
"""
Startup script that loads configuration data and starts the backend server.
This ensures the JSON configuration file is created before the server starts.
"""

import os
import sys
import subprocess
import time

def check_configuration():
    """Check if configuration exists from previous user uploads"""
    print("🔍 [STARTUP] Checking for existing configuration...")
    
    # Import and use the config service to check data
    from backend.src.services.config_service import config_service
    
    try:
        # Check if configuration exists from previous user uploads
        config = config_service.get_configuration()
        if config and len(config) > 0:
            total_fte = sum(office.get('total_fte', 0) for office in config.values())
            print(f"✅ [STARTUP] Found existing configuration: {len(config)} offices, {total_fte} total FTE")
            print("📤 [STARTUP] Users can upload new Excel files to update configuration")
            return True
        else:
            print("📤 [STARTUP] No configuration found - ready for user Excel upload")
            print("💡 [STARTUP] Users can upload Excel files via the Configuration page")
            return True  # Still return True to start the server
            
    except Exception as e:
        print(f"⚠️ [STARTUP] Error checking configuration: {e}")
        print("📤 [STARTUP] Server will start - users can upload Excel files")
        return True  # Still return True to start the server

def start_backend():
    """Start the backend server"""
    print("🌐 [STARTUP] Starting backend server...")
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = '.'
    
    # Start the backend server
    cmd = [
        sys.executable, '-m', 'uvicorn', 
        'backend.main:app', 
        '--reload', 
        '--host', '0.0.0.0', 
        '--port', '8000'
    ]
    
    try:
        # Run the server
        subprocess.run(cmd, env=env, cwd='.')
    except KeyboardInterrupt:
        print("\n🛑 [STARTUP] Server stopped by user")
    except Exception as e:
        print(f"❌ [STARTUP] Error starting server: {e}")

def main():
    """Main startup function"""
    print("🚀 [STARTUP] SimpleSim Server")
    print("=" * 50)
    
    # Check configuration status
    check_configuration()
    print("🌐 [STARTUP] Starting FastAPI backend...")
    start_backend()

if __name__ == "__main__":
    main() 