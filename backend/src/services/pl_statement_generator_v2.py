"""
P&L Statement Generator V2 - Financial Reporting Component

Generates comprehensive monthly Profit & Loss statements from V2 simulation results:
- Revenue breakdown by role and level
- Cost analysis including salaries and operating expenses
- Profit calculations with margin analysis
- Role-specific financial attribution
- Multi-month trend analysis
- Export capabilities for financial reporting

Integrates with enhanced business plan data and utilization-based calculations.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
from dataclasses import dataclass, field
import logging

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class PLLineItem:
    """Individual line item in P&L statement"""
    item_name: str
    amount: float
    percentage_of_revenue: float = 0.0
    notes: Optional[str] = None
    breakdown: Dict[str, float] = field(default_factory=dict)


@dataclass
class PLSection:
    """Section of P&L statement (Revenue, Costs, etc.)"""
    section_name: str
    line_items: List[PLLineItem] = field(default_factory=list)
    section_total: float = 0.0
    percentage_of_revenue: float = 0.0


@dataclass
class MonthlyPLStatement:
    """Complete monthly P&L statement"""
    office_id: str
    year: int
    month: int
    statement_date: date
    
    # P&L Sections
    revenue_section: PLSection = None
    cost_section: PLSection = None
    profit_section: PLSection = None
    
    # Summary metrics
    total_revenue: float = 0.0
    total_costs: float = 0.0
    gross_profit: float = 0.0
    profit_margin: float = 0.0
    
    # Workforce metrics
    total_headcount: int = 0
    billable_headcount: int = 0
    revenue_per_fte: float = 0.0
    cost_per_fte: float = 0.0
    
    # Additional context
    scenario_id: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PLTrendAnalysis:
    """Multi-month trend analysis for P&L statements"""
    office_id: str
    time_period: str
    statements: List[MonthlyPLStatement]
    
    # Trend metrics
    revenue_growth_rate: float = 0.0
    cost_growth_rate: float = 0.0
    profit_margin_trend: List[float] = field(default_factory=list)
    headcount_trend: List[int] = field(default_factory=list)
    
    # Key insights
    insights: List[str] = field(default_factory=list)


class PLStatementGeneratorV2:
    """
    Generates comprehensive P&L statements from V2 simulation results
    
    Key capabilities:
    - Monthly P&L statement generation with detailed breakdowns
    - Role-specific revenue and cost attribution
    - Utilization-based revenue calculation integration
    - Multi-month trend analysis and forecasting
    - Export formats for financial reporting
    """
    
    def __init__(self):
        self.role_definitions = self._load_role_definitions()
        
    def generate_monthly_pl(self, office_state, monthly_plan, monthly_kpis, 
                           scenario_id: Optional[str] = None) -> MonthlyPLStatement:
        """
        Generate comprehensive monthly P&L statement
        
        Args:
            office_state: Current office workforce state
            monthly_plan: Enhanced monthly plan with baseline FTE and utilization
            monthly_kpis: Monthly KPI results from simulation
            scenario_id: Optional scenario identifier
            
        Returns:
            Complete MonthlyPLStatement with detailed breakdowns
        """
        from .business_plan_processor_v2 import BusinessPlanProcessorV2
        
        # Initialize P&L statement
        pl_statement = MonthlyPLStatement(
            office_id=office_state.name,
            year=monthly_plan.year,
            month=monthly_plan.month,
            statement_date=date(monthly_plan.year, monthly_plan.month, 1),
            scenario_id=scenario_id
        )
        
        # Generate revenue section
        pl_statement.revenue_section = self._generate_revenue_section(
            office_state, monthly_plan, monthly_kpis
        )
        pl_statement.total_revenue = pl_statement.revenue_section.section_total
        
        # Generate cost section
        pl_statement.cost_section = self._generate_cost_section(
            office_state, monthly_plan, monthly_kpis
        )
        pl_statement.total_costs = pl_statement.cost_section.section_total
        
        # Generate profit section
        pl_statement.profit_section = self._generate_profit_section(
            pl_statement.total_revenue, pl_statement.total_costs
        )
        pl_statement.gross_profit = pl_statement.profit_section.section_total
        
        # Calculate summary metrics
        pl_statement.profit_margin = (
            pl_statement.gross_profit / pl_statement.total_revenue * 100 
            if pl_statement.total_revenue > 0 else 0.0
        )
        
        # Workforce metrics
        pl_statement.total_headcount = office_state.get_total_workforce()
        pl_statement.billable_headcount = self._count_billable_workforce(office_state)
        
        pl_statement.revenue_per_fte = (
            pl_statement.total_revenue / pl_statement.total_headcount 
            if pl_statement.total_headcount > 0 else 0.0
        )
        pl_statement.cost_per_fte = (
            pl_statement.total_costs / pl_statement.total_headcount 
            if pl_statement.total_headcount > 0 else 0.0
        )
        
        # Update percentage of revenue for all line items
        self._calculate_percentages(pl_statement)
        
        logger.info(f"Generated P&L for {office_state.name} {monthly_plan.year}-{monthly_plan.month:02d}: "
                   f"${pl_statement.total_revenue:,.0f} revenue, {pl_statement.profit_margin:.1f}% margin")
        
        return pl_statement
    
    def generate_trend_analysis(self, pl_statements: List[MonthlyPLStatement]) -> PLTrendAnalysis:
        """Generate multi-month trend analysis from P&L statements"""
        if not pl_statements:
            raise ValueError("At least one P&L statement required for trend analysis")
        
        # Sort statements by date
        sorted_statements = sorted(pl_statements, key=lambda x: (x.year, x.month))
        office_id = sorted_statements[0].office_id
        
        # Calculate trends
        revenue_trend = [stmt.total_revenue for stmt in sorted_statements]
        cost_trend = [stmt.total_costs for stmt in sorted_statements]
        profit_margin_trend = [stmt.profit_margin for stmt in sorted_statements]
        headcount_trend = [stmt.total_headcount for stmt in sorted_statements]
        
        # Calculate growth rates (last vs first)
        if len(sorted_statements) > 1:
            first_revenue = sorted_statements[0].total_revenue
            last_revenue = sorted_statements[-1].total_revenue
            revenue_growth_rate = ((last_revenue - first_revenue) / first_revenue * 100) if first_revenue > 0 else 0.0
            
            first_costs = sorted_statements[0].total_costs
            last_costs = sorted_statements[-1].total_costs
            cost_growth_rate = ((last_costs - first_costs) / first_costs * 100) if first_costs > 0 else 0.0
        else:
            revenue_growth_rate = 0.0
            cost_growth_rate = 0.0
        
        # Generate insights
        insights = self._generate_trend_insights(sorted_statements, revenue_growth_rate, cost_growth_rate)
        
        time_period = f"{sorted_statements[0].year}-{sorted_statements[0].month:02d} to {sorted_statements[-1].year}-{sorted_statements[-1].month:02d}"
        
        return PLTrendAnalysis(
            office_id=office_id,
            time_period=time_period,
            statements=sorted_statements,
            revenue_growth_rate=revenue_growth_rate,
            cost_growth_rate=cost_growth_rate,
            profit_margin_trend=profit_margin_trend,
            headcount_trend=headcount_trend,
            insights=insights
        )
    
    def export_pl_to_dict(self, pl_statement: MonthlyPLStatement) -> Dict[str, Any]:
        """Export P&L statement to dictionary format for JSON/API responses"""
        return {
            "statement_info": {
                "office_id": pl_statement.office_id,
                "year": pl_statement.year,
                "month": pl_statement.month,
                "statement_date": pl_statement.statement_date.isoformat(),
                "scenario_id": pl_statement.scenario_id,
                "generated_at": pl_statement.generated_at.isoformat()
            },
            "summary": {
                "total_revenue": pl_statement.total_revenue,
                "total_costs": pl_statement.total_costs,
                "gross_profit": pl_statement.gross_profit,
                "profit_margin": pl_statement.profit_margin,
                "total_headcount": pl_statement.total_headcount,
                "billable_headcount": pl_statement.billable_headcount,
                "revenue_per_fte": pl_statement.revenue_per_fte,
                "cost_per_fte": pl_statement.cost_per_fte
            },
            "revenue_breakdown": self._section_to_dict(pl_statement.revenue_section),
            "cost_breakdown": self._section_to_dict(pl_statement.cost_section),
            "profit_breakdown": self._section_to_dict(pl_statement.profit_section)
        }
    
    def export_trend_to_dict(self, trend_analysis: PLTrendAnalysis) -> Dict[str, Any]:
        """Export trend analysis to dictionary format"""
        return {
            "trend_info": {
                "office_id": trend_analysis.office_id,
                "time_period": trend_analysis.time_period,
                "statement_count": len(trend_analysis.statements)
            },
            "growth_metrics": {
                "revenue_growth_rate": trend_analysis.revenue_growth_rate,
                "cost_growth_rate": trend_analysis.cost_growth_rate
            },
            "trends": {
                "profit_margin_trend": trend_analysis.profit_margin_trend,
                "headcount_trend": trend_analysis.headcount_trend
            },
            "insights": trend_analysis.insights,
            "monthly_statements": [
                self.export_pl_to_dict(stmt) for stmt in trend_analysis.statements
            ]
        }
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _generate_revenue_section(self, office_state, monthly_plan, monthly_kpis) -> PLSection:
        """Generate revenue section of P&L statement"""
        revenue_section = PLSection(section_name="Revenue")
        
        # Use utilization-based calculation if available
        if hasattr(monthly_plan, 'utilization_targets') and monthly_plan.utilization_targets:
            # Calculate net sales by role and level
            consultant_revenue = self._calculate_consultant_revenue(office_state, monthly_plan)
            
            # Only consultants generate revenue in our business model
            consultant_line_item = PLLineItem(
                item_name="Consulting Services (Billable Hours)",
                amount=consultant_revenue,
                notes="Revenue from consultant billable hours based on utilization and pricing",
                breakdown=self._get_consultant_revenue_breakdown(office_state, monthly_plan)
            )
            revenue_section.line_items.append(consultant_line_item)
            
            # Other roles generate no revenue
            other_roles_line_item = PLLineItem(
                item_name="Other Services (Sales, Recruitment, Operations)",
                amount=0.0,
                notes="Support roles - no direct revenue generation"
            )
            revenue_section.line_items.append(other_roles_line_item)
            
            revenue_section.section_total = consultant_revenue
        else:
            # Fallback to business plan revenue
            total_revenue_line_item = PLLineItem(
                item_name="Total Revenue (Business Plan)",
                amount=monthly_plan.revenue,
                notes="Revenue from business plan targets"
            )
            revenue_section.line_items.append(total_revenue_line_item)
            revenue_section.section_total = monthly_plan.revenue
        
        return revenue_section
    
    def _generate_cost_section(self, office_state, monthly_plan, monthly_kpis) -> PLSection:
        """Generate cost section of P&L statement"""
        cost_section = PLSection(section_name="Costs")
        
        # Salary costs by role
        salary_breakdown = self._calculate_salary_costs_by_role(office_state, monthly_plan)
        total_salary_costs = sum(salary_breakdown.values())
        
        salary_line_item = PLLineItem(
            item_name="Salary Costs",
            amount=total_salary_costs,
            notes="Total salary costs across all roles and levels",
            breakdown=salary_breakdown
        )
        cost_section.line_items.append(salary_line_item)
        
        # Operating costs
        operating_costs = getattr(monthly_plan, 'operating_costs', monthly_plan.costs * 0.3)
        operating_line_item = PLLineItem(
            item_name="Operating Costs",
            amount=operating_costs,
            notes="Rent, utilities, equipment, and other non-salary expenses"
        )
        cost_section.line_items.append(operating_line_item)
        
        cost_section.section_total = total_salary_costs + operating_costs
        
        return cost_section
    
    def _generate_profit_section(self, total_revenue: float, total_costs: float) -> PLSection:
        """Generate profit section of P&L statement"""
        profit_section = PLSection(section_name="Profit")
        
        gross_profit = total_revenue - total_costs
        
        gross_profit_line_item = PLLineItem(
            item_name="Gross Profit",
            amount=gross_profit,
            notes="Revenue minus all costs"
        )
        profit_section.line_items.append(gross_profit_line_item)
        
        profit_section.section_total = gross_profit
        
        return profit_section
    
    def _calculate_consultant_revenue(self, office_state, monthly_plan) -> float:
        """Calculate consultant revenue using utilization-based formula"""
        consultant_workforce = office_state.workforce.get('Consultant', {})
        consultant_utilization = monthly_plan.utilization_targets.get('Consultant', 0.85)
        working_hours = getattr(monthly_plan, 'working_hours_per_month', 160)
        
        total_revenue = 0.0
        
        for level, people in consultant_workforce.items():
            active_count = len([p for p in people if p.is_active])
            level_price = monthly_plan.price_per_hour.get(level, 0.0)
            
            level_revenue = active_count * consultant_utilization * level_price * working_hours
            total_revenue += level_revenue
        
        return total_revenue
    
    def _get_consultant_revenue_breakdown(self, office_state, monthly_plan) -> Dict[str, float]:
        """Get detailed breakdown of consultant revenue by level"""
        consultant_workforce = office_state.workforce.get('Consultant', {})
        consultant_utilization = monthly_plan.utilization_targets.get('Consultant', 0.85)
        working_hours = getattr(monthly_plan, 'working_hours_per_month', 160)
        
        breakdown = {}
        
        for level, people in consultant_workforce.items():
            active_count = len([p for p in people if p.is_active])
            level_price = monthly_plan.price_per_hour.get(level, 0.0)
            
            level_revenue = active_count * consultant_utilization * level_price * working_hours
            breakdown[f"Consultant {level} ({active_count} people @ ${level_price:.0f}/hr)"] = level_revenue
        
        return breakdown
    
    def _calculate_salary_costs_by_role(self, office_state, monthly_plan) -> Dict[str, float]:
        """Calculate salary costs broken down by role"""
        salary_breakdown = {}
        
        for role, role_workforce in office_state.workforce.items():
            role_salary_total = 0.0
            
            for level, people in role_workforce.items():
                active_count = len([p for p in people if p.is_active])
                level_salary = monthly_plan.salary_per_role.get(role, {}).get(level, 0.0)
                
                level_salary_cost = active_count * level_salary
                role_salary_total += level_salary_cost
            
            if role_salary_total > 0:
                salary_breakdown[f"{role} Salaries"] = role_salary_total
        
        return salary_breakdown
    
    def _count_billable_workforce(self, office_state) -> int:
        """Count billable workforce (consultants only in our business model)"""
        consultant_workforce = office_state.workforce.get('Consultant', {})
        return sum(len([p for p in people if p.is_active]) for people in consultant_workforce.values())
    
    def _calculate_percentages(self, pl_statement: MonthlyPLStatement):
        """Calculate percentage of revenue for all line items"""
        total_revenue = pl_statement.total_revenue
        
        if total_revenue == 0:
            return
        
        # Revenue section percentages
        for item in pl_statement.revenue_section.line_items:
            item.percentage_of_revenue = item.amount / total_revenue * 100
        pl_statement.revenue_section.percentage_of_revenue = 100.0
        
        # Cost section percentages
        for item in pl_statement.cost_section.line_items:
            item.percentage_of_revenue = item.amount / total_revenue * 100
        pl_statement.cost_section.percentage_of_revenue = pl_statement.total_costs / total_revenue * 100
        
        # Profit section percentages
        for item in pl_statement.profit_section.line_items:
            item.percentage_of_revenue = item.amount / total_revenue * 100
        pl_statement.profit_section.percentage_of_revenue = pl_statement.gross_profit / total_revenue * 100
    
    def _generate_trend_insights(self, statements: List[MonthlyPLStatement], 
                                revenue_growth: float, cost_growth: float) -> List[str]:
        """Generate insights from trend analysis"""
        insights = []
        
        if revenue_growth > 10:
            insights.append(f"Strong revenue growth of {revenue_growth:.1f}% over the period")
        elif revenue_growth < -10:
            insights.append(f"Revenue declining by {abs(revenue_growth):.1f}% over the period")
        
        if cost_growth > revenue_growth:
            insights.append("Costs growing faster than revenue - margin pressure")
        elif revenue_growth > cost_growth > 0:
            insights.append("Revenue outpacing cost growth - improving efficiency")
        
        # Profit margin trend analysis
        margins = [stmt.profit_margin for stmt in statements]
        if len(margins) > 1:
            margin_change = margins[-1] - margins[0]
            if margin_change > 5:
                insights.append(f"Profit margins improving by {margin_change:.1f} percentage points")
            elif margin_change < -5:
                insights.append(f"Profit margins declining by {abs(margin_change):.1f} percentage points")
        
        # Headcount efficiency
        if len(statements) > 1:
            first_rpu = statements[0].revenue_per_fte
            last_rpu = statements[-1].revenue_per_fte
            if last_rpu > first_rpu * 1.1:
                insights.append("Revenue per employee improving - increasing productivity")
        
        return insights
    
    def _section_to_dict(self, section: PLSection) -> Dict[str, Any]:
        """Convert P&L section to dictionary format"""
        return {
            "section_name": section.section_name,
            "section_total": section.section_total,
            "percentage_of_revenue": section.percentage_of_revenue,
            "line_items": [
                {
                    "item_name": item.item_name,
                    "amount": item.amount,
                    "percentage_of_revenue": item.percentage_of_revenue,
                    "notes": item.notes,
                    "breakdown": item.breakdown
                }
                for item in section.line_items
            ]
        }
    
    def _load_role_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Load role business definitions"""
        return {
            'Consultant': {
                'billable': True,
                'generates_revenue': True,
                'revenue_model': 'billable_hours'
            },
            'Sales': {
                'billable': False,
                'generates_revenue': False,
                'revenue_model': 'support_role'
            },
            'Recruitment': {
                'billable': False,
                'generates_revenue': False,
                'revenue_model': 'support_role'
            },
            'Operations': {
                'billable': False,
                'generates_revenue': False,
                'revenue_model': 'support_role'
            }
        }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    'PLStatementGeneratorV2',
    'MonthlyPLStatement',
    'PLTrendAnalysis',
    'PLSection',
    'PLLineItem'
]