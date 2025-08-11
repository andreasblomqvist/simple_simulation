#!/usr/bin/env python3

import sys
import os
import json

# Add backend to path
sys.path.append('backend')

# Import config service directly
from src.services.config_service import config_service

def test_config():
    """Test the config service directly"""
    config = config_service.get_config()
    
    print("=== Config Service Test ===")
    print(f"Number of offices: {len(config)}")
    
    if 'Stockholm' in config:
        stockholm = config['Stockholm']
        print(f"Stockholm total_fte: {stockholm.get('total_fte', 'NOT FOUND')}")
        print(f"Stockholm name: {stockholm.get('name', 'NOT FOUND')}")
        print(f"Stockholm journey: {stockholm.get('journey', 'NOT FOUND')}")
    else:
        print("Stockholm not found in config!")
    
    print("\nAll office names:")
    for office_name in list(config.keys())[:5]:
        total_fte = config[office_name].get('total_fte', 'N/A')
        print(f"  {office_name}: {total_fte} FTE")

if __name__ == "__main__":
    test_config()