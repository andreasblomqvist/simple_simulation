"""
Scenario Router - FastAPI endpoints for scenario management and execution.

This router provides the API layer for the scenario runner frontend,
delegating all business logic to the scenario service.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging

from src.services.scenario_service import ScenarioService
from src.services.config_service import config_service
from src.services.scenario_models import (
    ScenarioDefinition,
    ScenarioRequest,
    ScenarioResponse,
    ScenarioListResponse,
    ScenarioComparisonRequest,
    ValidationResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

# Create scenario service instance
scenario_service = ScenarioService(config_service)

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

@router.post("/validate", response_model=ValidationResponse)
async def validate_scenario(scenario_def: ScenarioDefinition):
    """Validate a scenario definition without creating it."""
    try:
        # Validate the scenario definition
        scenario_service.scenario_validator.validate_scenario_definition(scenario_def)
        
        # Check if scenario name already exists (for new scenarios)
        if hasattr(scenario_def, 'id') and scenario_def.id:
            # This is an update, check name conflicts excluding current scenario
            if scenario_service.scenario_name_exists(scenario_def.name, exclude_id=scenario_def.id):
                return ValidationResponse(
                    valid=False,
                    errors=[f"Scenario with name '{scenario_def.name}' already exists. Please choose a different name."]
                )
        else:
            # This is a new scenario, check if name exists
            if scenario_service.scenario_name_exists(scenario_def.name):
                return ValidationResponse(
                    valid=False,
                    errors=[f"Scenario with name '{scenario_def.name}' already exists. Please choose a different name."]
                )
        
        return ValidationResponse(valid=True, errors=[])
    except Exception as e:
        logger.error(f"Error validating scenario: {e}")
        return ValidationResponse(valid=False, errors=[str(e)])

@router.post("/create", response_model=dict)
async def create_scenario(scenario_def: ScenarioDefinition):
    """Create a new scenario."""
    try:
        # Check if scenario name already exists
        if scenario_service.scenario_name_exists(scenario_def.name):
            raise HTTPException(
                status_code=400, 
                detail=f"Scenario with name '{scenario_def.name}' already exists. Please choose a different name."
            )
        
        scenario_id = scenario_service.create_scenario(scenario_def)
        return {"scenario_id": scenario_id, "message": "Scenario created successfully"}
    except HTTPException:
        raise
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
        # Validate scenario ID
        if not scenario_id or scenario_id in ['undefined', 'null']:
            raise HTTPException(status_code=400, detail=f"Invalid scenario ID: {scenario_id}")
        
        scenario = scenario_service.get_scenario(scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
        return scenario
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scenario: {str(e)}")

@router.put("/{scenario_id}")
async def update_scenario(scenario_id: str, scenario_def: ScenarioDefinition):
    """Update an existing scenario definition."""
    try:
        # Add debugging logs
        logger.info(f"[DEBUG] PUT /scenarios/{scenario_id} called")
        logger.info(f"[DEBUG] Scenario ID from URL: {scenario_id}")
        logger.info(f"[DEBUG] Scenario definition name: {scenario_def.name}")
        logger.info(f"[DEBUG] Scenario definition ID: {getattr(scenario_def, 'id', 'None')}")
        
        # Validate scenario ID
        if not scenario_id or scenario_id in ['undefined', 'null']:
            logger.error(f"[DEBUG] Invalid scenario ID: {scenario_id}")
            raise HTTPException(status_code=400, detail=f"Invalid scenario ID: {scenario_id}")
        
        # Check if scenario exists before updating
        existing_scenario = scenario_service.get_scenario(scenario_id)
        if not existing_scenario:
            logger.error(f"[DEBUG] Scenario not found: {scenario_id}")
            raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
        
        logger.info(f"[DEBUG] Found existing scenario: {existing_scenario.get('name', 'Unknown')}")
        
        # Check if the new name conflicts with another scenario (excluding the current one)
        if scenario_service.scenario_name_exists(scenario_def.name, exclude_id=scenario_id):
            logger.error(f"[DEBUG] Name conflict: {scenario_def.name} already exists")
            raise HTTPException(
                status_code=400, 
                detail=f"Scenario with name '{scenario_def.name}' already exists. Please choose a different name."
            )
        
        success = scenario_service.update_scenario(scenario_id, scenario_def)
        if not success:
            logger.error(f"[DEBUG] Update failed for scenario: {scenario_id}")
            raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
        
        logger.info(f"[DEBUG] Scenario {scenario_id} updated successfully")
        return {"message": f"Scenario {scenario_id} updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update scenario: {str(e)}")

@router.delete("/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """Delete a scenario and its results."""
    try:
        # Validate scenario ID
        if not scenario_id or scenario_id in ['undefined', 'null']:
            raise HTTPException(status_code=400, detail=f"Invalid scenario ID: {scenario_id}")
        
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
        
        # Get saved results using the service method
        results = scenario_service.get_scenario_results(scenario_id)
        
        if results is None:
            raise HTTPException(status_code=404, detail=f"No results found for scenario: {scenario_id}")
        
        return {
            "scenario_id": scenario_id,
            "scenario_name": scenario.get('name', 'Unknown'),
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting results for scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scenario results: {str(e)}")

@router.post("/cleanup-duplicates")
async def cleanup_duplicate_scenarios():
    """Clean up duplicate scenarios with the same name."""
    try:
        cleanup_stats = scenario_service.cleanup_duplicate_scenarios()
        
        if "error" in cleanup_stats:
            raise HTTPException(status_code=500, detail=f"Cleanup failed: {cleanup_stats['error']}")
        
        return {
            "message": "Duplicate scenarios cleaned up successfully",
            "statistics": cleanup_stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up duplicate scenarios: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean up duplicate scenarios: {str(e)}") 