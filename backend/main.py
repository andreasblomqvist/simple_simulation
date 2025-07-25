from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from src.services.simulation_engine import SimulationEngine
from routers import simulation, offices, health, scenarios, business_plans
from src.routes import mcp_routes
import os
import logging
from datetime import datetime
from src.services.config_service import config_service

# Configure logging
def setup_logging():
    """Setup logging to write to both console and file"""
    # Create logs directory if it doesn't exist
    os.makedirs("backend/logs", exist_ok=True)
    
    # Remove all handlers associated with the root logger object (to avoid duplicate logs)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configure root logging to capture ALL logs (including Uvicorn, FastAPI, etc.)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),  # Console
            logging.FileHandler("backend/logs/backend_full.log", mode='a'),  # Full log file in logs dir
            logging.FileHandler("backend/logs/backend.log", mode='a')  # Existing log file
        ]
    )
    
    # Create a logger for our application
    logger = logging.getLogger("simplesim")
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # File handler - use single log file, append mode
    file_handler = logging.FileHandler("backend/logs/backend.log", mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Ensure Uvicorn logs propagate to root logger
    logging.getLogger("uvicorn").propagate = True
    logging.getLogger("uvicorn.error").propagate = True
    logging.getLogger("uvicorn.access").propagate = True
    logging.getLogger("fastapi").propagate = True
    
    return logger

# Setup logging
logger = setup_logging()



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
    """Load configuration data during FastAPI startup"""
    logger.info("FastAPI server starting up...")
    
    # Use the same path logic as config service
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up to backend directory and then to config
    backend_dir = current_dir  # main.py is already in the backend directory
    json_config_file = os.path.join(backend_dir, "config", "office_configuration.json")
    
    if os.path.exists(json_config_file):
        logger.info(f"Found existing configuration file: {json_config_file}")
        # Load from existing JSON file
        config = config_service.get_config()
        if len(config) > 0:
            total_fte = sum(office.get('total_fte', 0) for office in config.values())
            logger.info(f"Loaded {len(config)} offices from JSON file")
            logger.info(f"Total FTE across all offices: {total_fte}")
            logger.info("Configuration loaded successfully from existing file")
        else:
            logger.warning("JSON file exists but is empty - server will start with empty configuration")
    else:
        logger.info("No existing configuration file found - server will start with empty configuration")

# Initialize simulation engine
engine = SimulationEngine()

# Include routers (no engine injection needed with JSON file approach)
app.include_router(health.router)
app.include_router(simulation.router)
app.include_router(offices.router)
app.include_router(scenarios.router)
app.include_router(business_plans.router)
app.include_router(mcp_routes.router)

# Legacy endpoint for backward compatibility
@app.post("/simulate")
def legacy_simulate(req: simulation.SimulationRequest):
    """Legacy simulation endpoint for backward compatibility"""
    logger.debug(f"Legacy /simulate endpoint called with: {req.start_year}-{req.start_month} to {req.end_year}-{req.end_month}")
    logger.debug(f"Office overrides provided: {req.office_overrides is not None}")
    if req.office_overrides:
        logger.debug(f"Office override keys: {list(req.office_overrides.keys())}")
    return simulation.run_simulation(req)

# Legacy office endpoints removed - now handled by offices router 