"""
Validation rules and utilities for office business planning data.
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from pydantic import ValidationError

try:
    from ..models.office import (
        OfficeConfig, WorkforceDistribution, MonthlyBusinessPlan, 
        ProgressionConfig, OfficeBusinessPlanSummary
    )
except ImportError:
    # Fallback for direct execution
    from backend.src.models.office import (
        OfficeConfig, WorkforceDistribution, MonthlyBusinessPlan, 
        ProgressionConfig, OfficeBusinessPlanSummary
    )


class OfficeValidationError(Exception):
    """Custom exception for office validation errors."""
    pass


class BusinessPlanValidator:
    """Comprehensive validation for office business plans."""

    @staticmethod
    def validate_office_consistency(office_summary: OfficeBusinessPlanSummary) -> List[str]:
        """
        Validate consistency across office configuration, workforce, and business plans.
        Returns list of validation errors.
        """
        errors = []
        
        # Validate workforce vs business plan consistency
        if office_summary.workforce_distribution and office_summary.monthly_plans:
            workforce_errors = BusinessPlanValidator._validate_workforce_business_plan_consistency(
                office_summary.workforce_distribution, 
                office_summary.monthly_plans
            )
            errors.extend(workforce_errors)
        
        # Validate progression configs
        if office_summary.progression_configs:
            progression_errors = BusinessPlanValidator._validate_progression_configs(
                office_summary.progression_configs
            )
            errors.extend(progression_errors)
        
        # Validate business plan data quality
        for plan in office_summary.monthly_plans:
            plan_errors = BusinessPlanValidator._validate_monthly_plan_quality(plan)
            errors.extend([f"Month {plan.month}/{plan.year}: {error}" for error in plan_errors])
        
        return errors

    @staticmethod
    def _validate_workforce_business_plan_consistency(
        workforce: WorkforceDistribution, 
        monthly_plans: List[MonthlyBusinessPlan]
    ) -> List[str]:
        """Validate that business plans align with workforce distribution."""
        errors = []
        
        # Get unique role/level combinations from workforce
        workforce_combinations = {(entry.role, entry.level) for entry in workforce.workforce}
        
        # Check each monthly plan
        for plan in monthly_plans:
            plan_combinations = {(entry.role, entry.level) for entry in plan.entries}
            
            # Check for business plan entries without corresponding workforce
            missing_workforce = plan_combinations - workforce_combinations
            if missing_workforce:
                missing_str = ", ".join([f"{role}-{level}" for role, level in missing_workforce])
                errors.append(
                    f"Month {plan.month}/{plan.year}: Business plan includes roles/levels "
                    f"not in workforce distribution: {missing_str}"
                )
            
            # Validate recruitment/churn vs existing workforce
            for entry in plan.entries:
                workforce_fte = next(
                    (w.fte for w in workforce.workforce 
                     if w.role == entry.role and w.level == entry.level), 
                    0
                )
                
                # Warning if churn exceeds current workforce
                if entry.churn > workforce_fte:
                    errors.append(
                        f"Month {plan.month}/{plan.year}: {entry.role}-{entry.level} "
                        f"churn ({entry.churn}) exceeds current workforce ({workforce_fte})"
                    )
        
        return errors

    @staticmethod
    def _validate_progression_configs(configs: List[ProgressionConfig]) -> List[str]:
        """Validate CAT progression configurations."""
        errors = []
        
        # Standard levels that should have progression configs
        standard_levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
        
        config_levels = {config.level for config in configs}
        missing_levels = set(standard_levels) - config_levels
        
        if missing_levels:
            errors.append(f"Missing progression configs for levels: {', '.join(missing_levels)}")
        
        # Validate individual progression configs
        for config in configs:
            if config.monthly_rate < 0 or config.monthly_rate > 1:
                errors.append(f"Level {config.level}: Invalid monthly rate {config.monthly_rate}")
            
            # Validate custom points if present
            if config.curve_type == "custom" and config.custom_points:
                months = [point.month for point in config.custom_points]
                if len(months) != len(set(months)):
                    errors.append(f"Level {config.level}: Duplicate months in custom progression points")
                
                for point in config.custom_points:
                    if point.rate < 0 or point.rate > 1:
                        errors.append(
                            f"Level {config.level}: Invalid progression rate {point.rate} for month {point.month}"
                        )
        
        return errors

    @staticmethod
    def _validate_monthly_plan_quality(plan: MonthlyBusinessPlan) -> List[str]:
        """Validate business rules and data quality for a monthly plan."""
        errors = []
        
        # Business rule validations
        for entry in plan.entries:
            # Utilization rate validation
            if entry.utr > 0.95:
                errors.append(
                    f"{entry.role}-{entry.level}: Very high utilization rate ({entry.utr:.2f}) may be unrealistic"
                )
            
            # Price validation (basic reasonableness check)
            if entry.price < 10 or entry.price > 1000:
                errors.append(
                    f"{entry.role}-{entry.level}: Hourly rate ({entry.price}) seems unrealistic"
                )
            
            # Salary validation (basic reasonableness check)
            if entry.salary < 1000 or entry.salary > 50000:
                errors.append(
                    f"{entry.role}-{entry.level}: Monthly salary ({entry.salary}) seems unrealistic"
                )
            
            # Recruitment/churn ratio validation
            if entry.recruitment > 0 and entry.churn > 0:
                if entry.churn > entry.recruitment * 2:
                    errors.append(
                        f"{entry.role}-{entry.level}: High churn relative to recruitment may indicate issues"
                    )
        
        # Plan-level validations
        total_recruitment = plan.get_total_recruitment()
        total_churn = plan.get_total_churn()
        
        # Extreme growth/decline warnings
        if total_recruitment > total_churn * 3:
            errors.append("Very high growth rate - may be difficult to achieve")
        elif total_churn > total_recruitment * 3:
            errors.append("Very high decline rate - may indicate organizational issues")
        
        return errors

    @staticmethod
    def validate_business_plan_completeness(
        office_summary: OfficeBusinessPlanSummary,
        required_months: List[Tuple[int, int]]  # List of (year, month) tuples
    ) -> List[str]:
        """Validate that business plans exist for all required months."""
        errors = []
        
        existing_months = {(plan.year, plan.month) for plan in office_summary.monthly_plans}
        missing_months = set(required_months) - existing_months
        
        if missing_months:
            missing_str = ", ".join([f"{month}/{year}" for year, month in sorted(missing_months)])
            errors.append(f"Missing business plans for months: {missing_str}")
        
        return errors

    @staticmethod
    def validate_role_level_definitions(
        workforce: WorkforceDistribution,
        monthly_plans: List[MonthlyBusinessPlan]
    ) -> List[str]:
        """Validate that role and level definitions are consistent."""
        errors = []
        
        # Standard roles and levels
        standard_roles = ['Consultant', 'Sales', 'Operations']
        standard_levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
        
        # Collect all roles and levels used
        all_roles = set()
        all_levels = set()
        
        for entry in workforce.workforce:
            all_roles.add(entry.role)
            all_levels.add(entry.level)
        
        for plan in monthly_plans:
            for entry in plan.entries:
                all_roles.add(entry.role)
                all_levels.add(entry.level)
        
        # Check for non-standard roles/levels (warnings, not errors)
        non_standard_roles = all_roles - set(standard_roles)
        non_standard_levels = all_levels - set(standard_levels)
        
        if non_standard_roles:
            errors.append(f"Non-standard roles detected: {', '.join(non_standard_roles)}")
        
        if non_standard_levels:
            errors.append(f"Non-standard levels detected: {', '.join(non_standard_levels)}")
        
        return errors


class OfficeConfigValidator:
    """Validation for office configuration."""

    @staticmethod
    def validate_office_name_uniqueness(name: str, existing_offices: List[OfficeConfig], exclude_id: Optional[UUID] = None) -> bool:
        """Check if office name is unique."""
        for office in existing_offices:
            if office.name.lower() == name.lower() and office.id != exclude_id:
                return False
        return True

    @staticmethod
    def validate_economic_parameters(params: Dict[str, float]) -> List[str]:
        """Validate economic parameters for reasonableness."""
        errors = []
        
        cost_of_living = params.get('cost_of_living', 1.0)
        market_multiplier = params.get('market_multiplier', 1.0)
        tax_rate = params.get('tax_rate', 0.0)
        
        # Cost of living validation
        if cost_of_living < 0.5 or cost_of_living > 3.0:
            errors.append(f"Cost of living multiplier ({cost_of_living}) seems unrealistic")
        
        # Market multiplier validation
        if market_multiplier < 0.5 or market_multiplier > 3.0:
            errors.append(f"Market multiplier ({market_multiplier}) seems unrealistic")
        
        # Tax rate validation
        if tax_rate < 0.0 or tax_rate > 0.7:
            errors.append(f"Tax rate ({tax_rate}) seems unrealistic")
        
        return errors


def validate_complete_office_setup(office_summary: OfficeBusinessPlanSummary) -> Dict[str, List[str]]:
    """
    Comprehensive validation of complete office setup.
    Returns dict with validation results by category.
    """
    validation_results = {
        "errors": [],
        "warnings": [],
        "info": []
    }
    
    try:
        # Basic consistency validation
        consistency_errors = BusinessPlanValidator.validate_office_consistency(office_summary)
        validation_results["errors"].extend(consistency_errors)
        
        # Role/level definition validation
        if office_summary.workforce_distribution:
            role_level_warnings = BusinessPlanValidator.validate_role_level_definitions(
                office_summary.workforce_distribution,
                office_summary.monthly_plans
            )
            validation_results["warnings"].extend(role_level_warnings)
        
        # Economic parameters validation
        economic_warnings = OfficeConfigValidator.validate_economic_parameters(
            office_summary.office.economic_parameters.dict()
        )
        validation_results["warnings"].extend(economic_warnings)
        
        # Summary information
        total_workforce = office_summary.workforce_distribution.get_total_fte() if office_summary.workforce_distribution else 0
        total_plans = len(office_summary.monthly_plans)
        total_progressions = len(office_summary.progression_configs)
        
        validation_results["info"].append(f"Total workforce: {total_workforce} FTE")
        validation_results["info"].append(f"Business plans: {total_plans} months")
        validation_results["info"].append(f"Progression configs: {total_progressions} levels")
        
    except Exception as e:
        validation_results["errors"].append(f"Validation error: {str(e)}")
    
    return validation_results