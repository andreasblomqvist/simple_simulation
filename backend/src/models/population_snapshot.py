"""
Population Snapshot Models
Comprehensive tracking of office populations, FTE counts, and settings over time
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from enum import Enum
from decimal import Decimal


class SnapshotType(str, Enum):
    """Types of snapshots"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    EVENT_DRIVEN = "event_driven"  # For major changes like reorganization


class EmployeeStatus(str, Enum):
    """Employee status options"""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    NOTICE_PERIOD = "notice_period"
    CONTRACTOR = "contractor"
    INTERN = "intern"


class OfficeJourney(str, Enum):
    """Office maturity journey stages"""
    EMERGING = "emerging"
    ESTABLISHED = "established"
    MATURE = "mature"


# Individual Employee Record (for detailed population tracking)

class EmployeeRecord(BaseModel):
    """Individual employee record within a population snapshot"""
    employee_id: str = Field(..., description="Unique employee identifier")
    employee_name: Optional[str] = Field(None, description="Employee name (optional for privacy)")
    role: str = Field(..., description="Employee role (e.g., Consultant, Operations)")
    level: Optional[str] = Field(None, description="Employee level (e.g., A, AC, C for Consultant)")
    status: EmployeeStatus = Field(..., description="Current employment status")
    fte_percentage: Decimal = Field(..., description="FTE percentage (1.0 = 100%, 0.5 = 50%)")
    start_date: date = Field(..., description="Employment start date")
    current_salary: Optional[Decimal] = Field(None, description="Current monthly salary")
    utilization_rate: Optional[Decimal] = Field(None, description="Current utilization rate")
    last_promotion_date: Optional[date] = Field(None, description="Date of last promotion")
    next_review_date: Optional[date] = Field(None, description="Next performance review date")
    cost_center: Optional[str] = Field(None, description="Cost center allocation")
    manager_id: Optional[str] = Field(None, description="Manager's employee ID")
    location: Optional[str] = Field(None, description="Work location (office, remote, hybrid)")
    contract_type: str = Field("permanent", description="Contract type (permanent, fixed-term, contractor)")
    
    # Skills and capabilities tracking
    skills: List[str] = Field(default_factory=list, description="Employee skills and certifications")
    languages: List[str] = Field(default_factory=list, description="Languages spoken")
    availability: Dict[str, Any] = Field(default_factory=dict, description="Availability constraints")
    
    @field_validator('fte_percentage')
    @classmethod
    def validate_fte_percentage(cls, v):
        if not 0 <= v <= 2.0:  # Allow up to 200% for exceptional cases
            raise ValueError('FTE percentage must be between 0 and 2.0')
        return v


# Aggregated Population Data (for efficient queries)

class RoleLevelPopulation(BaseModel):
    """Population count for a specific role and level combination"""
    role: str = Field(..., description="Role name")
    level: Optional[str] = Field(None, description="Level name (None for flat roles)")
    total_count: int = Field(..., description="Total number of employees")
    active_count: int = Field(..., description="Number of active employees")
    total_fte: Decimal = Field(..., description="Total FTE across all employees")
    active_fte: Decimal = Field(..., description="Active FTE (excluding leave, notice period)")
    average_salary: Optional[Decimal] = Field(None, description="Average monthly salary")
    average_utilization: Optional[Decimal] = Field(None, description="Average utilization rate")
    contractors_count: int = Field(0, description="Number of contractors")
    interns_count: int = Field(0, description="Number of interns")
    on_leave_count: int = Field(0, description="Number of employees on leave")
    
    # Tenure analysis
    average_tenure_months: Optional[Decimal] = Field(None, description="Average tenure in months")
    new_hires_last_3_months: int = Field(0, description="New hires in last 3 months")
    
    # Cost analysis
    total_monthly_cost: Optional[Decimal] = Field(None, description="Total monthly cost for this role/level")
    cost_per_fte: Optional[Decimal] = Field(None, description="Average cost per FTE")


class PopulationSummary(BaseModel):
    """High-level population summary for an office"""
    total_headcount: int = Field(..., description="Total number of employees")
    total_fte: Decimal = Field(..., description="Total FTE across all employees")
    active_headcount: int = Field(..., description="Number of active employees")
    active_fte: Decimal = Field(..., description="Active FTE")
    
    # Breakdown by employment type
    permanent_count: int = Field(0, description="Permanent employees")
    contractor_count: int = Field(0, description="Contractors")
    intern_count: int = Field(0, description="Interns")
    
    # Breakdown by status
    on_leave_count: int = Field(0, description="Employees on leave")
    notice_period_count: int = Field(0, description="Employees in notice period")
    
    # Demographics
    average_tenure_months: Optional[Decimal] = Field(None, description="Average tenure across office")
    turnover_rate_annual: Optional[Decimal] = Field(None, description="Annualized turnover rate")
    
    # Financial
    total_monthly_salary_cost: Optional[Decimal] = Field(None, description="Total monthly salary cost")
    average_salary: Optional[Decimal] = Field(None, description="Average monthly salary")
    average_utilization: Optional[Decimal] = Field(None, description="Average utilization rate")


# Office Settings Snapshot

class OfficeSettings(BaseModel):
    """Office configuration and settings at a specific point in time"""
    office_id: str = Field(..., description="Office identifier")
    office_name: str = Field(..., description="Office name")
    office_journey: OfficeJourney = Field(..., description="Office maturity stage")
    
    # Location and facilities
    country: str = Field(..., description="Country code")
    city: str = Field(..., description="City name")
    address: Optional[str] = Field(None, description="Office address")
    timezone: str = Field(..., description="Office timezone")
    office_capacity: Optional[int] = Field(None, description="Maximum office capacity")
    
    # Economic parameters
    currency: str = Field(..., description="Local currency code")
    working_hours_per_month: Decimal = Field(default=160.0, description="Standard working hours per month")
    employment_cost_rate: Decimal = Field(default=0.3, description="Employer cost rate (social security, etc.)")
    
    # Operational settings
    working_languages: List[str] = Field(default_factory=list, description="Working languages")
    business_model: str = Field("consulting", description="Primary business model")
    client_focus: List[str] = Field(default_factory=list, description="Primary client focus areas")
    
    # Financial settings
    billing_rates: Dict[str, Dict[str, Decimal]] = Field(default_factory=dict, description="Billing rates by role/level")
    salary_bands: Dict[str, Dict[str, Decimal]] = Field(default_factory=dict, description="Salary bands by role/level")
    progression_criteria: Dict[str, Any] = Field(default_factory=dict, description="Progression criteria")
    
    # Policies and procedures
    vacation_days_annual: int = Field(25, description="Annual vacation days")
    sick_leave_policy: Dict[str, Any] = Field(default_factory=dict, description="Sick leave policy")
    remote_work_policy: str = Field("hybrid", description="Remote work policy")
    performance_review_cycle: str = Field("annual", description="Performance review cycle")


# Complete Population Snapshot

class PopulationSnapshot(BaseModel):
    """Complete population snapshot for an office at a specific point in time"""
    snapshot_id: str = Field(..., description="Unique snapshot identifier")
    office_id: str = Field(..., description="Office identifier")
    snapshot_date: date = Field(..., description="Date of the snapshot")
    snapshot_type: SnapshotType = Field(..., description="Type of snapshot")
    
    # Population data
    summary: PopulationSummary = Field(..., description="High-level population summary")
    role_level_breakdown: List[RoleLevelPopulation] = Field(..., description="Breakdown by role and level")
    employee_records: List[EmployeeRecord] = Field(..., description="Individual employee records")
    
    # Office settings at time of snapshot
    office_settings: OfficeSettings = Field(..., description="Office settings at snapshot time")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(..., description="User who created the snapshot")
    snapshot_notes: Optional[str] = Field(None, description="Notes about this snapshot")
    data_source: str = Field("manual", description="Source of snapshot data")
    
    # Validation and quality metrics
    data_quality_score: Optional[Decimal] = Field(None, description="Data quality score (0-1)")
    validation_errors: List[str] = Field(default_factory=list, description="Data validation errors")
    completeness_percentage: Optional[Decimal] = Field(None, description="Data completeness percentage")
    
    def get_fte_by_role(self, role: str) -> Decimal:
        """Get total FTE for a specific role"""
        return sum(
            breakdown.total_fte 
            for breakdown in self.role_level_breakdown 
            if breakdown.role == role
        )
    
    def get_headcount_by_role(self, role: str) -> int:
        """Get total headcount for a specific role"""
        return sum(
            breakdown.total_count 
            for breakdown in self.role_level_breakdown 
            if breakdown.role == role
        )
    
    def get_roles(self) -> List[str]:
        """Get list of all roles in this snapshot"""
        return list(set(breakdown.role for breakdown in self.role_level_breakdown))
    
    def get_levels_for_role(self, role: str) -> List[str]:
        """Get list of levels for a specific role"""
        levels = [
            breakdown.level 
            for breakdown in self.role_level_breakdown 
            if breakdown.role == role and breakdown.level is not None
        ]
        return sorted(list(set(levels))) if levels else []


# Snapshot Comparison and Analysis

class SnapshotComparison(BaseModel):
    """Comparison between two population snapshots"""
    base_snapshot_id: str = Field(..., description="Base snapshot for comparison")
    comparison_snapshot_id: str = Field(..., description="Snapshot to compare against")
    comparison_date: date = Field(default_factory=date.today)
    
    # Summary changes
    headcount_change: int = Field(..., description="Change in total headcount")
    fte_change: Decimal = Field(..., description="Change in total FTE")
    headcount_change_percentage: Decimal = Field(..., description="Percentage change in headcount")
    fte_change_percentage: Decimal = Field(..., description="Percentage change in FTE")
    
    # Role-level changes
    role_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Changes by role")
    new_roles: List[str] = Field(default_factory=list, description="New roles added")
    removed_roles: List[str] = Field(default_factory=list, description="Roles removed")
    
    # Employee movements
    new_hires: List[str] = Field(default_factory=list, description="New employee IDs")
    departures: List[str] = Field(default_factory=list, description="Departed employee IDs")
    promotions: List[Dict[str, str]] = Field(default_factory=list, description="Promotions (employee_id, old_level, new_level)")
    role_changes_employees: List[Dict[str, str]] = Field(default_factory=list, description="Role changes")
    
    # Financial impact
    salary_cost_change: Optional[Decimal] = Field(None, description="Change in total salary cost")
    average_salary_change: Optional[Decimal] = Field(None, description="Change in average salary")
    
    # Settings changes
    settings_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Office settings changes")


# Snapshot Validation and Quality

class SnapshotValidationRule(BaseModel):
    """Validation rule for snapshot data quality"""
    rule_id: str = Field(..., description="Unique rule identifier")
    rule_name: str = Field(..., description="Human-readable rule name")
    rule_description: str = Field(..., description="Description of what the rule checks")
    rule_type: str = Field(..., description="Type of validation (business_rule, data_consistency, etc.)")
    severity: str = Field(..., description="Severity level (error, warning, info)")
    
    # Rule configuration
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Rule parameters")
    is_active: bool = Field(True, description="Whether rule is active")


class SnapshotValidationResult(BaseModel):
    """Result of snapshot validation"""
    snapshot_id: str = Field(..., description="Snapshot that was validated")
    validation_date: datetime = Field(default_factory=datetime.now)
    
    # Overall results
    is_valid: bool = Field(..., description="Whether snapshot passed all validations")
    quality_score: Decimal = Field(..., description="Overall quality score (0-1)")
    
    # Detailed results
    rule_results: List[Dict[str, Any]] = Field(default_factory=list, description="Results by validation rule")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    
    # Data completeness
    completeness_by_field: Dict[str, Decimal] = Field(default_factory=dict, description="Completeness by field")
    missing_mandatory_fields: List[str] = Field(default_factory=list, description="Missing mandatory fields")


# Historical Analysis Models

class PopulationTrend(BaseModel):
    """Population trend analysis over time"""
    office_id: str = Field(..., description="Office identifier")
    analysis_period_start: date = Field(..., description="Start of analysis period")
    analysis_period_end: date = Field(..., description="End of analysis period")
    
    # Trend metrics
    headcount_trend: List[Dict[str, Any]] = Field(default_factory=list, description="Monthly headcount trends")
    fte_trend: List[Dict[str, Any]] = Field(default_factory=list, description="Monthly FTE trends")
    turnover_trend: List[Dict[str, Any]] = Field(default_factory=list, description="Monthly turnover trends")
    
    # Growth analysis
    compound_growth_rate: Decimal = Field(..., description="Compound monthly growth rate")
    seasonal_patterns: Dict[str, Any] = Field(default_factory=dict, description="Identified seasonal patterns")
    growth_phases: List[Dict[str, Any]] = Field(default_factory=list, description="Identified growth phases")
    
    # Predictive insights
    projected_headcount: Optional[Dict[str, Any]] = Field(None, description="Projected future headcount")
    capacity_utilization: Optional[Decimal] = Field(None, description="Office capacity utilization")
    recommendations: List[str] = Field(default_factory=list, description="Growth recommendations")


# Bulk Operations and Management

class BulkSnapshotOperation(BaseModel):
    """Bulk operation for managing multiple snapshots"""
    operation_id: str = Field(..., description="Unique operation identifier")
    operation_type: str = Field(..., description="Type of operation (create, update, delete, compare)")
    office_ids: List[str] = Field(..., description="Office IDs to process")
    snapshot_dates: List[date] = Field(..., description="Snapshot dates to process")
    
    # Operation parameters
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation-specific parameters")
    batch_size: int = Field(10, description="Processing batch size")
    
    # Status tracking
    status: str = Field("pending", description="Operation status")
    progress_percentage: Decimal = Field(0, description="Completion percentage")
    started_at: Optional[datetime] = Field(None, description="Operation start time")
    completed_at: Optional[datetime] = Field(None, description="Operation completion time")
    
    # Results
    successful_snapshots: List[str] = Field(default_factory=list, description="Successfully processed snapshots")
    failed_snapshots: List[Dict[str, str]] = Field(default_factory=list, description="Failed snapshots with errors")
    operation_summary: Optional[Dict[str, Any]] = Field(None, description="Operation summary")