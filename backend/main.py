from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.src.services.simulation_engine import SimulationEngine
from backend.routers import simulation, offices, health

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

# Initialize simulation engine
engine = SimulationEngine()

# Inject engine into routers
simulation.set_engine(engine)
offices.set_engine(engine)
health.set_engine(engine)

# Include routers
app.include_router(health.router)
app.include_router(simulation.router)
app.include_router(offices.router)

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