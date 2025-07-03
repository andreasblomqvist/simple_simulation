"""
Scenario Router - FastAPI endpoints for scenario management and execution.

This router provides the API layer for the scenario runner frontend,
delegating all business logic to the scenario service.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging

from ..src.services.scenario_service import ScenarioService
from ..src.services.scenario_models import (
    ScenarioDefinition,
    ScenarioRequest,
    ScenarioResponse,
    ScenarioListResponse,
    ScenarioComparisonRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

# Create scenario service instance
scenario_service = ScenarioService()

@router.get("/health")
async def health_check():
    """Health check endpoint for scenario service."""
    try:
        # Simple health check - try to list scenarios
        scenarios = scenario_service.list_scenarios()
        return {
            "status": "healthy",
            "service": "scenario",
            "scenarios_count": len(scenarios)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")

@router.post("/create", response_model=Dict[str, str])
async def create_scenario(scenario_def: ScenarioDefinition):
    """Create a new scenario definition."""
    try:
        scenario_id = scenario_service.create_scenario(scenario_def)
        return {"scenario_id": scenario_id, "message": "Scenario created successfully"}
    except Exception as e:
        logger.error(f"Error creating scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create scenario: {str(e)}")

@router.get("/list", response_model=ScenarioListResponse)
async def list_scenarios():
    """List all saved scenarios."""
    try:
        scenarios = scenario_service.list_scenarios()
        return ScenarioListResponse(
            scenarios=scenarios,
            total_count=len(scenarios)
        )
    except Exception as e:
        logger.error(f"Error listing scenarios: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list scenarios: {str(e)}")

@router.post("/run", response_model=ScenarioResponse)
async def run_scenario(request: ScenarioRequest):
    """Run a scenario and return results."""
    try:
        response = scenario_service.run_scenario(request)
        
        if response.status == "error":
            # Check for specific error types
            if "Scenario not found" in response.error_message:
                raise HTTPException(status_code=404, detail=response.error_message)
            else:
                raise HTTPException(status_code=500, detail=response.error_message)
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run scenario: {str(e)}")

@router.post("/compare")
async def compare_scenarios(request: ScenarioComparisonRequest):
    """Compare multiple scenarios side by side."""
    try:
        # Get all scenarios
        scenarios = []
        for scenario_id in request.scenario_ids:
            scenario = scenario_service.get_scenario(scenario_id)
            if not scenario:
                raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
            scenarios.append(scenario)
        
        # Run all scenarios
        results = []
        for scenario in scenarios:
            request = ScenarioRequest(scenario_definition=scenario)
            response = scenario_service.run_scenario(request)
            if response.status == "error":
                raise HTTPException(status_code=500, detail=f"Failed to run scenario {scenario.name}: {response.error_message}")
            results.append(response)
        
        # Format comparison results
        comparison = {
            "scenarios": [
                {
                    "id": result.scenario_id,
                    "name": result.scenario_name,
                    "execution_time": result.execution_time,
                    "results": result.results
                }
                for result in results
            ],
            "comparison_type": request.comparison_type
        }
        
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing scenarios: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare scenarios: {str(e)}")

@router.get("/{scenario_id}", response_model=ScenarioDefinition)
async def get_scenario(scenario_id: str):
    """Get a specific scenario definition."""
    try:
        scenario = scenario_service.get_scenario(scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
        return scenario
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scenario: {str(e)}")

@router.delete("/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """Delete a scenario and its results."""
    try:
        success = scenario_service.delete_scenario(scenario_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
        
        return {"message": f"Scenario {scenario_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete scenario: {str(e)}")

@router.get("/{scenario_id}/results")
async def get_scenario_results(scenario_id: str):
    """Get saved results for a specific scenario."""
    try:
        # Check if scenario exists
        scenario = scenario_service.get_scenario(scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
        
        # Try to load saved results
        import os
        results_file = os.path.join(scenario_service.storage_dir, f"{scenario_id}_results.json")
        
        if not os.path.exists(results_file):
            raise HTTPException(status_code=404, detail=f"No results found for scenario: {scenario_id}")
        
        import json
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        return {
            "scenario_id": scenario_id,
            "scenario_name": scenario.name,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting results for scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scenario results: {str(e)}") 