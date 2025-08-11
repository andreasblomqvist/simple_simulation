"""
Business Plan Storage Service

Handles storage and retrieval of business plan data.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class BusinessPlanStorage:
    def __init__(self):
        self.storage_dir = Path(__file__).parent.parent.parent / "data" / "business_plans"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._plans: Dict[str, Dict[str, Any]] = {}
        self._load_existing_plans()
    
    def _load_existing_plans(self):
        """Load existing business plans from storage"""
        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    plan = json.load(f)
                    plan_id = plan.get('id')
                    if plan_id:
                        self._plans[plan_id] = plan
            except Exception as e:
                print(f"Warning: Could not load business plan from {file_path}: {e}")
    
    def _save_plan_to_file(self, plan: Dict[str, Any]):
        """Save a plan to file storage"""
        plan_id = plan['id']
        file_path = self.storage_dir / f"{plan_id}.json"
        try:
            with open(file_path, 'w') as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save business plan to {file_path}: {e}")
    
    def create_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new business plan"""
        plan_id = plan_data.get('id', str(uuid.uuid4()))
        
        plan = {
            "id": plan_id,
            "office_id": plan_data.get("office_id"),
            "year": plan_data.get("year"),
            "month": plan_data.get("month"),
            "entries": plan_data.get("entries", []),
            "created_at": plan_data.get("created_at", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat()
        }
        
        self._plans[plan_id] = plan
        self._save_plan_to_file(plan)
        return plan
    
    def get_plans(self, office_id: Optional[str] = None, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get business plans with optional filters"""
        plans = list(self._plans.values())
        
        if office_id:
            plans = [p for p in plans if p.get("office_id") == office_id]
        
        if year:
            plans = [p for p in plans if p.get("year") == year]
        
        # Sort by year, month
        plans.sort(key=lambda p: (p.get("year", 0), p.get("month", 0)))
        return plans
    
    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific business plan by ID"""
        return self._plans.get(plan_id)
    
    def update_plan(self, plan_id: str, plan_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing business plan"""
        if plan_id not in self._plans:
            return None
        
        plan = self._plans[plan_id].copy()
        plan.update({
            "office_id": plan_data.get("office_id", plan["office_id"]),
            "year": plan_data.get("year", plan["year"]),
            "month": plan_data.get("month", plan["month"]),
            "entries": plan_data.get("entries", plan["entries"]),
            "updated_at": datetime.now().isoformat()
        })
        
        self._plans[plan_id] = plan
        self._save_plan_to_file(plan)
        return plan
    
    def delete_plan(self, plan_id: str) -> bool:
        """Delete a business plan"""
        if plan_id not in self._plans:
            return False
        
        del self._plans[plan_id]
        
        # Remove file
        file_path = self.storage_dir / f"{plan_id}.json"
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            print(f"Warning: Could not delete business plan file {file_path}: {e}")
        
        return True
    
    def get_office_summary(self, office_id: str, year: Optional[int] = None) -> Dict[str, Any]:
        """Get summary of all business plans for an office"""
        plans = self.get_plans(office_id=office_id, year=year)
        
        if not plans:
            return {
                "office_id": office_id,
                "year": year,
                "monthly_plans": [],
                "summary": {
                    "total_months": 0,
                    "total_entries": 0,
                    "roles_covered": [],
                    "date_range": None
                }
            }
        
        # Calculate summary statistics
        total_entries = sum(len(plan.get("entries", [])) for plan in plans)
        roles_covered = set()
        for plan in plans:
            for entry in plan.get("entries", []):
                roles_covered.add(entry.get("role"))
        
        months = [p.get("month") for p in plans if p.get("month")]
        date_range = f"{min(months)}-{max(months)}" if months else None
        
        return {
            "office_id": office_id,
            "year": year,
            "monthly_plans": plans,
            "summary": {
                "total_months": len(plans),
                "total_entries": total_entries,
                "roles_covered": sorted(list(roles_covered)),
                "date_range": date_range
            }
        }
    
    def get_aggregated_plans(
        self, 
        year: Optional[int] = None, 
        office_ids: Optional[List[str]] = None,
        journey: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get aggregated business plans across multiple offices"""
        
        # Load office configuration to filter by journey if needed
        office_config = {}
        if journey:
            try:
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                         "config", "office_configuration.json")
                with open(config_path, 'r') as f:
                    office_config = json.load(f)
            except Exception:
                pass
        
        # Get all plans and filter by criteria
        all_plans = []
        filtered_office_ids = set()
        
        for plan in self._plans.values():
            plan_office_id = plan.get("office_id")
            plan_year = plan.get("year")
            
            # Year filter
            if year and plan_year != year:
                continue
                
            # Office IDs filter
            if office_ids and plan_office_id not in office_ids:
                continue
                
            # Journey filter
            if journey and office_config:
                # Handle both office ID and office name lookups
                office_data = office_config.get(plan_office_id, {})
                if not office_data:
                    # Try looking up by office name instead
                    for office_name, data in office_config.items():
                        if data.get("name", "").lower() == plan_office_id.lower():
                            office_data = data
                            break
                
                office_journey = office_data.get("journey", "").lower().replace(" office", "")
                if office_journey != journey.lower():
                    continue
            
            all_plans.append(plan)
            filtered_office_ids.add(plan_office_id)
        
        if not all_plans:
            return {
                "aggregated_plans": [],
                "summary": {
                    "total_offices": 0,
                    "total_months": 0,
                    "total_entries": 0,
                    "offices_included": [],
                    "date_range": None,
                    "roles_covered": [],
                    "aggregation_type": "all_offices" if not office_ids else "selected_offices",
                    "filters_applied": {
                        "year": year,
                        "office_ids": office_ids,
                        "journey": journey
                    }
                }
            }
        
        # Group plans by month for aggregation
        plans_by_month = {}
        for plan in all_plans:
            month = plan.get("month")
            if month not in plans_by_month:
                plans_by_month[month] = []
            plans_by_month[month].append(plan)
        
        # Aggregate entries by month
        aggregated_monthly_plans = []
        
        for month in sorted(plans_by_month.keys()):
            month_plans = plans_by_month[month]
            
            # Aggregate entries by role and level
            aggregated_entries = {}
            
            for plan in month_plans:
                for entry in plan.get("entries", []):
                    role = entry.get("role")
                    level = entry.get("level")
                    key = f"{role}-{level}"
                    
                    if key not in aggregated_entries:
                        aggregated_entries[key] = {
                            "role": role,
                            "level": level,
                            # Workforce fields
                            "recruitment": 0,
                            "churn": 0,
                            # Net Sales fields
                            "consultant_time": 0,
                            "planned_absence": 0,
                            "unplanned_absence": 0,
                            "vacation_withdrawal": 0,
                            "vacation": 0,
                            "invoiced_time": 0,
                            "average_price": 0,
                            # Operating Costs - Expenses
                            "client_loss": 0,
                            "education": 0,
                            "external_representation": 0,
                            "external_services": 0,
                            "internal_representation": 0,
                            "it_related_staff": 0,
                            "office_related": 0,
                            "office_rent": 0,
                            # Operating Costs - Salaries & Related
                            "salary": 0,
                            "variable_salary": 0,
                            "social_security": 0,
                            "other_expenses": 0,
                            "pension": 0,
                            # Legacy fields for compatibility
                            "price": 0,
                            "utr": 0,
                            "office_count": 0
                        }
                    
                    # Sum up numeric values
                    agg_entry = aggregated_entries[key]
                    # Workforce fields
                    agg_entry["recruitment"] += entry.get("recruitment", 0)
                    agg_entry["churn"] += entry.get("churn", 0)
                    # Net Sales fields
                    agg_entry["consultant_time"] += entry.get("consultant_time", 0)
                    agg_entry["planned_absence"] += entry.get("planned_absence", 0)
                    agg_entry["unplanned_absence"] += entry.get("unplanned_absence", 0)
                    agg_entry["vacation_withdrawal"] += entry.get("vacation_withdrawal", 0)
                    agg_entry["vacation"] += entry.get("vacation", 0)
                    agg_entry["invoiced_time"] += entry.get("invoiced_time", 0)
                    agg_entry["average_price"] += entry.get("average_price", 0)
                    # Operating Costs - Expenses
                    agg_entry["client_loss"] += entry.get("client_loss", 0)
                    agg_entry["education"] += entry.get("education", 0)
                    agg_entry["external_representation"] += entry.get("external_representation", 0)
                    agg_entry["external_services"] += entry.get("external_services", 0)
                    agg_entry["internal_representation"] += entry.get("internal_representation", 0)
                    agg_entry["it_related_staff"] += entry.get("it_related_staff", 0)
                    agg_entry["office_related"] += entry.get("office_related", 0)
                    agg_entry["office_rent"] += entry.get("office_rent", 0)
                    # Operating Costs - Salaries & Related
                    agg_entry["salary"] += entry.get("salary", 0)
                    agg_entry["variable_salary"] += entry.get("variable_salary", 0)
                    agg_entry["social_security"] += entry.get("social_security", 0)
                    agg_entry["other_expenses"] += entry.get("other_expenses", 0)
                    agg_entry["pension"] += entry.get("pension", 0)
                    # Legacy fields
                    agg_entry["price"] += entry.get("price", 0)
                    agg_entry["utr"] += entry.get("utr", 0)
                    agg_entry["office_count"] += 1
            
            # Calculate weighted averages for pricing and rate fields, sum for cost fields
            for entry in aggregated_entries.values():
                if entry["office_count"] > 0:
                    # Average these fields across offices
                    entry["average_price"] = round(entry["average_price"] / entry["office_count"])
                    entry["consultant_time"] = round(entry["consultant_time"] / entry["office_count"])
                    entry["planned_absence"] = round(entry["planned_absence"] / entry["office_count"])
                    entry["unplanned_absence"] = round(entry["unplanned_absence"] / entry["office_count"])
                    entry["vacation_withdrawal"] = round(entry["vacation_withdrawal"] / entry["office_count"])
                    entry["vacation"] = round(entry["vacation"] / entry["office_count"])
                    entry["invoiced_time"] = round(entry["invoiced_time"] / entry["office_count"])
                    # Salary fields are averaged per person
                    entry["salary"] = round(entry["salary"] / entry["office_count"])
                    entry["variable_salary"] = round(entry["variable_salary"] / entry["office_count"])
                    entry["social_security"] = round(entry["social_security"] / entry["office_count"])
                    entry["pension"] = round(entry["pension"] / entry["office_count"])
                    # Legacy fields
                    if entry["price"] > 0:
                        entry["price"] = round(entry["price"] / entry["office_count"])
                    if entry["utr"] > 0:
                        entry["utr"] = round(entry["utr"] / entry["office_count"], 2)
                    # Note: Cost fields like client_loss, education, etc. are summed, not averaged
                
                # Remove office_count from final output
                del entry["office_count"]
            
            # Create aggregated monthly plan
            aggregated_plan = {
                "month": month,
                "year": year or (all_plans[0].get("year") if all_plans else 2025),
                "entries": list(aggregated_entries.values()),
                "offices_included": list(set(p.get("office_id") for p in month_plans)),
                "source_plans_count": len(month_plans)
            }
            
            aggregated_monthly_plans.append(aggregated_plan)
        
        # Calculate summary statistics
        total_entries = sum(len(plan["entries"]) for plan in aggregated_monthly_plans)
        roles_covered = set()
        for plan in aggregated_monthly_plans:
            for entry in plan["entries"]:
                roles_covered.add(entry["role"])
        
        months = [p["month"] for p in aggregated_monthly_plans]
        date_range = f"{min(months)}-{max(months)}" if months else None
        
        return {
            "aggregated_plans": aggregated_monthly_plans,
            "summary": {
                "total_offices": len(filtered_office_ids),
                "total_months": len(aggregated_monthly_plans),
                "total_entries": total_entries,
                "offices_included": sorted(list(filtered_office_ids)),
                "date_range": date_range,
                "roles_covered": sorted(list(roles_covered)),
                "aggregation_type": "journey_filtered" if journey else ("selected_offices" if office_ids else "all_offices"),
                "filters_applied": {
                    "year": year,
                    "office_ids": office_ids,
                    "journey": journey
                }
            }
        }

    def export_as_simulation_baseline(
        self, 
        office_id: str, 
        year: int, 
        start_month: int = 1, 
        end_month: int = 12
    ) -> Dict[str, Any]:
        """Export business plan data as simulation baseline format
        
        Args:
            office_id: Office to export
            year: Year to export
            start_month: Starting month (1-12)
            end_month: Ending month (1-12)
            
        Returns:
            BaselineInput compatible structure
        """
        plans = self.get_plans(office_id=office_id, year=year)
        if not plans:
            raise ValueError(f"No business plans found for office {office_id} in year {year}")
        
        # Filter plans to specified month range
        filtered_plans = [
            plan for plan in plans 
            if start_month <= plan["month"] <= end_month
        ]
        
        if not filtered_plans:
            raise ValueError(f"No plans found for months {start_month}-{end_month}")
        
        # Convert to BaselineInput format expected by BaselineInputGridV2
        global_data = {
            "recruitment": {},
            "churn": {}
        }
        
        # Group by role and process entries
        for plan in filtered_plans:
            month_str = f"{year}{plan['month']:02d}"  # YYYYMM format
            
            for entry in plan.get("entries", []):
                role = entry["role"]
                
                # Initialize role structure if not exists
                if role not in global_data["recruitment"]:
                    global_data["recruitment"][role] = {"levels": {}}
                    global_data["churn"][role] = {"levels": {}}
                
                # Handle leveled vs flat roles
                level = entry.get("level")
                if level:
                    # Leveled role (e.g., Consultant) - with levels wrapper
                    if level not in global_data["recruitment"][role]["levels"]:
                        global_data["recruitment"][role]["levels"][level] = {
                            "recruitment": {"values": {}},
                            "churn": {"values": {}}
                        }
                        global_data["churn"][role]["levels"][level] = {
                            "recruitment": {"values": {}},
                            "churn": {"values": {}}
                        }
                    
                    global_data["recruitment"][role]["levels"][level]["recruitment"]["values"][month_str] = entry.get("recruitment", 0)
                    global_data["recruitment"][role]["levels"][level]["churn"]["values"][month_str] = entry.get("churn", 0)
                    # FIXED: Use actual churn data, not duplicated recruitment data
                    global_data["churn"][role]["levels"][level]["recruitment"]["values"][month_str] = 0  # No recruitment in churn section
                    global_data["churn"][role]["levels"][level]["churn"]["values"][month_str] = entry.get("churn", 0)
                else:
                    # Flat role (e.g., Operations) - still needs levels wrapper for consistency
                    if "default" not in global_data["recruitment"][role]["levels"]:
                        global_data["recruitment"][role]["levels"]["default"] = {
                            "recruitment": {"values": {}},
                            "churn": {"values": {}}
                        }
                        global_data["churn"][role]["levels"]["default"] = {
                            "recruitment": {"values": {}},
                            "churn": {"values": {}}
                        }
                    
                    global_data["recruitment"][role]["levels"]["default"]["recruitment"]["values"][month_str] = entry.get("recruitment", 0)
                    global_data["recruitment"][role]["levels"]["default"]["churn"]["values"][month_str] = entry.get("churn", 0)
                    # FIXED: Use actual churn data, not duplicated recruitment data
                    global_data["churn"][role]["levels"]["default"]["recruitment"]["values"][month_str] = 0  # No recruitment in churn section
                    global_data["churn"][role]["levels"]["default"]["churn"]["values"][month_str] = entry.get("churn", 0)
        
        return {
            "global": global_data
        }

    def export_aggregated_as_simulation_baseline(
        self,
        year: int,
        office_ids: Optional[List[str]] = None,
        journey: Optional[str] = None,
        start_month: int = 1,
        end_month: int = 12
    ) -> Dict[str, Any]:
        """Export aggregated business plan data as simulation baseline format
        
        Args:
            year: Year to export
            office_ids: List of office IDs to include (optional)
            journey: Journey type filter (optional)
            start_month: Starting month (1-12)
            end_month: Ending month (1-12)
            
        Returns:
            BaselineInput compatible structure with aggregated data
        """
        # Get aggregated plans
        aggregated_data = self.get_aggregated_plans(
            year=year,
            office_ids=office_ids,
            journey=journey
        )
        
        if not aggregated_data or not aggregated_data.get("aggregated_plans"):
            raise ValueError("No aggregated business plans found for specified criteria")
        
        # Filter to specified month range
        filtered_plans = [
            plan for plan in aggregated_data["aggregated_plans"]
            if start_month <= plan["month"] <= end_month
        ]
        
        if not filtered_plans:
            raise ValueError(f"No plans found for months {start_month}-{end_month}")
        
        # Convert to BaselineInput format expected by BaselineInputGridV2
        global_data = {
            "recruitment": {},
            "churn": {}
        }
        
        # Process aggregated entries
        for plan in filtered_plans:
            month_str = f"{year}{plan['month']:02d}"  # YYYYMM format
            
            for entry in plan.get("entries", []):
                role = entry["role"]
                
                # Initialize role structure if not exists
                if role not in global_data["recruitment"]:
                    global_data["recruitment"][role] = {"levels": {}}
                    global_data["churn"][role] = {"levels": {}}
                
                # Handle leveled vs flat roles
                level = entry.get("level")
                if level:
                    # Leveled role (e.g., Consultant) - with levels wrapper
                    if level not in global_data["recruitment"][role]["levels"]:
                        global_data["recruitment"][role]["levels"][level] = {
                            "recruitment": {"values": {}},
                            "churn": {"values": {}}
                        }
                        global_data["churn"][role]["levels"][level] = {
                            "recruitment": {"values": {}},
                            "churn": {"values": {}}
                        }
                    
                    global_data["recruitment"][role]["levels"][level]["recruitment"]["values"][month_str] = entry.get("recruitment", 0)
                    global_data["recruitment"][role]["levels"][level]["churn"]["values"][month_str] = entry.get("churn", 0)
                    # FIXED: Use actual churn data, not duplicated recruitment data
                    global_data["churn"][role]["levels"][level]["recruitment"]["values"][month_str] = 0  # No recruitment in churn section
                    global_data["churn"][role]["levels"][level]["churn"]["values"][month_str] = entry.get("churn", 0)
                else:
                    # Flat role (e.g., Operations) - still needs levels wrapper for consistency
                    if "default" not in global_data["recruitment"][role]["levels"]:
                        global_data["recruitment"][role]["levels"]["default"] = {
                            "recruitment": {"values": {}},
                            "churn": {"values": {}}
                        }
                        global_data["churn"][role]["levels"]["default"] = {
                            "recruitment": {"values": {}},
                            "churn": {"values": {}}
                        }
                    
                    global_data["recruitment"][role]["levels"]["default"]["recruitment"]["values"][month_str] = entry.get("recruitment", 0)
                    global_data["recruitment"][role]["levels"]["default"]["churn"]["values"][month_str] = entry.get("churn", 0)
                    # FIXED: Use actual churn data, not duplicated recruitment data
                    global_data["churn"][role]["levels"]["default"]["recruitment"]["values"][month_str] = 0  # No recruitment in churn section
                    global_data["churn"][role]["levels"]["default"]["churn"]["values"][month_str] = entry.get("churn", 0)
        
        return {
            "global": global_data,
            "metadata": {
                "source": "aggregated_business_plans",
                "offices_included": aggregated_data["summary"]["offices_included"],
                "year": year,
                "month_range": f"{start_month}-{end_month}"
            }
        }

    def get_unified_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get unified business plan in V2 engine format by aggregating monthly records
        
        Option A implementation: Aggregate-on-Demand
        This method takes a business plan ID and finds all related monthly records
        to create the unified yearly structure expected by the V2 engine.
        
        Args:
            plan_id: Business plan ID (any monthly record ID from the set)
            
        Returns:
            Unified business plan with monthly_plans structure or None if not found
        """
        # Get the base plan to extract office_id and year
        base_plan = self.get_plan(plan_id)
        if not base_plan:
            return None
        
        office_id = base_plan.get("office_id")
        year = base_plan.get("year")
        
        if not office_id or not year:
            return None
        
        # Get all plans for this office and year
        all_plans = self.get_plans(office_id=office_id, year=year)
        
        if not all_plans:
            return None
        
        # Build monthly_plans structure
        monthly_plans = {}
        
        for plan in all_plans:
            month = plan.get("month")
            if month:
                # Convert month to V2 engine format: "YYYY-MM"
                month_key = f"{year}-{month:02d}"
                
                # Transform entries to expected format
                monthly_plan = {
                    "month": month,
                    "year": year,
                    "entries": plan.get("entries", [])
                }
                
                monthly_plans[month_key] = monthly_plan
        
        # Return unified plan structure expected by V2 engine
        unified_plan = {
            "id": f"{office_id}-{year}",  # Create unified ID
            "office_id": office_id,
            "year": year,
            "monthly_plans": monthly_plans,
            "created_at": base_plan.get("created_at"),
            "updated_at": datetime.now().isoformat(),
            "source": "aggregated_monthly_records",
            "original_plan_count": len(all_plans)
        }
        
        return unified_plan

# Global instance
business_plan_storage = BusinessPlanStorage()