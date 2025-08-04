"""
API routes for office management operations.
"""
from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

from ..models.office import (
    OfficeConfig, WorkforceDistribution, MonthlyBusinessPlan,
    ProgressionConfig, OfficeBusinessPlanSummary, OfficeJourney
)
from ..services.office_service import OfficeService, OfficeServiceError
from ..validators.office_validators import validate_complete_office_setup


router = APIRouter(prefix="/api/offices", tags=["offices"])


# Dependency to get office service
def get_office_service() -> OfficeService:
    return OfficeService()


# ================================================
# REQUEST/RESPONSE MODELS
# ================================================

class OfficeCreateRequest(BaseModel):
    """Request model for creating an office."""
    name: str
    journey: OfficeJourney
    timezone: str = "UTC"
    economic_parameters: Optional[Dict] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Stockholm",
                "journey": "mature",
                "timezone": "Europe/Stockholm",
                "economic_parameters": {
                    "cost_of_living": 1.2,
                    "market_multiplier": 1.1,
                    "tax_rate": 0.25
                }
            }
        }


class OfficeUpdateRequest(BaseModel):
    """Request model for updating an office."""
    name: Optional[str] = None
    journey: Optional[OfficeJourney] = None
    timezone: Optional[str] = None
    economic_parameters: Optional[Dict] = None


class ValidationResponse(BaseModel):
    """Response model for validation results."""
    errors: List[str]
    warnings: List[str]
    info: List[str]


class OfficeListResponse(BaseModel):
    """Response model for office list."""
    offices: List[OfficeConfig]
    total: int
    by_journey: Dict[str, int]


# ================================================
# OFFICE CONFIGURATION ENDPOINTS
# ================================================

@router.post("/", response_model=OfficeConfig)
async def create_office(
    request: OfficeCreateRequest,
    office_service: OfficeService = Depends(get_office_service)
):
    """Create a new office configuration."""
    try:
        # Convert request to office config
        office_config = OfficeConfig(
            name=request.name,
            journey=request.journey,
            timezone=request.timezone,
            economic_parameters=request.economic_parameters or {}
        )
        
        return await office_service.create_office(office_config)
    
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=OfficeListResponse)
async def list_offices(
    journey: Optional[OfficeJourney] = Query(None, description="Filter by office journey"),
    office_service: OfficeService = Depends(get_office_service)
):
    """List all offices, optionally filtered by journey."""
    try:
        offices = await office_service.list_offices(journey)
        
        # Count by journey
        by_journey = {"emerging": 0, "established": 0, "mature": 0}
        for office in offices:
            by_journey[office.journey] += 1
        
        return OfficeListResponse(
            offices=offices,
            total=len(offices),
            by_journey=by_journey
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/by-journey", response_model=Dict[str, List[OfficeConfig]])
async def get_offices_by_journey(
    office_service: OfficeService = Depends(get_office_service)
):
    """Get offices grouped by journey."""
    try:
        return await office_service.get_offices_by_journey()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{office_id}", response_model=OfficeConfig)
async def get_office(
    office_id: UUID,
    office_service: OfficeService = Depends(get_office_service)
):
    """Get office configuration by ID."""
    try:
        office = await office_service.get_office(office_id)
        if not office:
            raise HTTPException(status_code=404, detail="Office not found")
        
        return office
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/name/{office_name}", response_model=OfficeConfig)
async def get_office_by_name(
    office_name: str,
    office_service: OfficeService = Depends(get_office_service)
):
    """Get office configuration by name."""
    try:
        office = await office_service.get_office_by_name(office_name)
        if not office:
            raise HTTPException(status_code=404, detail="Office not found")
        
        return office
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{office_id}", response_model=OfficeConfig)
async def update_office(
    office_id: UUID,
    request: OfficeUpdateRequest,
    office_service: OfficeService = Depends(get_office_service)
):
    """Update office configuration."""
    try:
        # Get existing office
        existing = await office_service.get_office(office_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Office not found")
        
        # Update only provided fields
        update_data = existing.dict()
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        updated_office = OfficeConfig(**update_data)
        result = await office_service.update_office(office_id, updated_office)
        
        if not result:
            raise HTTPException(status_code=404, detail="Office not found")
        
        return result
    
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{office_id}")
async def delete_office(
    office_id: UUID,
    office_service: OfficeService = Depends(get_office_service)
):
    """Delete office and all associated data."""
    try:
        success = await office_service.delete_office(office_id)
        if not success:
            raise HTTPException(status_code=404, detail="Office not found")
        
        return {"message": "Office deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ================================================
# WORKFORCE DISTRIBUTION ENDPOINTS
# ================================================

@router.post("/{office_id}/workforce", response_model=WorkforceDistribution)
async def create_workforce_distribution(
    office_id: UUID,
    workforce: WorkforceDistribution,
    office_service: OfficeService = Depends(get_office_service)
):
    """Create workforce distribution for an office."""
    try:
        workforce.office_id = office_id
        return await office_service.create_workforce_distribution(workforce)
    
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{office_id}/workforce", response_model=Optional[WorkforceDistribution])
async def get_workforce_distribution(
    office_id: UUID,
    start_date: Optional[date] = Query(None, description="Specific start date, defaults to most recent"),
    office_service: OfficeService = Depends(get_office_service)
):
    """Get workforce distribution for an office."""
    try:
        return await office_service.get_workforce_distribution(office_id, start_date)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{office_id}/workforce", response_model=WorkforceDistribution)
async def update_workforce_distribution(
    office_id: UUID,
    workforce: WorkforceDistribution,
    start_date: date = Query(..., description="Start date for the workforce distribution"),
    office_service: OfficeService = Depends(get_office_service)
):
    """Update workforce distribution."""
    try:
        workforce.office_id = office_id
        workforce.start_date = start_date
        
        result = await office_service.update_workforce_distribution(office_id, start_date, workforce)
        if not result:
            # Create new if doesn't exist
            result = await office_service.create_workforce_distribution(workforce)
        
        return result
    
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ================================================
# PROGRESSION CONFIG ENDPOINTS
# ================================================

@router.get("/{office_id}/progression", response_model=List[ProgressionConfig])
async def get_progression_configs(
    office_id: UUID,
    office_service: OfficeService = Depends(get_office_service)
):
    """Get CAT progression configurations for an office."""
    try:
        return await office_service.get_progression_configs_for_office(office_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{office_id}/progression", response_model=ProgressionConfig)
async def create_progression_config(
    office_id: UUID,
    config: ProgressionConfig,
    office_service: OfficeService = Depends(get_office_service)
):
    """Create CAT progression configuration."""
    try:
        config.office_id = office_id
        return await office_service.create_progression_config(config)
    
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{office_id}/progression/{level}", response_model=ProgressionConfig)
async def update_progression_config(
    office_id: UUID,
    level: str,
    config: ProgressionConfig,
    office_service: OfficeService = Depends(get_office_service)
):
    """Update CAT progression configuration for a specific level."""
    try:
        config.office_id = office_id
        config.level = level
        
        result = await office_service.update_progression_config(office_id, level, config)
        if not result:
            # Create new if doesn't exist
            result = await office_service.create_progression_config(config)
        
        return result
    
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ================================================
# COMPREHENSIVE OFFICE ENDPOINTS
# ================================================

@router.get("/{office_id}/summary", response_model=OfficeBusinessPlanSummary)
async def get_office_summary(
    office_id: UUID,
    office_service: OfficeService = Depends(get_office_service)
):
    """Get complete office summary with all associated data."""
    try:
        summary = await office_service.get_office_summary(office_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Office not found")
        
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{office_id}/validate", response_model=ValidationResponse)
async def validate_office_setup(
    office_id: UUID,
    office_service: OfficeService = Depends(get_office_service)
):
    """Validate complete office setup and return validation results."""
    try:
        validation_results = await office_service.validate_office_setup(office_id)
        
        return ValidationResponse(
            errors=validation_results.get("errors", []),
            warnings=validation_results.get("warnings", []),
            info=validation_results.get("info", [])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{target_office_id}/copy-from/{source_office_id}", response_model=List[MonthlyBusinessPlan])
async def copy_business_plan_template(
    source_office_id: UUID,
    target_office_id: UUID,
    year: int = Query(..., description="Year to copy business plans for"),
    office_service: OfficeService = Depends(get_office_service)
):
    """Copy business plan template from one office to another."""
    try:
        return await office_service.copy_business_plan_template(
            source_office_id, target_office_id, year
        )
    
    except OfficeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ================================================
# HEALTH CHECK
# ================================================

@router.get("/health/check")
async def health_check():
    """Health check endpoint for office service."""
    return {"status": "healthy", "service": "office_management"}