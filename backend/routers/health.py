from fastapi import APIRouter
from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import config_service

router = APIRouter(tags=["health"])

# Create engine instance (no injection needed with JSON file approach)
engine = SimulationEngine()

@router.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Organization Growth Simulator API",
        "version": "1.0.0",
        "status": "running"
    }

@router.get("/health")
def health_check():
    """Health check endpoint with configuration service status"""
    config = config_service.get_config()
    total_fte = sum(office.get('total_fte', 0) for office in config.values()) if config else 0
    office_names = list(config.keys()) if config else []
    
    return {
        "status": "healthy",
        "engine_initialized": True,  # Always true with JSON file approach
        "total_offices": len(config),
        "total_fte": total_fte,
        "office_names": office_names,
        "config_service_status": "loaded" if config else "empty"
    } 