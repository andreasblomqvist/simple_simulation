from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter(
    prefix="/business-plans",
    tags=["business-plans"]
)

class MonthlyPlanEntry(BaseModel):
    role: str
    level: str
    recruitment: float = 0
    churn: float = 0
    price: float = 100
    utr: float = 0.75
    salary: float = 5000

class MonthlyBusinessPlan(BaseModel):
    id: str
    office_id: str
    year: int
    month: int
    entries: List[MonthlyPlanEntry]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@router.get("")
def get_business_plans(office_id: str, year: Optional[int] = None):
    """Get business plans for an office"""
    # For now, return empty list - this will be implemented with actual data storage
    return []

@router.post("")
def create_business_plan(plan_data: dict):
    """Create a new business plan"""
    # For now, return a mock response
    return {
        "id": "mock-plan-id",
        "office_id": plan_data.get("office_id"),
        "year": plan_data.get("year"),
        "month": plan_data.get("month"),
        "entries": plan_data.get("entries", []),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

@router.put("/{plan_id}")
def update_business_plan(plan_id: str, plan_data: dict):
    """Update an existing business plan"""
    # For now, return a mock response
    return {
        "id": plan_id,
        "office_id": plan_data.get("office_id"),
        "year": plan_data.get("year"),
        "month": plan_data.get("month"),
        "entries": plan_data.get("entries", []),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

@router.delete("/{plan_id}")
def delete_business_plan(plan_id: str):
    """Delete a business plan"""
    return {"message": f"Business plan {plan_id} deleted"} 