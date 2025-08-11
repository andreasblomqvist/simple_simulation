from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import uuid
from datetime import datetime
from src.services.config_service import config_service
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

# Import models from the main models file
from src.models.office import (
    OfficeJourney, 
    EconomicParameters, 
    CATMatrix, 
    PopulationSnapshot, 
    BusinessPlan
)

# Define API-specific OfficeConfig model with proper schema
class OfficeConfig(BaseModel):
    """Complete office configuration with all related data"""
    id: str = Field(..., description="Office identifier")
    name: str = Field(..., description="Office name")
    journey: OfficeJourney = Field(..., description="Office maturity level")
    timezone: str = Field("UTC", description="Office timezone")
    economic_parameters: EconomicParameters = Field(..., description="Economic parameters")
    cat_matrix: Optional[CATMatrix] = Field(None, description="Career advancement timeline matrix")
    snapshots: List[PopulationSnapshot] = Field(default_factory=list, description="Population snapshots")
    business_plans: List[BusinessPlan] = Field(default_factory=list, description="Business plans")
    current_snapshot_id: Optional[str] = Field(None, description="ID of currently active snapshot")
    active_business_plan_id: Optional[str] = Field(None, description="ID of currently active business plan")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "Stockholm",
                "name": "Stockholm",
                "journey": "mature",
                "timezone": "Europe/Stockholm",
                "economic_parameters": {
                    "cost_of_living": 1.2,
                    "market_multiplier": 1.1,
                    "tax_rate": 0.25
                },
                "cat_matrix": {
                    "A": {"CAT0": 0.0, "CAT6": 0.919, "CAT12": 0.85},
                    "AC": {"CAT0": 0.0, "CAT6": 0.054, "CAT12": 0.759}
                },
                "snapshots": [
                    {
                        "id": "snapshot1",
                        "name": "Stockholm - Current Baseline",
                        "snapshot_date": "2025-01-01",
                        "description": "Current workforce baseline",
                        "total_fte": 120.5,
                        "created_at": "2025-01-06T12:00:00Z",
                        "is_default": True
                    }
                ],
                "business_plans": [
                    {
                        "id": "bp1",
                        "name": "Stockholm - 2025 Growth Plan",
                        "plan_date": "2025-01-01",
                        "description": "Annual growth and hiring plan",
                        "created_at": "2025-01-06T12:00:00Z",
                        "is_active": True
                    }
                ],
                "current_snapshot_id": "snapshot1",
                "active_business_plan_id": "bp1"
            }
        }

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

# CRITICAL: This route must be first to avoid being caught by /{office_id}
@router.get("/all")
def get_all_offices():
    """Get all offices with total_fte from snapshots"""
    config = config_service.get_config()
    offices = []
    
    for office_name, office_data in config.items():
        # Get total_fte directly from office configuration
        total_fte = float(office_data.get('total_fte', 0))
        
        office = {
            "id": office_name,
            "name": office_name,
            "journey": JOURNEY_MAP.get(office_data.get("journey", "emerging").strip(), "emerging"),
            "total_fte": total_fte,
            "economic_parameters": office_data.get("economic_parameters", {
                "cost_of_living": 1.0,
                "market_multiplier": 1.0,
                "tax_rate": 0.25
            })
        }
        offices.append(office)
    
    return offices

# Add this mapping at the top of the file (after imports)
JOURNEY_MAP = {
    "Mature Office": "mature",
    "Established Office": "established",
    "Emerging Office": "emerging",
    "mature": "mature",
    "established": "established",
    "emerging": "emerging"
}

def _build_office_config(name: str, data: dict) -> OfficeConfig:
    """Helper function to build OfficeConfig with all fields"""
    journey_raw = data.get("journey", "emerging")
    journey = JOURNEY_MAP.get(journey_raw.strip(), "emerging")
    
    # Get total_fte from snapshots if available, otherwise calculate from roles
    total_fte = 0.0
    if 'snapshots' in data and data['snapshots']:
        # Use FTE from existing snapshot
        snapshot = data['snapshots'][0] if isinstance(data['snapshots'], list) else data['snapshots']
        total_fte = snapshot.get('total_fte', 0.0)
    elif 'roles' in data:
        # Fallback: calculate from roles data
        for role_name, role_data in data['roles'].items():
            if isinstance(role_data, dict):
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, dict) and 'fte' in level_data:
                        total_fte += level_data['fte']
    
    # Mock CAT matrix data (in production, this would come from database)
    default_cat_matrix = CATMatrix(
        A={"CAT0": 0.0, "CAT6": 0.919, "CAT12": 0.85, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0},
        AC={"CAT0": 0.0, "CAT6": 0.054, "CAT12": 0.759, "CAT18": 0.4, "CAT24": 0.0, "CAT30": 0.0},
        C={"CAT0": 0.0, "CAT6": 0.05, "CAT12": 0.442, "CAT18": 0.597, "CAT24": 0.278, "CAT30": 0.643},
        SrC={"CAT0": 0.0, "CAT6": 0.206, "CAT12": 0.438, "CAT18": 0.317, "CAT24": 0.211, "CAT30": 0.206},
        AM={"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.189, "CAT24": 0.197, "CAT30": 0.234},
        M={"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.01, "CAT18": 0.02, "CAT24": 0.03, "CAT30": 0.04},
        SrM={"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.005, "CAT18": 0.01, "CAT24": 0.015, "CAT30": 0.02},
        Pi={},
        P={},
        X={},
        OPE={}
    )
    
    # Create snapshot with actual total_fte from office configuration
    actual_total_fte = float(data.get('total_fte', 0))
    print(f"DEBUG: Office {name} - data keys: {list(data.keys())}")
    print(f"DEBUG: Office {name} - raw total_fte: {data.get('total_fte')}")
    print(f"DEBUG: Office {name} - actual_total_fte: {actual_total_fte}")
    mock_snapshots = [
        PopulationSnapshot(
            id="snapshot1",
            name=f"{name} - Current Baseline",
            snapshot_date="2025-01-01",
            description="Current workforce baseline",
            total_fte=actual_total_fte,  # Use real total_fte from config file
            created_at="2025-01-06T12:00:00Z",
            is_default=True
        )
    ]
    
    # Mock business plans (in production, this would come from database)
    mock_business_plans = [
        BusinessPlan(
            id="bp1",
            name=f"{name} - 2025 Growth Plan",
            plan_date="2025-01-01",
            description="Annual growth and hiring plan",
            created_at="2025-01-06T12:00:00Z",
            is_active=True
        )
    ]
    
    return OfficeConfig(
        id=name,
        name=name,
        journey=journey,
        timezone=data.get("timezone", "UTC"),
        economic_parameters=EconomicParameters(
            cost_of_living=data.get("economic_parameters", {}).get("cost_of_living", 1.0),
            market_multiplier=data.get("economic_parameters", {}).get("market_multiplier", 1.0),
            tax_rate=data.get("economic_parameters", {}).get("tax_rate", 0.25)
        ),
        cat_matrix=data.get("cat_matrix", default_cat_matrix),
        snapshots=mock_snapshots,
        business_plans=mock_business_plans,
        current_snapshot_id="snapshot1",
        active_business_plan_id="bp1"
    )

# All specific routes must come BEFORE any generic /{office_id} routes

# Other specific routes continue below

# Simple test endpoint
@router.get("/{office_id}/test-simple")
def test_simple(office_id: str):
    return {"test": "works", "office": office_id}

# CAT matrix endpoints
@router.get("/{office_id}/cat-matrix", response_model=CATMatrix)
def get_office_cat_matrix(office_id: str):
    """Get CAT matrix for a specific office"""
    config = config_service.get_config()
    if office_id not in config:
        raise HTTPException(status_code=404, detail="Office not found")
    
    # Return the same default CAT matrix (in production, this would be office-specific)
    return CATMatrix(
        A={"CAT0": 0.0, "CAT6": 0.919, "CAT12": 0.85, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0},
        AC={"CAT0": 0.0, "CAT6": 0.054, "CAT12": 0.759, "CAT18": 0.4, "CAT24": 0.0, "CAT30": 0.0},
        C={"CAT0": 0.0, "CAT6": 0.05, "CAT12": 0.442, "CAT18": 0.597, "CAT24": 0.278, "CAT30": 0.643},
        SrC={"CAT0": 0.0, "CAT6": 0.206, "CAT12": 0.438, "CAT18": 0.317, "CAT24": 0.211, "CAT30": 0.206},
        AM={"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.189, "CAT24": 0.197, "CAT30": 0.234},
        M={"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.01, "CAT18": 0.02, "CAT24": 0.03, "CAT30": 0.04},
        SrM={"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.005, "CAT18": 0.01, "CAT24": 0.015, "CAT30": 0.02}
    )

@router.put("/{office_id}/cat-matrix", response_model=dict)
def update_office_cat_matrix(office_id: str, cat_matrix: CATMatrix):
    """Update CAT matrix for a specific office"""
    config = config_service.get_config()
    if office_id not in config:
        raise HTTPException(status_code=404, detail="Office not found")
    
    # In production, this would save to database
    # For now, just return success
    return {"message": "CAT matrix updated successfully"}

@router.post("/{office_id}/cat-matrix/reset", response_model=CATMatrix)
def reset_office_cat_matrix(office_id: str):
    """Reset CAT matrix to default values for a specific office"""
    config = config_service.get_config()
    if office_id not in config:
        raise HTTPException(status_code=404, detail="Office not found")
    
    # Return default CAT matrix
    default_matrix = CATMatrix(
        A={"CAT0": 0.0, "CAT6": 0.919, "CAT12": 0.85, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0},
        AC={"CAT0": 0.0, "CAT6": 0.054, "CAT12": 0.759, "CAT18": 0.4, "CAT24": 0.0, "CAT30": 0.0},
        C={"CAT0": 0.0, "CAT6": 0.05, "CAT12": 0.442, "CAT18": 0.597, "CAT24": 0.278, "CAT30": 0.643},
        SrC={"CAT0": 0.0, "CAT6": 0.206, "CAT12": 0.438, "CAT18": 0.317, "CAT24": 0.211, "CAT30": 0.206}
    )
    return default_matrix

# Other specific office routes
@router.get("/{office_id}/workforce")
def get_office_workforce(office_id: str):
    """Get workforce distribution for an office from its current snapshot"""
    config = config_service.get_config()
    if office_id not in config:
        raise HTTPException(status_code=404, detail="Office not found")
    
    office_data = config[office_id]
    workforce = []
    
    # Extract workforce data from office configuration roles
    if 'roles' in office_data:
        for role_name, role_data in office_data['roles'].items():
            if isinstance(role_data, dict):
                # Check if this is a flat role (has fte directly) or leveled role
                if 'fte' in role_data:
                    # Flat role like Operations
                    workforce.append({
                        "role": role_name,
                        "level": "All",  # Use "All" for flat roles
                        "fte": role_data['fte'],
                        "notes": f"{role_name} (all levels)"
                    })
                else:
                    # Leveled role like Consultant, Sales, Recruitment
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, dict) and 'fte' in level_data:
                            workforce.append({
                                "role": role_name,
                                "level": level_name,
                                "fte": level_data['fte'],
                                "notes": f"{role_name} {level_name} level"
                            })
    
    return {
        "office_id": office_id,
        "start_date": "2025-01-01",
        "workforce": workforce
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

# Static endpoints (no parameters) - these must come before generic /{office_id} routes
@router.get("/health")
def office_health_check():
    """Health check for office API"""
    return {"status": "ok"}

# Snapshot endpoints (simple implementation without database)
@router.get("/snapshots/{snapshot_id}")
def get_snapshot(snapshot_id: str):
    """Get a snapshot by ID - generates from config data"""
    # For now, support a default snapshot per office
    if not snapshot_id.startswith("snapshot"):
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    # Extract office name from snapshot_id (format: snapshot1, snapshot_stockholm, etc)
    if snapshot_id == "snapshot1":
        # Default snapshot - try Stockholm as example
        office_name = "Stockholm"
    else:
        # Extract office name from snapshot id
        office_name = snapshot_id.replace("snapshot_", "").replace("snapshot", "").capitalize()
    
    config = config_service.get_config()
    if office_name not in config:
        raise HTTPException(status_code=404, detail="Office not found for snapshot")
    
    office_data = config[office_name]
    
    # Generate workforce data from config
    workforce_data = {}
    if 'roles' in office_data:
        for role_name, role_data in office_data['roles'].items():
            if isinstance(role_data, dict):
                if 'fte' in role_data:
                    # Flat role
                    workforce_data[role_name] = {"All": role_data['fte']}
                else:
                    # Leveled role
                    role_levels = {}
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, dict) and 'fte' in level_data:
                            role_levels[level_name] = level_data['fte']
                    if role_levels:
                        workforce_data[role_name] = role_levels
    
    total_fte = office_data.get('total_fte', 0)
    
    return {
        "id": snapshot_id,
        "office_id": office_name,
        "office_name": office_name,
        "snapshot_date": "2025-01-01",
        "snapshot_name": f"{office_name} - Current Baseline",
        "description": f"Current workforce baseline for {office_name}",
        "total_fte": total_fte,
        "is_default": True,
        "is_approved": True,
        "source": "current",
        "created_at": "2025-01-06T12:00:00Z",
        "created_by": "system",
        "last_used_at": "2025-01-06T12:00:00Z",
        "tags": ["baseline", "current"],
        "workforce_data": workforce_data,
        "metadata": {
            "total_fte": total_fte,
            "role_count": len(workforce_data),
            "journey": office_data.get("journey", "mature")
        }
    }

@router.get("/debug-config")
def debug_office_config():
    """Debug endpoint to see raw config data"""
    config = config_service.get_config()
    stockholm_data = config.get('Stockholm', {})
    return {
        "stockholm_total_fte": stockholm_data.get('total_fte'),
        "stockholm_name": stockholm_data.get('name'),
        "config_keys": list(config.keys())[:5]
    }


@router.get("/export")
def export_offices():
    """Export office config as Excel"""
    config = config_service.get_config()
    df = pd.DataFrame.from_dict(config, orient="index")
    output = io.BytesIO()
    df.to_excel(output)
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=offices.xlsx"})

# Generic office endpoints - must be last to avoid path conflicts
@router.get("/{office_id}")
def get_office(office_id: str):
    """Get a specific office by ID"""
    print(f"DEBUG: get_office called with office_id: {office_id}")
    config = config_service.get_config()
    if office_id in config:
        data = config[office_id]
        try:
            return _build_office_config(office_id, data)
        except Exception as e:
            print(f"Error building office config: {e}")
            # Return minimal valid structure
            return {
                "id": office_id,
                "name": office_id,
                "journey": "mature",
                "timezone": "UTC",
                "economic_parameters": {"cost_of_living": 1.0, "market_multiplier": 1.0, "tax_rate": 0.25},
                "cat_matrix": None,
                "snapshots": [],
                "business_plans": [],
                "current_snapshot_id": None,
                "active_business_plan_id": None
            }
    
    raise HTTPException(status_code=404, detail="Office not found")

@router.delete("/{office_name}")
def delete_office(office_name: str):
    """Delete an office by name"""
    success = config_service.delete_office(office_name)
    if not success:
        raise HTTPException(status_code=404, detail="Office not found")
    return {"message": f"Office '{office_name}' deleted"}

 