"""
Simulation V2 API Router

FastAPI router for SimpleSim Engine V2 with comprehensive endpoints:
- Scenario execution with V2 engine
- KPI calculation and analytics
- Individual event tracking
- Performance monitoring
- Feature flag switching between V1/V2
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging
import asyncio
from datetime import datetime, date
import json

# V2 Engine imports
from src.services.simulation_engine_v2 import (
    SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
    SimulationResults, Person, PersonEvent, EventType
)

# Set up logging
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2", tags=["Simulation V2"])

# ============================================================================
# Pydantic Models for API
# ============================================================================

class TimeRangeRequest(BaseModel):
    """Time range for simulation"""
    start_year: int = Field(..., ge=2020, le=2050)
    start_month: int = Field(..., ge=1, le=12)
    end_year: int = Field(..., ge=2020, le=2050)
    end_month: int = Field(..., ge=1, le=12)

class LeversRequest(BaseModel):
    """Scenario levers for adjustments"""
    recruitment_multiplier: float = Field(1.0, ge=0.1, le=5.0)
    churn_multiplier: float = Field(1.0, ge=0.1, le=5.0)
    progression_multiplier: float = Field(1.0, ge=0.1, le=5.0)
    price_multiplier: float = Field(1.0, ge=0.1, le=5.0)
    salary_multiplier: float = Field(1.0, ge=0.1, le=5.0)

class ScenarioRequestV2(BaseModel):
    """V2 Scenario request model"""
    scenario_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    time_range: TimeRangeRequest
    office_ids: List[str] = Field(..., min_items=1, max_items=20)
    levers: LeversRequest = Field(default_factory=LeversRequest)
    
    # V2 specific options
    include_kpis: bool = Field(True, description="Calculate KPIs")
    include_events: bool = Field(True, description="Include individual events")
    validation_enabled: bool = Field(True, description="Enable validation")
    random_seed: Optional[int] = Field(None, description="Random seed for deterministic results")

class SimulationStatusResponse(BaseModel):
    """Simulation status response"""
    scenario_id: str
    status: str  # "running", "completed", "failed", "queued"
    progress_percent: Optional[float] = None
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class KPIResponse(BaseModel):
    """KPI response model"""
    workforce_kpis: Dict[str, Any]
    financial_kpis: Dict[str, Any]
    business_intelligence_kpis: Dict[str, Any]
    comparative_analysis: Dict[str, Any]
    executive_summary: Dict[str, Any]
    calculation_metadata: Dict[str, Any]

class EventResponse(BaseModel):
    """Individual event response"""
    date: str
    event_type: str
    person_id: str
    details: Dict[str, Any]
    from_state: Optional[Dict[str, Any]]
    to_state: Optional[Dict[str, Any]]
    probability_used: Optional[float]

class SimulationResultsResponse(BaseModel):
    """Complete simulation results response"""
    scenario_id: str
    execution_time_seconds: float
    total_months: int
    total_events: int
    final_workforce_count: int
    
    # Optional detailed data
    monthly_results: Optional[Dict[str, Any]] = None
    events: Optional[List[EventResponse]] = None
    kpis: Optional[KPIResponse] = None
    office_summary: Optional[Dict[str, Any]] = None

# ============================================================================
# Global State Management
# ============================================================================

class SimulationManager:
    """Manages running simulations and caching"""
    
    def __init__(self):
        self.running_simulations: Dict[str, Dict[str, Any]] = {}
        self.completed_results: Dict[str, SimulationResults] = {}
        self.engine_cache: Dict[str, Any] = {}
    
    def start_simulation(self, scenario_id: str, scenario_request: ScenarioRequestV2) -> None:
        """Start simulation tracking"""
        self.running_simulations[scenario_id] = {
            "status": "queued",
            "progress": 0.0,
            "started_at": datetime.now(),
            "scenario": scenario_request
        }
    
    def update_progress(self, scenario_id: str, progress: float, status: str = "running"):
        """Update simulation progress"""
        if scenario_id in self.running_simulations:
            self.running_simulations[scenario_id].update({
                "status": status,
                "progress": progress
            })
    
    def complete_simulation(self, scenario_id: str, results: SimulationResults):
        """Mark simulation as completed"""
        self.completed_results[scenario_id] = results
        if scenario_id in self.running_simulations:
            self.running_simulations[scenario_id].update({
                "status": "completed",
                "progress": 100.0,
                "completed_at": datetime.now()
            })
    
    def fail_simulation(self, scenario_id: str, error_message: str):
        """Mark simulation as failed"""
        if scenario_id in self.running_simulations:
            self.running_simulations[scenario_id].update({
                "status": "failed",
                "progress": 0.0,
                "error_message": error_message,
                "completed_at": datetime.now()
            })

# Global simulation manager
simulation_manager = SimulationManager()

# ============================================================================
# Engine Factory Functions
# ============================================================================

def get_v2_engine(config_type: str = "production"):
    """Get V2 engine instance with caching"""
    cache_key = f"engine_v2_{config_type}"
    
    if cache_key not in simulation_manager.engine_cache:
        if config_type == "production":
            engine = SimulationEngineV2Factory.create_production_engine()
        elif config_type == "test":
            engine = SimulationEngineV2Factory.create_test_engine()
        elif config_type == "development":
            engine = SimulationEngineV2Factory.create_development_engine()
        else:
            engine = SimulationEngineV2Factory.create_production_engine()
        
        simulation_manager.engine_cache[cache_key] = engine
    
    return simulation_manager.engine_cache[cache_key]

# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check for V2 engine"""
    try:
        # Test engine creation
        engine = get_v2_engine("test")
        return {
            "status": "healthy",
            "version": "0.8.0-beta",
            "engine": "SimulationEngineV2",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"V2 engine health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"V2 engine unhealthy: {str(e)}")

@router.post("/scenarios/run", response_model=SimulationStatusResponse)
async def run_scenario_v2(
    scenario: ScenarioRequestV2,
    background_tasks: BackgroundTasks,
    engine_type: str = Query("production", regex="^(production|test|development)$")
):
    """
    Run simulation scenario with V2 engine
    
    - **scenario**: Complete scenario configuration
    - **engine_type**: Engine configuration (production/test/development)
    """
    try:
        # Validate scenario
        if scenario.scenario_id in simulation_manager.running_simulations:
            running_status = simulation_manager.running_simulations[scenario.scenario_id]["status"]
            if running_status in ["running", "queued"]:
                raise HTTPException(
                    status_code=409, 
                    detail=f"Scenario {scenario.scenario_id} is already {running_status}"
                )
        
        # Start tracking
        simulation_manager.start_simulation(scenario.scenario_id, scenario)
        
        # Queue background simulation
        background_tasks.add_task(
            execute_simulation_background,
            scenario.scenario_id,
            scenario,
            engine_type
        )
        
        return SimulationStatusResponse(
            scenario_id=scenario.scenario_id,
            status="queued",
            started_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start V2 simulation {scenario.scenario_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start simulation: {str(e)}")

@router.get("/scenarios/{scenario_id}/status", response_model=SimulationStatusResponse)
async def get_scenario_status(scenario_id: str):
    """Get simulation status"""
    if scenario_id not in simulation_manager.running_simulations:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    
    status_data = simulation_manager.running_simulations[scenario_id]
    return SimulationStatusResponse(
        scenario_id=scenario_id,
        status=status_data["status"],
        progress_percent=status_data.get("progress"),
        error_message=status_data.get("error_message"),
        started_at=status_data.get("started_at"),
        completed_at=status_data.get("completed_at")
    )

@router.get("/scenarios/{scenario_id}/results", response_model=SimulationResultsResponse)
async def get_scenario_results(
    scenario_id: str,
    include_monthly: bool = Query(False, description="Include monthly results"),
    include_events: bool = Query(False, description="Include individual events"),
    include_kpis: bool = Query(True, description="Include KPIs")
):
    """Get simulation results"""
    if scenario_id not in simulation_manager.completed_results:
        # Check if still running
        if scenario_id in simulation_manager.running_simulations:
            status = simulation_manager.running_simulations[scenario_id]["status"]
            if status in ["running", "queued"]:
                raise HTTPException(status_code=202, detail=f"Simulation still {status}")
            elif status == "failed":
                error_msg = simulation_manager.running_simulations[scenario_id].get("error_message", "Unknown error")
                raise HTTPException(status_code=500, detail=f"Simulation failed: {error_msg}")
        
        raise HTTPException(status_code=404, detail=f"Results for scenario {scenario_id} not found")
    
    results = simulation_manager.completed_results[scenario_id]
    status_data = simulation_manager.running_simulations.get(scenario_id, {})
    
    # Calculate execution time
    started_at = status_data.get("started_at")
    completed_at = status_data.get("completed_at")
    execution_time = 0.0
    if started_at and completed_at:
        execution_time = (completed_at - started_at).total_seconds()
    
    # Build response
    response = SimulationResultsResponse(
        scenario_id=scenario_id,
        execution_time_seconds=execution_time,
        total_months=len(results.monthly_results),
        total_events=len(results.all_events),
        final_workforce_count=sum(office.get_total_workforce() for office in results.final_workforce.values())
    )
    
    # Add optional data
    if include_monthly and results.monthly_results:
        response.monthly_results = {
            key: {
                "year": month_result.year,
                "month": month_result.month,
                "office_results": month_result.office_results,
                "event_count": len(month_result.events)
            }
            for key, month_result in results.monthly_results.items()
        }
    
    if include_events and results.all_events:
        response.events = [
            EventResponse(
                date=event.date.isoformat(),
                event_type=event.event_type.value,
                person_id=event.details.get("person_id", "unknown"),
                details=event.details,
                from_state=event.from_state,
                to_state=event.to_state,
                probability_used=event.probability_used
            )
            for event in results.all_events[:1000]  # Limit to prevent huge responses
        ]
    
    if include_kpis and results.kpi_data:
        response.kpis = KPIResponse(**results.kpi_data)
    
    # Office summary
    response.office_summary = {
        office_id: {
            "final_workforce": office_state.get_total_workforce(),
            "workforce_by_role": {
                role: sum(len([p for p in people if p.is_active]) 
                         for people in levels.values())
                for role, levels in office_state.workforce.items()
            }
        }
        for office_id, office_state in results.final_workforce.items()
    }
    
    return response

@router.get("/scenarios/{scenario_id}/events", response_model=List[EventResponse])
async def get_scenario_events(
    scenario_id: str,
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    office_id: Optional[str] = Query(None, description="Filter by office"),
    limit: int = Query(100, ge=1, le=10000, description="Maximum events to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get individual events from simulation"""
    if scenario_id not in simulation_manager.completed_results:
        raise HTTPException(status_code=404, detail=f"Results for scenario {scenario_id} not found")
    
    results = simulation_manager.completed_results[scenario_id]
    events = results.all_events
    
    # Apply filters
    if event_type:
        try:
            event_type_enum = EventType(event_type)
            events = [e for e in events if e.event_type == event_type_enum]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")
    
    if office_id:
        events = [e for e in events if e.details.get("office") == office_id]
    
    # Apply pagination
    events = events[offset:offset + limit]
    
    return [
        EventResponse(
            date=event.date.isoformat(),
            event_type=event.event_type.value,
            person_id=event.details.get("person_id", "unknown"),
            details=event.details,
            from_state=event.from_state,
            to_state=event.to_state,
            probability_used=event.probability_used
        )
        for event in events
    ]

@router.get("/scenarios/{scenario_id}/kpis", response_model=KPIResponse)
async def get_scenario_kpis(scenario_id: str):
    """Get KPIs for completed scenario"""
    if scenario_id not in simulation_manager.completed_results:
        raise HTTPException(status_code=404, detail=f"Results for scenario {scenario_id} not found")
    
    results = simulation_manager.completed_results[scenario_id]
    
    if not results.kpi_data:
        raise HTTPException(status_code=404, detail=f"KPI data not available for scenario {scenario_id}")
    
    return KPIResponse(**results.kpi_data)

@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """Delete scenario and its results"""
    deleted_items = []
    
    if scenario_id in simulation_manager.running_simulations:
        del simulation_manager.running_simulations[scenario_id]
        deleted_items.append("simulation_status")
    
    if scenario_id in simulation_manager.completed_results:
        del simulation_manager.completed_results[scenario_id]
        deleted_items.append("results")
    
    if not deleted_items:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    
    return {"message": f"Deleted {scenario_id}", "deleted": deleted_items}

@router.get("/scenarios", response_model=List[Dict[str, Any]])
async def list_scenarios():
    """List all scenarios"""
    scenarios = []
    
    # Running simulations
    for scenario_id, data in simulation_manager.running_simulations.items():
        scenarios.append({
            "scenario_id": scenario_id,
            "name": data.get("scenario", {}).get("name", "Unknown"),
            "status": data["status"],
            "started_at": data.get("started_at"),
            "progress": data.get("progress", 0.0)
        })
    
    return scenarios

@router.get("/engine/stats")
async def get_engine_stats():
    """Get V2 engine statistics"""
    return {
        "version": "0.8.0-beta",
        "running_simulations": len(simulation_manager.running_simulations),
        "completed_simulations": len(simulation_manager.completed_results),
        "cached_engines": len(simulation_manager.engine_cache),
        "uptime": datetime.now().isoformat()
    }

# ============================================================================
# Background Task Functions
# ============================================================================

async def execute_simulation_background(scenario_id: str, scenario: ScenarioRequestV2, engine_type: str):
    """Execute simulation in background"""
    try:
        logger.info(f"Starting V2 simulation: {scenario_id}")
        simulation_manager.update_progress(scenario_id, 10.0, "starting")
        
        # Get engine
        engine = get_v2_engine(engine_type)
        simulation_manager.update_progress(scenario_id, 20.0, "running")
        
        # Convert API request to engine format
        time_range = TimeRange(
            scenario.time_range.start_year,
            scenario.time_range.start_month,
            scenario.time_range.end_year,
            scenario.time_range.end_month
        )
        
        levers = Levers(
            recruitment_multiplier=scenario.levers.recruitment_multiplier,
            churn_multiplier=scenario.levers.churn_multiplier,
            progression_multiplier=scenario.levers.progression_multiplier,
            price_multiplier=scenario.levers.price_multiplier,
            salary_multiplier=scenario.levers.salary_multiplier
        )
        
        engine_scenario = ScenarioRequest(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
            time_range=time_range,
            office_ids=scenario.office_ids,
            levers=levers
        )
        
        simulation_manager.update_progress(scenario_id, 30.0, "running")
        
        # Run simulation
        results = engine.run_simulation(engine_scenario)
        simulation_manager.update_progress(scenario_id, 90.0, "completing")
        
        # Complete
        simulation_manager.complete_simulation(scenario_id, results)
        logger.info(f"Completed V2 simulation: {scenario_id}")
        
    except Exception as e:
        logger.error(f"V2 simulation failed {scenario_id}: {str(e)}")
        simulation_manager.fail_simulation(scenario_id, str(e))


# ============================================================================
# Module Export
# ============================================================================

__all__ = [
    'router',
    'simulation_manager',
    'SimulationResultsResponse',
    'KPIResponse',
    'EventResponse'
]