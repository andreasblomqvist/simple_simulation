from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import uuid
from datetime import datetime
from src.services.config_service import config_service
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

# Office API models
class OfficeJourney(str, Enum):
    EMERGING = "emerging"
    ESTABLISHED = "established"
    MATURE = "mature"

class EconomicParameters(BaseModel):
    cost_of_living: float = 1.0
    market_multiplier: float = 1.0
    tax_rate: float = 0.25

class OfficeConfig(BaseModel):
    id: str
    name: str
    journey: OfficeJourney
    timezone: str = "UTC"
    economic_parameters: EconomicParameters
    total_fte: float
    roles: dict

class WorkforceEntry(BaseModel):
    role: str
    level: str
    fte: float
    notes: Optional[str] = None

class WorkforceDistribution(BaseModel):
    office_id: str
    start_date: str
    workforce: List[WorkforceEntry]

class OfficeBusinessPlanSummary(BaseModel):
    office_id: str
    monthly_plans: List[Dict[str, Any]] = []
    workforce_distribution: Optional[WorkforceDistribution] = None

router = APIRouter(
    prefix="/offices",  # No /api prefix
    tags=["offices"]
)

# Add this mapping at the top of the file (after imports)
JOURNEY_MAP = {
    "Mature Office": "mature",
    "Established Office": "established",
    "Emerging Office": "emerging",
    "mature": "mature",
    "established": "established",
    "emerging": "emerging"
}

@router.get("", response_model=List[OfficeConfig])
def get_offices():
    """Get all offices"""
    config = config_service.get_config()
    offices = []
    for name, data in config.items():
        journey_raw = data.get("journey", "emerging")
        journey = JOURNEY_MAP.get(journey_raw.strip(), "emerging")
        offices.append(OfficeConfig(
            id=name,  # Use office name as ID for consistency
            name=name,
            journey=journey,
            timezone=data.get("timezone", "UTC"),
            economic_parameters=EconomicParameters(**data.get("economic_parameters", {})),
            total_fte=data.get("total_fte", 0),
            roles=data.get("roles", {})
        ))
    return offices

@router.get("/{office_id}", response_model=OfficeConfig)
def get_office(office_id: str):
    """Get a specific office by ID"""
    config = config_service.get_config()
    if office_id in config:
        data = config[office_id]
        journey_raw = data.get("journey", "emerging")
        journey = JOURNEY_MAP.get(journey_raw.strip(), "emerging")
        return OfficeConfig(
            id=office_id,  # Use office name as ID for consistency
            name=office_id,
            journey=journey,
            timezone=data.get("timezone", "UTC"),
            economic_parameters=EconomicParameters(**data.get("economic_parameters", {})),
            total_fte=data.get("total_fte", 0),
            roles=data.get("roles", {})
        )
    
    raise HTTPException(status_code=404, detail="Office not found")

@router.get("/health")
def office_health_check():
    """Health check for office API"""
    return {"status": "ok"}

@router.get("/export")
def export_offices():
    """Export office config as Excel"""
    config = config_service.get_config()
    df = pd.DataFrame.from_dict(config, orient="index")
    output = io.BytesIO()
    df.to_excel(output)
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=offices.xlsx"})

@router.delete("/{office_name}")
def delete_office(office_name: str):
    """Delete an office by name"""
    success = config_service.delete_office(office_name)
    if not success:
        raise HTTPException(status_code=404, detail="Office not found")
    return {"message": f"Office '{office_name}' deleted"}

@router.get("/{office_id}/workforce")
def get_office_workforce(office_id: str):
    """Get workforce distribution for an office"""
    config = config_service.get_config()
    if office_id not in config:
        raise HTTPException(status_code=404, detail="Office not found")
    
    # Create workforce distribution from office roles
    workforce_entries = []
    office_data = config[office_id]
    roles = office_data.get("roles", {})
    
    for role_name, role_data in roles.items():
        for level_name, level_data in role_data.items():
            if isinstance(level_data, dict) and "fte" in level_data:
                workforce_entries.append({
                    "role": role_name,
                    "level": level_name,
                    "fte": level_data["fte"],
                    "notes": f"{role_name} {level_name}"
                })
    
    return {
        "office_id": office_id,
        "start_date": "2025-01-01",
        "workforce": workforce_entries
    }

@router.get("/{office_id}/summary")
def get_office_summary(office_id: str):
    """Get complete office summary including workforce and business plans"""
    config = config_service.get_config()
    if office_id not in config:
        raise HTTPException(status_code=404, detail="Office not found")
    
    # Get workforce distribution
    workforce_response = get_office_workforce(office_id)
    
    return {
        "office_id": office_id,
        "monthly_plans": [],  # Empty for now, will be implemented later
        "workforce_distribution": workforce_response
    }

 