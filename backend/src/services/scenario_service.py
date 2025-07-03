"""
Scenario Service - Thin adapter layer between frontend scenario runner and simulation engine.

This service follows the architectural principle of being a thin adapter that:
- Translates scenario runner payloads into simulation engine lever plan format
- Validates inputs but does not recalculate business logic
- Maintains single source of truth (all calculations in simulation engine)
- Provides scenario persistence and management
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from .scenario_models import (
    ScenarioDefinition, 
    ScenarioRequest, 
    ScenarioResponse, 
    LeverPlan
)
from .config_service import config_service
from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi import KPIService, EconomicParameters

logger = logging.getLogger(__name__)

class ScenarioService:
    """Thin adapter service for scenario management and execution."""
    
    def __init__(self, storage_dir: str = None):
        # Use environment variable if available, otherwise use default
        if storage_dir is None:
            storage_dir = os.environ.get("SCENARIO_STORAGE_DIR", "data/scenarios")
        self.storage_dir = storage_dir
        self.engine = SimulationEngine()
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure the scenario storage directory exists."""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            logger.info(f"Created scenario storage directory: {self.storage_dir}")
    
    def create_scenario(self, scenario_def: ScenarioDefinition) -> str:
        """Create and save a new scenario definition."""
        scenario_id = str(uuid.uuid4())
        scenario_def.created_at = datetime.now()
        scenario_def.updated_at = datetime.now()
        
        scenario_data = {
            "id": scenario_id,
            "definition": scenario_def.model_dump(),
            "created_at": scenario_def.created_at.isoformat(),
            "updated_at": scenario_def.updated_at.isoformat()
        }
        
        file_path = os.path.join(self.storage_dir, f"{scenario_id}.json")
        with open(file_path, 'w') as f:
            json.dump(scenario_data, f, indent=2, default=str)
        
        logger.info(f"Created scenario: {scenario_id} - {scenario_def.name}")
        return scenario_id
    
    def get_scenario(self, scenario_id: str) -> Optional[ScenarioDefinition]:
        """Retrieve a scenario definition by ID."""
        file_path = os.path.join(self.storage_dir, f"{scenario_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                scenario_data = json.load(f)
            
            return ScenarioDefinition(**scenario_data["definition"])
        except Exception as e:
            logger.error(f"Error loading scenario {scenario_id}: {e}")
            return None
    
    def list_scenarios(self) -> List[Dict[str, Any]]:
        """List all saved scenarios with metadata."""
        scenarios = []
        
        if not os.path.exists(self.storage_dir):
            return scenarios
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        scenario_data = json.load(f)
                    
                    scenarios.append({
                        "id": scenario_data["id"],
                        "name": scenario_data["definition"]["name"],
                        "description": scenario_data["definition"]["description"],
                        "created_at": scenario_data["created_at"],
                        "updated_at": scenario_data["updated_at"]
                    })
                except Exception as e:
                    logger.error(f"Error loading scenario from {filename}: {e}")
        
        # Sort by updated_at descending
        scenarios.sort(key=lambda x: x["updated_at"], reverse=True)
        return scenarios
    
    def run_scenario(self, request: ScenarioRequest) -> ScenarioResponse:
        """Run a scenario and return results."""
        start_time = datetime.now()
        
        try:
            # Get scenario definition
            if request.scenario_definition:
                scenario_def = request.scenario_definition
                scenario_id = self.create_scenario(scenario_def)
            else:
                scenario_def = self.get_scenario(request.scenario_id)
                if not scenario_def:
                    raise ValueError(f"Scenario not found: {request.scenario_id}")
                scenario_id = request.scenario_id
            
            # Override office scope if provided
            if request.office_scope:
                scenario_def.office_scope = request.office_scope
            
            # Transform scenario definition to lever plan
            lever_plan = self._transform_to_lever_plan(scenario_def)
            
            # Create economic parameters
            economic_params = self._create_economic_params(scenario_def)
            
            # Run simulation through engine
            results = self._call_simulation_engine(scenario_def, lever_plan, economic_params)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Save results
            self._save_scenario_results(scenario_id, results)
            
            return ScenarioResponse(
                scenario_id=scenario_id,
                scenario_name=scenario_def.name,
                execution_time=execution_time,
                results=results,
                status="success"
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Scenario execution failed: {e}")
            
            return ScenarioResponse(
                scenario_id=request.scenario_id or "unknown",
                scenario_name=request.scenario_definition.name if request.scenario_definition else "unknown",
                execution_time=execution_time,
                results={},
                status="error",
                error_message=str(e)
            )
    
    def _transform_to_lever_plan(self, scenario_def: ScenarioDefinition) -> Dict[str, Any]:
        """
        Transform scenario definition to simulation engine lever plan format.
        
        This is the key transformation that converts the frontend's lever multipliers
        into the engine's expected format with monthly values for each office/role/level.
        """
        lever_plan = {"offices": {}}
        
        # Get baseline configuration to calculate actual values
        config = config_service.get_config()
        
        for office_name in scenario_def.office_scope:
            if office_name not in config:
                logger.warning(f"Office {office_name} not found in configuration, skipping")
                continue
            
            lever_plan["offices"][office_name] = {"Consultant": {}}
            office_config = config[office_name]
            
            # Process each lever type (recruitment, churn, progression)
            for lever_type, level_multipliers in scenario_def.levers.items():
                for level, multiplier in level_multipliers.items():
                    # Get baseline values from configuration
                    baseline_values = self._get_baseline_values(
                        office_config, level, lever_type
                    )
                    
                    # Apply multiplier to each month
                    for month in range(1, 13):
                        field_name = f"{lever_type}_{month}"
                        baseline_value = baseline_values.get(month, 0.0)
                        adjusted_value = baseline_value * multiplier
                        
                        # Initialize level structure if needed
                        if level not in lever_plan["offices"][office_name]["Consultant"]:
                            lever_plan["offices"][office_name]["Consultant"][level] = {}
                        
                        lever_plan["offices"][office_name]["Consultant"][level][field_name] = adjusted_value
            
            logger.info(f"Created lever plan for {office_name} with {len(scenario_def.levers)} lever types")
        
        return lever_plan
    
    def _get_baseline_values(self, office_config: Dict[str, Any], level: str, lever_type: str) -> Dict[int, float]:
        """Get baseline values for a specific level and lever type from configuration."""
        baseline_values = {}
        
        try:
            # Navigate to the level data in the configuration
            level_data = office_config.get("roles", {}).get("Consultant", {}).get(level, {})
            
            # Extract monthly values for the lever type
            for month in range(1, 13):
                field_name = f"{lever_type}_{month}"
                baseline_values[month] = level_data.get(field_name, 0.0)
                
        except Exception as e:
            logger.warning(f"Error getting baseline values for {level}.{lever_type}: {e}")
            # Return zeros if baseline not found
            for month in range(1, 13):
                baseline_values[month] = 0.0
        
        return baseline_values
    
    def _create_economic_params(self, scenario_def: ScenarioDefinition) -> EconomicParameters:
        """Create economic parameters from scenario definition."""
        # Use default economic parameters if not specified in scenario
        economic_data = scenario_def.economic_params or {}
        
        return EconomicParameters(
            unplanned_absence=economic_data.get("unplanned_absence", 0.05),
            other_expense=economic_data.get("other_expense", 19000000.0),
            employment_cost_rate=economic_data.get("employment_cost_rate", 0.40),
            working_hours_per_month=economic_data.get("working_hours_per_month", 166.4),
            utilization=economic_data.get("utilization", 0.85)
        )
    
    def _call_simulation_engine(self, scenario_def: ScenarioDefinition, lever_plan: Dict[str, Any], economic_params: EconomicParameters) -> Dict[str, Any]:
        """
        Call the simulation engine with the transformed lever plan.
        
        This method maintains the single source of truth principle by delegating
        all calculations to the simulation engine.
        """
        logger.info(f"Running simulation for scenario: {scenario_def.name}")
        
        # Reset engine state for fresh simulation
        self.engine.reset_simulation_state()
        
        # Get price and salary increases from scenario definition
        economic_data = scenario_def.economic_params or {}
        price_increase = economic_data.get("price_increase", 0.0)
        salary_increase = economic_data.get("salary_increase", 0.0)
        
        # Run simulation through engine
        results = self.engine.run_simulation(
            start_year=scenario_def.time_range["start_year"],
            start_month=scenario_def.time_range["start_month"],
            end_year=scenario_def.time_range["end_year"],
            end_month=scenario_def.time_range["end_month"],
            price_increase=price_increase,
            salary_increase=salary_increase,
            lever_plan=lever_plan,
            economic_params=economic_params
        )
        
        # Calculate KPIs using the KPI service (separation of concerns)
        try:
            kpi_service = KPIService(economic_params=economic_params)
            
            # Calculate simulation duration in months
            start_date = datetime(scenario_def.time_range["start_year"], scenario_def.time_range["start_month"], 1)
            end_date = datetime(scenario_def.time_range["end_year"], scenario_def.time_range["end_month"], 1)
            simulation_duration_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
            
            # Calculate KPIs for the simulation
            kpi_results = kpi_service.calculate_all_kpis(
                results,
                simulation_duration_months,
                economic_params=economic_params
            )
            
            # Convert dataclasses to dicts for JSON serialization
            def to_dict(data):
                if hasattr(data, '__dataclass_fields__'):
                    return {k: to_dict(getattr(data, k)) for k in data.__dataclass_fields__}
                elif isinstance(data, dict):
                    return {k: to_dict(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [to_dict(i) for i in data]
                else:
                    return data
            
            results['kpis'] = to_dict(kpi_results)
            logger.info("KPIs calculated successfully")
            
        except Exception as e:
            logger.error(f"KPI calculation failed: {e}")
            results['kpis'] = None
        
        # Clean results for JSON serialization by removing non-serializable objects
        def clean_for_serialization(data):
            if isinstance(data, dict):
                cleaned = {}
                for k, v in data.items():
                    # Skip EventLogger and other non-serializable objects
                    if hasattr(v, '__class__') and 'EventLogger' in str(v.__class__):
                        continue
                    if hasattr(v, '__class__') and 'Logger' in str(v.__class__):
                        continue
                    cleaned[k] = clean_for_serialization(v)
                return cleaned
            elif isinstance(data, list):
                return [clean_for_serialization(item) for item in data]
            else:
                return data
        
        return clean_for_serialization(results)
    
    def _save_scenario_results(self, scenario_id: str, results: Dict[str, Any]):
        """Save scenario results to storage."""
        results_file = os.path.join(self.storage_dir, f"{scenario_id}_results.json")
        
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Saved results for scenario: {scenario_id}")
        except Exception as e:
            logger.error(f"Error saving results for scenario {scenario_id}: {e}")
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario and its results."""
        try:
            # Check if scenario exists
            scenario_file = os.path.join(self.storage_dir, f"{scenario_id}.json")
            if not os.path.exists(scenario_file):
                return False
            
            # Delete scenario definition
            os.remove(scenario_file)
            
            # Delete results file if it exists
            results_file = os.path.join(self.storage_dir, f"{scenario_id}_results.json")
            if os.path.exists(results_file):
                os.remove(results_file)
            
            logger.info(f"Deleted scenario: {scenario_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting scenario {scenario_id}: {e}")
            return False 