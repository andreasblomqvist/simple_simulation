from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.src.services.simulation_engine import SimulationEngine
from backend.routers import simulation, offices, health
from backend.src.routes import mcp_routes
import os
import pandas as pd
from backend.src.services.config_service import config_service



# Create FastAPI app
app = FastAPI(
    title="Organization Growth Simulator API",
    description="API for simulating organizational growth and workforce planning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration during startup
@app.on_event("startup")
async def startup_event():
    """Initialize configuration service during FastAPI startup"""
    print("🚀 [STARTUP] FastAPI server starting up...")
    
    # Check if JSON configuration file already exists from previous user uploads
    json_config_file = "config/office_configuration.json"
    
    if os.path.exists(json_config_file):
        print(f"📄 [STARTUP] Found existing configuration file: {json_config_file}")
        config = config_service.get_configuration()
        if len(config) > 0:
            total_fte = sum(office.get('total_fte', 0) for office in config.values())
            print(f"✅ [STARTUP] Loaded {len(config)} offices from previous user uploads")
            print(f"✅ [STARTUP] Total FTE across all offices: {total_fte}")
            print("✅ [STARTUP] Configuration ready - users can upload Excel files to update")
        else:
            print("📄 [STARTUP] Configuration file exists but is empty")
            print("📤 [STARTUP] Ready for user to upload Excel configuration file")
    else:
        print("📤 [STARTUP] No configuration file found - ready for user to upload Excel file")
        print("💡 [STARTUP] Users can upload Excel files via the Configuration page")

# Initialize simulation engine
engine = SimulationEngine()

# Include routers (no engine injection needed with JSON file approach)
app.include_router(health.router)
app.include_router(simulation.router)
app.include_router(offices.router)
app.include_router(mcp_routes.router)

# Legacy endpoint for backward compatibility
@app.post("/simulate")
def legacy_simulate(req: simulation.SimulationRequest):
    """Legacy simulation endpoint for backward compatibility"""
    print(f"[DEBUG] Legacy /simulate endpoint called with: {req.start_year}-{req.start_month} to {req.end_year}-{req.end_month}")
    print(f"[DEBUG] Office overrides provided: {req.office_overrides is not None}")
    if req.office_overrides:
        print(f"[DEBUG] Office override keys: {list(req.office_overrides.keys())}")
    return simulation.run_simulation(req)

@app.get("/offices")
def legacy_offices():
    """Legacy offices endpoint for backward compatibility"""
    return offices.list_offices()

@app.get("/offices/config")
def legacy_offices_config():
    """Legacy offices config endpoint for backward compatibility"""
    return offices.get_office_config()

@app.post("/import-office-levers")
async def legacy_import(file: UploadFile = File(...)):
    """Legacy import endpoint for backward compatibility"""
    return await offices.import_office_levers(file) 