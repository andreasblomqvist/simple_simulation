"""
Office management models for business planning and configuration.
"""
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, root_validator


class OfficeJourney(str, Enum):
    """Office maturity levels."""
    EMERGING = "emerging"
    ESTABLISHED = "established"
    MATURE = "mature"


class ProgressionCurve(str, Enum):
    """CAT progression curve types."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    CUSTOM = "custom"


class EconomicParameters(BaseModel):
    """Economic parameters for office configuration."""
    cost_of_living: float = Field(ge=0.1, le=3.0, description="Cost of living multiplier")
    market_multiplier: float = Field(ge=0.1, le=3.0, description="Market rate multiplier")
    tax_rate: float = Field(ge=0.0, le=1.0, description="Tax rate (0.0 to 1.0)")

    class Config:
        schema_extra = {
            "example": {
                "cost_of_living": 1.2,
                "market_multiplier": 1.1,
                "tax_rate": 0.25
            }
        }


class OfficeConfig(BaseModel):
    """Office configuration model."""
    id: Optional[UUID] = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=100, description="Office name")
    journey: OfficeJourney = Field(description="Office maturity level")
    timezone: str = Field(default="UTC", max_length=50, description="Office timezone")
    economic_parameters: EconomicParameters = Field(default_factory=lambda: EconomicParameters(
        cost_of_living=1.0,
        market_multiplier=1.0,
        tax_rate=0.25
    ))
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('Office name cannot be empty or whitespace')
        return v.strip()

    @validator('timezone')
    def validate_timezone(cls, v):
        # Basic timezone validation - could be expanded with pytz
        if not v or v.isspace():
            raise ValueError('Timezone cannot be empty')
        return v.strip()

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "name": "Stockholm",
                "journey": "mature",
                "timezone": "Europe/Stockholm",
                "economic_parameters": {
                    "cost_of_living": 1.2,
                    "market_multiplier": 1.1,
                    "tax_rate": 0.25
                }
            }
        }


class WorkforceEntry(BaseModel):
    """Single workforce entry for a role/level combination."""
    role: str = Field(min_length=1, max_length=50, description="Role name (e.g., Consultant, Sales)")
    level: str = Field(min_length=1, max_length=10, description="Level name (e.g., A, AC, C, SrC)")
    fte: int = Field(ge=0, description="Full-time equivalent count")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")

    @validator('role', 'level')
    def validate_role_level(cls, v):
        if not v or v.isspace():
            raise ValueError('Role and level cannot be empty')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "role": "Consultant",
                "level": "SrC",
                "fte": 5,
                "notes": "Senior consultants for project leadership"
            }
        }


class WorkforceDistribution(BaseModel):
    """Workforce distribution for an office."""
    id: Optional[UUID] = Field(default_factory=uuid4)
    office_id: UUID = Field(description="Office ID")
    start_date: date = Field(description="Effective start date for this distribution")
    workforce: List[WorkforceEntry] = Field(description="Workforce entries by role and level")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('workforce')
    def validate_workforce(cls, v):
        if not v:
            return v
        
        # Check for duplicate role/level combinations
        role_level_pairs = [(entry.role, entry.level) for entry in v]
        if len(role_level_pairs) != len(set(role_level_pairs)):
            raise ValueError('Duplicate role/level combinations found in workforce')
        
        return v

    def get_total_fte(self) -> int:
        """Calculate total FTE across all workforce entries."""
        return sum(entry.fte for entry in self.workforce)

    def get_fte_by_role(self, role: str) -> int:
        """Get total FTE for a specific role."""
        return sum(entry.fte for entry in self.workforce if entry.role == role)

    def get_fte_by_level(self, level: str) -> int:
        """Get total FTE for a specific level."""
        return sum(entry.fte for entry in self.workforce if entry.level == level)

    class Config:
        schema_extra = {
            "example": {
                "office_id": "123e4567-e89b-12d3-a456-426614174000",
                "start_date": "2024-01-01",
                "workforce": [
                    {"role": "Consultant", "level": "A", "fte": 25, "notes": "Associate consultants"},
                    {"role": "Consultant", "level": "AC", "fte": 18, "notes": "Advanced consultants"},
                    {"role": "Consultant", "level": "SrC", "fte": 8, "notes": "Senior consultants"}
                ]
            }
        }


class MonthlyPlanEntry(BaseModel):
    """Monthly business plan entry for a role/level combination."""
    role: str = Field(min_length=1, max_length=50, description="Role name")
    level: str = Field(min_length=1, max_length=10, description="Level name")
    recruitment: int = Field(ge=0, description="Planned new hires for this month")
    churn: int = Field(ge=0, description="Planned departures for this month")
    price: float = Field(ge=0, description="Hourly billing rate")
    utr: float = Field(ge=0, le=1, description="Utilization rate (0.0 to 1.0)")
    salary: float = Field(ge=0, description="Monthly salary")

    @validator('role', 'level')
    def validate_role_level(cls, v):
        if not v or v.isspace():
            raise ValueError('Role and level cannot be empty')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "role": "Consultant",
                "level": "SrC",
                "recruitment": 2,
                "churn": 1,
                "price": 150.0,
                "utr": 0.75,
                "salary": 8500.0
            }
        }


class MonthlyBusinessPlan(BaseModel):
    """Monthly business plan for an office."""
    id: Optional[UUID] = Field(default_factory=uuid4)
    office_id: UUID = Field(description="Office ID")
    year: int = Field(ge=2020, le=2050, description="Plan year")
    month: int = Field(ge=1, le=12, description="Plan month (1-12)")
    entries: List[MonthlyPlanEntry] = Field(description="Business plan entries by role and level")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('entries')
    def validate_entries(cls, v):
        if not v:
            return v
        
        # Check for duplicate role/level combinations
        role_level_pairs = [(entry.role, entry.level) for entry in v]
        if len(role_level_pairs) != len(set(role_level_pairs)):
            raise ValueError('Duplicate role/level combinations found in business plan')
        
        return v

    def get_total_recruitment(self) -> int:
        """Calculate total planned recruitment for the month."""
        return sum(entry.recruitment for entry in self.entries)

    def get_total_churn(self) -> int:
        """Calculate total planned churn for the month."""
        return sum(entry.churn for entry in self.entries)

    def get_net_change(self) -> int:
        """Calculate net headcount change (recruitment - churn)."""
        return self.get_total_recruitment() - self.get_total_churn()

    def get_revenue_potential(self) -> float:
        """Calculate total monthly revenue potential."""
        # Assuming 160 working hours per month
        return sum(entry.price * entry.utr * 160 for entry in self.entries)

    def get_total_salary_cost(self) -> float:
        """Calculate total monthly salary cost."""
        return sum(entry.salary for entry in self.entries)

    class Config:
        schema_extra = {
            "example": {
                "office_id": "123e4567-e89b-12d3-a456-426614174000",
                "year": 2024,
                "month": 3,
                "entries": [
                    {
                        "role": "Consultant",
                        "level": "SrC",
                        "recruitment": 2,
                        "churn": 1,
                        "price": 150.0,
                        "utr": 0.75,
                        "salary": 8500.0
                    }
                ]
            }
        }


class ProgressionPoint(BaseModel):
    """Custom progression curve point."""
    month: int = Field(ge=1, description="Month number (1-12)")
    rate: float = Field(ge=0, le=1, description="Progression rate for this month")

    class Config:
        schema_extra = {
            "example": {
                "month": 6,
                "rate": 0.08
            }
        }


class ProgressionConfig(BaseModel):
    """CAT progression configuration for a specific level."""
    id: Optional[UUID] = Field(default_factory=uuid4)
    office_id: UUID = Field(description="Office ID")
    level: str = Field(min_length=1, max_length=10, description="Level name")
    monthly_rate: float = Field(ge=0, le=1, description="Base monthly progression rate")
    curve_type: ProgressionCurve = Field(default=ProgressionCurve.LINEAR, description="Progression curve type")
    custom_points: List[ProgressionPoint] = Field(default_factory=list, description="Custom curve points")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('level')
    def validate_level(cls, v):
        if not v or v.isspace():
            raise ValueError('Level cannot be empty')
        return v.strip()

    @validator('custom_points')
    def validate_custom_points(cls, v, values):
        curve_type = values.get('curve_type')
        
        if curve_type == ProgressionCurve.CUSTOM:
            if not v:
                raise ValueError('Custom points required when curve_type is custom')
            
            # Check for duplicate months
            months = [point.month for point in v]
            if len(months) != len(set(months)):
                raise ValueError('Duplicate months found in custom points')
        
        return v

    def get_rate_for_month(self, month: int) -> float:
        """Get progression rate for a specific month."""
        if self.curve_type == ProgressionCurve.LINEAR:
            return self.monthly_rate
        elif self.curve_type == ProgressionCurve.EXPONENTIAL:
            # Simple exponential curve - could be made more sophisticated
            return self.monthly_rate * (1.1 ** (month - 1))
        elif self.curve_type == ProgressionCurve.CUSTOM:
            # Find the custom point for this month
            for point in self.custom_points:
                if point.month == month:
                    return point.rate
            # Fall back to base rate if no custom point found
            return self.monthly_rate
        
        return self.monthly_rate

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "office_id": "123e4567-e89b-12d3-a456-426614174000",
                "level": "SrC",
                "monthly_rate": 0.05,
                "curve_type": "linear",
                "custom_points": []
            }
        }


class OfficeBusinessPlanSummary(BaseModel):
    """Summary view of an office's complete business plan."""
    office: OfficeConfig
    workforce_distribution: Optional[WorkforceDistribution] = None
    monthly_plans: List[MonthlyBusinessPlan] = Field(default_factory=list)
    progression_configs: List[ProgressionConfig] = Field(default_factory=list)

    def get_plan_for_month(self, year: int, month: int) -> Optional[MonthlyBusinessPlan]:
        """Get business plan for a specific month."""
        for plan in self.monthly_plans:
            if plan.year == year and plan.month == month:
                return plan
        return None

    def get_progression_for_level(self, level: str) -> Optional[ProgressionConfig]:
        """Get progression configuration for a specific level."""
        for config in self.progression_configs:
            if config.level == level:
                return config
        return None

    def get_annual_summary(self, year: int) -> Dict[str, Any]:
        """Get annual summary statistics for a specific year."""
        year_plans = [plan for plan in self.monthly_plans if plan.year == year]
        
        if not year_plans:
            return {"year": year, "total_recruitment": 0, "total_churn": 0, "net_change": 0}
        
        total_recruitment = sum(plan.get_total_recruitment() for plan in year_plans)
        total_churn = sum(plan.get_total_churn() for plan in year_plans)
        
        return {
            "year": year,
            "total_recruitment": total_recruitment,
            "total_churn": total_churn,
            "net_change": total_recruitment - total_churn,
            "months_planned": len(year_plans)
        }

    class Config:
        schema_extra = {
            "example": {
                "office": {
                    "name": "Stockholm",
                    "journey": "mature",
                    "timezone": "Europe/Stockholm"
                },
                "workforce_distribution": {
                    "start_date": "2024-01-01",
                    "workforce": [
                        {"role": "Consultant", "level": "SrC", "fte": 20}
                    ]
                },
                "monthly_plans": [
                    {
                        "year": 2024,
                        "month": 3,
                        "entries": [
                            {
                                "role": "Consultant",
                                "level": "SrC",
                                "recruitment": 2,
                                "churn": 1,
                                "price": 150.0,
                                "utr": 0.75,
                                "salary": 8500.0
                            }
                        ]
                    }
                ]
            }
        }