"""
KPI Calculator V2 - External Analytics Component

Handles all KPI calculations separately from the simulation engine:
- Workforce metrics (headcount, turnover, progression rates)
- Financial metrics (revenue, costs, profitability)
- Business intelligence (utilization, efficiency, growth rates)
- Comparative analysis (vs targets, vs previous periods)
- Executive summary generation
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
import logging
import statistics
from dataclasses import dataclass, field
from collections import defaultdict

from .simulation_engine_v2 import (
    SimulationResults, BusinessModel, PersonEvent, EventType, MonthlyResults,
    Person, OfficeState, KPICalculatorInterface, ValidationResult
)

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class WorkforceKPIs:
    """Workforce-related KPI metrics"""
    total_headcount: int
    headcount_by_role: Dict[str, int]
    headcount_by_level: Dict[str, int]
    headcount_by_office: Dict[str, int]
    
    total_recruitment: int
    recruitment_by_role: Dict[str, int]
    recruitment_rate: float  # % of workforce
    
    total_churn: int
    churn_by_role: Dict[str, int]
    churn_rate: float  # % of workforce
    
    net_recruitment: int
    growth_rate: float  # Net recruitment as % of workforce
    
    total_promotions: int
    promotion_rate: float  # % of workforce promoted
    promotion_by_level: Dict[str, int]
    
    average_tenure_months: float
    tenure_distribution: Dict[str, int]  # "0-6", "6-12", etc.


@dataclass
class FinancialKPIs:
    """Financial-related KPI metrics"""
    total_revenue: float
    revenue_growth_rate: float
    revenue_per_fte: float
    
    total_costs: float
    cost_growth_rate: float
    cost_per_fte: float
    
    gross_profit: float
    profit_margin: float
    
    total_salary_costs: float
    salary_per_fte: float
    
    operating_efficiency: float  # Revenue / Operating Costs
    fte_productivity: float      # Revenue per FTE


@dataclass
class BusinessIntelligenceKPIs:
    """Business intelligence and efficiency metrics"""
    average_utilization_rate: float
    utilization_by_role: Dict[str, float]
    
    revenue_per_role: Dict[str, float]
    profitability_by_role: Dict[str, float]
    
    growth_momentum: float  # Trend indicator
    market_expansion_rate: float
    
    operational_metrics: Dict[str, float]  # Custom business metrics


@dataclass
class ComparativeAnalysis:
    """Comparative analysis against targets and benchmarks"""
    vs_targets: Dict[str, Dict[str, float]]  # metric -> {actual, target, variance}
    vs_previous_period: Dict[str, Dict[str, float]]  # metric -> {current, previous, change}
    
    performance_summary: Dict[str, str]  # metric -> "above_target" | "below_target" | "on_target"
    key_insights: List[str]


@dataclass
class ExecutiveSummary:
    """High-level executive summary of simulation results"""
    period_description: str
    total_workforce_change: str  # e.g., "+15% growth (85 → 98 FTE)"
    financial_performance: str   # e.g., "Revenue up 12%, costs up 8%"
    key_achievements: List[str]
    areas_of_concern: List[str]
    recommended_actions: List[str]


class KPICalculatorV2(KPICalculatorInterface):
    """
    Calculates comprehensive KPIs from simulation results
    
    Key capabilities:
    - Calculate workforce metrics from person events
    - Compute financial KPIs from business model data
    - Generate business intelligence insights
    - Perform comparative analysis against targets
    - Create executive summaries for stakeholders
    """
    
    def __init__(self):
        self.benchmark_data: Dict[str, Any] = {}
        self.calculation_cache: Dict[str, Any] = {}
        self.custom_kpi_definitions: Dict[str, Any] = {}
        
    def initialize(self, **kwargs) -> bool:
        """Initialize KPI calculator with configuration"""
        if 'benchmark_data' in kwargs:
            self.benchmark_data = kwargs['benchmark_data']
        if 'custom_kpis' in kwargs:
            self.custom_kpi_definitions = kwargs['custom_kpis']
            
        logger.info("KPICalculatorV2 initialized successfully")
        return True
    
    def calculate_workforce_kpis(self, results: SimulationResults) -> WorkforceKPIs:
        """
        Calculate comprehensive workforce KPIs from simulation results
        
        Args:
            results: SimulationResults from simulation
            
        Returns:
            WorkforceKPIs object with all workforce metrics
        """
        # Get final workforce state
        final_workforce = self._get_final_workforce_counts(results.final_workforce)
        
        # Get event-based metrics
        all_events = results.all_events
        hire_events = [e for e in all_events if e.event_type == EventType.HIRED]
        churn_events = [e for e in all_events if e.event_type == EventType.CHURNED]
        promotion_events = [e for e in all_events if e.event_type == EventType.PROMOTED]
        
        # Calculate basic metrics
        total_headcount = final_workforce['total']
        total_recruitment = len(hire_events)
        total_churn = len(churn_events)
        total_promotions = len(promotion_events)
        
        # Calculate rates
        recruitment_rate = (total_recruitment / total_headcount * 100) if total_headcount > 0 else 0
        churn_rate = (total_churn / total_headcount * 100) if total_headcount > 0 else 0
        promotion_rate = (total_promotions / total_headcount * 100) if total_headcount > 0 else 0
        
        net_recruitment = total_recruitment - total_churn
        growth_rate = (net_recruitment / total_headcount * 100) if total_headcount > 0 else 0
        
        # Calculate tenure metrics
        tenure_stats = self._calculate_tenure_statistics(results.final_workforce)
        
        workforce_kpis = WorkforceKPIs(
            total_headcount=total_headcount,
            headcount_by_role=final_workforce['by_role'],
            headcount_by_level=final_workforce['by_level'],
            headcount_by_office=final_workforce['by_office'],
            
            total_recruitment=total_recruitment,
            recruitment_by_role=self._count_events_by_role(hire_events),
            recruitment_rate=recruitment_rate,
            
            total_churn=total_churn,
            churn_by_role=self._count_events_by_role(churn_events),
            churn_rate=churn_rate,
            
            net_recruitment=net_recruitment,
            growth_rate=growth_rate,
            
            total_promotions=total_promotions,
            promotion_rate=promotion_rate,
            promotion_by_level=self._count_promotions_by_level(promotion_events),
            
            average_tenure_months=tenure_stats['average_tenure'],
            tenure_distribution=tenure_stats['distribution']
        )
        
        logger.info(f"Calculated workforce KPIs: {total_headcount} FTE, {growth_rate:.1f}% growth")
        return workforce_kpis
    
    def calculate_financial_kpis(self, results: SimulationResults, business_model: BusinessModel) -> FinancialKPIs:
        """
        Calculate financial KPIs from simulation results and business model
        
        Args:
            results: SimulationResults from simulation
            business_model: BusinessModel with financial data
            
        Returns:
            FinancialKPIs object with all financial metrics
        """
        # Aggregate financial data from monthly results
        total_revenue = 0.0
        total_costs = 0.0
        total_salary_costs = 0.0
        monthly_revenues = []
        monthly_costs = []
        
        for monthly_result in results.monthly_results.values():
            # Extract financial data from monthly results
            month_revenue = self._extract_monthly_revenue(monthly_result)
            month_costs = self._extract_monthly_costs(monthly_result)
            month_salary = self._extract_monthly_salary_costs(monthly_result)
            
            total_revenue += month_revenue
            total_costs += month_costs
            total_salary_costs += month_salary
            
            monthly_revenues.append(month_revenue)
            monthly_costs.append(month_costs)
        
        # Calculate workforce size
        workforce_size = self._get_final_workforce_counts(results.final_workforce)['total']
        
        # Calculate derived metrics
        gross_profit = total_revenue - total_costs
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        revenue_per_fte = total_revenue / workforce_size if workforce_size > 0 else 0
        cost_per_fte = total_costs / workforce_size if workforce_size > 0 else 0
        salary_per_fte = total_salary_costs / workforce_size if workforce_size > 0 else 0
        
        operating_efficiency = total_revenue / total_costs if total_costs > 0 else 0
        fte_productivity = revenue_per_fte
        
        # Calculate growth rates
        revenue_growth_rate = self._calculate_growth_rate(monthly_revenues)
        cost_growth_rate = self._calculate_growth_rate(monthly_costs)
        
        financial_kpis = FinancialKPIs(
            total_revenue=total_revenue,
            revenue_growth_rate=revenue_growth_rate,
            revenue_per_fte=revenue_per_fte,
            
            total_costs=total_costs,
            cost_growth_rate=cost_growth_rate,
            cost_per_fte=cost_per_fte,
            
            gross_profit=gross_profit,
            profit_margin=profit_margin,
            
            total_salary_costs=total_salary_costs,
            salary_per_fte=salary_per_fte,
            
            operating_efficiency=operating_efficiency,
            fte_productivity=fte_productivity
        )
        
        logger.info(f"Calculated financial KPIs: ${total_revenue:,.0f} revenue, {profit_margin:.1f}% margin")
        return financial_kpis
    
    def calculate_business_intelligence_kpis(self, results: SimulationResults, 
                                           business_model: BusinessModel) -> BusinessIntelligenceKPIs:
        """Calculate advanced business intelligence KPIs"""
        # Calculate utilization metrics
        utilization_by_role = self._calculate_utilization_by_role(results, business_model)
        average_utilization = sum(utilization_by_role.values()) / len(utilization_by_role) if utilization_by_role else 0
        
        # Calculate profitability by role
        profitability_by_role = self._calculate_profitability_by_role(results, business_model)
        revenue_per_role = self._calculate_revenue_by_role(results, business_model)
        
        # Calculate growth momentum (trend indicator)
        growth_momentum = self._calculate_growth_momentum(results)
        
        # Calculate market expansion rate
        market_expansion_rate = self._calculate_market_expansion_rate(results)
        
        # Calculate custom operational metrics
        operational_metrics = self._calculate_operational_metrics(results, business_model)
        
        bi_kpis = BusinessIntelligenceKPIs(
            average_utilization_rate=average_utilization,
            utilization_by_role=utilization_by_role,
            
            revenue_per_role=revenue_per_role,
            profitability_by_role=profitability_by_role,
            
            growth_momentum=growth_momentum,
            market_expansion_rate=market_expansion_rate,
            
            operational_metrics=operational_metrics
        )
        
        logger.info(f"Calculated BI KPIs: {average_utilization:.1f}% avg utilization")
        return bi_kpis
    
    def calculate_comparative_analysis(self, workforce_kpis: WorkforceKPIs, 
                                     financial_kpis: FinancialKPIs,
                                     targets: Optional[Dict[str, Any]] = None) -> ComparativeAnalysis:
        """Perform comparative analysis against targets and benchmarks"""
        vs_targets = {}
        vs_previous_period = {}
        performance_summary = {}
        key_insights = []
        
        # Compare against targets if provided
        if targets:
            vs_targets = self._compare_against_targets(workforce_kpis, financial_kpis, targets)
            performance_summary = self._generate_performance_summary(vs_targets)
            key_insights.extend(self._generate_target_insights(vs_targets))
        
        # Compare against previous period if available in cache
        if 'previous_period' in self.calculation_cache:
            vs_previous_period = self._compare_against_previous_period(
                workforce_kpis, financial_kpis, self.calculation_cache['previous_period']
            )
            key_insights.extend(self._generate_period_comparison_insights(vs_previous_period))
        
        # Cache current period for future comparisons
        self.calculation_cache['previous_period'] = {
            'workforce_kpis': workforce_kpis,
            'financial_kpis': financial_kpis
        }
        
        return ComparativeAnalysis(
            vs_targets=vs_targets,
            vs_previous_period=vs_previous_period,
            performance_summary=performance_summary,
            key_insights=key_insights
        )
    
    def generate_executive_summary(self, workforce_kpis: WorkforceKPIs, 
                                  financial_kpis: FinancialKPIs,
                                  bi_kpis: BusinessIntelligenceKPIs,
                                  comparative: ComparativeAnalysis) -> ExecutiveSummary:
        """Generate executive summary of simulation results"""
        
        # Create period description
        period_description = f"Simulation Results Analysis"
        
        # Workforce change summary
        total_workforce_change = f"{workforce_kpis.growth_rate:+.1f}% growth ({workforce_kpis.total_headcount} FTE)"
        
        # Financial performance summary
        financial_performance = f"Revenue: ${financial_kpis.total_revenue:,.0f} ({financial_kpis.revenue_growth_rate:+.1f}%), " \
                               f"Profit Margin: {financial_kpis.profit_margin:.1f}%"
        
        # Key achievements
        key_achievements = []
        if workforce_kpis.growth_rate > 10:
            key_achievements.append(f"Strong workforce growth of {workforce_kpis.growth_rate:.1f}%")
        if financial_kpis.profit_margin > 20:
            key_achievements.append(f"Healthy profit margin of {financial_kpis.profit_margin:.1f}%")
        if bi_kpis.average_utilization_rate > 85:
            key_achievements.append(f"High utilization rate of {bi_kpis.average_utilization_rate:.1f}%")
        
        # Areas of concern
        areas_of_concern = []
        if workforce_kpis.churn_rate > 20:
            areas_of_concern.append(f"High churn rate of {workforce_kpis.churn_rate:.1f}%")
        if financial_kpis.profit_margin < 10:
            areas_of_concern.append(f"Low profit margin of {financial_kpis.profit_margin:.1f}%")
        if bi_kpis.growth_momentum < 0:
            areas_of_concern.append("Negative growth momentum detected")
        
        # Recommended actions
        recommended_actions = []
        if workforce_kpis.churn_rate > 15:
            recommended_actions.append("Implement retention programs to reduce churn")
        if financial_kpis.cost_growth_rate > financial_kpis.revenue_growth_rate:
            recommended_actions.append("Focus on cost optimization to improve profitability")
        if bi_kpis.average_utilization_rate < 75:
            recommended_actions.append("Improve resource utilization and project allocation")
        
        return ExecutiveSummary(
            period_description=period_description,
            total_workforce_change=total_workforce_change,
            financial_performance=financial_performance,
            key_achievements=key_achievements,
            areas_of_concern=areas_of_concern,
            recommended_actions=recommended_actions
        )
    
    def calculate_all_kpis(self, results: SimulationResults, 
                          business_model: BusinessModel,
                          targets: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate all KPIs and return comprehensive analytics package"""
        workforce_kpis = self.calculate_workforce_kpis(results)
        financial_kpis = self.calculate_financial_kpis(results, business_model)
        bi_kpis = self.calculate_business_intelligence_kpis(results, business_model)
        comparative = self.calculate_comparative_analysis(workforce_kpis, financial_kpis, targets)
        executive_summary = self.generate_executive_summary(workforce_kpis, financial_kpis, bi_kpis, comparative)
        
        return {
            'workforce_kpis': workforce_kpis,
            'financial_kpis': financial_kpis,
            'business_intelligence_kpis': bi_kpis,
            'comparative_analysis': comparative,
            'executive_summary': executive_summary,
            'calculation_metadata': {
                'calculated_at': datetime.now().isoformat(),
                'total_events_analyzed': len(results.all_events),
                'simulation_period': f"{len(results.monthly_results)} months"
            }
        }
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _get_final_workforce_counts(self, final_workforce: Dict[str, OfficeState]) -> Dict[str, Any]:
        """Get comprehensive workforce counts from final state"""
        total = 0
        by_role = defaultdict(int)
        by_level = defaultdict(int)
        by_office = defaultdict(int)
        
        for office_name, office_state in final_workforce.items():
            office_total = 0
            for role, levels in office_state.workforce.items():
                for level, people in levels.items():
                    active_count = len([p for p in people if p.is_active])
                    
                    total += active_count
                    office_total += active_count
                    by_role[role] += active_count
                    by_level[level] += active_count
            
            by_office[office_name] = office_total
        
        return {
            'total': total,
            'by_role': dict(by_role),
            'by_level': dict(by_level),
            'by_office': dict(by_office)
        }
    
    def _count_events_by_role(self, events: List[PersonEvent]) -> Dict[str, int]:
        """Count events by role"""
        counts = defaultdict(int)
        for event in events:
            role = event.details.get('role')
            if role:
                counts[role] += 1
        return dict(counts)
    
    def _count_promotions_by_level(self, promotion_events: List[PersonEvent]) -> Dict[str, int]:
        """Count promotions by from_level"""
        counts = defaultdict(int)
        for event in promotion_events:
            from_level = event.details.get('from_level')
            if from_level:
                counts[from_level] += 1
        return dict(counts)
    
    def _calculate_tenure_statistics(self, final_workforce: Dict[str, OfficeState]) -> Dict[str, Any]:
        """Calculate tenure statistics from final workforce"""
        all_tenures = []
        distribution = {"0-6": 0, "6-12": 0, "12-24": 0, "24+": 0}
        
        current_date = date.today()  # Would use simulation end date in real implementation
        
        for office_state in final_workforce.values():
            for role, levels in office_state.workforce.items():
                for level, people in levels.items():
                    for person in people:
                        if person.is_active:
                            tenure_months = person.get_tenure_months(current_date)
                            all_tenures.append(tenure_months)
                            
                            # Categorize for distribution
                            if tenure_months < 6:
                                distribution["0-6"] += 1
                            elif tenure_months < 12:
                                distribution["6-12"] += 1
                            elif tenure_months < 24:
                                distribution["12-24"] += 1
                            else:
                                distribution["24+"] += 1
        
        average_tenure = statistics.mean(all_tenures) if all_tenures else 0
        
        return {
            'average_tenure': average_tenure,
            'distribution': distribution
        }
    
    def _extract_monthly_revenue(self, monthly_result: MonthlyResults) -> float:
        """Extract revenue from monthly results"""
        total_revenue = 0.0
        for office_metrics in monthly_result.office_results.values():
            total_revenue += office_metrics.get('revenue', 0.0)
        return total_revenue
    
    def _extract_monthly_costs(self, monthly_result: MonthlyResults) -> float:
        """Extract costs from monthly results"""
        total_costs = 0.0
        for office_metrics in monthly_result.office_results.values():
            total_costs += office_metrics.get('costs', 0.0)
        return total_costs
    
    def _extract_monthly_salary_costs(self, monthly_result: MonthlyResults) -> float:
        """Extract salary costs from monthly results"""
        total_salary = 0.0
        for office_metrics in monthly_result.office_results.values():
            total_salary += office_metrics.get('salary_costs', 0.0)
        return total_salary
    
    def _calculate_growth_rate(self, monthly_values: List[float]) -> float:
        """Calculate compound annual growth rate from monthly values"""
        if len(monthly_values) < 2:
            return 0.0
        
        first_value = monthly_values[0] if monthly_values[0] > 0 else 1
        last_value = monthly_values[-1]
        months = len(monthly_values) - 1
        
        if months == 0 or first_value <= 0:
            return 0.0
        
        # Calculate compound monthly growth rate and annualize
        monthly_growth_rate = (last_value / first_value) ** (1/months) - 1
        annual_growth_rate = ((1 + monthly_growth_rate) ** 12 - 1) * 100
        
        return annual_growth_rate
    
    def _calculate_utilization_by_role(self, results: SimulationResults, 
                                      business_model: BusinessModel) -> Dict[str, float]:
        """Calculate utilization rates by role"""
        # This would require actual utilization data from business model
        # Placeholder implementation
        return {
            "Consultant": 85.0,
            "Sales": 75.0,
            "Operations": 90.0,
            "Recruitment": 80.0
        }
    
    def _calculate_profitability_by_role(self, results: SimulationResults,
                                        business_model: BusinessModel) -> Dict[str, float]:
        """Calculate profitability by role"""
        # This would require detailed financial calculations per role
        # Placeholder implementation
        return {
            "Consultant": 25.0,  # 25% margin
            "Sales": 30.0,       # 30% margin
            "Operations": 15.0,  # 15% margin
            "Recruitment": 20.0  # 20% margin
        }
    
    def _calculate_revenue_by_role(self, results: SimulationResults,
                                  business_model: BusinessModel) -> Dict[str, float]:
        """Calculate revenue contribution by role"""
        # Placeholder implementation
        return {
            "Consultant": 150000.0,  # Revenue per FTE
            "Sales": 120000.0,
            "Operations": 80000.0,
            "Recruitment": 100000.0
        }
    
    def _calculate_growth_momentum(self, results: SimulationResults) -> float:
        """Calculate growth momentum indicator"""
        # Analyze recruitment vs churn trends over time
        monthly_net_recruitment = []
        
        for monthly_result in results.monthly_results.values():
            month_hires = len([e for e in monthly_result.events if e.event_type == EventType.HIRED])
            month_churn = len([e for e in monthly_result.events if e.event_type == EventType.CHURNED])
            monthly_net_recruitment.append(month_hires - month_churn)
        
        if len(monthly_net_recruitment) < 2:
            return 0.0
        
        # Simple trend calculation
        recent_avg = statistics.mean(monthly_net_recruitment[-3:]) if len(monthly_net_recruitment) >= 3 else monthly_net_recruitment[-1]
        earlier_avg = statistics.mean(monthly_net_recruitment[:3]) if len(monthly_net_recruitment) >= 3 else monthly_net_recruitment[0]
        
        return recent_avg - earlier_avg
    
    def _calculate_market_expansion_rate(self, results: SimulationResults) -> float:
        """Calculate market expansion rate"""
        # Simplified calculation based on revenue growth
        monthly_revenues = []
        for monthly_result in results.monthly_results.values():
            monthly_revenues.append(self._extract_monthly_revenue(monthly_result))
        
        return self._calculate_growth_rate(monthly_revenues)
    
    def _calculate_operational_metrics(self, results: SimulationResults,
                                      business_model: BusinessModel) -> Dict[str, float]:
        """Calculate custom operational metrics"""
        return {
            "time_to_productivity_months": 3.5,  # Average time for new hires to be productive
            "employee_satisfaction_score": 7.8,  # Out of 10
            "client_satisfaction_score": 8.2,    # Out of 10
            "project_delivery_rate": 95.0,       # % of projects delivered on time
            "capacity_utilization": 88.0         # % of available capacity used
        }
    
    def _compare_against_targets(self, workforce_kpis: WorkforceKPIs, 
                                financial_kpis: FinancialKPIs,
                                targets: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Compare KPIs against targets"""
        comparisons = {}
        
        # Workforce comparisons
        if 'headcount_target' in targets:
            comparisons['headcount'] = {
                'actual': workforce_kpis.total_headcount,
                'target': targets['headcount_target'],
                'variance': (workforce_kpis.total_headcount - targets['headcount_target']) / targets['headcount_target'] * 100
            }
        
        if 'churn_rate_target' in targets:
            comparisons['churn_rate'] = {
                'actual': workforce_kpis.churn_rate,
                'target': targets['churn_rate_target'],
                'variance': workforce_kpis.churn_rate - targets['churn_rate_target']
            }
        
        # Financial comparisons
        if 'revenue_target' in targets:
            comparisons['revenue'] = {
                'actual': financial_kpis.total_revenue,
                'target': targets['revenue_target'],
                'variance': (financial_kpis.total_revenue - targets['revenue_target']) / targets['revenue_target'] * 100
            }
        
        if 'profit_margin_target' in targets:
            comparisons['profit_margin'] = {
                'actual': financial_kpis.profit_margin,
                'target': targets['profit_margin_target'],
                'variance': financial_kpis.profit_margin - targets['profit_margin_target']
            }
        
        return comparisons
    
    def _generate_performance_summary(self, vs_targets: Dict[str, Dict[str, float]]) -> Dict[str, str]:
        """Generate performance summary from target comparisons"""
        summary = {}
        
        for metric, comparison in vs_targets.items():
            variance = comparison['variance']
            if abs(variance) <= 5:  # Within 5% is "on target"
                summary[metric] = "on_target"
            elif variance > 5:
                summary[metric] = "above_target"
            else:
                summary[metric] = "below_target"
        
        return summary
    
    def _generate_target_insights(self, vs_targets: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate insights from target analysis"""
        insights = []
        
        for metric, comparison in vs_targets.items():
            variance = comparison['variance']
            if abs(variance) > 10:  # Significant variance
                direction = "above" if variance > 0 else "below"
                insights.append(f"{metric.replace('_', ' ').title()} is {abs(variance):.1f}% {direction} target")
        
        return insights
    
    def _compare_against_previous_period(self, workforce_kpis: WorkforceKPIs,
                                       financial_kpis: FinancialKPIs,
                                       previous_data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Compare against previous period data"""
        # Implementation would compare current vs previous period KPIs
        return {}  # Placeholder
    
    def _generate_period_comparison_insights(self, vs_previous: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate insights from period comparison"""
        return []  # Placeholder


# ============================================================================
# KPI Utilities
# ============================================================================

class KPIUtilities:
    """Utility functions for KPI calculations"""
    
    @staticmethod
    def create_industry_benchmarks() -> Dict[str, Any]:
        """Create industry benchmark data for comparison"""
        return {
            'consulting': {
                'churn_rate': 15.0,      # 15% annual churn
                'profit_margin': 22.0,    # 22% profit margin
                'utilization_rate': 85.0, # 85% utilization
                'revenue_per_fte': 180000 # $180k revenue per FTE
            },
            'technology': {
                'churn_rate': 12.0,
                'profit_margin': 25.0,
                'utilization_rate': 88.0,
                'revenue_per_fte': 200000
            }
        }
    
    @staticmethod
    def format_kpi_for_display(value: float, kpi_type: str) -> str:
        """Format KPI value for display"""
        if kpi_type == 'currency':
            return f"${value:,.0f}"
        elif kpi_type == 'percentage':
            return f"{value:.1f}%"
        elif kpi_type == 'integer':
            return f"{int(value):,}"
        elif kpi_type == 'decimal':
            return f"{value:.2f}"
        else:
            return str(value)


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    'KPICalculatorV2',
    'WorkforceKPIs',
    'FinancialKPIs',
    'BusinessIntelligenceKPIs',
    'ComparativeAnalysis',
    'ExecutiveSummary',
    'KPIUtilities'
]