#!/usr/bin/env python3
"""
Import Excel configuration file to restore proper workforce data
"""

import requests
import sys
import os

def import_config(file_path):
    """Import configuration from Excel file"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    url = "http://localhost:8000/offices/config/import"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully imported configuration")
            print(f"📊 {result.get('message', 'Import completed')}")
            return True
        else:
            print(f"❌ Import failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing configuration: {e}")
        return False

if __name__ == "__main__":
    file_path = "scripts/office_config_20250628_224437.xlsx"
    success = import_config(file_path)
    sys.exit(0 if success else 1) 