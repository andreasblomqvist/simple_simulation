"""
Unified Data Structure Models for SimpleSim

This module defines the exact data structures as documented in docs/SIMULATION_DATA_STRUCTURES.md
to ensure consistency across all system components.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from enum import Enum


class TimeRange(BaseModel):
    """Time range for scenario execution"""
    start_year: int = Field(..., ge=2020, le=2040)
    start_month: int = Field(..., ge=1, le=12)
    end_year: int = Field(..., ge=2020, le=2040)
    end_month: int = Field(..., ge=1, le=12)
    
    @field_validator('end_year')
    @classmethod
    def validate_end_after_start(cls, v, info):
        if hasattr(info, 'data') and 'start_year' in info.data and v < info.data['start_year']:
            raise ValueError('End year must be after or equal to start year')
        return v


class EconomicParameters(BaseModel):
    """Economic parameters for simulation"""
    working_hours_per_month: float = Field(default=160.0, gt=0)
    employment_cost_rate: float = Field(default=0.3, ge=0, le=1)
    unplanned_absence: float = Field(default=0.05, ge=0, le=1)
    other_expense: float = Field(default=1000000.0, ge=0)


class ProgressionLevelConfig(BaseModel):
    """Configuration for a single progression level"""
    progression_months: List[int] = Field(..., description="Months when progression can occur (1-12)")
    start_tenure: int = Field(..., ge=1, description="Starting tenure in months")
    time_on_level: int = Field(..., ge=1, description="Minimum time on level in months")
    next_level: Optional[str] = Field(None, description="Next level in progression path")
    journey: str = Field(..., description="Journey identifier (e.g., 'J-1')")
    
    @field_validator('progression_months')
    @classmethod
    def validate_progression_months(cls, v):
        if not all(1 <= month <= 12 for month in v):
            raise ValueError('Progression months must be between 1 and 12')
        return v


class ProgressionConfig(BaseModel):
    """Complete progression configuration for all levels"""
    levels: Dict[str, ProgressionLevelConfig] = Field(..., description="Level configurations")
    
    @field_validator('levels')
    @classmethod
    def validate_levels_not_empty(cls, v):
        if not v:
            raise ValueError('At least one level configuration is required')
        return v


class CATCurveLevel(BaseModel):
    """CAT curve configuration for a single level"""
    curves: Dict[str, float] = Field(..., description="CAT curves (e.g., 'CAT0': 0.0, 'CAT6': 0.919)")
    
    @field_validator('curves')
    @classmethod
    def validate_cat_values(cls, v):
        for cat_key, value in v.items():
            if not cat_key.startswith('CAT'):
                raise ValueError(f'CAT curve key must start with "CAT": {cat_key}')
            if not 0 <= value <= 1:
                raise ValueError(f'CAT curve value must be between 0 and 1: {value}')
        return v


class CATCurves(BaseModel):
    """Complete CAT curves configuration"""
    curves: Dict[str, CATCurveLevel] = Field(..., description="CAT curves by level")


class MonthlyValues(BaseModel):
    """Monthly values using YYYYMM format keys"""
    values: Dict[str, float] = Field(..., description="Monthly values with YYYYMM keys")
    
    @field_validator('values')
    @classmethod
    def validate_month_format(cls, v):
        for month_key, value in v.items():
            if not (len(month_key) == 6 and month_key.isdigit()):
                raise ValueError(f'Month key must be in YYYYMM format: {month_key}')
            year = int(month_key[:4])
            month = int(month_key[4:6])
            if not (2020 <= year <= 2040):
                raise ValueError(f'Year must be between 2020 and 2040: {year}')
            if not (1 <= month <= 12):
                raise ValueError(f'Month must be between 1 and 12: {month}')
            if value < 0:
                raise ValueError(f'Values cannot be negative: {value}')
        return v


class LevelData(BaseModel):
    """Data for a single level within a role"""
    recruitment: MonthlyValues = Field(..., description="Monthly recruitment values")
    churn: MonthlyValues = Field(..., description="Monthly churn values")


class RoleData(BaseModel):
    """Data for a role - either leveled (dict) or flat (direct monthly values)"""
    # For leveled roles (e.g., Consultant)
    levels: Optional[Dict[str, LevelData]] = Field(None, description="Level data for leveled roles")
    
    # For flat roles (e.g., Operations)
    recruitment: Optional[MonthlyValues] = Field(None, description="Direct recruitment for flat roles")
    churn: Optional[MonthlyValues] = Field(None, description="Direct churn for flat roles")
    
    @field_validator('levels', 'recruitment', 'churn')
    @classmethod
    def validate_role_structure(cls, v, info):
        # Either levels OR direct recruitment/churn, not both
        if hasattr(info, 'field_name') and hasattr(info, 'data'):
            field_name = info.field_name
            data = info.data
            
            if field_name == 'levels' and v is not None:
                if data.get('recruitment') is not None or data.get('churn') is not None:
                    raise ValueError('Cannot have both levels and direct recruitment/churn')
            elif field_name in ['recruitment', 'churn'] and v is not None:
                if data.get('levels') is not None:
                    raise ValueError('Cannot have both levels and direct recruitment/churn')
        return v


class BaselineInput(BaseModel):
    """Baseline input structure as documented"""
    model_config = ConfigDict(populate_by_name=True)
    
    global_data: Dict[str, Dict[str, RoleData]] = Field(..., alias="global")
    
    @field_validator('global_data')
    @classmethod
    def validate_global_structure(cls, v):
        required_keys = {'recruitment', 'churn'}
        if not all(key in v for key in required_keys):
            raise ValueError(f'Global data must contain keys: {required_keys}')
        return v


class Levers(BaseModel):
    """Lever multipliers by type and level"""
    recruitment: Dict[str, float] = Field(default_factory=dict, description="Recruitment multipliers by level")
    churn: Dict[str, float] = Field(default_factory=dict, description="Churn multipliers by level")
    progression: Dict[str, float] = Field(default_factory=dict, description="Progression multipliers by level")
    
    @field_validator('recruitment', 'churn', 'progression')
    @classmethod
    def validate_multipliers(cls, v):
        for level, multiplier in v.items():
            if multiplier < 0:
                raise ValueError(f'Multiplier cannot be negative: {multiplier}')
        return v


class ScenarioDefinition(BaseModel):
    """Complete scenario definition following documented structure"""
    id: Optional[str] = Field(None, description="Unique scenario identifier")
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    time_range: TimeRange = Field(..., description="Time range for execution")
    office_scope: List[str] = Field(..., description="Offices to include in scenario")
    levers: Levers = Field(default_factory=Levers, description="Lever multipliers")
    economic_params: EconomicParameters = Field(default_factory=EconomicParameters)
    progression_config: Optional[ProgressionConfig] = Field(None, description="Custom progression configuration")
    cat_curves: Optional[CATCurves] = Field(None, description="Custom CAT curves")
    business_plan_id: Optional[str] = Field(None, description="Business plan ID to use as baseline")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # baseline_input removed - V2 engine uses business plans instead
    model_config = ConfigDict(populate_by_name=True)


# Simulation Results Structure (Output)

class MonthlyResult(BaseModel):
    """Monthly result data as documented"""
    fte: float = Field(..., description="Full-time equivalent count")
    price: float = Field(..., description="Monthly price")
    salary: float = Field(..., description="Monthly salary")
    recruitment: int = Field(..., description="Recruitment count")
    churn: int = Field(..., description="Churn count")
    progression: int = Field(default=0, description="Progression count")


class LevelResults(BaseModel):
    """Results for a single level - list of 12 monthly results"""
    months: List[MonthlyResult] = Field(..., description="12 monthly results (0-indexed)")
    
    @field_validator('months')
    @classmethod
    def validate_months_count(cls, v):
        if len(v) != 12:
            raise ValueError('Must have exactly 12 monthly results')
        return v


class RoleResults(BaseModel):
    """Results for a role - either leveled (dict) or flat (list)"""
    # For leveled roles
    levels: Optional[Dict[str, LevelResults]] = Field(None, description="Results by level")
    
    # For flat roles
    months: Optional[List[MonthlyResult]] = Field(None, description="Direct monthly results")
    
    @field_validator('months')
    @classmethod
    def validate_flat_months(cls, v):
        if v is not None and len(v) != 12:
            raise ValueError('Flat role must have exactly 12 monthly results')
        return v


class OfficeResults(BaseModel):
    """Results for a single office"""
    roles: Dict[str, RoleResults] = Field(..., description="Results by role")


class YearResults(BaseModel):
    """Results for a single year"""
    offices: Dict[str, OfficeResults] = Field(..., description="Results by office")


class SimulationResults(BaseModel):
    """Complete simulation results structure"""
    years: Dict[str, YearResults] = Field(..., description="Results by year")


# Validation Utilities

def validate_scenario_definition(scenario_data: Dict[str, Any]) -> ScenarioDefinition:
    """Validate and convert scenario data to unified structure"""
    try:
        return ScenarioDefinition.model_validate(scenario_data)
    except Exception as e:
        raise ValueError(f"Invalid scenario definition: {e}")


def validate_baseline_input_structure(baseline_input: Dict[str, Any]) -> BaselineInput:
    """Validate baseline input structure"""
    try:
        return BaselineInput.model_validate(baseline_input)
    except Exception as e:
        raise ValueError(f"Invalid baseline input structure: {e}")


def is_leveled_role(role_data: Union[Dict, List]) -> bool:
    """Check if role data represents a leveled role (dict) or flat role (list)"""
    return isinstance(role_data, dict) and 'levels' in role_data


def get_monthly_value(monthly_data: Union[Dict[str, float], List[float]], month_index: int) -> float:
    """Get monthly value from either YYYYMM dict or 0-indexed list"""
    if isinstance(monthly_data, dict):
        # Convert month_index to YYYYMM format (assuming current year)
        year = datetime.now().year
        month = month_index + 1  # Convert 0-indexed to 1-indexed
        month_key = f"{year}{month:02d}"
        return monthly_data.get(month_key, 0.0)
    elif isinstance(monthly_data, list):
        return monthly_data[month_index] if month_index < len(monthly_data) else 0.0
    else:
        return 0.0


# Migration Utilities

def migrate_old_scenario_to_unified(old_scenario: Dict[str, Any]) -> ScenarioDefinition:
    """Migrate old scenario format to unified structure"""
    # Handle field name changes
    if 'total' in old_scenario:
        old_scenario['fte'] = old_scenario.pop('total')
    
    # Handle price structure changes
    if any(f'price_{i}' in old_scenario for i in range(1, 13)):
        monthly_prices = {}
        for i in range(1, 13):
            price_key = f'price_{i}'
            if price_key in old_scenario:
                year = datetime.now().year
                month_key = f"{year}{i:02d}"
                monthly_prices[month_key] = old_scenario.pop(price_key)
        old_scenario['price'] = monthly_prices
    
    # Remove deprecated fields
    old_scenario.pop('progression_rate', None)
    
    return validate_scenario_definition(old_scenario)