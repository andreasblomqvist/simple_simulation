#!/usr/bin/env python3

import sys
import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add backend to path
sys.path.append('backend')

from src.services.config_service import config_service

# Create simple FastAPI app without database
app = FastAPI(title="SimpleSim Test API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test/offices/debug-config")
def debug_office_config():
    """Debug endpoint to see raw config data"""
    config = config_service.get_config()
    stockholm_data = config.get('Stockholm', {})
    return {
        "stockholm_total_fte": stockholm_data.get('total_fte'),
        "stockholm_name": stockholm_data.get('name'),
        "stockholm_journey": stockholm_data.get('journey'),
        "config_keys": list(config.keys())[:5]
    }

@app.get("/test/offices/{office_id}")
def get_office_simple(office_id: str):
    """Get office with correct total_fte from config"""
    config = config_service.get_config()
    if office_id not in config:
        return {"error": "Office not found"}
    
    office_data = config[office_id]
    return {
        "id": office_id,
        "name": office_data.get('name', office_id),
        "total_fte": office_data.get('total_fte', 0),
        "journey": office_data.get('journey', 'unknown'),
        "snapshots": [{
            "id": "snapshot1",
            "name": f"{office_id} - Current Baseline",
            "total_fte": office_data.get('total_fte', 0),
            "is_default": True
        }]
    }

@app.get("/test/offices/all")
def get_all_offices_simple():
    """Get all offices with correct total_fte"""
    config = config_service.get_config()
    offices = []
    
    for office_name, office_data in config.items():
        offices.append({
            "id": office_name,
            "name": office_data.get('name', office_name),
            "total_fte": office_data.get('total_fte', 0),
            "journey": office_data.get('journey', 'unknown')
        })
    
    return offices

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)