from fastapi import APIRouter
from backend.src.services.simulation_engine import SimulationEngine

router = APIRouter(tags=["health"])

# Global engine instance - will be injected from main
engine: SimulationEngine = None

def set_engine(simulation_engine: SimulationEngine):
    """Set the global engine instance"""
    global engine
    engine = simulation_engine

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
    """Health check endpoint"""
    total_offices = len(engine.offices) if engine else 0
    total_fte = sum(office.total_fte for office in engine.offices.values()) if engine else 0
    
    return {
        "status": "healthy",
        "engine_initialized": engine is not None,
        "total_offices": total_offices,
        "total_fte": total_fte
    } 