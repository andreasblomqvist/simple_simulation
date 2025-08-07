"""
FastAPI router for population snapshot endpoints
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field, validator

from src.database.connection import get_db
from src.database.models import SnapshotSource
from src.services.snapshot_service import (
    get_snapshot_service,
    SnapshotService,
    SnapshotCreationRequest,
    SimulationSnapshotRequest
)

logger = logging.getLogger(__name__)

# Pydantic models for API

class SnapshotSourceEnum(str, Enum):
    MANUAL = "manual"
    SIMULATION = "simulation"
    IMPORT = "import"
    BUSINESS_PLAN = "business_plan"
    CURRENT = "current"

class CreateSnapshotRequest(BaseModel):
    office_id: UUID
    snapshot_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = Field(default_factory=list)
    is_default: bool = False
    created_by: str = Field(..., min_length=1, max_length=100)
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            return [tag.strip() for tag in v if tag.strip()]
        return []

class CreateFromSimulationRequest(BaseModel):
    office_name: str = Field(..., min_length=1, max_length=100)
    simulation_results: Dict[str, Any]
    snapshot_date: str = Field(..., pattern=r'^\d{6}$')  # YYYYMM format
    snapshot_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = Field(default_factory=list)
    created_by: str = Field(..., min_length=1, max_length=100)
    
    @validator('snapshot_date')
    def validate_snapshot_date(cls, v):
        try:
            year = int(v[:4])
            month = int(v[4:])
            if year < 2020 or year > 2050 or month < 1 or month > 12:
                raise ValueError("Invalid year or month")
            return v
        except ValueError:
            raise ValueError("snapshot_date must be in YYYYMM format with valid year and month")
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            return [tag.strip() for tag in v if tag.strip()]
        return []

class CreateFromBusinessPlanRequest(BaseModel):
    office_id: UUID
    business_plan_data: Dict[str, Any]
    snapshot_name: str = Field(..., min_length=1, max_length=200)
    snapshot_date: str = Field(..., pattern=r'^\d{6}$')  # YYYYMM format
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = Field(default_factory=list)
    created_by: str = Field(..., min_length=1, max_length=100)

class UpdateSnapshotRequest(BaseModel):
    snapshot_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_approved: Optional[bool] = None
    updated_by: Optional[str] = Field(None, min_length=1, max_length=100)

class UpdateWorkforceDataRequest(BaseModel):
    workforce_data: Dict[str, Any]
    
class UpdateTagsRequest(BaseModel):
    tags: List[str] = Field(default_factory=list)
    
    @validator('tags')
    def validate_tags(cls, v):
        return [tag.strip() for tag in v if tag.strip()]

class SnapshotResponse(BaseModel):
    id: UUID
    office_id: UUID
    office_name: Optional[str] = None
    snapshot_date: str
    snapshot_name: str
    description: Optional[str] = None
    total_fte: int
    is_default: bool
    is_approved: bool
    source: str
    created_at: datetime
    created_by: str
    last_used_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    workforce_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SnapshotListResponse(BaseModel):
    snapshots: List[SnapshotResponse]
    total_count: int
    page: int
    limit: int

class ComparisonResponse(BaseModel):
    snapshot_1: SnapshotResponse
    snapshot_2: SnapshotResponse
    total_fte_delta: int
    workforce_changes: Dict[str, Any]
    insights: List[str]

class AuditLogEntry(BaseModel):
    id: UUID
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    user_id: Optional[str] = None
    timestamp: datetime
    details: Dict[str, Any] = Field(default_factory=dict)

# Router setup
router = APIRouter(
    prefix="/snapshots",
    tags=["snapshots"]
)

def get_snapshot_service_dep() -> SnapshotService:
    """Dependency for snapshot service"""
    return get_snapshot_service()

def convert_snapshot_to_response(snapshot) -> SnapshotResponse:
    """Convert database model to API response"""
    return SnapshotResponse(
        id=snapshot.id,
        office_id=snapshot.office_id,
        office_name=snapshot.office.name if hasattr(snapshot, 'office') and snapshot.office else None,
        snapshot_date=snapshot.snapshot_date,
        snapshot_name=snapshot.snapshot_name,
        description=snapshot.description,
        total_fte=snapshot.total_fte,
        is_default=snapshot.is_default,
        is_approved=snapshot.is_approved,
        source=snapshot.source.value if snapshot.source else "unknown",
        created_at=snapshot.created_at,
        created_by=snapshot.created_by,
        last_used_at=snapshot.last_used_at,
        tags=snapshot.tag_list,
        workforce_data=snapshot.to_dict()["workforce_data"],
        metadata=snapshot.metadata or {}
    )

# Endpoints

@router.post("/", response_model=SnapshotResponse)
async def create_snapshot_from_current(
    request: CreateSnapshotRequest,
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Create a snapshot from current office workforce"""
    try:
        creation_request = SnapshotCreationRequest(
            office_id=request.office_id,
            snapshot_name=request.snapshot_name,
            description=request.description,
            tags=request.tags,
            is_default=request.is_default,
            created_by=request.created_by
        )
        
        snapshot = await service.create_snapshot_from_current(creation_request)
        return convert_snapshot_to_response(snapshot)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating snapshot: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/from-simulation", response_model=SnapshotResponse)
async def create_snapshot_from_simulation(
    request: CreateFromSimulationRequest,
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Create a snapshot from simulation results"""
    try:
        sim_request = SimulationSnapshotRequest(
            office_name=request.office_name,
            simulation_results=request.simulation_results,
            snapshot_date=request.snapshot_date,
            snapshot_name=request.snapshot_name,
            description=request.description,
            tags=request.tags,
            created_by=request.created_by
        )
        
        snapshot = await service.create_snapshot_from_simulation(sim_request)
        return convert_snapshot_to_response(snapshot)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating snapshot from simulation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/from-business-plan", response_model=SnapshotResponse)
async def create_snapshot_from_business_plan(
    request: CreateFromBusinessPlanRequest,
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Create a snapshot from business plan data"""
    try:
        snapshot = await service.create_snapshot_from_business_plan(
            office_id=request.office_id,
            business_plan_data=request.business_plan_data,
            snapshot_name=request.snapshot_name,
            snapshot_date=request.snapshot_date,
            created_by=request.created_by,
            description=request.description,
            tags=request.tags
        )
        
        return convert_snapshot_to_response(snapshot)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating snapshot from business plan: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{snapshot_id}", response_model=SnapshotResponse)
async def get_snapshot(
    snapshot_id: UUID = Path(..., description="Snapshot ID"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Get a snapshot by ID"""
    try:
        snapshot = await service.get_snapshot(snapshot_id)
        if not snapshot:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        return convert_snapshot_to_response(snapshot)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving snapshot {snapshot_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=SnapshotListResponse)
async def search_snapshots(
    office_id: Optional[UUID] = Query(None, description="Filter by office ID"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    source: Optional[SnapshotSourceEnum] = Query(None, description="Filter by source"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYYMM)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYYMM)"),
    search_term: Optional[str] = Query(None, description="Search in name and description"),
    approved_only: bool = Query(False, description="Show only approved snapshots"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Search snapshots with filters"""
    try:
        offset = (page - 1) * limit
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else None
        
        snapshots, total_count = await service.search_snapshots(
            office_id=office_id,
            tags=tag_list,
            source=SnapshotSource(source.value) if source else None,
            date_from=date_from,
            date_to=date_to,
            search_term=search_term,
            approved_only=approved_only,
            limit=limit,
            offset=offset
        )
        
        return SnapshotListResponse(
            snapshots=[convert_snapshot_to_response(s) for s in snapshots],
            total_count=total_count,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error searching snapshots: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/office/{office_id}", response_model=List[SnapshotResponse])
async def get_office_snapshots(
    office_id: UUID = Path(..., description="Office ID"),
    approved_only: bool = Query(False, description="Show only approved snapshots"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of snapshots"),
    offset: Optional[int] = Query(None, ge=0, description="Number of snapshots to skip"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Get all snapshots for an office"""
    try:
        snapshots = await service.get_office_snapshots(
            office_id=office_id,
            approved_only=approved_only,
            limit=limit,
            offset=offset
        )
        
        return [convert_snapshot_to_response(s) for s in snapshots]
        
    except Exception as e:
        logger.error(f"Error retrieving office snapshots: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/office/{office_id}/default", response_model=Optional[SnapshotResponse])
async def get_default_snapshot(
    office_id: UUID = Path(..., description="Office ID"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Get the default snapshot for an office"""
    try:
        snapshot = await service.get_default_snapshot(office_id)
        if not snapshot:
            return None
        
        return convert_snapshot_to_response(snapshot)
        
    except Exception as e:
        logger.error(f"Error retrieving default snapshot: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{snapshot_id}", response_model=SnapshotResponse)
async def update_snapshot(
    request: UpdateSnapshotRequest,
    snapshot_id: UUID = Path(..., description="Snapshot ID"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Update snapshot properties"""
    try:
        updates = {}
        if request.snapshot_name is not None:
            updates["snapshot_name"] = request.snapshot_name
        if request.description is not None:
            updates["description"] = request.description
        if request.is_approved is not None:
            updates["is_approved"] = request.is_approved
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        snapshot = await service.update_snapshot(
            snapshot_id=snapshot_id,
            updates=updates,
            updated_by=request.updated_by
        )
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        return convert_snapshot_to_response(snapshot)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating snapshot {snapshot_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{snapshot_id}/set-default")
async def set_default_snapshot(
    snapshot_id: UUID = Path(..., description="Snapshot ID"),
    user_id: Optional[str] = Query(None, description="User ID for audit trail"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Set a snapshot as the default for its office"""
    try:
        success = await service.set_default_snapshot(snapshot_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        return {"message": "Snapshot set as default successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting default snapshot {snapshot_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{snapshot_id}/approve")
async def approve_snapshot(
    snapshot_id: UUID = Path(..., description="Snapshot ID"),
    user_id: Optional[str] = Query(None, description="User ID for audit trail"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Approve a snapshot for official use"""
    try:
        success = await service.approve_snapshot(snapshot_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        return {"message": "Snapshot approved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving snapshot {snapshot_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: UUID = Path(..., description="Snapshot ID"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Delete a snapshot"""
    try:
        success = await service.delete_snapshot(snapshot_id)
        if not success:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        return {"message": "Snapshot deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting snapshot {snapshot_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{snapshot_id}/workforce", response_model=dict)
async def update_workforce_data(
    request: UpdateWorkforceDataRequest,
    snapshot_id: UUID = Path(..., description="Snapshot ID"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Update workforce data for a snapshot"""
    try:
        success = await service.update_workforce_data(
            snapshot_id=snapshot_id,
            workforce_data=request.workforce_data
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        return {"message": "Workforce data updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workforce data for snapshot {snapshot_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{snapshot_id}/tags", response_model=dict)
async def update_tags(
    request: UpdateTagsRequest,
    snapshot_id: UUID = Path(..., description="Snapshot ID"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Update tags for a snapshot"""
    try:
        success = await service.update_tags(
            snapshot_id=snapshot_id,
            tags=request.tags
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        return {"message": "Tags updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tags for snapshot {snapshot_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{snapshot_1_id}/compare/{snapshot_2_id}", response_model=ComparisonResponse)
async def compare_snapshots(
    snapshot_1_id: UUID = Path(..., description="First snapshot ID"),
    snapshot_2_id: UUID = Path(..., description="Second snapshot ID"),
    user_id: Optional[str] = Query(None, description="User ID for audit trail"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Compare two snapshots"""
    try:
        comparison = await service.compare_snapshots(
            snapshot_1_id=snapshot_1_id,
            snapshot_2_id=snapshot_2_id,
            user_id=user_id
        )
        
        return ComparisonResponse(
            snapshot_1=convert_snapshot_to_response(comparison.snapshot_1),
            snapshot_2=convert_snapshot_to_response(comparison.snapshot_2),
            total_fte_delta=comparison.total_fte_delta,
            workforce_changes=comparison.workforce_changes,
            insights=comparison.insights
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error comparing snapshots: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{snapshot_id}/audit-log", response_model=List[AuditLogEntry])
async def get_audit_log(
    snapshot_id: UUID = Path(..., description="Snapshot ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of log entries"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Get audit log for a snapshot"""
    try:
        logs = await service.get_audit_log(snapshot_id, limit)
        
        return [
            AuditLogEntry(
                id=UUID(log["id"]),
                action=log["action"],
                entity_type=log["entity_type"],
                entity_id=UUID(log["entity_id"]) if log["entity_id"] else None,
                user_id=log["user_id"],
                timestamp=datetime.fromisoformat(log["timestamp"]),
                details=log["details"]
            )
            for log in logs
        ]
        
    except Exception as e:
        logger.error(f"Error retrieving audit log for snapshot {snapshot_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{snapshot_id}/use-in-scenario/{scenario_id}")
async def use_snapshot_in_scenario(
    snapshot_id: UUID = Path(..., description="Snapshot ID"),
    scenario_id: UUID = Path(..., description="Scenario ID"),
    user_id: Optional[str] = Query(None, description="User ID for audit trail"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Record usage of snapshot in a scenario"""
    try:
        success = await service.use_snapshot_in_scenario(
            snapshot_id=snapshot_id,
            scenario_id=scenario_id,
            user_id=user_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        return {"message": "Snapshot usage recorded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording snapshot usage: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{snapshot_id}/use-in-business-plan/{business_plan_id}")
async def use_snapshot_in_business_plan(
    snapshot_id: UUID = Path(..., description="Snapshot ID"),
    business_plan_id: UUID = Path(..., description="Business plan ID"),
    user_id: Optional[str] = Query(None, description="User ID for audit trail"),
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    """Record usage of snapshot in a business plan"""
    try:
        success = await service.use_snapshot_in_business_plan(
            snapshot_id=snapshot_id,
            business_plan_id=business_plan_id,
            user_id=user_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        return {"message": "Snapshot usage recorded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording snapshot usage: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@router.get("/health", tags=["health"])
async def snapshot_health_check():
    """Health check for snapshot API"""
    return {"status": "ok", "service": "snapshots"}