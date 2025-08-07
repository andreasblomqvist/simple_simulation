"""
Growth Model Manager V2 - Multi-Year Modeling Component

Handles sophisticated growth rate modeling and business plan extrapolation:
- Multi-year growth rate application
- Business plan extrapolation beyond defined periods
- Compound growth calculations
- Scenario parameter extension
- Growth pattern analysis and validation
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
import logging
import math
from dataclasses import dataclass, field
import copy

from .simulation_engine_v2 import (
    BusinessModel, BusinessPlan, MonthlyPlan, GrowthRates, TimeRange,
    GrowthModelManagerInterface, ValidationResult
)

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class GrowthPattern:
    """Represents a growth pattern over time"""
    pattern_type: str  # "linear", "exponential", "sigmoid", "seasonal"
    base_rate: float   # Base growth rate
    seasonality_factor: Dict[int, float] = field(default_factory=dict)  # Month -> multiplier
    acceleration: float = 0.0  # Growth acceleration factor
    max_rate: Optional[float] = None  # Maximum growth rate cap


@dataclass
class GrowthModelConfiguration:
    """Configuration for growth model manager"""
    default_recruitment_pattern: GrowthPattern = field(default_factory=lambda: GrowthPattern("exponential", 0.05))
    default_price_pattern: GrowthPattern = field(default_factory=lambda: GrowthPattern("linear", 0.03))
    default_salary_pattern: GrowthPattern = field(default_factory=lambda: GrowthPattern("linear", 0.025))
    default_cost_pattern: GrowthPattern = field(default_factory=lambda: GrowthPattern("linear", 0.02))
    
    # Validation settings
    max_annual_growth_rate: float = 2.0  # 200% max annual growth
    min_annual_growth_rate: float = -0.5  # -50% min annual growth
    require_positive_extrapolation: bool = True


@dataclass
class EconomicScenario:
    """Economic scenario affecting growth rates"""
    name: str
    description: str
    growth_adjustments: Dict[str, float]  # metric -> adjustment factor
    duration_months: Optional[int] = None  # How long scenario lasts
    start_month: Optional[Tuple[int, int]] = None  # (year, month) when scenario starts


class GrowthModelManagerV2(GrowthModelManagerInterface):
    """
    Manages sophisticated multi-year growth modeling
    
    Key capabilities:
    - Create comprehensive business models from office data
    - Apply various growth patterns (linear, exponential, seasonal)
    - Extrapolate business plans beyond defined periods
    - Handle economic scenarios and external factors
    - Validate growth assumptions and constraints
    """
    
    def __init__(self):
        self.config = GrowthModelConfiguration()
        self.economic_scenarios: List[EconomicScenario] = []
        self.growth_history: Dict[str, List[float]] = {}  # Track historical growth rates
        
    def initialize(self, **kwargs) -> bool:
        """Initialize growth model manager"""
        if 'config' in kwargs:
            self.config = kwargs['config']
        if 'economic_scenarios' in kwargs:
            self.economic_scenarios = kwargs['economic_scenarios']
            
        logger.info("GrowthModelManagerV2 initialized successfully")
        return True
    
    def create_growth_model(self, offices: List[Dict[str, Any]], time_range: TimeRange) -> BusinessModel:
        """
        Create comprehensive business model from office data
        
        Args:
            offices: List of office configuration data
            time_range: Time range for the business model
            
        Returns:
            BusinessModel with growth-adjusted plans
        """
        office_plans = {}
        
        for office_data in offices:
            office_id = office_data.get('id')
            if not office_id:
                continue
            
            # Extract or create business plan
            business_plan = office_data.get('business_plan')
            if business_plan:
                # Convert to monthly plans
                monthly_plans = self._convert_business_plan_to_monthly(business_plan, time_range)
            else:
                # Create default business plan from office configuration
                monthly_plans = self._create_default_monthly_plans(office_data, time_range)
            
            office_plans[office_id] = monthly_plans
        
        # Create default growth rates
        default_growth_rates = GrowthRates(
            recruitment_growth_rate=self.config.default_recruitment_pattern.base_rate,
            price_growth_rate=self.config.default_price_pattern.base_rate,
            salary_growth_rate=self.config.default_salary_pattern.base_rate,
            cost_growth_rate=self.config.default_cost_pattern.base_rate
        )
        
        business_model = BusinessModel(
            office_plans=office_plans,
            growth_rates=default_growth_rates,
            time_range=time_range
        )
        
        logger.info(f"Created business model for {len(offices)} offices over {time_range.get_total_months()} months")
        return business_model
    
    def extrapolate_beyond_plan(self, last_month_data: MonthlyPlan, growth_rates: GrowthRates) -> List[MonthlyPlan]:
        """
        Extrapolate business plan beyond defined period using sophisticated growth modeling
        
        Args:
            last_month_data: Last month of actual business plan data
            growth_rates: Growth rates to apply
            
        Returns:
            List of extrapolated MonthlyPlan objects
        """
        extrapolated_plans = []
        
        # Start from the month after last_month_data
        current_year = last_month_data.year
        current_month = last_month_data.month + 1
        if current_month > 12:
            current_month = 1
            current_year += 1
        
        # Extrapolate for next 12 months (or configurable period)
        base_plan = copy.deepcopy(last_month_data)
        
        for i in range(12):
            months_forward = i + 1
            years_forward = months_forward / 12.0
            
            # Apply growth patterns
            extrapolated_plan = self._apply_growth_patterns(
                base_plan, 
                years_forward,
                growth_rates,
                current_month
            )
            
            # Update month/year
            extrapolated_plan.year = current_year
            extrapolated_plan.month = current_month
            
            extrapolated_plans.append(extrapolated_plan)
            
            # Move to next month
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
        
        logger.debug(f"Extrapolated {len(extrapolated_plans)} months beyond business plan")
        return extrapolated_plans
    
    def apply_compound_growth(self, base_value: float, growth_rate: float, years: float) -> float:
        """
        Apply compound growth calculation
        
        Args:
            base_value: Starting value
            growth_rate: Annual growth rate (as decimal, e.g., 0.05 for 5%)
            years: Number of years to compound
            
        Returns:
            Value after compound growth
        """
        if growth_rate <= -1.0:  # Prevent negative or zero base
            growth_rate = -0.99
            
        return base_value * ((1 + growth_rate) ** years)
    
    def create_seasonal_growth_model(self, base_growth_rate: float, seasonality: Dict[int, float]) -> GrowthPattern:
        """
        Create seasonal growth pattern
        
        Args:
            base_growth_rate: Base annual growth rate
            seasonality: Month-specific multipliers (1-12 -> multiplier)
            
        Returns:
            GrowthPattern with seasonal adjustments
        """
        return GrowthPattern(
            pattern_type="seasonal",
            base_rate=base_growth_rate,
            seasonality_factor=seasonality
        )
    
    def add_economic_scenario(self, scenario: EconomicScenario):
        """Add economic scenario to affect growth calculations"""
        self.economic_scenarios.append(scenario)
        logger.info(f"Added economic scenario: {scenario.name}")
    
    def calculate_dynamic_growth_rate(self, metric: str, current_month: Tuple[int, int], 
                                    base_rate: float) -> float:
        """
        Calculate dynamic growth rate considering economic scenarios and seasonality
        
        Args:
            metric: Metric name (e.g., "recruitment", "price", "salary")
            current_month: (year, month) tuple
            base_rate: Base growth rate
            
        Returns:
            Adjusted growth rate
        """
        adjusted_rate = base_rate
        year, month = current_month
        
        # Apply economic scenarios
        for scenario in self.economic_scenarios:
            if self._is_scenario_active(scenario, current_month):
                adjustment = scenario.growth_adjustments.get(metric, 1.0)
                adjusted_rate *= adjustment
        
        # Apply seasonality
        pattern = self._get_growth_pattern_for_metric(metric)
        if pattern.seasonality_factor:
            seasonal_multiplier = pattern.seasonality_factor.get(month, 1.0)
            adjusted_rate *= seasonal_multiplier
        
        # Apply constraints
        adjusted_rate = max(adjusted_rate, self.config.min_annual_growth_rate)
        adjusted_rate = min(adjusted_rate, self.config.max_annual_growth_rate)
        
        return adjusted_rate
    
    def validate_growth_assumptions(self, growth_rates: GrowthRates, time_range: TimeRange) -> ValidationResult:
        """Validate growth rate assumptions"""
        result = ValidationResult(True)
        
        # Check for reasonable growth rates
        if abs(growth_rates.recruitment_growth_rate) > self.config.max_annual_growth_rate:
            result.add_error(f"Recruitment growth rate ({growth_rates.recruitment_growth_rate:.1%}) exceeds maximum")
        
        if abs(growth_rates.price_growth_rate) > self.config.max_annual_growth_rate:
            result.add_error(f"Price growth rate ({growth_rates.price_growth_rate:.1%}) exceeds maximum")
        
        if abs(growth_rates.salary_growth_rate) > self.config.max_annual_growth_rate:
            result.add_error(f"Salary growth rate ({growth_rates.salary_growth_rate:.1%}) exceeds maximum")
        
        # Check for logical consistency
        if growth_rates.salary_growth_rate > growth_rates.price_growth_rate + 0.1:
            result.add_error("Salary growth significantly exceeds price growth - may impact profitability")
        
        # Check time range reasonableness
        if time_range.get_total_months() > 120:  # 10 years
            result.add_error("Time range exceeds 10 years - long-term growth assumptions may be unreliable")
        
        return result
    
    def analyze_growth_trends(self, historical_plans: List[MonthlyPlan]) -> Dict[str, Any]:
        """Analyze growth trends from historical business plan data"""
        if len(historical_plans) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Sort by date
        sorted_plans = sorted(historical_plans, key=lambda p: (p.year, p.month))
        
        # Calculate month-over-month growth rates
        revenue_growth_rates = []
        recruitment_growth_rates = []
        
        for i in range(1, len(sorted_plans)):
            current = sorted_plans[i]
            previous = sorted_plans[i-1]
            
            # Revenue growth
            if previous.revenue > 0:
                revenue_growth = (current.revenue - previous.revenue) / previous.revenue
                revenue_growth_rates.append(revenue_growth)
            
            # Total recruitment growth
            prev_recruitment = sum(sum(levels.values()) for levels in previous.recruitment.values())
            curr_recruitment = sum(sum(levels.values()) for levels in current.recruitment.values())
            
            if prev_recruitment > 0:
                recruitment_growth = (curr_recruitment - prev_recruitment) / prev_recruitment
                recruitment_growth_rates.append(recruitment_growth)
        
        # Calculate statistics
        analysis = {
            "revenue_growth": {
                "average_monthly": sum(revenue_growth_rates) / len(revenue_growth_rates) if revenue_growth_rates else 0,
                "annualized": ((1 + sum(revenue_growth_rates) / len(revenue_growth_rates)) ** 12 - 1) if revenue_growth_rates else 0,
                "volatility": self._calculate_volatility(revenue_growth_rates),
                "trend": self._calculate_trend(revenue_growth_rates)
            },
            "recruitment_growth": {
                "average_monthly": sum(recruitment_growth_rates) / len(recruitment_growth_rates) if recruitment_growth_rates else 0,
                "annualized": ((1 + sum(recruitment_growth_rates) / len(recruitment_growth_rates)) ** 12 - 1) if recruitment_growth_rates else 0,
                "volatility": self._calculate_volatility(recruitment_growth_rates),
                "trend": self._calculate_trend(recruitment_growth_rates)
            },
            "data_points": len(sorted_plans),
            "time_span_months": len(sorted_plans) - 1
        }
        
        return analysis
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _apply_growth_patterns(self, base_plan: MonthlyPlan, years_forward: float, 
                              growth_rates: GrowthRates, current_month: int) -> MonthlyPlan:
        """Apply sophisticated growth patterns to base plan"""
        extrapolated_plan = copy.deepcopy(base_plan)
        
        # Apply recruitment growth with pattern
        recruitment_pattern = self.config.default_recruitment_pattern
        recruitment_multiplier = self._calculate_pattern_multiplier(
            recruitment_pattern, years_forward, current_month
        )
        
        for role, levels in extrapolated_plan.recruitment.items():
            for level in levels:
                extrapolated_plan.recruitment[role][level] *= recruitment_multiplier
        
        # Apply price growth with pattern
        price_pattern = self.config.default_price_pattern
        price_multiplier = self._calculate_pattern_multiplier(
            price_pattern, years_forward, current_month
        )
        
        extrapolated_plan.revenue *= price_multiplier
        
        for role, levels in extrapolated_plan.price_per_role.items():
            for level in levels:
                extrapolated_plan.price_per_role[role][level] *= price_multiplier
        
        # Apply salary growth
        salary_pattern = self.config.default_salary_pattern
        salary_multiplier = self._calculate_pattern_multiplier(
            salary_pattern, years_forward, current_month
        )
        
        for role, levels in extrapolated_plan.salary_per_role.items():
            for level in levels:
                extrapolated_plan.salary_per_role[role][level] *= salary_multiplier
        
        # Apply cost growth
        cost_pattern = self.config.default_cost_pattern
        cost_multiplier = self._calculate_pattern_multiplier(
            cost_pattern, years_forward, current_month
        )
        
        extrapolated_plan.costs *= cost_multiplier
        
        return extrapolated_plan
    
    def _calculate_pattern_multiplier(self, pattern: GrowthPattern, years_forward: float, 
                                     current_month: int) -> float:
        """Calculate growth multiplier based on pattern type"""
        base_multiplier = 1.0
        
        if pattern.pattern_type == "linear":
            base_multiplier = 1 + (pattern.base_rate * years_forward)
        
        elif pattern.pattern_type == "exponential":
            base_multiplier = (1 + pattern.base_rate) ** years_forward
        
        elif pattern.pattern_type == "sigmoid":
            # S-curve growth that levels off
            max_multiplier = pattern.max_rate or (1 + pattern.base_rate * 5)
            base_multiplier = max_multiplier / (1 + math.exp(-pattern.base_rate * (years_forward - 2)))
        
        elif pattern.pattern_type == "seasonal":
            # Base exponential with seasonal adjustment
            base_multiplier = (1 + pattern.base_rate) ** years_forward
            seasonal_factor = pattern.seasonality_factor.get(current_month, 1.0)
            base_multiplier *= seasonal_factor
        
        # Apply acceleration if configured
        if pattern.acceleration != 0:
            acceleration_factor = 1 + (pattern.acceleration * years_forward ** 2)
            base_multiplier *= acceleration_factor
        
        # Apply maximum rate cap
        if pattern.max_rate and base_multiplier > pattern.max_rate:
            base_multiplier = pattern.max_rate
        
        return max(base_multiplier, 0.1)  # Prevent negative growth from destroying values
    
    def _convert_business_plan_to_monthly(self, business_plan: Dict[str, Any], 
                                         time_range: TimeRange) -> List[MonthlyPlan]:
        """Convert business plan data to MonthlyPlan objects"""
        monthly_plans = []
        
        # This would need to parse actual business plan format
        # Placeholder implementation
        for year, month in time_range.get_month_list():
            monthly_plan = MonthlyPlan(
                year=year,
                month=month,
                recruitment=business_plan.get('recruitment', {}),
                churn=business_plan.get('churn', {}),
                revenue=business_plan.get('monthly_revenue', 50000.0),
                costs=business_plan.get('monthly_costs', 30000.0),
                price_per_role=business_plan.get('price_per_role', {}),
                salary_per_role=business_plan.get('salary_per_role', {}),
                utr_per_role=business_plan.get('utr_per_role', {})
            )
            monthly_plans.append(monthly_plan)
        
        return monthly_plans
    
    def _create_default_monthly_plans(self, office_data: Dict[str, Any], 
                                     time_range: TimeRange) -> List[MonthlyPlan]:
        """Create default monthly plans from office configuration"""
        monthly_plans = []
        
        # Extract office size and journey for scaling
        total_fte = office_data.get('total_fte', 100)
        journey = office_data.get('journey', 'Emerging')
        
        # Scale targets based on office size
        base_recruitment = max(1, total_fte // 20)  # ~5% monthly recruitment
        base_revenue = total_fte * 8000  # ~$8k revenue per FTE per month
        base_costs = base_revenue * 0.6   # 60% cost ratio
        
        for year, month in time_range.get_month_list():
            monthly_plan = MonthlyPlan(
                year=year,
                month=month,
                recruitment={
                    "Consultant": {"A": float(base_recruitment * 0.6), "AC": float(base_recruitment * 0.3), "C": float(base_recruitment * 0.1)},
                    "Sales": {"A": float(base_recruitment * 0.2), "AC": float(base_recruitment * 0.1)}
                },
                churn={
                    "Consultant": {"A": float(base_recruitment * 0.3), "AC": float(base_recruitment * 0.15), "C": float(base_recruitment * 0.05)},
                    "Sales": {"A": float(base_recruitment * 0.1), "AC": float(base_recruitment * 0.05)}
                },
                revenue=base_revenue,
                costs=base_costs,
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
            monthly_plans.append(monthly_plan)
        
        return monthly_plans
    
    def _is_scenario_active(self, scenario: EconomicScenario, current_month: Tuple[int, int]) -> bool:
        """Check if economic scenario is active for given month"""
        if not scenario.start_month:
            return True  # Always active if no start specified
        
        start_year, start_month = scenario.start_month
        current_year, current_month_num = current_month
        
        # Calculate months since scenario start
        months_since_start = (current_year - start_year) * 12 + (current_month_num - start_month)
        
        if months_since_start < 0:
            return False  # Scenario hasn't started yet
        
        if scenario.duration_months and months_since_start >= scenario.duration_months:
            return False  # Scenario has ended
        
        return True
    
    def _get_growth_pattern_for_metric(self, metric: str) -> GrowthPattern:
        """Get growth pattern for specific metric"""
        patterns = {
            "recruitment": self.config.default_recruitment_pattern,
            "price": self.config.default_price_pattern,
            "salary": self.config.default_salary_pattern,
            "costs": self.config.default_cost_pattern
        }
        return patterns.get(metric, self.config.default_recruitment_pattern)
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation) of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear regression slope
        n = len(values)
        x_mean = (n - 1) / 2  # 0, 1, 2, ... n-1
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "flat"
        
        slope = numerator / denominator
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "flat"


# ============================================================================
# Growth Model Utilities
# ============================================================================

class GrowthModelUtilities:
    """Utility functions for growth modeling"""
    
    @staticmethod
    def create_recession_scenario() -> EconomicScenario:
        """Create economic scenario modeling a recession"""
        return EconomicScenario(
            name="Economic Recession",
            description="6-month recession with reduced growth rates",
            growth_adjustments={
                "recruitment": 0.3,  # 70% reduction in recruitment growth
                "price": 0.8,        # 20% reduction in price growth
                "salary": 0.9,       # 10% reduction in salary growth
                "costs": 1.1         # 10% increase in cost growth
            },
            duration_months=6
        )
    
    @staticmethod
    def create_expansion_scenario() -> EconomicScenario:
        """Create economic scenario modeling rapid expansion"""
        return EconomicScenario(
            name="Market Expansion",
            description="12-month expansion with accelerated growth",
            growth_adjustments={
                "recruitment": 2.0,  # Double recruitment growth
                "price": 1.3,        # 30% increase in price growth
                "salary": 1.1,       # 10% increase in salary growth
                "costs": 1.2         # 20% increase in cost growth
            },
            duration_months=12
        )
    
    @staticmethod
    def create_seasonal_consulting_pattern() -> Dict[int, float]:
        """Create seasonal pattern typical for consulting businesses"""
        return {
            1: 0.8,   # January - slow start
            2: 0.9,   # February - building up
            3: 1.1,   # March - Q1 push
            4: 1.2,   # April - strong growth
            5: 1.3,   # May - peak hiring season
            6: 1.2,   # June - Q2 end
            7: 0.9,   # July - summer slowdown
            8: 0.8,   # August - vacation season
            9: 1.3,   # September - back to work surge
            10: 1.2,  # October - strong autumn
            11: 1.0,  # November - pre-holidays
            12: 0.7   # December - holiday slowdown
        }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    'GrowthModelManagerV2',
    'GrowthPattern',
    'GrowthModelConfiguration',
    'EconomicScenario',
    'GrowthModelUtilities'
]