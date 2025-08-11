"""
Business Plan Processor V2 - Business Logic Component

Handles business plan processing and financial modeling:
- Monthly target calculation from business plans
- Growth rate application for multi-year modeling
- Scenario lever integration
- Financial metrics calculation
- Business plan validation and extrapolation
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
import logging
import math
from dataclasses import dataclass, asdict

# Avoid circular imports - define interfaces locally
from typing import Protocol

class BusinessPlanProcessorInterface(Protocol):
    def initialize(self, **kwargs) -> None: pass
    def load_business_plan(self, office_id: str, business_plan_data: Dict[str, Any]) -> bool: pass
    def get_monthly_targets(self, office_id: str, year: int, month: int) -> 'MonthlyTargets': pass
    def apply_scenario_levers(self, targets: 'MonthlyTargets', levers: 'Levers') -> 'MonthlyTargets': pass

# Define data classes locally to avoid circular imports
@dataclass
class BusinessPlan:
    office_id: str
    monthly_plans: Dict[str, 'MonthlyPlan']
    metadata: Dict[str, Any]

@dataclass
class MonthlyPlan:
    month: str
    total_fte: float
    role_breakdown: Dict[str, float]
    financial_targets: Dict[str, float]
    
@dataclass 
class MonthlyTargets:
    recruitment_targets: Dict[str, float]
    churn_targets: Dict[str, float]
    progression: Dict[str, float] = None
    financial: Dict[str, float] = None
    revenue_target: float = 0.0
    operating_costs: float = 0.0
    salary_budget: float = 0.0
    year: int = 2025
    month: int = 1

@dataclass
class GrowthRates:
    annual_growth: float
    market_adjustment: float
    
@dataclass
class Levers:
    recruitment_multiplier: float = 1.0
    churn_multiplier: float = 1.0
    progression_multiplier: float = 1.0
    price_multiplier: float = 1.0
    salary_multiplier: float = 1.0

@dataclass
class TimeRange:
    start_year: int
    start_month: int
    end_year: int
    end_month: int

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class FinancialMetrics:
    """Financial metrics calculated from business plan"""
    total_revenue: float
    total_costs: float
    gross_profit: float
    profit_margin: float
    revenue_per_fte: float
    cost_per_fte: float


@dataclass
class BusinessPlanValidation:
    """Business plan validation configuration"""
    allow_negative_targets: bool = False
    max_monthly_growth_rate: float = 0.5  # 50% max monthly growth
    require_complete_year: bool = True
    validate_financial_consistency: bool = True


class BusinessPlanProcessorV2(BusinessPlanProcessorInterface):
    """
    Processes business plans and applies growth modeling
    
    Key capabilities:
    - Extract monthly targets from business plans
    - Apply compound growth rates for multi-year scenarios
    - Integrate scenario levers for target adjustments
    - Validate business plan consistency
    - Calculate financial metrics and projections
    """
    
    def __init__(self):
        self.loaded_plans: Dict[str, BusinessPlan] = {}
        self.validation_config = BusinessPlanValidation()
        self.default_growth_rates = GrowthRates(annual_growth=0.05, market_adjustment=1.0)
        
    def initialize(self, **kwargs) -> bool:
        """Initialize business plan processor"""
        if 'validation_config' in kwargs:
            self.validation_config = kwargs['validation_config']
        if 'default_growth_rates' in kwargs:
            self.default_growth_rates = kwargs['default_growth_rates']
            
        logger.info("BusinessPlanProcessorV2 initialized successfully")
        return True
    
    def get_monthly_targets(self, office: str, year: int, month: int) -> MonthlyTargets:
        """
        Get monthly targets for office from business plan
        
        Args:
            office: Office identifier
            year: Target year
            month: Target month (1-12)
            
        Returns:
            MonthlyTargets object with recruitment, churn, and financial targets
        """
        business_plan = self.loaded_plans.get(office)
        if not business_plan:
            logger.warning(f"No business plan found for office {office}")
            return self._create_empty_targets(year, month)
        
        # Extract targets from unified business plan format (new format)
        if isinstance(business_plan, dict) and 'monthly_plans' in business_plan:
            return self._extract_targets_from_unified_plan(business_plan, year, month)
        
        # Extract targets from raw business plan entries (old single-month format)
        if isinstance(business_plan, dict) and 'entries' in business_plan:
            return self._extract_targets_from_raw_plan(business_plan, year, month)
        
        # Fallback to complex BusinessPlan object format (legacy)
        monthly_plan = business_plan.get_plan_for_month(year, month)
        if not monthly_plan:
            logger.warning(f"No monthly plan found for {office} {year}-{month:02d}")
            return self._create_empty_targets(year, month)
        
        # Convert MonthlyPlan to MonthlyTargets
        targets = MonthlyTargets(
            year=year,
            month=month,
            recruitment_targets=self._convert_to_int_targets(monthly_plan.recruitment),
            churn_targets=self._convert_to_int_targets(monthly_plan.churn),
            revenue_target=monthly_plan.revenue,
            operating_costs=monthly_plan.costs,
            salary_budget=self._calculate_salary_budget(monthly_plan)
        )
        
        return targets
    
    def apply_growth_rates(self, base_targets: MonthlyTargets, years_forward: int) -> MonthlyTargets:
        """
        Apply growth rates to base targets for future projection
        
        Args:
            base_targets: Base targets to grow from
            years_forward: Number of years to project forward
            
        Returns:
            MonthlyTargets with growth rates applied
        """
        if years_forward <= 0:
            return base_targets
        
        growth_rates = self.default_growth_rates
        
        # Calculate compound growth multipliers
        recruitment_multiplier = (1 + growth_rates.recruitment_growth_rate) ** years_forward
        price_multiplier = (1 + growth_rates.price_growth_rate) ** years_forward
        salary_multiplier = (1 + growth_rates.salary_growth_rate) ** years_forward
        cost_multiplier = (1 + growth_rates.cost_growth_rate) ** years_forward
        
        # Apply growth to recruitment targets
        grown_recruitment = {}
        for role, levels in base_targets.recruitment_targets.items():
            grown_recruitment[role] = {}
            for level, count in levels.items():
                grown_recruitment[role][level] = int(count * recruitment_multiplier)
        
        # Churn typically doesn't grow (or grows more slowly)
        grown_churn = base_targets.churn_targets  # Keep same for now
        
        # Apply growth to financial targets
        grown_targets = MonthlyTargets(
            year=base_targets.year + years_forward,
            month=base_targets.month,
            recruitment_targets=grown_recruitment,
            churn_targets=grown_churn,
            revenue_target=base_targets.revenue_target * price_multiplier,
            operating_costs=base_targets.operating_costs * cost_multiplier,
            salary_budget=base_targets.salary_budget * salary_multiplier
        )
        
        logger.debug(f"Applied {years_forward} years growth: recruitment x{recruitment_multiplier:.2f}, "
                    f"revenue x{price_multiplier:.2f}")
        
        return grown_targets
    
    def apply_scenario_levers(self, targets: MonthlyTargets, levers: Levers) -> MonthlyTargets:
        """
        Apply scenario levers to adjust targets
        
        Args:
            targets: Base targets to adjust
            levers: Scenario levers with multipliers
            
        Returns:
            MonthlyTargets with lever adjustments applied
        """
        # Apply recruitment lever
        adjusted_recruitment = {}
        for role, levels in targets.recruitment_targets.items():
            adjusted_recruitment[role] = {}
            for level, count in levels.items():
                adjusted_recruitment[role][level] = int(count * levers.recruitment_multiplier)
        
        # Apply churn lever
        adjusted_churn = {}
        for role, levels in targets.churn_targets.items():
            adjusted_churn[role] = {}
            for level, count in levels.items():
                adjusted_churn[role][level] = int(count * levers.churn_multiplier)
        
        # Apply financial levers
        adjusted_targets = MonthlyTargets(
            year=targets.year,
            month=targets.month,
            recruitment_targets=adjusted_recruitment,
            churn_targets=adjusted_churn,
            revenue_target=targets.revenue_target * levers.price_multiplier,
            operating_costs=targets.operating_costs,  # Costs typically not adjusted by price lever
            salary_budget=targets.salary_budget * levers.salary_multiplier
        )
        
        logger.debug(f"Applied scenario levers: recruitment x{levers.recruitment_multiplier}, "
                    f"churn x{levers.churn_multiplier}, price x{levers.price_multiplier}")
        
        return adjusted_targets
    
    def load_business_plan(self, office: str, business_plan) -> bool:
        """Load business plan for office (supports both raw dict and BusinessPlan object)"""
        try:
            # Handle raw business plan format (dict)
            if isinstance(business_plan, dict):
                # Check for unified format first (monthly_plans)
                if business_plan.get('monthly_plans'):
                    self.loaded_plans[office] = business_plan
                    monthly_count = len(business_plan.get('monthly_plans', {}))
                    logger.info(f"Loaded unified business plan for {office} with {monthly_count} monthly plans")
                    return True
                
                # Check for old single-month format (entries)
                elif business_plan.get('entries'):
                    self.loaded_plans[office] = business_plan
                    logger.info(f"Loaded raw business plan for {office} with {len(business_plan['entries'])} entries")
                    return True
                
                else:
                    logger.error(f"Business plan for {office} has no entries or monthly_plans")
                    return False
            
            # Handle complex BusinessPlan object (legacy)
            validation_result = self.validate_business_plan(business_plan)
            if not validation_result.is_valid:
                logger.error(f"Invalid business plan for {office}: {validation_result.errors}")
                return False
            
            self.loaded_plans[office] = business_plan
            logger.info(f"Loaded business plan for {office} with {len(business_plan.monthly_plans)} monthly plans")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load business plan for {office}: {str(e)}")
            return False
    
    def validate_business_plan(self, business_plan: BusinessPlan) -> ValidationResult:
        """Validate business plan data"""
        result = ValidationResult(True)
        
        if not business_plan.office_id:
            result.add_error("Business plan office ID is required")
        
        if not business_plan.name:
            result.add_error("Business plan name is required")
        
        if not business_plan.monthly_plans:
            result.add_error("At least one monthly plan is required")
        
        # Validate monthly plans
        for month_key, monthly_plan in business_plan.monthly_plans.items():
            plan_errors = self._validate_monthly_plan(monthly_plan, month_key)
            result.errors.extend(plan_errors)
            if plan_errors:
                result.is_valid = False
        
        # Business rule validations
        if result.is_valid and self.validation_config.validate_financial_consistency:
            consistency_errors = self._validate_financial_consistency(business_plan)
            result.errors.extend(consistency_errors)
            if consistency_errors:
                result.is_valid = False
        
        return result
    
    def calculate_financial_metrics(self, business_plan: BusinessPlan, time_range: TimeRange) -> FinancialMetrics:
        """Calculate financial metrics for business plan over time range"""
        total_revenue = 0.0
        total_costs = 0.0
        total_months = 0
        
        for year, month in time_range.get_month_list():
            monthly_plan = business_plan.get_plan_for_month(year, month)
            if monthly_plan:
                total_revenue += monthly_plan.revenue
                total_costs += monthly_plan.costs
                total_months += 1
        
        if total_months == 0:
            return FinancialMetrics(0, 0, 0, 0, 0, 0)
        
        gross_profit = total_revenue - total_costs
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Estimate FTE from recruitment data (simplified)
        avg_fte = self._estimate_average_fte(business_plan, time_range)
        revenue_per_fte = (total_revenue / avg_fte) if avg_fte > 0 else 0
        cost_per_fte = (total_costs / avg_fte) if avg_fte > 0 else 0
        
        return FinancialMetrics(
            total_revenue=total_revenue,
            total_costs=total_costs,
            gross_profit=gross_profit,
            profit_margin=profit_margin,
            revenue_per_fte=revenue_per_fte,
            cost_per_fte=cost_per_fte
        )
    
    def extrapolate_business_plan(self, business_plan: BusinessPlan, extend_to_date: Tuple[int, int],
                                 growth_rates: Optional[GrowthRates] = None) -> BusinessPlan:
        """
        Extrapolate business plan beyond current time range using growth rates
        
        Args:
            business_plan: Base business plan to extend
            extend_to_date: (year, month) to extend to
            growth_rates: Optional growth rates (uses default if not provided)
            
        Returns:
            Extended BusinessPlan
        """
        if not growth_rates:
            growth_rates = self.default_growth_rates
        
        # Find last month in current plan
        last_month_key = max(business_plan.monthly_plans.keys())
        last_monthly_plan = business_plan.monthly_plans[last_month_key]
        
        # Parse last month date
        last_year, last_month = map(int, last_month_key.split('-'))
        target_year, target_month = extend_to_date
        
        # Create extended plan
        extended_plans = dict(business_plan.monthly_plans)
        
        current_year, current_month = last_year, last_month
        while current_year < target_year or (current_year == target_year and current_month < target_month):
            # Move to next month
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
            
            # Calculate years forward from last plan
            years_forward = current_year - last_year + (current_month - last_month) / 12.0
            
            # Create extrapolated plan
            extrapolated_plan = self._extrapolate_monthly_plan(last_monthly_plan, years_forward, growth_rates)
            extrapolated_plan.year = current_year
            extrapolated_plan.month = current_month
            
            month_key = f"{current_year:04d}-{current_month:02d}"
            extended_plans[month_key] = extrapolated_plan
        
        return BusinessPlan(
            office_id=business_plan.office_id,
            name=f"{business_plan.name} (Extended)",
            monthly_plans=extended_plans
        )
    
    def create_scenario_adjusted_plan(self, base_plan: BusinessPlan, levers: Levers) -> BusinessPlan:
        """Create business plan adjusted for scenario levers"""
        adjusted_plans = {}
        
        for month_key, monthly_plan in base_plan.monthly_plans.items():
            # Apply levers to monthly plan
            adjusted_recruitment = {}
            for role, levels in monthly_plan.recruitment.items():
                adjusted_recruitment[role] = {}
                for level, count in levels.items():
                    adjusted_recruitment[role][level] = count * levers.recruitment_multiplier
            
            adjusted_churn = {}
            for role, levels in monthly_plan.churn.items():
                adjusted_churn[role] = {}
                for level, count in levels.items():
                    adjusted_churn[role][level] = count * levers.churn_multiplier
            
            # Create adjusted plan
            adjusted_plan = MonthlyPlan(
                year=monthly_plan.year,
                month=monthly_plan.month,
                recruitment=adjusted_recruitment,
                churn=adjusted_churn,
                revenue=monthly_plan.revenue * levers.price_multiplier,
                costs=monthly_plan.costs,
                price_per_role=self._apply_price_lever_to_roles(monthly_plan.price_per_role, levers.price_multiplier),
                salary_per_role=self._apply_salary_lever_to_roles(monthly_plan.salary_per_role, levers.salary_multiplier),
                utr_per_role=monthly_plan.utr_per_role  # UTR typically not adjusted
            )
            
            adjusted_plans[month_key] = adjusted_plan
        
        return BusinessPlan(
            office_id=base_plan.office_id,
            name=f"{base_plan.name} (Scenario Adjusted)",
            monthly_plans=adjusted_plans
        )
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _create_empty_targets(self, year: int, month: int) -> MonthlyTargets:
        """Create empty monthly targets"""
        return MonthlyTargets(
            year=year,
            month=month,
            recruitment_targets={},
            churn_targets={},
            revenue_target=0.0,
            operating_costs=0.0,
            salary_budget=0.0
        )
    
    def _convert_to_int_targets(self, float_targets: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, int]]:
        """Convert float recruitment/churn targets to integers"""
        int_targets = {}
        for role, levels in float_targets.items():
            int_targets[role] = {}
            for level, count in levels.items():
                int_targets[role][level] = int(round(count))
        return int_targets
    
    def _calculate_salary_budget(self, monthly_plan: MonthlyPlan) -> float:
        """Calculate total salary budget from role-level salaries and baseline FTE"""
        total_budget = 0.0
        
        # ENHANCED: Use baseline FTE for accurate salary calculation
        if hasattr(monthly_plan, 'baseline_fte') and monthly_plan.baseline_fte:
            for role, levels in monthly_plan.salary_per_role.items():
                baseline_role = monthly_plan.baseline_fte.get(role, {})
                for level, salary in levels.items():
                    fte_count = baseline_role.get(level, 0)
                    total_budget += salary * fte_count
        else:
            # Fallback to simplified calculation
            for role, levels in monthly_plan.salary_per_role.items():
                for level, salary in levels.items():
                    total_budget += salary  # Simplified
        
        return total_budget
    
    def _validate_monthly_plan(self, plan: MonthlyPlan, month_key: str) -> List[str]:
        """Validate individual monthly plan"""
        errors = []
        
        if plan.revenue < 0 and not self.validation_config.allow_negative_targets:
            errors.append(f"Monthly plan {month_key}: Negative revenue not allowed")
        
        if plan.costs < 0 and not self.validation_config.allow_negative_targets:
            errors.append(f"Monthly plan {month_key}: Negative costs not allowed")
        
        # Validate recruitment targets
        for role, levels in plan.recruitment.items():
            for level, count in levels.items():
                if count < 0 and not self.validation_config.allow_negative_targets:
                    errors.append(f"Monthly plan {month_key}: Negative recruitment for {role} {level}")
        
        # Validate churn targets
        for role, levels in plan.churn.items():
            for level, count in levels.items():
                if count < 0 and not self.validation_config.allow_negative_targets:
                    errors.append(f"Monthly plan {month_key}: Negative churn for {role} {level}")
        
        return errors
    
    def _validate_financial_consistency(self, business_plan: BusinessPlan) -> List[str]:
        """Validate financial consistency across business plan"""
        errors = []
        
        # Check for reasonable growth rates between months
        sorted_keys = sorted(business_plan.monthly_plans.keys())
        for i in range(1, len(sorted_keys)):
            current_key = sorted_keys[i]
            prev_key = sorted_keys[i-1]
            
            current_plan = business_plan.monthly_plans[current_key]
            prev_plan = business_plan.monthly_plans[prev_key]
            
            # Check revenue growth
            if prev_plan.revenue > 0:
                growth_rate = (current_plan.revenue - prev_plan.revenue) / prev_plan.revenue
                if abs(growth_rate) > self.validation_config.max_monthly_growth_rate:
                    errors.append(f"Excessive revenue growth rate ({growth_rate:.1%}) between {prev_key} and {current_key}")
        
        return errors
    
    def _estimate_average_fte(self, business_plan: BusinessPlan, time_range: TimeRange) -> float:
        """Estimate average FTE over time range (simplified)"""
        # This would require actual workforce simulation - simplified calculation
        total_recruitment = 0
        total_months = 0
        
        for year, month in time_range.get_month_list():
            monthly_plan = business_plan.get_plan_for_month(year, month)
            if monthly_plan:
                month_recruitment = sum(
                    sum(levels.values()) 
                    for levels in monthly_plan.recruitment.values()
                )
                total_recruitment += month_recruitment
                total_months += 1
        
        # Rough estimate: cumulative recruitment minus some churn
        return total_recruitment * 0.8 if total_months > 0 else 0
    
    def _extrapolate_monthly_plan(self, base_plan: MonthlyPlan, years_forward: float, 
                                 growth_rates: GrowthRates) -> MonthlyPlan:
        """Extrapolate single monthly plan using growth rates"""
        recruitment_multiplier = (1 + growth_rates.recruitment_growth_rate) ** years_forward
        price_multiplier = (1 + growth_rates.price_growth_rate) ** years_forward
        salary_multiplier = (1 + growth_rates.salary_growth_rate) ** years_forward
        cost_multiplier = (1 + growth_rates.cost_growth_rate) ** years_forward
        
        # Extrapolate recruitment
        extrapolated_recruitment = {}
        for role, levels in base_plan.recruitment.items():
            extrapolated_recruitment[role] = {}
            for level, count in levels.items():
                extrapolated_recruitment[role][level] = count * recruitment_multiplier
        
        # Extrapolate financial data
        return MonthlyPlan(
            year=base_plan.year,  # Will be updated by caller
            month=base_plan.month,  # Will be updated by caller
            recruitment=extrapolated_recruitment,
            churn=base_plan.churn,  # Churn typically doesn't grow as fast
            revenue=base_plan.revenue * price_multiplier,
            costs=base_plan.costs * cost_multiplier,
            price_per_role=self._apply_price_lever_to_roles(base_plan.price_per_role, price_multiplier),
            salary_per_role=self._apply_salary_lever_to_roles(base_plan.salary_per_role, salary_multiplier),
            utr_per_role=base_plan.utr_per_role  # UTR stays constant
        )
    
    def _apply_price_lever_to_roles(self, role_prices: Dict[str, Dict[str, float]], multiplier: float) -> Dict[str, Dict[str, float]]:
        """Apply price multiplier to role-level prices"""
        adjusted_prices = {}
        for role, levels in role_prices.items():
            adjusted_prices[role] = {}
            for level, price in levels.items():
                adjusted_prices[role][level] = price * multiplier
        return adjusted_prices
    
    def _apply_salary_lever_to_roles(self, role_salaries: Dict[str, Dict[str, float]], multiplier: float) -> Dict[str, Dict[str, float]]:
        """Apply salary multiplier to role-level salaries"""
        adjusted_salaries = {}
        for role, levels in role_salaries.items():
            adjusted_salaries[role] = {}
            for level, salary in levels.items():
                adjusted_salaries[role][level] = salary * multiplier
        return adjusted_salaries
    
    def calculate_net_sales_utilization_based(self, monthly_plan: MonthlyPlan, 
                                            current_workforce: Dict[str, Dict[str, int]] = None) -> float:
        """
        Calculate net sales based on consultant utilization formula:
        Net Sales = Sum across all consultant levels of:
        (Number of Consultants at Level) × (Utilization Rate) × (Price per Hour for Level) × (Working Hours per Month)
        """
        if not hasattr(monthly_plan, 'utilization_targets') or not monthly_plan.utilization_targets:
            logger.warning("Monthly plan missing utilization targets, using legacy revenue calculation")
            return monthly_plan.revenue
        
        # Use current workforce if provided, otherwise use baseline FTE
        workforce_data = current_workforce if current_workforce else getattr(monthly_plan, 'baseline_fte', {})
        
        if not workforce_data:
            logger.warning("No workforce data available for net sales calculation")
            return monthly_plan.revenue
        
        total_revenue = 0.0
        consultant_workforce = workforce_data.get('Consultant', {})
        consultant_utilization = monthly_plan.utilization_targets.get('Consultant', 0.85)  # Default 85%
        working_hours = getattr(monthly_plan, 'working_hours_per_month', 160)
        
        for level, consultant_count in consultant_workforce.items():
            if consultant_count > 0:
                # Get price per hour for this level
                level_price = monthly_plan.price_per_hour.get(level, 0.0)
                if level_price == 0.0:
                    # Fallback to price_per_role if price_per_hour not available
                    level_price = monthly_plan.price_per_role.get('Consultant', {}).get(level, 0.0)
                
                level_revenue = (
                    consultant_count * 
                    consultant_utilization * 
                    level_price * 
                    working_hours
                )
                
                total_revenue += level_revenue
                
                logger.debug(f"Level {level}: {consultant_count} consultants × {consultant_utilization:.0%} util × "
                           f"${level_price}/hr × {working_hours}hrs = ${level_revenue:,.0f}")
        
        logger.debug(f"Total net sales (utilization-based): ${total_revenue:,.0f}")
        return total_revenue
    
    def sync_baseline_fte_from_snapshot(self, business_plan: BusinessPlan, 
                                      population_snapshot: 'PopulationSnapshot') -> BusinessPlan:
        """
        Sync baseline FTE data from population snapshot into business plan
        
        Args:
            business_plan: Business plan to enhance
            population_snapshot: Population snapshot with current workforce
            
        Returns:
            Enhanced BusinessPlan with baseline FTE data
        """
        from .simulation_engine_v2 import PopulationSnapshot, MonthlyPlan
        
        # Count workforce by role and level
        workforce_counts = {}
        for entry in population_snapshot.workforce:
            if entry.role not in workforce_counts:
                workforce_counts[entry.role] = {}
            if entry.level not in workforce_counts[entry.role]:
                workforce_counts[entry.role][entry.level] = 0
            workforce_counts[entry.role][entry.level] += 1
        
        # Update all monthly plans with baseline FTE
        enhanced_monthly_plans = {}
        for month_key, monthly_plan in business_plan.monthly_plans.items():
            # Create enhanced monthly plan with baseline FTE
            enhanced_plan = MonthlyPlan(
                year=monthly_plan.year,
                month=monthly_plan.month,
                recruitment=monthly_plan.recruitment,
                churn=monthly_plan.churn,
                revenue=monthly_plan.revenue,
                costs=monthly_plan.costs,
                price_per_role=monthly_plan.price_per_role,
                salary_per_role=monthly_plan.salary_per_role,
                utr_per_role=monthly_plan.utr_per_role,
                baseline_fte=workforce_counts,  # Add baseline workforce data
                utilization_targets=self._create_default_utilization_targets(),
                price_per_hour=self._extract_price_per_hour(monthly_plan),
                working_hours_per_month=160,
                operating_costs=monthly_plan.costs * 0.3,  # Estimate 30% operating costs
                total_costs=monthly_plan.costs
            )
            
            enhanced_monthly_plans[month_key] = enhanced_plan
        
        enhanced_business_plan = BusinessPlan(
            office_id=business_plan.office_id,
            name=f"{business_plan.name} (Enhanced)",
            monthly_plans=enhanced_monthly_plans
        )
        
        logger.info(f"Enhanced business plan with baseline FTE: {len(workforce_counts)} roles, "
                   f"{sum(sum(levels.values()) for levels in workforce_counts.values())} total FTE")
        
        return enhanced_business_plan
    
    def _create_default_utilization_targets(self) -> Dict[str, float]:
        """Create default utilization targets by role"""
        return {
            'Consultant': 0.85,    # 85% billable utilization
            'Sales': 0.0,          # Non-billable
            'Recruitment': 0.0,    # Non-billable  
            'Operations': 0.0      # Non-billable
        }
    
    def _extract_targets_from_raw_plan(self, business_plan: Dict[str, Any], year: int, month: int) -> MonthlyTargets:
        """Extract monthly targets from raw business plan entries format
        
        Raw format: {id, office_id, year, month, entries: [{role, level, recruitment, churn, salary, price, utr}]}
        """
        # Check if this business plan matches the requested year
        plan_year = business_plan.get('year')
        
        if plan_year != year:
            logger.warning(f"Business plan is for year {plan_year}, requested year {year}")
            return self._create_empty_targets(year, month)
        
        # Extract recruitment/churn targets from entries
        recruitment_targets = {}
        churn_targets = {}
        total_revenue = 0.0
        total_salary = 0.0
        
        for entry in business_plan.get('entries', []):
            role = entry.get('role', 'Unknown')
            level = entry.get('level', 'default')
            
            # Initialize role structures if needed
            if role not in recruitment_targets:
                recruitment_targets[role] = {}
                churn_targets[role] = {}
            
            # Extract targets as integers - people are whole numbers
            recruitment = int(entry.get('recruitment', 0))
            churn = int(entry.get('churn', 0))
            salary = float(entry.get('salary', 0))
            price = float(entry.get('price', 0))
            
            recruitment_targets[role][level] = recruitment
            churn_targets[role][level] = churn
            
            # Debug logging
            if recruitment > 0 or churn > 0:
                logger.info(f"Business plan targets: {role} {level} - recruitment={recruitment}, churn={churn}, salary={salary}, price={price}")
            
            # Calculate revenue and salary budget
            # Revenue = recruitment * price (simplified)
            total_revenue += recruitment * price
            total_salary += recruitment * salary
        
        logger.debug(f"Extracted targets from raw business plan: {len(business_plan.get('entries', []))} entries, "
                    f"${total_revenue:,.0f} revenue, ${total_salary:,.0f} salary budget")
        
        return MonthlyTargets(
            year=year,
            month=month,
            recruitment_targets=recruitment_targets,
            churn_targets=churn_targets,
            revenue_target=total_revenue,
            operating_costs=total_salary * 0.3,  # Estimate 30% of salary as operating costs
            salary_budget=total_salary
        )
    
    def _extract_targets_from_unified_plan(self, business_plan: Dict[str, Any], year: int, month: int) -> MonthlyTargets:
        """Extract monthly targets from unified business plan format with monthly_plans
        
        Unified format: {id, office_id, year, monthly_plans: {"YYYY-MM": {month, year, entries: [...]}}}
        """
        monthly_plans = business_plan.get('monthly_plans', {})
        month_key = f"{year}-{month:02d}"
        
        # Look for the specific month in monthly_plans
        monthly_plan = monthly_plans.get(month_key)
        if not monthly_plan:
            logger.warning(f"No monthly plan found for {year}-{month:02d} in unified business plan")
            return self._create_empty_targets(year, month)
        
        # Extract recruitment/churn targets from entries
        recruitment_targets = {}
        churn_targets = {}
        total_revenue = 0.0
        total_salary = 0.0
        
        for entry in monthly_plan.get('entries', []):
            role = entry.get('role', 'Unknown')
            level = entry.get('level', 'default')
            
            # Initialize role structures if needed
            if role not in recruitment_targets:
                recruitment_targets[role] = {}
                churn_targets[role] = {}
            
            # Extract targets
            recruitment = entry.get('recruitment', 0)
            churn = entry.get('churn', 0)
            salary = float(entry.get('salary', 0))
            price = float(entry.get('price', 0))
            
            # Debug log
            logger.debug(f"Processing entry: {role} {level} - recruitment: {recruitment}, churn: {churn}, salary: {salary}, price: {price}")
            
            recruitment_targets[role][level] = int(recruitment)
            churn_targets[role][level] = int(churn)
            
            # Calculate revenue and salary budget
            # Revenue = recruitment * price (simplified)
            total_revenue += recruitment * price
            total_salary += recruitment * salary
        
        logger.debug(f"Extracted targets from unified business plan for {month_key}: {len(monthly_plan.get('entries', []))} entries, "
                    f"${total_revenue:,.0f} revenue, ${total_salary:,.0f} salary budget")
        
        return MonthlyTargets(
            year=year,
            month=month,
            recruitment_targets=recruitment_targets,
            churn_targets=churn_targets,
            revenue_target=total_revenue,
            operating_costs=total_salary * 0.3,  # Estimate 30% of salary as operating costs
            salary_budget=total_salary
        )

    def _extract_price_per_hour(self, monthly_plan: MonthlyPlan) -> Dict[str, float]:
        """Extract price per hour by level from existing price_per_role data"""
        price_per_hour = {}
        
        # Extract from consultant pricing (main billable role)
        consultant_pricing = monthly_plan.price_per_role.get('Consultant', {})
        for level, monthly_price in consultant_pricing.items():
            # Convert monthly price to hourly (assume 160 hours/month)
            hourly_rate = monthly_price / 160.0
            price_per_hour[level] = hourly_rate
        
        return price_per_hour


# ============================================================================
# Business Plan Utilities
# ============================================================================

class BusinessPlanUtilities:
    """Utility functions for business plan operations"""
    
    @staticmethod
    def create_sample_business_plan(office_id: str, start_year: int, months: int = 12) -> BusinessPlan:
        """Create sample business plan for testing"""
        monthly_plans = {}
        
        for i in range(months):
            month = (i % 12) + 1
            year = start_year + (i // 12)
            
            # Create sample monthly plan
            monthly_plan = MonthlyPlan(
                year=year,
                month=month,
                recruitment={
                    "Consultant": {"A": 5.0, "AC": 2.0, "C": 1.0},
                    "Sales": {"A": 3.0, "AC": 1.0}
                },
                churn={
                    "Consultant": {"A": 2.0, "AC": 1.0, "C": 0.5},
                    "Sales": {"A": 1.5, "AC": 0.5}
                },
                revenue=100000.0 + (i * 5000),  # Growing revenue
                costs=60000.0 + (i * 2000),     # Growing costs
                price_per_role={
                    "Consultant": {"A": 5000.0, "AC": 7000.0, "C": 10000.0},
                    "Sales": {"A": 4000.0, "AC": 6000.0}
                },
                salary_per_role={
                    "Consultant": {"A": 4000.0, "AC": 5500.0, "C": 7000.0},
                    "Sales": {"A": 3500.0, "AC": 4500.0}
                },
                utr_per_role={
                    "Consultant": {"A": 0.8, "AC": 0.85, "C": 0.9},
                    "Sales": {"A": 0.75, "AC": 0.8}
                }
            )
            
            month_key = f"{year:04d}-{month:02d}"
            monthly_plans[month_key] = monthly_plan
        
        return BusinessPlan(
            office_id=office_id,
            name=f"Sample Business Plan - {office_id}",
            monthly_plans=monthly_plans
        )


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    'BusinessPlanProcessorV2',
    'FinancialMetrics',
    'BusinessPlanValidation',
    'BusinessPlanUtilities'
]