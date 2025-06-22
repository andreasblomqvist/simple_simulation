#!/usr/bin/env python3
"""
Startup script that loads configuration data and starts the backend server.
This ensures the JSON configuration file is created before the server starts.
"""

import os
import sys
import subprocess
import time

def load_configuration():
    """Load configuration data into the JSON file"""
    print("🚀 [STARTUP] Loading configuration data...")
    
    # Import and use the config service to load data
    from backend.src.services.config_service import config_service
    
    # Load the Excel file
    excel_file = "office_config_correct_progression_20250618_135815.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ [STARTUP] Excel file not found: {excel_file}")
        return False
    
    try:
        # Import the Excel data
        import pandas as pd
        df = pd.read_excel(excel_file)
        print(f"📊 [STARTUP] Read {len(df)} rows from Excel file")
        
        # Import into config service (this will create the JSON file)
        config_service.import_from_excel(df)
        
        # Verify the configuration was loaded
        config = config_service.get_configuration()
        if config:
            total_fte = sum(office.get('total_fte', 0) for office in config.values())
            print(f"✅ [STARTUP] Configuration loaded: {len(config)} offices, {total_fte} total FTE")
            return True
        else:
            print("❌ [STARTUP] Failed to load configuration")
            return False
            
    except Exception as e:
        print(f"❌ [STARTUP] Error loading configuration: {e}")
        return False

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
    print("🚀 [STARTUP] SimpleSim Configuration Loader")
    print("=" * 50)
    
    # Load configuration first
    if load_configuration():
        print("✅ [STARTUP] Configuration loaded successfully")
        print("🌐 [STARTUP] Starting FastAPI backend...")
        start_backend()
    else:
        print("❌ [STARTUP] Failed to load configuration. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main() 