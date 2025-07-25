"""
Pydantic models for scenario definitions and API requests/responses.
Updated to use unified data structures.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Any, Optional
from datetime import datetime
from .unified_data_models import (
    ScenarioDefinition as UnifiedScenarioDefinition,
    TimeRange,
    EconomicParameters,
    BaselineInput,
    Levers
)

# Use the unified ScenarioDefinition as the base, with backward compatibility
ScenarioDefinition = UnifiedScenarioDefinition

class ValidationResponse(BaseModel):
    """Response from scenario validation."""
    valid: bool = Field(..., description="Whether the scenario is valid")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")

class LegacyScenarioDefinition(BaseModel):
    """Legacy scenario definition for backward compatibility"""
    id: Optional[str] = Field(None, description="Unique scenario identifier")
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    time_range: Dict[str, int] = Field(..., description="Start and end year/month")
    office_scope: List[str] = Field(..., description="List of offices to include in scenario")
    levers: Dict[str, Any] = Field(default_factory=dict, description="Lever multipliers by type and level")
    economic_params: Optional[Dict[str, float]] = Field(default=None, description="Economic parameters")
    progression_config: Optional[Dict[str, Any]] = Field(default=None, description="Custom progression configuration")
    cat_curves: Optional[Dict[str, Any]] = Field(default=None, description="Custom CAT curves configuration")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    baseline_input: Optional[Dict[str, Any]] = None
    
    @field_validator('time_range')
    @classmethod
    def validate_time_range(cls, v):
        required_keys = {'start_year', 'start_month', 'end_year', 'end_month'}
        if not all(key in v for key in required_keys):
            raise ValueError(f"Time range must include: {required_keys}")
        
        if v['start_year'] > v['end_year']:
            raise ValueError("Start year cannot be after end year")
        
        if v['start_month'] < 1 or v['start_month'] > 12:
            raise ValueError("Start month must be between 1 and 12")
        
        if v['end_month'] < 1 or v['end_month'] > 12:
            raise ValueError("End month must be between 1 and 12")
        
        return v

class ScenarioRequest(BaseModel):
    """Request to run a scenario."""
    scenario_id: Optional[str] = Field(None, description="ID of existing scenario to run")
    scenario_definition: Optional[ScenarioDefinition] = Field(None, description="New scenario definition")
    office_scope: Optional[List[str]] = Field(None, description="Override office scope for existing scenario")
    
    @field_validator('scenario_id', 'scenario_definition')
    @classmethod
    def validate_scenario_source(cls, v, info):
        data = info.data
        if 'scenario_id' in data and 'scenario_definition' in data:
            if data['scenario_id'] is None and data['scenario_definition'] is None:
                raise ValueError("Either scenario_id or scenario_definition must be provided")
            if data['scenario_id'] is not None and data['scenario_definition'] is not None:
                raise ValueError("Cannot provide both scenario_id and scenario_definition")
        return v

class ScenarioResponse(BaseModel):
    """Response from scenario execution."""
    scenario_id: str = Field(..., description="Unique scenario identifier")
    scenario_name: str = Field(..., description="Scenario name")
    execution_time: float = Field(..., description="Execution time in seconds")
    results: Dict[str, Any] = Field(..., description="Simulation results")
    status: str = Field(..., description="Execution status (success, error)")
    error_message: Optional[str] = Field(None, description="Error message if status is error")

class ScenarioListResponse(BaseModel):
    """Response for listing scenarios."""
    scenarios: List[Dict[str, Any]] = Field(..., description="List of scenario metadata")
    total_count: int = Field(..., description="Total number of scenarios")

class ScenarioComparisonRequest(BaseModel):
    """Request to compare multiple scenarios."""
    scenario_ids: List[str] = Field(..., description="List of scenario IDs to compare")
    comparison_type: str = Field(default="side_by_side", description="Type of comparison")
    
    @field_validator('scenario_ids')
    @classmethod
    def validate_scenario_ids(cls, v):
        if len(v) < 2:
            raise ValueError("At least 2 scenario IDs required for comparison")
        if len(v) > 5:
            raise ValueError("Maximum 5 scenarios can be compared at once")
        return v

class LeverPlan(BaseModel):
    """Internal model for the lever plan format expected by the simulation engine."""
    offices: Dict[str, Dict[str, Dict[str, Dict[str, float]]]] = Field(..., description="Office -> Role -> Level -> Attribute -> Value") 