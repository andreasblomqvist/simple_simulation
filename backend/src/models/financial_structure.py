"""
Financial Structure Models for SimpleSim
Mirrors detailed expense structure from Planacy budget system
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum
from decimal import Decimal


class CurrencyCode(str, Enum):
    """Supported currency codes"""
    USD = "USD"
    EUR = "EUR"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    GBP = "GBP"
    CHF = "CHF"


class ExpenseCategory(str, Enum):
    """Major expense categories"""
    RECRUITMENT_BUDGET = "recruitment_budget"
    SALES = "sales"
    PROJECT_COSTS = "project_costs" 
    OFFICE_EXPENSES = "office_expenses"
    STAFF_COSTS = "staff_costs"
    DEPRECIATION = "depreciation"


class MonthlyFinancialValue(BaseModel):
    """Financial value with currency and monthly breakdown"""
    amount: Decimal = Field(..., description="Amount in local currency")
    currency: CurrencyCode = Field(..., description="Currency code")
    month_key: str = Field(..., description="YYYYMM format")
    
    @field_validator('month_key')
    @classmethod
    def validate_month_format(cls, v):
        if not (len(v) == 6 and v.isdigit()):
            raise ValueError(f'Month key must be in YYYYMM format: {v}')
        year = int(v[:4])
        month = int(v[4:6])
        if not (2020 <= year <= 2040):
            raise ValueError(f'Year must be between 2020 and 2040: {year}')
        if not (1 <= month <= 12):
            raise ValueError(f'Month must be between 1 and 12: {month}')
        return v


class FinancialTimeSeries(BaseModel):
    """Time series of financial values"""
    values: Dict[str, MonthlyFinancialValue] = Field(..., description="Monthly values by YYYYMM key")
    currency: CurrencyCode = Field(..., description="Base currency")
    
    def get_total(self) -> Decimal:
        """Calculate total across all months"""
        return sum(val.amount for val in self.values.values())
    
    def get_monthly_average(self) -> Decimal:
        """Calculate monthly average"""
        if not self.values:
            return Decimal(0)
        return self.get_total() / len(self.values)


# Staff Cost Structure - Detailed Salary Breakdown

class SalaryComponents(BaseModel):
    """Detailed salary cost breakdown"""
    base_salary: FinancialTimeSeries = Field(..., description="Base monthly salary")
    variable_salary: FinancialTimeSeries = Field(..., description="Variable/bonus components")
    social_security: FinancialTimeSeries = Field(..., description="Employer social security")
    pension_contribution: FinancialTimeSeries = Field(..., description="Pension contributions")
    insurance_benefits: FinancialTimeSeries = Field(..., description="Health/life insurance")
    overtime_allowance: FinancialTimeSeries = Field(..., description="Overtime payments")
    bonus_payments: FinancialTimeSeries = Field(..., description="Annual bonus allocations")
    stock_options: FinancialTimeSeries = Field(..., description="Stock option valuations")
    other_benefits: FinancialTimeSeries = Field(..., description="Other benefit costs")
    
    def get_total_compensation(self) -> FinancialTimeSeries:
        """Calculate total compensation across all components"""
        total_values = {}
        all_months = set()
        
        # Collect all month keys
        for component in [self.base_salary, self.variable_salary, self.social_security, 
                         self.pension_contribution, self.insurance_benefits, self.overtime_allowance,
                         self.bonus_payments, self.stock_options, self.other_benefits]:
            all_months.update(component.values.keys())
        
        # Sum all components for each month
        for month_key in all_months:
            total_amount = Decimal(0)
            currency = self.base_salary.currency  # Use base currency
            
            for component in [self.base_salary, self.variable_salary, self.social_security, 
                             self.pension_contribution, self.insurance_benefits, self.overtime_allowance,
                             self.bonus_payments, self.stock_options, self.other_benefits]:
                if month_key in component.values:
                    total_amount += component.values[month_key].amount
            
            total_values[month_key] = MonthlyFinancialValue(
                amount=total_amount,
                currency=currency,
                month_key=month_key
            )
        
        return FinancialTimeSeries(
            values=total_values,
            currency=self.base_salary.currency
        )


class StaffCostsByRole(BaseModel):
    """Staff costs breakdown by role and level"""
    role_name: str = Field(..., description="Role name (e.g., Consultant, Operations)")
    level_name: Optional[str] = Field(None, description="Level name (e.g., A, AC, C)")
    headcount: FinancialTimeSeries = Field(..., description="FTE count over time")
    salary_components: SalaryComponents = Field(..., description="Detailed salary breakdown")
    recruitment_costs: FinancialTimeSeries = Field(..., description="Recruitment and onboarding costs")
    training_costs: FinancialTimeSeries = Field(..., description="Training and development costs")
    equipment_costs: FinancialTimeSeries = Field(..., description="Equipment and tool costs")


# Office Expense Structure

class OfficeExpenseItem(BaseModel):
    """Individual office expense item"""
    category: str = Field(..., description="Expense category")
    subcategory: Optional[str] = Field(None, description="Expense subcategory")
    description: str = Field(..., description="Expense description")
    costs: FinancialTimeSeries = Field(..., description="Monthly cost breakdown")
    is_fixed: bool = Field(True, description="Whether expense is fixed or variable")
    allocation_method: str = Field("direct", description="Cost allocation method (direct, headcount, revenue)")


class OfficeExpenses(BaseModel):
    """Complete office expense structure"""
    # Facilities & Infrastructure
    office_rent: OfficeExpenseItem = Field(..., description="Office rent and utilities")
    office_utilities: OfficeExpenseItem = Field(..., description="Electricity, heating, internet")
    cleaning_services: OfficeExpenseItem = Field(..., description="Cleaning and maintenance")
    security_services: OfficeExpenseItem = Field(..., description="Security and access control")
    
    # IT & Equipment
    it_infrastructure: OfficeExpenseItem = Field(..., description="Servers, network equipment")
    software_licenses: OfficeExpenseItem = Field(..., description="Software and SaaS subscriptions")
    hardware_depreciation: OfficeExpenseItem = Field(..., description="Computer and equipment depreciation")
    
    # Operations
    office_supplies: OfficeExpenseItem = Field(..., description="General office supplies")
    phone_communications: OfficeExpenseItem = Field(..., description="Phone and communication costs")
    mail_shipping: OfficeExpenseItem = Field(..., description="Mail and shipping costs")
    
    # People & Culture
    conference_costs: OfficeExpenseItem = Field(..., description="Conferences and events")
    education_training: OfficeExpenseItem = Field(..., description="Education and training")
    team_events: OfficeExpenseItem = Field(..., description="Team building and social events")
    external_representation: OfficeExpenseItem = Field(..., description="Client entertainment")
    
    # Professional Services
    legal_services: OfficeExpenseItem = Field(..., description="Legal and compliance costs")
    accounting_audit: OfficeExpenseItem = Field(..., description="Accounting and audit fees")
    consulting_services: OfficeExpenseItem = Field(..., description="External consulting")
    
    # Travel & Transport
    travel_expenses: OfficeExpenseItem = Field(..., description="Business travel costs")
    local_transport: OfficeExpenseItem = Field(..., description="Local transportation")
    
    # Insurance & Risk
    business_insurance: OfficeExpenseItem = Field(..., description="Business insurance premiums")
    professional_liability: OfficeExpenseItem = Field(..., description="Professional liability insurance")
    
    # Other
    bank_charges: OfficeExpenseItem = Field(..., description="Banking and financial charges")
    miscellaneous: OfficeExpenseItem = Field(..., description="Other miscellaneous expenses")


# Revenue Structure

class RevenueStream(BaseModel):
    """Individual revenue stream"""
    stream_name: str = Field(..., description="Revenue stream name")
    category: str = Field(..., description="Revenue category (consulting, products, etc.)")
    revenue: FinancialTimeSeries = Field(..., description="Monthly revenue")
    client_type: str = Field(..., description="Client type (enterprise, sme, government)")
    service_type: str = Field(..., description="Service type (consulting, implementation, etc.)")


class ProjectCosts(BaseModel):
    """Project-related costs"""
    consultant_project_costs: FinancialTimeSeries = Field(..., description="Internal consultant costs")
    sub_consultant_costs: FinancialTimeSeries = Field(..., description="External consultant costs")
    project_materials: FinancialTimeSeries = Field(..., description="Project materials and supplies")
    project_travel: FinancialTimeSeries = Field(..., description="Project-specific travel")
    project_software: FinancialTimeSeries = Field(..., description="Project-specific software/tools")
    client_expenses: FinancialTimeSeries = Field(..., description="Reimbursable client expenses")


class SalesMetrics(BaseModel):
    """Sales performance and costs"""
    gross_sales: FinancialTimeSeries = Field(..., description="Total gross sales")
    sales_adjustments: FinancialTimeSeries = Field(..., description="Returns, discounts, adjustments")
    net_sales: FinancialTimeSeries = Field(..., description="Net sales after adjustments")
    
    # Sales costs
    sales_compensation: FinancialTimeSeries = Field(..., description="Sales team compensation")
    sales_commissions: FinancialTimeSeries = Field(..., description="Sales commissions")
    marketing_costs: FinancialTimeSeries = Field(..., description="Marketing and advertising")
    client_acquisition: FinancialTimeSeries = Field(..., description="Client acquisition costs")


# Financial Metrics & KPIs

class FinancialKPIs(BaseModel):
    """Key financial performance indicators"""
    ebitda: FinancialTimeSeries = Field(..., description="Earnings Before Interest, Tax, Depreciation, Amortization")
    ebit: FinancialTimeSeries = Field(..., description="Earnings Before Interest and Tax")
    ebitda_margin: FinancialTimeSeries = Field(..., description="EBITDA margin percentage")
    revenue_per_fte: FinancialTimeSeries = Field(..., description="Revenue per full-time employee")
    cost_per_fte: FinancialTimeSeries = Field(..., description="Total cost per full-time employee")
    utilization_rate: FinancialTimeSeries = Field(..., description="Billable utilization rate")
    gross_margin: FinancialTimeSeries = Field(..., description="Gross profit margin")
    operating_margin: FinancialTimeSeries = Field(..., description="Operating profit margin")


# Complete Financial Model

class ComprehensiveFinancialModel(BaseModel):
    """Complete financial model for an office or organization"""
    office_id: str = Field(..., description="Office identifier")
    office_name: str = Field(..., description="Office name")
    currency: CurrencyCode = Field(..., description="Reporting currency")
    fiscal_year: int = Field(..., description="Fiscal year")
    
    # Revenue
    revenue_streams: List[RevenueStream] = Field(..., description="All revenue streams")
    sales_metrics: SalesMetrics = Field(..., description="Sales performance metrics")
    
    # Costs
    staff_costs: List[StaffCostsByRole] = Field(..., description="Staff costs by role/level")
    office_expenses: OfficeExpenses = Field(..., description="Office operating expenses")
    project_costs: ProjectCosts = Field(..., description="Project-related costs")
    
    # Depreciation
    depreciation_it: FinancialTimeSeries = Field(..., description="IT equipment depreciation")
    depreciation_furniture: FinancialTimeSeries = Field(..., description="Furniture depreciation")
    depreciation_other: FinancialTimeSeries = Field(..., description="Other asset depreciation")
    
    # Financial Performance
    kpis: FinancialKPIs = Field(..., description="Calculated financial KPIs")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = Field("1.0", description="Model version")
    
    def calculate_total_revenue(self) -> FinancialTimeSeries:
        """Calculate total revenue across all streams"""
        # Implementation would sum all revenue streams
        pass
    
    def calculate_total_costs(self) -> FinancialTimeSeries:
        """Calculate total costs across all categories"""
        # Implementation would sum all cost categories
        pass
    
    def calculate_ebitda(self) -> FinancialTimeSeries:
        """Calculate EBITDA: Revenue - Operating Expenses (before depreciation)"""
        # Implementation would calculate EBITDA
        pass


# Budget vs Actual Tracking

class BudgetActualComparison(BaseModel):
    """Budget vs actual performance tracking"""
    period: str = Field(..., description="Period identifier (YYYYMM)")
    budget_amount: Decimal = Field(..., description="Budgeted amount")
    actual_amount: Optional[Decimal] = Field(None, description="Actual amount")
    variance_amount: Optional[Decimal] = Field(None, description="Variance (actual - budget)")
    variance_percentage: Optional[float] = Field(None, description="Variance percentage")
    
    def calculate_variance(self):
        """Calculate variance metrics"""
        if self.actual_amount is not None:
            self.variance_amount = self.actual_amount - self.budget_amount
            if self.budget_amount != 0:
                self.variance_percentage = float(self.variance_amount / self.budget_amount * 100)


class BudgetPlan(BaseModel):
    """Complete budget plan with variance tracking"""
    plan_id: str = Field(..., description="Unique plan identifier")
    office_id: str = Field(..., description="Office identifier")
    plan_name: str = Field(..., description="Budget plan name")
    fiscal_year: int = Field(..., description="Fiscal year")
    currency: CurrencyCode = Field(..., description="Planning currency")
    
    # Budget data
    financial_model: ComprehensiveFinancialModel = Field(..., description="Complete financial model")
    
    # Variance tracking
    variance_tracking: Dict[str, List[BudgetActualComparison]] = Field(
        default_factory=dict, 
        description="Variance tracking by expense category"
    )
    
    # Planning parameters
    assumptions: Dict[str, str] = Field(default_factory=dict, description="Planning assumptions")
    scenarios: List[str] = Field(default_factory=list, description="Linked scenario IDs")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(..., description="User who created the plan")
    status: str = Field("draft", description="Plan status (draft, approved, active)")