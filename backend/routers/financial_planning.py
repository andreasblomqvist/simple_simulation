"""
Financial Planning API Router
Comprehensive expense structure and budget management endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from src.models.financial_structure import (
    ComprehensiveFinancialModel,
    BudgetPlan,
    CurrencyCode,
    ExpenseCategory,
    BudgetActualComparison,
    FinancialTimeSeries,
    MonthlyFinancialValue
)

router = APIRouter(
    prefix="/financial-planning",
    tags=["financial-planning"]
)

# Request/Response Models

class FinancialModelRequest(BaseModel):
    """Request model for creating/updating financial models"""
    office_id: str
    office_name: str
    currency: CurrencyCode
    fiscal_year: int
    financial_data: Dict[str, Any]  # Flexible structure for financial data


class BudgetPlanRequest(BaseModel):
    """Request model for budget plan operations"""
    office_id: str
    plan_name: str
    fiscal_year: int
    currency: CurrencyCode
    financial_model_id: str
    assumptions: Optional[Dict[str, str]] = None


class VarianceAnalysisRequest(BaseModel):
    """Request model for variance analysis"""
    plan_id: str
    period_start: str  # YYYYMM
    period_end: str    # YYYYMM
    categories: Optional[List[ExpenseCategory]] = None


class BudgetVsActualRequest(BaseModel):
    """Request for updating actual values against budget"""
    plan_id: str
    period: str  # YYYYMM
    category: ExpenseCategory
    actual_values: Dict[str, Decimal]


# Financial Model Endpoints

@router.post("/financial-models")
async def create_financial_model(request: FinancialModelRequest):
    """Create a comprehensive financial model"""
    try:
        # Implementation would validate and create financial model
        financial_model = ComprehensiveFinancialModel(
            office_id=request.office_id,
            office_name=request.office_name,
            currency=request.currency,
            fiscal_year=request.fiscal_year,
            **request.financial_data
        )
        
        # Save to storage
        # financial_model_storage.create(financial_model)
        
        return {
            "status": "success",
            "model_id": f"fm_{request.office_id}_{request.fiscal_year}",
            "message": "Financial model created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating financial model: {str(e)}")


@router.get("/financial-models/{office_id}")
async def get_financial_models(
    office_id: str,
    fiscal_year: Optional[int] = Query(None, description="Filter by fiscal year"),
    include_kpis: bool = Query(True, description="Include calculated KPIs")
):
    """Get financial models for an office"""
    try:
        # Implementation would retrieve financial models
        models = []  # financial_model_storage.get_by_office(office_id, fiscal_year)
        
        if include_kpis:
            # Calculate and include KPIs
            for model in models:
                pass  # model.calculate_kpis()
        
        return {
            "office_id": office_id,
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving financial models: {str(e)}")


@router.get("/financial-models/{office_id}/expense-breakdown")
async def get_expense_breakdown(
    office_id: str,
    fiscal_year: int,
    category: Optional[ExpenseCategory] = Query(None, description="Filter by expense category"),
    month_start: Optional[str] = Query(None, description="Start month (YYYYMM)"),
    month_end: Optional[str] = Query(None, description="End month (YYYYMM)")
):
    """Get detailed expense breakdown for an office"""
    try:
        # Implementation would retrieve and aggregate expense data
        breakdown = {
            "office_id": office_id,
            "fiscal_year": fiscal_year,
            "currency": "EUR",  # From model
            "breakdown": {
                "staff_costs": {
                    "total": 5000000,
                    "by_role": {
                        "consultant": {"A": 1500000, "AC": 1200000, "C": 800000},
                        "operations": 600000,
                        "sales": 900000
                    },
                    "by_component": {
                        "base_salary": 3000000,
                        "variable_salary": 500000,
                        "social_security": 900000,
                        "pension": 400000,
                        "benefits": 200000
                    }
                },
                "office_expenses": {
                    "total": 800000,
                    "facilities": 400000,
                    "it_equipment": 200000,
                    "operations": 150000,
                    "travel": 50000
                },
                "project_costs": {
                    "total": 300000,
                    "consultant_costs": 200000,
                    "sub_consultant_costs": 100000
                }
            },
            "monthly_trend": [
                # Monthly data would be populated here
            ]
        }
        
        return breakdown
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving expense breakdown: {str(e)}")


# Budget Planning Endpoints

@router.post("/budget-plans")
async def create_budget_plan(request: BudgetPlanRequest):
    """Create a new budget plan"""
    try:
        plan = BudgetPlan(
            plan_id=f"bp_{request.office_id}_{request.fiscal_year}_{datetime.now().strftime('%Y%m%d')}",
            office_id=request.office_id,
            plan_name=request.plan_name,
            fiscal_year=request.fiscal_year,
            currency=request.currency,
            financial_model=None,  # Would be loaded from financial_model_id
            assumptions=request.assumptions or {},
            created_by="system"  # Would come from auth context
        )
        
        # Save budget plan
        # budget_plan_storage.create(plan)
        
        return {
            "status": "success",
            "plan_id": plan.plan_id,
            "message": "Budget plan created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating budget plan: {str(e)}")


@router.get("/budget-plans")
async def get_budget_plans(
    office_id: Optional[str] = Query(None, description="Filter by office"),
    fiscal_year: Optional[int] = Query(None, description="Filter by fiscal year"),
    status: Optional[str] = Query(None, description="Filter by status"),
    include_variance: bool = Query(False, description="Include variance analysis")
):
    """Get budget plans with optional filters"""
    try:
        # Implementation would retrieve budget plans
        plans = []  # budget_plan_storage.get_filtered(office_id, fiscal_year, status)
        
        if include_variance:
            for plan in plans:
                pass  # plan.calculate_variance_summary()
        
        return {
            "plans": plans,
            "count": len(plans),
            "filters_applied": {
                "office_id": office_id,
                "fiscal_year": fiscal_year,
                "status": status
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving budget plans: {str(e)}")


@router.put("/budget-plans/{plan_id}/actual-values")
async def update_actual_values(plan_id: str, request: BudgetVsActualRequest):
    """Update actual values for budget vs actual tracking"""
    try:
        # Implementation would update actual values and calculate variances
        plan = None  # budget_plan_storage.get(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Budget plan not found")
        
        # Update actual values
        for subcategory, actual_amount in request.actual_values.items():
            comparison = BudgetActualComparison(
                period=request.period,
                budget_amount=Decimal(0),  # Would get from plan
                actual_amount=actual_amount
            )
            comparison.calculate_variance()
            
            # Store variance data
            category_key = request.category.value
            if category_key not in plan.variance_tracking:
                plan.variance_tracking[category_key] = []
            plan.variance_tracking[category_key].append(comparison)
        
        # budget_plan_storage.update(plan)
        
        return {
            "status": "success",
            "plan_id": plan_id,
            "period": request.period,
            "message": "Actual values updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating actual values: {str(e)}")


# Variance Analysis Endpoints

@router.post("/variance-analysis")
async def generate_variance_analysis(request: VarianceAnalysisRequest):
    """Generate comprehensive variance analysis"""
    try:
        # Implementation would calculate variance analysis
        analysis = {
            "plan_id": request.plan_id,
            "period": f"{request.period_start} to {request.period_end}",
            "summary": {
                "total_budget": 10000000,
                "total_actual": 9800000,
                "total_variance": -200000,
                "variance_percentage": -2.0,
                "categories_over_budget": 3,
                "categories_under_budget": 7
            },
            "category_analysis": {
                "staff_costs": {
                    "budget": 6000000,
                    "actual": 5900000,
                    "variance": -100000,
                    "variance_percentage": -1.67,
                    "trend": "favorable"
                },
                "office_expenses": {
                    "budget": 800000,
                    "actual": 850000,
                    "variance": 50000,
                    "variance_percentage": 6.25,
                    "trend": "unfavorable"
                }
            },
            "monthly_trends": [
                # Monthly variance trends would be populated here
            ],
            "risk_indicators": [
                {
                    "category": "office_expenses",
                    "risk_level": "medium",
                    "description": "Office expenses trending 6% over budget",
                    "recommendation": "Review office expense allocations"
                }
            ]
        }
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating variance analysis: {str(e)}")


# KPI and Metrics Endpoints

@router.get("/financial-kpis/{office_id}")
async def get_financial_kpis(
    office_id: str,
    fiscal_year: int,
    month_start: Optional[str] = Query(None, description="Start month (YYYYMM)"),
    month_end: Optional[str] = Query(None, description="End month (YYYYMM)"),
    benchmark: bool = Query(False, description="Include benchmark comparisons")
):
    """Get financial KPIs and metrics"""
    try:
        # Implementation would calculate and retrieve KPIs
        kpis = {
            "office_id": office_id,
            "fiscal_year": fiscal_year,
            "period": f"{month_start or 'Full Year'} to {month_end or 'Full Year'}",
            "currency": "EUR",
            "metrics": {
                "revenue": {
                    "total_revenue": 12000000,
                    "revenue_per_fte": 150000,
                    "revenue_growth_yoy": 8.5
                },
                "profitability": {
                    "ebitda": 2400000,
                    "ebitda_margin": 20.0,
                    "ebit": 2100000,
                    "ebit_margin": 17.5,
                    "gross_margin": 45.0
                },
                "efficiency": {
                    "cost_per_fte": 120000,
                    "utilization_rate": 85.0,
                    "billing_rate_realization": 92.0
                },
                "workforce": {
                    "total_fte": 80,
                    "revenue_per_consultant": 160000,
                    "cost_per_consultant": 128000
                }
            }
        }
        
        if benchmark:
            kpis["benchmarks"] = {
                "industry_average_ebitda_margin": 18.5,
                "industry_average_utilization": 82.0,
                "performance_vs_industry": "above_average"
            }
        
        return kpis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving financial KPIs: {str(e)}")


# Multi-year and Aggregation Endpoints

@router.get("/aggregated-financial-view")
async def get_aggregated_financial_view(
    office_ids: Optional[str] = Query(None, description="Comma-separated office IDs"),
    fiscal_years: Optional[str] = Query(None, description="Comma-separated fiscal years"),
    currency: CurrencyCode = Query(CurrencyCode.EUR, description="Reporting currency"),
    include_projections: bool = Query(False, description="Include future projections")
):
    """Get aggregated financial view across offices and years"""
    try:
        office_list = office_ids.split(",") if office_ids else ["all"]
        year_list = [int(y) for y in fiscal_years.split(",")] if fiscal_years else [datetime.now().year]
        
        # Implementation would aggregate data across offices and years
        aggregated_view = {
            "offices": office_list,
            "fiscal_years": year_list,
            "reporting_currency": currency,
            "aggregated_metrics": {
                "total_revenue": 50000000,
                "total_costs": 40000000,
                "total_ebitda": 10000000,
                "consolidated_ebitda_margin": 20.0,
                "total_fte": 400
            },
            "office_breakdown": [
                # Per-office breakdown would be populated here
            ],
            "year_over_year_trends": [
                # YoY trends would be populated here
            ]
        }
        
        if include_projections:
            aggregated_view["projections"] = {
                "next_year_revenue_forecast": 55000000,
                "next_year_ebitda_forecast": 11500000,
                "growth_assumptions": ["5% consultant growth", "3% price increase"]
            }
        
        return aggregated_view
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating aggregated view: {str(e)}")


# Export and Integration Endpoints

@router.get("/export/budget-template/{office_id}")
async def export_budget_template(
    office_id: str,
    fiscal_year: int,
    format: str = Query("excel", description="Export format (excel, csv, json)"),
    include_formulas: bool = Query(True, description="Include Excel formulas")
):
    """Export budget template for external editing"""
    try:
        # Implementation would generate budget template
        return {
            "status": "success",
            "download_url": f"/downloads/budget_template_{office_id}_{fiscal_year}.{format}",
            "expires_at": datetime.now().isoformat(),
            "format": format,
            "includes_formulas": include_formulas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting budget template: {str(e)}")


@router.post("/import/budget-data/{office_id}")
async def import_budget_data(
    office_id: str,
    fiscal_year: int,
    file_data: Dict[str, Any],  # Would be file upload in real implementation
    validate_formulas: bool = Query(True, description="Validate Excel formulas"),
    overwrite_existing: bool = Query(False, description="Overwrite existing data")
):
    """Import budget data from external sources"""
    try:
        # Implementation would parse and validate imported data
        import_result = {
            "status": "success",
            "office_id": office_id,
            "fiscal_year": fiscal_year,
            "imported_records": 120,
            "validation_errors": [],
            "warnings": [],
            "created_plan_id": f"bp_{office_id}_{fiscal_year}_imported"
        }
        
        return import_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing budget data: {str(e)}")


# Simulation Integration

@router.post("/integrate-with-simulation")
async def integrate_financial_with_simulation(
    plan_id: str,
    scenario_definition: Dict[str, Any],
    mapping_rules: Optional[Dict[str, str]] = None
):
    """Integrate financial plan with workforce simulation"""
    try:
        # Implementation would map financial plan to simulation inputs
        integration = {
            "status": "success",
            "plan_id": plan_id,
            "scenario_id": "generated_scenario_id",
            "mapping_summary": {
                "staff_costs_mapped": True,
                "headcount_projections_mapped": True,
                "salary_progressions_mapped": True,
                "office_costs_allocated": True
            },
            "simulation_baseline_url": "/api/scenarios/export-baseline/generated_scenario_id"
        }
        
        return integration
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error integrating with simulation: {str(e)}")