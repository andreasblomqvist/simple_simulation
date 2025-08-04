"""
API routes for business plan management operations.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

from ..models.office import MonthlyBusinessPlan, MonthlyPlanEntry
from ..services.office_service import OfficeService, OfficeServiceError
from ..validators.office_validators import BusinessPlanValidator


router = APIRouter(prefix="/api/offices", tags=["business_plans"])


# Dependency to get office service
def get_office_service() -> OfficeService:
    return OfficeService()


# ================================================
# REQUEST/RESPONSE MODELS
# ================================================

class BusinessPlanCreateRequest(BaseModel):
    """Request model for creating a business plan."""
    year: int
    month: int
    entries: List[MonthlyPlanEntry]

    class Config:
        schema_extra = {
            "example": {
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


class BusinessPlanUpdateRequest(BaseModel):
    """Request model for updating a business plan."""
    entries: List[MonthlyPlanEntry]


class BulkUpdateRequest(BaseModel):
    """Request model for bulk updating business plans."""
    plans: List[BusinessPlanCreateRequest]


class BusinessPlanSummary(BaseModel):
    """Summary statistics for business plans."""
    total_plans: int
    years_covered: List[int]
    total_recruitment: int
    total_churn: int
    net_change: int
    revenue_potential: float
    salary_cost: float


class ValidationRequest(BaseModel):
    """Request model for business plan validation."""
    office_id: UUID
    plans: List[BusinessPlanCreateRequest]


# ================================================
# BUSINESS PLAN CRUD ENDPOINTS
# ================================================

@router.post("/{office_id}/business-plan", response_model=MonthlyBusinessPlan)
async def create_business_plan(
    office_id: UUID,
    request: BusinessPlanCreateRequest,
    office_service: OfficeService = Depends(get_office_service)
):
    """Create a monthly business plan for an office."""
    try:
        plan = MonthlyBusinessPlan(
            office_id=office_id,
            year=request.year,
            month=request.month,
            entries=request.entries
        )
        
        return await office_service.create_monthly_business_plan(plan)
    
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{office_id}/business-plan", response_model=List[MonthlyBusinessPlan])
async def get_business_plans(
    office_id: UUID,
    year: Optional[int] = Query(None, description="Filter by year"),
    office_service: OfficeService = Depends(get_office_service)
):
    """Get all business plans for an office."""
    try:
        return await office_service.get_business_plans_for_office(office_id, year)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{office_id}/business-plan/{year}/{month}", response_model=MonthlyBusinessPlan)
async def get_monthly_business_plan(
    office_id: UUID,
    year: int,
    month: int,
    office_service: OfficeService = Depends(get_office_service)
):
    """Get a specific monthly business plan."""
    try:
        plan = await office_service.get_monthly_business_plan(office_id, year, month)
        if not plan:
            raise HTTPException(status_code=404, detail="Business plan not found")
        
        return plan
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{office_id}/business-plan/{year}/{month}", response_model=MonthlyBusinessPlan)
async def update_business_plan(
    office_id: UUID,
    year: int,
    month: int,
    request: BusinessPlanUpdateRequest,
    office_service: OfficeService = Depends(get_office_service)
):
    """Update a monthly business plan."""
    try:
        plan = MonthlyBusinessPlan(
            office_id=office_id,
            year=year,
            month=month,
            entries=request.entries
        )
        
        result = await office_service.update_monthly_business_plan(office_id, year, month, plan)
        if not result:
            # Create new if doesn't exist
            result = await office_service.create_monthly_business_plan(plan)
        
        return result
    
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{office_id}/business-plan/bulk", response_model=List[MonthlyBusinessPlan])
async def bulk_update_business_plans(
    office_id: UUID,
    request: BulkUpdateRequest,
    office_service: OfficeService = Depends(get_office_service)
):
    """Bulk update multiple business plans for an office."""
    try:
        plans = []
        for plan_request in request.plans:
            plan = MonthlyBusinessPlan(
                office_id=office_id,
                year=plan_request.year,
                month=plan_request.month,
                entries=plan_request.entries
            )
            plans.append(plan)
        
        return await office_service.bulk_update_business_plans(office_id, plans)
    
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ================================================
# BUSINESS PLAN ANALYSIS ENDPOINTS
# ================================================

@router.get("/{office_id}/business-plan/summary", response_model=BusinessPlanSummary)
async def get_business_plan_summary(
    office_id: UUID,
    year: Optional[int] = Query(None, description="Filter by year"),
    office_service: OfficeService = Depends(get_office_service)
):
    """Get summary statistics for office business plans."""
    try:
        plans = await office_service.get_business_plans_for_office(office_id, year)
        
        if not plans:
            return BusinessPlanSummary(
                total_plans=0,
                years_covered=[],
                total_recruitment=0,
                total_churn=0,
                net_change=0,
                revenue_potential=0.0,
                salary_cost=0.0
            )
        
        years_covered = sorted(list(set(plan.year for plan in plans)))
        total_recruitment = sum(plan.get_total_recruitment() for plan in plans)
        total_churn = sum(plan.get_total_churn() for plan in plans)
        revenue_potential = sum(plan.get_revenue_potential() for plan in plans)
        salary_cost = sum(plan.get_total_salary_cost() for plan in plans)
        
        return BusinessPlanSummary(
            total_plans=len(plans),
            years_covered=years_covered,
            total_recruitment=total_recruitment,
            total_churn=total_churn,
            net_change=total_recruitment - total_churn,
            revenue_potential=revenue_potential,
            salary_cost=salary_cost
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{office_id}/business-plan/{year}/summary")
async def get_annual_plan_summary(
    office_id: UUID,
    year: int,
    office_service: OfficeService = Depends(get_office_service)
):
    """Get annual summary for a specific year."""
    try:
        office_summary = await office_service.get_office_summary(office_id)
        if not office_summary:
            raise HTTPException(status_code=404, detail="Office not found")
        
        annual_summary = office_summary.get_annual_summary(year)
        return annual_summary
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ================================================
# BUSINESS PLAN VALIDATION ENDPOINTS
# ================================================

@router.post("/{office_id}/business-plan/validate")
async def validate_business_plans(
    office_id: UUID,
    request: ValidationRequest,
    office_service: OfficeService = Depends(get_office_service)
):
    """Validate business plans for consistency and quality."""
    try:
        # Get office summary for context
        office_summary = await office_service.get_office_summary(office_id)
        if not office_summary:
            raise HTTPException(status_code=404, detail="Office not found")
        
        # Convert request plans to MonthlyBusinessPlan objects
        plans = []
        for plan_request in request.plans:
            plan = MonthlyBusinessPlan(
                office_id=office_id,
                year=plan_request.year,
                month=plan_request.month,
                entries=plan_request.entries
            )
            plans.append(plan)
        
        # Validate plans
        validation_errors = []
        
        # Validate individual plans
        for plan in plans:
            plan_errors = BusinessPlanValidator._validate_monthly_plan_quality(plan)
            if plan_errors:
                validation_errors.extend([
                    f"Month {plan.month}/{plan.year}: {error}" for error in plan_errors
                ])
        
        # Validate against workforce if available
        if office_summary.workforce_distribution:
            workforce_errors = BusinessPlanValidator._validate_workforce_business_plan_consistency(
                office_summary.workforce_distribution, plans
            )
            validation_errors.extend(workforce_errors)
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "plans_validated": len(plans)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ================================================
# BUSINESS PLAN TEMPLATES ENDPOINTS
# ================================================

@router.post("/{office_id}/business-plan/copy-from/{source_office_id}")
async def copy_business_plan_from_office(
    office_id: UUID,
    source_office_id: UUID,
    year: int = Query(..., description="Year to copy"),
    office_service: OfficeService = Depends(get_office_service)
):
    """Copy business plans from another office."""
    try:
        return await office_service.copy_business_plan_template(
            source_office_id, office_id, year
        )
    
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{office_id}/business-plan/generate-template")
async def generate_business_plan_template(
    office_id: UUID,
    year: int = Query(..., description="Year to generate template for"),
    base_recruitment: int = Query(0, description="Base monthly recruitment"),
    base_churn: int = Query(0, description="Base monthly churn"),
    office_service: OfficeService = Depends(get_office_service)
):
    """Generate a basic business plan template for an office."""
    try:
        # Get office and workforce information
        office_summary = await office_service.get_office_summary(office_id)
        if not office_summary:
            raise HTTPException(status_code=404, detail="Office not found")
        
        if not office_summary.workforce_distribution:
            raise HTTPException(
                status_code=400, 
                detail="Workforce distribution required to generate template"
            )
        
        # Generate template plans for all 12 months
        generated_plans = []
        
        for month in range(1, 13):
            entries = []
            
            # Create entries for each role/level in workforce
            for workforce_entry in office_summary.workforce_distribution.workforce:
                # Basic template values - could be made more sophisticated
                entry = MonthlyPlanEntry(
                    role=workforce_entry.role,
                    level=workforce_entry.level,
                    recruitment=base_recruitment,
                    churn=base_churn,
                    price=100.0,  # Default hourly rate
                    utr=0.75,     # Default utilization
                    salary=5000.0  # Default monthly salary
                )
                entries.append(entry)
            
            plan = MonthlyBusinessPlan(
                office_id=office_id,
                year=year,
                month=month,
                entries=entries
            )
            
            created_plan = await office_service.create_monthly_business_plan(plan)
            generated_plans.append(created_plan)
        
        return {
            "message": f"Generated business plan template for {year}",
            "plans_created": len(generated_plans),
            "plans": generated_plans
        }
    
    except HTTPException:
        raise
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ================================================
# COMPARISON ENDPOINTS
# ================================================

@router.get("/{office_id}/business-plan/compare/{other_office_id}")
async def compare_business_plans(
    office_id: UUID,
    other_office_id: UUID,
    year: int = Query(..., description="Year to compare"),
    office_service: OfficeService = Depends(get_office_service)
):
    """Compare business plans between two offices."""
    try:
        # Get plans for both offices
        office1_plans = await office_service.get_business_plans_for_office(office_id, year)
        office2_plans = await office_service.get_business_plans_for_office(other_office_id, year)
        
        # Get office names for response
        office1 = await office_service.get_office(office_id)
        office2 = await office_service.get_office(other_office_id)
        
        if not office1 or not office2:
            raise HTTPException(status_code=404, detail="One or both offices not found")
        
        # Calculate summaries
        office1_recruitment = sum(plan.get_total_recruitment() for plan in office1_plans)
        office1_churn = sum(plan.get_total_churn() for plan in office1_plans)
        office1_revenue = sum(plan.get_revenue_potential() for plan in office1_plans)
        
        office2_recruitment = sum(plan.get_total_recruitment() for plan in office2_plans)
        office2_churn = sum(plan.get_total_churn() for plan in office2_plans)
        office2_revenue = sum(plan.get_revenue_potential() for plan in office2_plans)
        
        return {
            "year": year,
            "office1": {
                "id": office_id,
                "name": office1.name,
                "plans_count": len(office1_plans),
                "total_recruitment": office1_recruitment,
                "total_churn": office1_churn,
                "net_change": office1_recruitment - office1_churn,
                "revenue_potential": office1_revenue
            },
            "office2": {
                "id": other_office_id,
                "name": office2.name,
                "plans_count": len(office2_plans),
                "total_recruitment": office2_recruitment,
                "total_churn": office2_churn,
                "net_change": office2_recruitment - office2_churn,
                "revenue_potential": office2_revenue
            },
            "differences": {
                "recruitment_diff": office1_recruitment - office2_recruitment,
                "churn_diff": office1_churn - office2_churn,
                "net_change_diff": (office1_recruitment - office1_churn) - (office2_recruitment - office2_churn),
                "revenue_diff": office1_revenue - office2_revenue
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")