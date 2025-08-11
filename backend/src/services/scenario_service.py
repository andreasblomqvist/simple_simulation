"""
Scenario Service - Orchestrates scenario execution using focused services.

This service now acts as a thin orchestrator that coordinates:
- Scenario resolution (via ScenarioResolver)
- Office building (via OfficeBuilder)
- Storage management
- Simulation execution
"""
import json
import os
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import copy

from src.services.scenario_models import (
    ScenarioDefinition, 
    ScenarioRequest, 
    ScenarioResponse, 
    LeverPlan
)
from src.services.simulation.progression_models import ProgressionConfig, CATCurves
from src.services.config_service import config_service
from src.services.simulation_engine import SimulationEngine
from src.services.simulation_engine_v2 import SimulationEngineV2
from src.services.kpi import KPIService
from src.services.kpi.kpi_models import EconomicParameters
from src.services.scenario_resolver import ScenarioResolver
from src.services.office_builder import OfficeBuilder
from src.services.scenario_validator import ScenarioValidator
from src.services.scenario_storage import ScenarioStorageService
from src.services.scenario_transformer import ScenarioTransformer
from src.services.error_handler import handle_service_errors
from src.services.logger_service import LoggerService

logger = logging.getLogger(__name__)

class ScenarioService:
    """
    Orchestrates scenario execution using focused services.
    Coordinates data flow between frontend, resolution, building, and simulation engine.
    """
    def __init__(self, config_service):
        """Initialize with dependencies."""
        self.config_service = config_service
        self.storage_service = ScenarioStorageService('data/scenarios')
        self.scenario_resolver = ScenarioResolver(config_service)
        self.office_builder = OfficeBuilder()
        self.scenario_validator = ScenarioValidator()
        self.scenario_transformer = ScenarioTransformer()
        self.logger = LoggerService("scenario_service")

    def resolve_scenario(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: resolves scenario data into offices, progression config, and CAT curves.
        Returns a dict with keys: 'offices', 'progression_config', 'cat_curves'.
        """
        correlation_id = str(uuid.uuid4())[:8]
        self.logger.info("Starting scenario resolution", correlation_id=correlation_id, extra={"scenario_data_keys": list(scenario_data.keys())})
        
        try:
            logger.info(f"[SCENARIO RECEIVED] scenario_data from frontend: {json.dumps(scenario_data, indent=2, default=str)[:5000]}")
            self.scenario_validator.validate_scenario_data(scenario_data)
            self.logger.info("Scenario data validation passed", correlation_id=correlation_id)
            
            # Use ScenarioResolver to transform data
            resolved_data = self.scenario_resolver.resolve_scenario(scenario_data)
            self.logger.info("Scenario resolution completed", correlation_id=correlation_id, extra={"offices_count": len(resolved_data.get('offices', {}))})
            
            # Use OfficeBuilder to create Office objects
            offices = self.office_builder.build_offices_from_config(
                resolved_data['offices_config'], 
                resolved_data['progression_config']
            )
            self.logger.info("Office objects built successfully", correlation_id=correlation_id, extra={"offices_built": len(offices)})
            
            return {
                'offices': offices,
                'progression_config': resolved_data['progression_config'],
                'cat_curves': resolved_data['cat_curves']
            }
            
        except Exception as e:
            self.logger.error(f"Scenario resolution failed: {e}", correlation_id=correlation_id)
            raise

    def list_scenarios(self) -> list:
        """
        List all saved scenarios using the storage service. Returns a list of scenario metadata dictionaries with IDs.
        """
        try:
            scenarios = self.storage_service.list_scenarios()
            return scenarios
        except Exception as e:
            logger.error(f"Error listing scenarios: {e}")
            return []

    def create_scenario(self, scenario_def: ScenarioDefinition) -> str:
        """
        Create and save a new scenario definition using ScenarioStorageService.
        Includes improved name validation to prevent race conditions.
        """
        # Handle both ScenarioDefinition objects and dictionaries
        scenario_name = scenario_def.name if hasattr(scenario_def, 'name') else scenario_def.get('name')
        if not scenario_name:
            raise ValueError("Scenario definition must have a name")
        
        # Double-check name uniqueness right before creation to prevent race conditions
        if self.scenario_name_exists(scenario_name):
            raise ValueError(f"Scenario with name '{scenario_name}' already exists")
        
        # Create the scenario
        scenario_id = self.storage_service.create_scenario(scenario_def)
        
        # Verify the scenario was created successfully and name is still unique
        created_scenario = self.get_scenario(scenario_id)
        if not created_scenario:
            raise ValueError("Failed to create scenario")
        
        # Final check: ensure no other scenarios with the same name exist
        scenarios_with_same_name = [
            s for s in self.storage_service.list_scenarios() 
            if s.get('name') == scenario_name and s.get('id') != scenario_id
        ]
        
        if scenarios_with_same_name:
            # Clean up the created scenario and raise error
            self.storage_service.delete_scenario(scenario_id)
            raise ValueError(f"Scenario with name '{scenario_name}' already exists (race condition detected)")
        
        return scenario_id

    def cleanup_duplicate_scenarios(self) -> Dict[str, int]:
        """
        Clean up duplicate scenarios with the same name.
        Keeps the most recently updated scenario for each name.
        Returns a dictionary with cleanup statistics.
        """
        try:
            scenarios = self.storage_service.list_scenarios()
            name_groups = {}
            
            # Group scenarios by name
            for scenario in scenarios:
                name = scenario.get('name', 'Unknown')
                if name not in name_groups:
                    name_groups[name] = []
                name_groups[name].append(scenario)
            
            # Find duplicates and clean them up
            cleaned_count = 0
            for name, scenario_list in name_groups.items():
                if len(scenario_list) > 1:
                    # Sort by updated_at (most recent first)
                    scenario_list.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
                    
                    # Keep the first (most recent) one, delete the rest
                    for scenario in scenario_list[1:]:
                        scenario_id = scenario.get('id')
                        if scenario_id:
                            logger.info(f"Deleting duplicate scenario: {scenario_id} (name: {name})")
                            if self.storage_service.delete_scenario(scenario_id):
                                cleaned_count += 1
                            else:
                                logger.error(f"Failed to delete duplicate scenario: {scenario_id}")
            
            return {
                "duplicates_found": sum(len(scenarios) - 1 for scenarios in name_groups.values() if len(scenarios) > 1),
                "duplicates_cleaned": cleaned_count,
                "unique_names": len(name_groups)
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up duplicate scenarios: {e}")
            return {"error": str(e)}

    def get_scenario(self, scenario_id: str) -> Optional[dict]:
        """
        Retrieve a scenario definition by ID and return as a dictionary, or None if not found.
        """
        scenario = self.storage_service.get_scenario(scenario_id)
        if scenario is not None:
            return scenario.model_dump()
        return None

    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario definition and its results."""
        return self.storage_service.delete_scenario(scenario_id)

    def update_scenario(self, scenario_id: str, scenario_def: ScenarioDefinition) -> bool:
        """
        Update an existing scenario by ID. Returns True if successful, False if not found.
        """
        try:
            return self.storage_service.update_scenario(scenario_id, scenario_def)
        except Exception as e:
            logger.error(f"Error updating scenario {scenario_id}: {e}")
            return False

    def scenario_name_exists(self, name: str, exclude_id: str = None) -> bool:
        """
        Check if a scenario with the given name already exists.
        Optionally exclude a specific scenario ID (for updates).
        """
        try:
            scenarios = self.storage_service.list_scenarios()
            for scenario in scenarios:
                if scenario.get('name') == name and (exclude_id is None or scenario.get('id') != exclude_id):
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking scenario name existence: {e}")
            return False

    def _load_scenario_definition(self, request: ScenarioRequest, correlation_id: str) -> ScenarioDefinition:
        """
        Load scenario definition from request or storage. Raises ValueError if not found.
        """
        scenario_def = request.scenario_definition
        if not scenario_def and request.scenario_id:
            self.logger.info("Loading scenario from storage", correlation_id=correlation_id, extra={"scenario_id": request.scenario_id})
            scenario = self.storage_service.get_scenario(request.scenario_id)
            if not scenario:
                self.logger.error("Scenario not found in storage", correlation_id=correlation_id, extra={"scenario_id": request.scenario_id})
                raise ValueError(f"Scenario not found: {request.scenario_id}")
            scenario_def = scenario
            scenario_name = scenario_def.name if hasattr(scenario_def, 'name') else scenario_def.get('name', 'Unknown')
            self.logger.info("Scenario loaded from storage", correlation_id=correlation_id, extra={"scenario_name": scenario_name})
        elif not scenario_def:
            self.logger.error("No scenario definition provided", correlation_id=correlation_id)
            raise ValueError("No scenario definition provided")
        return scenario_def

    def _validate_scenario(self, scenario_def, resolved_data=None, correlation_id=None):
        """
        Validate scenario definition and optionally resolved data.
        Raises ValueError if validation fails.
        """
        scenario_name = scenario_def.name if hasattr(scenario_def, 'name') else scenario_def.get('name', 'Unknown')
        self.logger.info("Validating scenario definition", correlation_id=correlation_id, extra={"scenario_name": scenario_name})
        self.scenario_validator.validate_scenario_definition(scenario_def)
        self.logger.info("Scenario definition validation passed", correlation_id=correlation_id)
        if resolved_data is not None:
            self.logger.info("Validating resolved scenario data", correlation_id=correlation_id)
            self.scenario_validator.validate_scenario_data(resolved_data)
            self.logger.info("Resolved scenario data validation passed", correlation_id=correlation_id)

    def _resolve_and_validate_scenario_data(self, scenario_def, correlation_id=None):
        """
        Resolve scenario data and validate the result.
        Returns resolved_data dict. Raises ValueError if validation fails.
        """
        self.logger.info("Resolving scenario data", correlation_id=correlation_id)
        
        # Check if this is a business plan scenario (V2)
        has_business_plan = hasattr(scenario_def, 'business_plan_id') and scenario_def.business_plan_id
        
        if has_business_plan:
            # For V2 engine, skip resolution and return minimal data
            resolved_data = {
                'business_plan_id': scenario_def.business_plan_id,
                'time_range': scenario_def.time_range,
                'office_scope': scenario_def.office_scope,
                'levers': scenario_def.levers.model_dump() if hasattr(scenario_def.levers, 'model_dump') else scenario_def.levers,
            }
        else:
            # Convert Pydantic models to dictionaries as expected by the scenario resolver
            resolved_data = self.scenario_resolver.resolve_scenario({
                'time_range': scenario_def.time_range,
                'office_scope': scenario_def.office_scope,
                'levers': scenario_def.levers.model_dump() if hasattr(scenario_def.levers, 'model_dump') else scenario_def.levers,
                'baseline_input': {},  # Not used with business plans
                'business_plan_id': scenario_def.business_plan_id if hasattr(scenario_def, 'business_plan_id') else None,
                'progression_config': scenario_def.progression_config.model_dump() if hasattr(scenario_def.progression_config, 'model_dump') else scenario_def.progression_config,
                'cat_curves': scenario_def.cat_curves.model_dump() if hasattr(scenario_def.cat_curves, 'model_dump') else scenario_def.cat_curves
            })
        try:
            self._validate_scenario(scenario_def, resolved_data=resolved_data, correlation_id=correlation_id)
        except Exception as e:
            self.logger.error(f"Resolved scenario data validation failed: {e}", correlation_id=correlation_id)
            raise ValueError(f"Resolved scenario data validation failed: {e}")
        self.logger.info("Scenario data resolved and validated", correlation_id=correlation_id)
        return resolved_data

    def _execute_simulation(self, scenario_def, resolved_data, correlation_id=None):
        """
        Execute the simulation engine and return results.
        Always uses V2 engine (V1 is legacy and will be removed).
        Handles business plan scenarios and scenarios without business plans.
        Raises ValueError on failure.
        """
        # Always use V2 engine (V1 is legacy)
        has_business_plan = hasattr(scenario_def, 'business_plan_id') and scenario_def.business_plan_id
        
        if has_business_plan:
            import sys
            sys.stderr.write("ABOUT TO LOG: Using V2 simulation engine with business plan\n")
            sys.stderr.flush()
            self.logger.info("Using V2 simulation engine with business plan", correlation_id=correlation_id, extra={
                "business_plan_id": scenario_def.business_plan_id
            })
            sys.stderr.write("LOGGED: Using V2 simulation engine with business plan\n")
            sys.stderr.flush()
        else:
            self.logger.info("Using V2 simulation engine without business plan", correlation_id=correlation_id)
        
        try:
            import sys
            sys.stderr.write("ABOUT TO CALL _call_simulation_engine_v2!\n")
            sys.stderr.flush()
            results = self._call_simulation_engine_v2(scenario_def, correlation_id)
            sys.stderr.write("RETURNED FROM _call_simulation_engine_v2!\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"EXCEPTION IN _call_simulation_engine_v2: {e}\n")
            sys.stderr.flush()
            self.logger.error(f"V2 simulation engine failed: {e}", correlation_id=correlation_id)
            raise ValueError(f"V2 simulation engine failed: {e}")
        
        self.logger.info("Simulation engine completed successfully", correlation_id=correlation_id)
        return results

    def _persist_scenario_results(self, request, scenario_def, results, execution_time, correlation_id=None):
        """
        Save scenario definition (if new) and results. Returns scenario_id.
        """
        scenario_id = request.scenario_id or str(uuid.uuid4())
        self.logger.info("Starting to persist scenario results", correlation_id=correlation_id, extra={
            "scenario_id": scenario_id,
            "has_existing_id": bool(request.scenario_id),
            "results_size": len(str(results)) if results else 0
        })
        
        # If this is a new scenario (no ID provided), save the scenario definition first
        if not request.scenario_id:
            scenario_def.id = scenario_id
            self.storage_service.create_scenario(scenario_def)
            scenario_name = scenario_def.name if hasattr(scenario_def, 'name') else scenario_def.get('name', 'Unknown')
            self.logger.info("Created new scenario definition", correlation_id=correlation_id, extra={
                "scenario_id": scenario_id,
                "scenario_name": scenario_name
            })
        
        # Save results
        try:
            save_success = self.storage_service.save_scenario_results(scenario_id, results)
            if save_success:
                self.logger.info("Scenario results saved successfully", correlation_id=correlation_id, extra={
                    "scenario_id": scenario_id,
                    "execution_time": execution_time
                })
            else:
                self.logger.error("Failed to save scenario results", correlation_id=correlation_id, extra={
                    "scenario_id": scenario_id,
                    "execution_time": execution_time
                })
        except Exception as e:
            self.logger.error("Exception while saving scenario results", correlation_id=correlation_id, extra={
                "scenario_id": scenario_id,
                "error": str(e),
                "execution_time": execution_time
            })
            raise
        
        return scenario_id

    def _call_simulation_engine_v2(self, scenario_def, correlation_id: str = None) -> Dict[str, Any]:
        """Call the V2 simulation engine for business plan scenarios."""
        try:
            import sys
            sys.stderr.write("ENTERING _call_simulation_engine_v2 METHOD!\n")
            sys.stderr.flush()
            self.logger.info("Initializing V2 simulation engine", correlation_id=correlation_id)
            
            # Create V2 engine
            engine = SimulationEngineV2()
            
            # Initialize V2 engine components
            if not engine.initialize():
                raise RuntimeError("Failed to initialize V2 simulation engine")
            
            # Convert scenario definition to V2 format
            from src.services.simulation_engine_v2 import ScenarioRequest as V2ScenarioRequest, TimeRange as V2TimeRange, Levers as V2Levers
            
            # Extract time range
            time_range_dict = scenario_def.time_range.model_dump() if hasattr(scenario_def.time_range, 'model_dump') else scenario_def.time_range
            
            # Convert levers from Pydantic model to V2 engine format (fixed levers access)
            if scenario_def.levers:
                # Extract representative multiplier for each lever type (use 'A' level as default, or first available)
                recruitment_mult = scenario_def.levers.recruitment.get('A', 1.0) if scenario_def.levers.recruitment else 1.0
                if recruitment_mult == 1.0 and scenario_def.levers.recruitment:
                    # If 'A' not found, use first available value
                    recruitment_mult = next(iter(scenario_def.levers.recruitment.values()), 1.0)
                
                churn_mult = scenario_def.levers.churn.get('A', 1.0) if scenario_def.levers.churn else 1.0
                if churn_mult == 1.0 and scenario_def.levers.churn:
                    churn_mult = next(iter(scenario_def.levers.churn.values()), 1.0)
                
                progression_mult = scenario_def.levers.progression.get('A', 1.0) if scenario_def.levers.progression else 1.0
                if progression_mult == 1.0 and scenario_def.levers.progression:
                    progression_mult = next(iter(scenario_def.levers.progression.values()), 1.0)
                
                levers = V2Levers(
                    recruitment_multiplier=recruitment_mult,
                    churn_multiplier=churn_mult,
                    progression_multiplier=progression_mult,
                    price_multiplier=1.0,
                    salary_multiplier=1.0
                )
            else:
                levers = V2Levers(
                    recruitment_multiplier=1.0,
                    churn_multiplier=1.0,
                    progression_multiplier=1.0,
                    price_multiplier=1.0,
                    salary_multiplier=1.0
                )
            
            # Create V2 scenario request
            v2_request = V2ScenarioRequest(
                scenario_id=scenario_def.id or str(uuid.uuid4()),
                name=scenario_def.name,
                time_range=V2TimeRange(
                    start_year=time_range_dict['start_year'],
                    start_month=time_range_dict['start_month'],
                    end_year=time_range_dict['end_year'],
                    end_month=time_range_dict['end_month']
                ),
                office_ids=scenario_def.office_scope or ['Group'],
                levers=levers,
                business_plan_id=scenario_def.business_plan_id,
                include_kpis=True,
                include_events=True,
                validation_enabled=True
            )
            
            self.logger.info("Running V2 simulation", correlation_id=correlation_id, extra={
                "scenario_id": v2_request.scenario_id,
                "business_plan_id": scenario_def.business_plan_id,
                "offices": v2_request.office_ids
            })
            
            # Run simulation
            results = engine.run_simulation(v2_request)
            
            self.logger.info("V2 simulation completed", correlation_id=correlation_id, extra={
                "scenario_id": v2_request.scenario_id,
                "results_structure": type(results).__name__
            })
            
            # Convert V2 results to V1-compatible format for frontend compatibility
            if hasattr(results, 'to_dict'):
                v2_results = results.to_dict()
            elif hasattr(results, 'model_dump'):
                v2_results = results.model_dump()
            else:
                # For dataclass objects, convert to dict
                from dataclasses import asdict, is_dataclass
                if is_dataclass(results):
                    v2_results = asdict(results)
                else:
                    # Fallback: try to convert using dict() or return as-is
                    try:
                        v2_results = dict(results) if hasattr(results, '__iter__') else results
                    except (TypeError, ValueError):
                        v2_results = results
            
            # DEBUG: Log what we're passing to transformation - FORCE OUTPUT
            import sys
            debug_msg = f"PRE-TRANSFORM DEBUG: V2 results keys = {list(v2_results.keys())}"
            print(debug_msg, flush=True)
            sys.stderr.write(debug_msg + "\n")
            sys.stderr.flush()
            
            if 'years' in v2_results:
                skip_msg = "PRE-TRANSFORM DEBUG: V2 results already contain 'years' key - will skip transformation!"
                print(skip_msg, flush=True)
                sys.stderr.write(skip_msg + "\n")
                sys.stderr.flush()
            else:
                transform_msg = "PRE-TRANSFORM DEBUG: V2 results in proper V2 format - will transform"
                print(transform_msg, flush=True)
                sys.stderr.write(transform_msg + "\n")
                sys.stderr.flush()
            
            # Transform V2 results to V1 format expected by frontend
            return self._transform_v2_to_v1_format(v2_results, correlation_id)
                
        except Exception as e:
            self.logger.error(f"V2 engine execution failed: {e}", correlation_id=correlation_id)
            raise

    @handle_service_errors
    def run_scenario(self, request: ScenarioRequest) -> ScenarioResponse:
        """
        Run a scenario and return the results.
        This is the main entry point for scenario execution.
        """
        correlation_id = str(uuid.uuid4())[:8]
        start_time = datetime.now()
        self.logger.info("Starting scenario execution", correlation_id=correlation_id, extra={
            "scenario_id": request.scenario_id,
            "has_scenario_definition": request.scenario_definition is not None
        })
        try:
            # 1. Load scenario definition
            try:
                scenario_def = self._load_scenario_definition(request, correlation_id)
            except ValueError as e:
                return ScenarioResponse(
                    status="error",
                    error_message=str(e),
                    scenario_id=request.scenario_id or "",
                    scenario_name="",
                    execution_time=0,
                    results={}
                )
            # 2. Validate scenario definition
            try:
                self._validate_scenario(scenario_def, correlation_id=correlation_id)
            except Exception as e:
                return ScenarioResponse(
                    status="error",
                    error_message=f"Validation failed: {e}",
                    scenario_id=request.scenario_id or "",
                    scenario_name=getattr(scenario_def, 'name', ""),
                    execution_time=0,
                    results={}
                )
            # 3. Resolve and validate scenario data
            try:
                resolved_data = self._resolve_and_validate_scenario_data(scenario_def, correlation_id=correlation_id)
            except Exception as e:
                return ScenarioResponse(
                    status="error",
                    error_message=f"Scenario data resolution failed: {e}",
                    scenario_id=request.scenario_id or "",
                    scenario_name=getattr(scenario_def, 'name', ""),
                    execution_time=0,
                    results={}
                )
            # 4. Execute simulation
            try:
                results = self._execute_simulation(scenario_def, resolved_data, correlation_id=correlation_id)
            except Exception as e:
                return ScenarioResponse(
                    status="error",
                    error_message=f"Simulation execution failed: {e}",
                    scenario_id=request.scenario_id or "",
                    scenario_name=getattr(scenario_def, 'name', ""),
                    execution_time=0,
                    results={}
                )
            # 5. Persist scenario definition and results
            execution_time = (datetime.now() - start_time).total_seconds()
            scenario_id = self._persist_scenario_results(request, scenario_def, results, execution_time, correlation_id=correlation_id)
            # 6. Return response
            scenario_name = scenario_def.name if hasattr(scenario_def, 'name') else scenario_def.get('name', 'Unknown')
            return ScenarioResponse(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                execution_time=execution_time,
                results=results,
                status="success"
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            scenario_name = ""
            if request.scenario_definition:
                scenario_name = request.scenario_definition.name if hasattr(request.scenario_definition, 'name') else request.scenario_definition.get('name', 'Unknown')
            self.logger.error(f"Error running scenario: {e}", correlation_id=correlation_id, extra={
                "execution_time": execution_time,
                "scenario_id": request.scenario_id or "",
                "scenario_name": scenario_name
            })
            return ScenarioResponse(
                status="error",
                error_message=str(e),
                scenario_id=request.scenario_id or "",
                scenario_name=scenario_name,
                execution_time=execution_time,
                results={}
            )

    def _call_simulation_engine(self, scenario_def: ScenarioDefinition, resolved_data: Dict[str, Any], economic_params: EconomicParameters, correlation_id: str = None) -> Dict[str, Any]:
        """Call the simulation engine with the prepared data."""
        try:
            # Extract time range from scenario definition
            # Convert time_range to dict if it's a Pydantic model
            time_range_dict = scenario_def.time_range.model_dump() if hasattr(scenario_def.time_range, 'model_dump') else scenario_def.time_range
            
            start_year = time_range_dict['start_year']
            start_month = time_range_dict['start_month']
            end_year = time_range_dict['end_year']
            end_month = time_range_dict['end_month']

            # Create simulation engine
            engine = SimulationEngine()
            
            # Build Office objects from the resolved configuration
            offices = self.office_builder.build_offices_from_config(
                resolved_data['offices_config'], 
                resolved_data['progression_config']
            )
            self.logger.info("Office objects built successfully", correlation_id=correlation_id, extra={"offices_built": len(offices)})
            
            # Create engine-ready data structure
            engine_ready_data = {
                'offices': offices,
                'progression_config': resolved_data['progression_config'],
                'cat_curves': resolved_data['cat_curves']
            }
            
            # Transform data for engine consumption
            engine_data = self.scenario_transformer.transform_scenario_data_for_engine(engine_ready_data, correlation_id)
            progression_config = engine_data['progression_config']
            cat_curves = engine_data['cat_curves']
            
            # Run simulation using the pure function approach
            results = engine.run_simulation_with_offices(
                start_year=start_year,
                start_month=start_month,
                end_year=end_year,
                end_month=end_month,
                offices=offices,
                progression_config=progression_config,
                cat_curves=cat_curves,
                economic_params=economic_params
            )
            
            # Transform results to serializable format
            final_results = self.scenario_transformer.transform_results_to_serializable(results, correlation_id)
            
            # Calculate KPIs for the simulation results
            try:
                from .kpi.kpi_service import KPIService
                kpi_service = KPIService(economic_params)
                
                # Calculate simulation duration in months
                simulation_duration_months = ((end_year - start_year) * 12) + (end_month - start_month + 1)
                
                # Calculate KPIs
                kpi_results = kpi_service.calculate_all_kpis(
                    final_results,
                    simulation_duration_months,
                    economic_params
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
                
                # Add KPIs to final results - but preserve the 'years' structure
                # The simulation engine already returns {'years': yearly_results}
                # We need to add year-specific KPIs to each year's data, not the same KPIs
                if 'years' in final_results:
                    for year_key, year_data in final_results['years'].items():
                        if isinstance(year_data, dict):
                            # Use year-specific KPIs from yearly_kpis dictionary
                            if hasattr(kpi_results, 'yearly_kpis') and year_key in kpi_results.yearly_kpis:
                                year_data['kpis'] = to_dict(kpi_results.yearly_kpis[year_key])
                            else:
                                # Fallback to main KPIs if year-specific not found
                                year_data['kpis'] = to_dict(kpi_results)
                
                self.logger.info("KPI calculation completed successfully", correlation_id=correlation_id)
                
            except Exception as e:
                self.logger.warning(f"KPI calculation failed: {e}", correlation_id=correlation_id)
                # If KPI calculation fails, still preserve the years structure
                if 'years' in final_results:
                    for year_key, year_data in final_results['years'].items():
                        if isinstance(year_data, dict):
                            year_data['kpis'] = {}
            
            self.logger.info(f"Simulation completed successfully for scenario: {scenario_def.name}", correlation_id=correlation_id)
            return final_results
            
        except Exception as e:
            self.logger.error(f"Simulation engine error: {e}", correlation_id=correlation_id)
            raise

    def get_scenario_results(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Get saved results for a specific scenario.
        """
        try:
            return self.storage_service.get_scenario_results(scenario_id)
        except Exception as e:
            logger.error(f"Error getting scenario results for {scenario_id}: {e}")
            return None

    def _transform_v2_to_v1_format(self, v2_results: Dict[str, Any], correlation_id: str = None) -> Dict[str, Any]:
        """
        Transform V2 simulation results to V1 format expected by frontend.
        
        V2 format: {
            scenario_id: str,
            monthly_results: { "YYYY-MM": MonthlyResults },
            all_events: PersonEvent[],
            final_workforce: { office: OfficeState }
        }
        
        V1 format: {
            years: {
                "YYYY": {
                    offices: {
                        "OfficeName": {
                            roles: {
                                "RoleName": {
                                    levels?: { "Level": [monthly_results] } OR
                                    months?: [monthly_results]
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        self.logger.info("Transforming V2 results to V1 format", correlation_id=correlation_id)
        
        # DEBUG: Log V2 results structure with print for immediate visibility
        monthly_results = v2_results.get('monthly_results', {})
        if monthly_results:
            first_month = next(iter(monthly_results.values()))
            first_office = next(iter(first_month.get('office_results', {}).values()))
            workforce_by_role = first_office.get('workforce_by_role', {})
            print(f"TRANSFORMATION DEBUG: workforce_by_role = {workforce_by_role}")
            for role, data in workforce_by_role.items():
                print(f"TRANSFORMATION DEBUG: {role} -> {type(data)} -> {data}")
        else:
            print(f"TRANSFORMATION DEBUG: No monthly_results found, v2_results keys: {list(v2_results.keys())}")
        
        try:
            # Check if this is already in V1 format
            if 'years' in v2_results:
                self.logger.info("Results already in V1 format - RETURNING EARLY!", correlation_id=correlation_id)
                self.logger.info(f"DEBUG: v2_results has 'years' key, bypassing transformation. Keys: {list(v2_results.keys())}", correlation_id=correlation_id)
                return v2_results
            
            # Extract monthly results from V2 format
            monthly_results = v2_results.get('monthly_results', {})
            
            if not monthly_results:
                self.logger.warning("No monthly_results found in V2 format", correlation_id=correlation_id)
                return {'years': {}}
            
            # Group monthly results by year
            years = {}
            for month_key, month_data in monthly_results.items():
                try:
                    year = str(month_data.get('year', month_key.split('-')[0]))
                    month_num = month_data.get('month', int(month_key.split('-')[1]))
                    
                    if year not in years:
                        years[year] = {
                            'offices': {}
                        }
                    
                    # Transform office results
                    office_results = month_data.get('office_results', {})
                    for office_name, office_data in office_results.items():
                        if office_name not in years[year]['offices']:
                            years[year]['offices'][office_name] = {
                                'roles': {}
                            }
                        
                        # Transform workforce data to role format
                        workforce_by_role = office_data.get('workforce_by_role', {})
                        for role_name, role_data in workforce_by_role.items():
                            if role_name not in years[year]['offices'][office_name]['roles']:
                                # Initialize role structure
                                if isinstance(role_data, dict):
                                    # Leveled role (e.g., Consultant: {'A': 5, 'AC': 5, ...})
                                    years[year]['offices'][office_name]['roles'][role_name] = {'levels': {}}
                                    for level_name, level_count in role_data.items():
                                        if level_name not in years[year]['offices'][office_name]['roles'][role_name]['levels']:
                                            years[year]['offices'][office_name]['roles'][role_name]['levels'][level_name] = [
                                                {'fte': 0, 'price': 0, 'salary': 0, 'recruitment': 0, 'churn': 0, 'progression': 0}
                                                for _ in range(12)
                                            ]
                                else:
                                    # Flat role (e.g., Operations: 5)
                                    years[year]['offices'][office_name]['roles'][role_name] = {
                                        'months': [
                                            {'fte': 0, 'price': 0, 'salary': 0, 'recruitment': 0, 'churn': 0, 'progression': 0}
                                            for _ in range(12)
                                        ]
                                    }
                            
                            # Update monthly data
                            month_index = month_num - 1  # Convert to 0-indexed
                            if isinstance(role_data, dict):
                                # Leveled role
                                for level_name, level_count in role_data.items():
                                    if level_name in years[year]['offices'][office_name]['roles'][role_name]['levels']:
                                        monthly_result = years[year]['offices'][office_name]['roles'][role_name]['levels'][level_name][month_index]
                                        monthly_result['fte'] = level_count if isinstance(level_count, (int, float)) else 0
                                        # Get proper price and salary from business plan instead of incorrect calculations
                                        monthly_result['salary'] = self._get_business_plan_salary(office_name, role_name, level_name)
                                        monthly_result['price'] = self._get_business_plan_price(office_name, role_name, level_name)
                                        
                                        # Add recruitment and churn data
                                        recruitment_data = office_data.get('recruitment_by_role', {}).get(role_name, {})
                                        churn_data = office_data.get('churn_by_role', {}).get(role_name, {})
                                        monthly_result['recruitment'] = recruitment_data.get(level_name, 0)
                                        monthly_result['churn'] = churn_data.get(level_name, 0)
                            else:
                                # Flat role
                                if 'months' in years[year]['offices'][office_name]['roles'][role_name]:
                                    monthly_result = years[year]['offices'][office_name]['roles'][role_name]['months'][month_index]
                                    monthly_result['fte'] = role_data if isinstance(role_data, (int, float)) else 0
                                    monthly_result['salary'] = self._get_business_plan_salary(office_name, role_name)
                                    monthly_result['price'] = self._get_business_plan_price(office_name, role_name)
                                    
                                    # Add recruitment and churn data for flat roles
                                    recruitment_data = office_data.get('recruitment_by_role', {}).get(role_name, {})
                                    churn_data = office_data.get('churn_by_role', {}).get(role_name, {})
                                    total_recruitment = sum(recruitment_data.values()) if recruitment_data else 0
                                    total_churn = sum(churn_data.values()) if churn_data else 0
                                    monthly_result['recruitment'] = total_recruitment
                                    monthly_result['churn'] = total_churn
                        
                        # If no workforce data, create empty structure
                        if not workforce_by_role and office_data.get('total_workforce', 0) == 0:
                            # Add empty roles for common role types based on office data
                            pass  # Keep empty for now
                    
                except (ValueError, KeyError, IndexError) as e:
                    self.logger.warning(f"Error processing month {month_key}: {e}", correlation_id=correlation_id)
                    continue
            
            v1_results = {'years': years}
            self.logger.info(f"Transformed V2 to V1 format: {len(years)} years", correlation_id=correlation_id)
            
            return v1_results
            
        except Exception as e:
            self.logger.error(f"Error transforming V2 to V1 format: {e}", correlation_id=correlation_id)
            # Return empty V1 structure as fallback
            return {'years': {}}

    def _get_business_plan_price(self, office_name: str, role_name: str, level_name: str = None) -> float:
        """Get price from business plan for specific role/level"""
        try:
            # Check if we have a loaded business plan for this office
            business_plans = getattr(self.simulation_engine, 'business_processor', None)
            if not business_plans or not hasattr(business_plans, 'loaded_plans'):
                self.logger.warning(f"No business_processor or loaded_plans for {office_name}")
                return 1128.0  # Oslo default
            
            # Get business plan for office
            office_plan = business_plans.loaded_plans.get(office_name)
            if not office_plan:
                self.logger.warning(f"No business plan loaded for office {office_name}, available: {list(business_plans.loaded_plans.keys())}")
                return 1128.0  # Oslo default
                
            # Handle raw business plan format (entries)
            if isinstance(office_plan, dict) and 'entries' in office_plan:
                for entry in office_plan['entries']:
                    if entry.get('role') == role_name:
                        if level_name is None or entry.get('level') == level_name:
                            price = float(entry.get('price', 1128.0))
                            self.logger.info(f"Found business plan price for {office_name} {role_name} {level_name}: {price}")
                            return price
            
            self.logger.warning(f"No matching entry found for {office_name} {role_name} {level_name}")
            return 1128.0  # Oslo default fallback
            
        except Exception as e:
            self.logger.warning(f"Error getting business plan price: {e}")
            return 1128.0  # Oslo default fallback

    def _get_business_plan_salary(self, office_name: str, role_name: str, level_name: str = None) -> float:
        """Get salary from business plan for specific role/level"""
        try:
            # Check if we have a loaded business plan for this office
            business_plans = getattr(self.simulation_engine, 'business_processor', None)
            if not business_plans or not hasattr(business_plans, 'loaded_plans'):
                self.logger.warning(f"No business_processor or loaded_plans for {office_name}")
                return 40000.0  # Oslo default
            
            # Get business plan for office
            office_plan = business_plans.loaded_plans.get(office_name)
            if not office_plan:
                self.logger.warning(f"No business plan loaded for office {office_name}, available: {list(business_plans.loaded_plans.keys())}")
                return 40000.0  # Oslo default
                
            # Handle raw business plan format (entries)
            if isinstance(office_plan, dict) and 'entries' in office_plan:
                for entry in office_plan['entries']:
                    if entry.get('role') == role_name:
                        if level_name is None or entry.get('level') == level_name:
                            salary = float(entry.get('salary', 40000.0))
                            self.logger.info(f"Found business plan salary for {office_name} {role_name} {level_name}: {salary}")
                            return salary
            
            self.logger.warning(f"No matching salary entry found for {office_name} {role_name} {level_name}")
            return 40000.0  # Oslo default fallback
            
        except Exception as e:
            self.logger.warning(f"Error getting business plan salary: {e}")
            return 40000.0  # Oslo default fallback 