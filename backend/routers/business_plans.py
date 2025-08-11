from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.services.business_plan_storage import business_plan_storage

router = APIRouter(
    prefix="/business-plans",
    tags=["business-plans"]
)

class MonthlyPlanEntry(BaseModel):
    role: str
    level: str
    # Workforce fields
    recruitment: float = 0
    churn: float = 0
    # Net Sales fields
    consultant_time: float = 160
    planned_absence: float = 20
    unplanned_absence: float = 10
    vacation_withdrawal: float = 0
    vacation: float = 16
    invoiced_time: float = 110
    average_price: float = 1200
    # Operating Costs - Expenses
    client_loss: float = 0
    education: float = 10000
    external_representation: float = 5000
    external_services: float = 15000
    internal_representation: float = 3000
    it_related_staff: float = 20000
    office_related: float = 5000
    office_rent: float = 50000
    # Operating Costs - Salaries & Related
    salary: float = 65000
    variable_salary: float = 0
    social_security: float = 0
    other_expenses: float = 5000
    pension: float = 0
    # Legacy fields for compatibility
    price: float = 1200  # Now maps to average_price
    utr: float = 0.75    # Calculated from available/invoiced time

class MonthlyBusinessPlan(BaseModel):
    id: str
    office_id: str
    year: int
    month: int
    entries: List[MonthlyPlanEntry]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@router.get("")
def get_business_plans(office_id: Optional[str] = None, year: Optional[int] = None):
    """Get business plans with optional filters"""
    return business_plan_storage.get_plans(office_id=office_id, year=year)

@router.get("/aggregated")
def get_aggregated_business_plans(
    year: Optional[int] = None,
    office_ids: Optional[str] = None,
    journey: Optional[str] = None
):
    """Get aggregated business plans across all or selected offices
    
    Args:
        year: Year to filter by (optional)
        office_ids: Comma-separated list of office IDs to include (optional, default: all)
        journey: Filter by office journey type (emerging, established, mature) (optional)
    """
    try:
        result = business_plan_storage.get_aggregated_plans(
            year=year,
            office_ids=office_ids.split(",") if office_ids else None,
            journey=journey
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error aggregating business plans: {str(e)}")

@router.get("/export-baseline")
def export_business_plan_baseline(
    office_id: str,
    year: int,
    start_month: int = 1,
    end_month: int = 12
):
    """Export business plan data as simulation baseline format
    
    Args:
        office_id: Office ID to export
        year: Year to export  
        start_month: Starting month (1-12)
        end_month: Ending month (1-12)
    """
    try:
        baseline = business_plan_storage.export_as_simulation_baseline(
            office_id=office_id,
            year=year,
            start_month=start_month,
            end_month=end_month
        )
        return baseline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting baseline: {str(e)}")

@router.get("/aggregated/export-baseline")
def export_aggregated_baseline(
    year: int,
    office_ids: Optional[str] = None,
    journey: Optional[str] = None,
    start_month: int = 1,
    end_month: int = 12
):
    """Export aggregated business plan data as simulation baseline format
    
    Args:
        year: Year to export
        office_ids: Comma-separated list of office IDs (optional, default: all)
        journey: Filter by office journey type (optional)
        start_month: Starting month (1-12)
        end_month: Ending month (1-12)
    """
    try:
        baseline = business_plan_storage.export_aggregated_as_simulation_baseline(
            year=year,
            office_ids=office_ids.split(",") if office_ids else None,
            journey=journey,
            start_month=start_month,
            end_month=end_month
        )
        return baseline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting aggregated baseline: {str(e)}")

@router.get("/{plan_id}")
def get_business_plan(plan_id: str):
    """Get a specific business plan by ID"""
    plan = business_plan_storage.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Business plan not found")
    return plan

@router.post("")
def create_business_plan(plan_data: dict):
    """Create a new business plan"""
    return business_plan_storage.create_plan(plan_data)

@router.put("/{plan_id}")
def update_business_plan(plan_id: str, plan_data: dict):
    """Update an existing business plan"""
    plan = business_plan_storage.update_plan(plan_id, plan_data)
    if not plan:
        raise HTTPException(status_code=404, detail="Business plan not found")
    return plan

@router.delete("/{plan_id}")
def delete_business_plan(plan_id: str):
    """Delete a business plan or yearly business plan (all monthly plans for office-year)"""
    # Check if this is a yearly plan ID (office_id-year format)
    if '-' in plan_id and len(plan_id.split('-')) >= 2:
        parts = plan_id.split('-')
        # Try to parse the last part as a year
        try:
            year = int(parts[-1])
            office_id = '-'.join(parts[:-1])  # Rejoin in case office has hyphens
            
            # Get all monthly plans for this office and year
            monthly_plans = business_plan_storage.get_plans(office_id=office_id, year=year)
            if not monthly_plans:
                raise HTTPException(status_code=404, detail="Business plan not found")
            
            # Delete all monthly plans
            deleted_count = 0
            for plan in monthly_plans:
                if business_plan_storage.delete_plan(plan['id']):
                    deleted_count += 1
            
            return {"message": f"Deleted {deleted_count} monthly plans for {office_id} {year}"}
        except ValueError:
            # Not a year, treat as regular plan ID
            pass
    
    # Regular single plan deletion
    success = business_plan_storage.delete_plan(plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Business plan not found")
    return {"message": f"Business plan {plan_id} deleted"}

@router.get("/office/{office_id}/summary")
def get_office_business_plan_summary(office_id: str, year: Optional[int] = None):
    """Get complete business plan summary for an office"""
    return business_plan_storage.get_office_summary(office_id=office_id, year=year) 