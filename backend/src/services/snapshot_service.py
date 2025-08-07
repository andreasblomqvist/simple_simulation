"""
Snapshot Service - Business logic layer for population snapshot management
Integrates with simulation engine and existing office services
"""
from typing import List, Optional, Dict, Any, Tuple, Union
from uuid import UUID, uuid4
from datetime import datetime
import logging
from dataclasses import dataclass

from ..database.connection import get_database_manager
from ..database.models import SnapshotSource, SnapshotAction, PopulationSnapshot
from ..repositories.snapshot_repository import SnapshotRepository
from .config_service import config_service
from .simulation_engine import SimulationEngine
from .scenario_service import ScenarioService

logger = logging.getLogger(__name__)


@dataclass
class SnapshotCreationRequest:
    """Request model for creating snapshots"""
    office_id: UUID
    snapshot_name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_default: bool = False
    created_by: str = "system"


@dataclass
class SimulationSnapshotRequest:
    """Request for creating snapshot from simulation results"""
    office_name: str
    simulation_results: Dict[str, Any]
    snapshot_date: str  # YYYYMM format
    snapshot_name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    created_by: str = "system"


@dataclass
class SnapshotComparison:
    """Model for snapshot comparison results"""
    snapshot_1: PopulationSnapshot
    snapshot_2: PopulationSnapshot
    total_fte_delta: int
    workforce_changes: Dict[str, Any]
    insights: List[str]


class SnapshotService:
    """Service layer for population snapshot management"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        self.simulation_engine = SimulationEngine()
    
    async def create_snapshot_from_current(
        self,
        request: SnapshotCreationRequest
    ) -> PopulationSnapshot:
        """Create a snapshot from current office workforce"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            
            # Get current workforce data from config service
            workforce_data = await self._get_current_workforce_data(request.office_id)
            
            # Calculate snapshot date (current month)
            snapshot_date = datetime.now().strftime("%Y%m")
            
            # Calculate total FTE
            total_fte = self._calculate_total_fte(workforce_data)
            
            # Create the snapshot
            snapshot = await repo.create_snapshot(
                office_id=request.office_id,
                snapshot_name=request.snapshot_name,
                snapshot_date=snapshot_date,
                total_fte=total_fte,
                source=SnapshotSource.CURRENT,
                created_by=request.created_by,
                description=request.description,
                workforce_data=workforce_data,
                tags=request.tags,
                is_default=request.is_default
            )
            
            logger.info(f"Created snapshot from current workforce: {request.snapshot_name}")
            return snapshot
    
    async def create_snapshot_from_simulation(
        self,
        request: SimulationSnapshotRequest
    ) -> PopulationSnapshot:
        """Create a snapshot from simulation results"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            
            # Get office ID from name
            office_id = await self._get_office_id_by_name(request.office_name)
            if not office_id:
                raise ValueError(f"Office '{request.office_name}' not found")
            
            # Extract workforce data from simulation results
            workforce_data = self._extract_workforce_from_simulation(
                request.simulation_results,
                request.office_name,
                request.snapshot_date
            )
            
            # Calculate total FTE
            total_fte = self._calculate_total_fte(workforce_data)
            
            # Create metadata about the simulation
            metadata = {
                "simulation_source": "scenario_results",
                "extraction_date": request.snapshot_date,
                "office_name": request.office_name
            }
            
            # Create the snapshot
            snapshot = await repo.create_snapshot(
                office_id=office_id,
                snapshot_name=request.snapshot_name,
                snapshot_date=request.snapshot_date,
                total_fte=total_fte,
                source=SnapshotSource.SIMULATION,
                created_by=request.created_by,
                description=request.description,
                workforce_data=workforce_data,
                tags=request.tags,
                metadata=metadata
            )
            
            logger.info(f"Created snapshot from simulation: {request.snapshot_name}")
            return snapshot
    
    async def create_snapshot_from_business_plan(
        self,
        office_id: UUID,
        business_plan_data: Dict[str, Any],
        snapshot_name: str,
        snapshot_date: str,
        created_by: str = "system",
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> PopulationSnapshot:
        """Create a snapshot from business plan data"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            
            # Transform business plan data to workforce format
            workforce_data = self._transform_business_plan_to_workforce(
                business_plan_data,
                snapshot_date
            )
            
            # Calculate total FTE
            total_fte = self._calculate_total_fte(workforce_data)
            
            # Create metadata
            metadata = {
                "business_plan_source": True,
                "plan_date": snapshot_date
            }
            
            # Create the snapshot
            snapshot = await repo.create_snapshot(
                office_id=office_id,
                snapshot_name=snapshot_name,
                snapshot_date=snapshot_date,
                total_fte=total_fte,
                source=SnapshotSource.BUSINESS_PLAN,
                created_by=created_by,
                description=description,
                workforce_data=workforce_data,
                tags=tags,
                metadata=metadata
            )
            
            logger.info(f"Created snapshot from business plan: {snapshot_name}")
            return snapshot
    
    async def get_snapshot(self, snapshot_id: UUID) -> Optional[PopulationSnapshot]:
        """Get a snapshot by ID"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.get_snapshot_by_id(snapshot_id)
    
    async def get_office_snapshots(
        self,
        office_id: UUID,
        approved_only: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[PopulationSnapshot]:
        """Get all snapshots for an office"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.get_snapshots_by_office(
                office_id=office_id,
                include_unapproved=not approved_only,
                limit=limit,
                offset=offset
            )
    
    async def get_default_snapshot(self, office_id: UUID) -> Optional[PopulationSnapshot]:
        """Get the default snapshot for an office"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.get_default_snapshot(office_id)
    
    async def search_snapshots(
        self,
        office_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        source: Optional[SnapshotSource] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        search_term: Optional[str] = None,
        approved_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[PopulationSnapshot], int]:
        """Search snapshots with filters"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.search_snapshots(
                office_id=office_id,
                tags=tags,
                source=source,
                date_from=date_from,
                date_to=date_to,
                search_term=search_term,
                approved_only=approved_only,
                limit=limit,
                offset=offset
            )
    
    async def update_snapshot(
        self,
        snapshot_id: UUID,
        updates: Dict[str, Any],
        updated_by: Optional[str] = None
    ) -> Optional[PopulationSnapshot]:
        """Update snapshot properties"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.update_snapshot(snapshot_id, updates, updated_by)
    
    async def set_default_snapshot(
        self,
        snapshot_id: UUID,
        user_id: Optional[str] = None
    ) -> bool:
        """Set a snapshot as the default for its office"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.set_default_snapshot(snapshot_id, user_id)
    
    async def approve_snapshot(
        self,
        snapshot_id: UUID,
        user_id: Optional[str] = None
    ) -> bool:
        """Approve a snapshot for official use"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.approve_snapshot(snapshot_id, user_id)
    
    async def delete_snapshot(self, snapshot_id: UUID) -> bool:
        """Delete a snapshot"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.delete_snapshot(snapshot_id)
    
    async def update_workforce_data(
        self,
        snapshot_id: UUID,
        workforce_data: Dict[str, Any]
    ) -> bool:
        """Update workforce data for a snapshot"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.update_workforce_data(snapshot_id, workforce_data)
    
    async def update_tags(
        self,
        snapshot_id: UUID,
        tags: List[str]
    ) -> bool:
        """Update tags for a snapshot"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.update_tags(snapshot_id, tags)
    
    async def compare_snapshots(
        self,
        snapshot_1_id: UUID,
        snapshot_2_id: UUID,
        user_id: Optional[str] = None
    ) -> SnapshotComparison:
        """Compare two snapshots and generate insights"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            
            # Get both snapshots
            snapshot_1 = await repo.get_snapshot_by_id(snapshot_1_id)
            snapshot_2 = await repo.get_snapshot_by_id(snapshot_2_id)
            
            if not snapshot_1 or not snapshot_2:
                raise ValueError("One or both snapshots not found")
            
            # Calculate workforce comparison
            workforce_1 = self._build_workforce_map(snapshot_1)
            workforce_2 = self._build_workforce_map(snapshot_2)
            
            # Calculate deltas
            total_fte_delta = snapshot_2.total_fte - snapshot_1.total_fte
            workforce_changes = self._calculate_workforce_changes(workforce_1, workforce_2)
            
            # Generate insights
            insights = self._generate_comparison_insights(
                snapshot_1, snapshot_2, total_fte_delta, workforce_changes
            )
            
            return SnapshotComparison(
                snapshot_1=snapshot_1,
                snapshot_2=snapshot_2,
                total_fte_delta=total_fte_delta,
                workforce_changes=workforce_changes,
                insights=insights
            )
    
    async def use_snapshot_in_scenario(
        self,
        snapshot_id: UUID,
        scenario_id: UUID,
        user_id: Optional[str] = None
    ) -> bool:
        """Record usage of snapshot in a scenario"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.record_usage(
                snapshot_id=snapshot_id,
                action=SnapshotAction.USED_IN_SCENARIO,
                entity_type="scenario",
                entity_id=scenario_id,
                user_id=user_id
            )
    
    async def use_snapshot_in_business_plan(
        self,
        snapshot_id: UUID,
        business_plan_id: UUID,
        user_id: Optional[str] = None
    ) -> bool:
        """Record usage of snapshot in a business plan"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            return await repo.record_usage(
                snapshot_id=snapshot_id,
                action=SnapshotAction.USED_IN_PLAN,
                entity_type="business_plan",
                entity_id=business_plan_id,
                user_id=user_id
            )
    
    async def get_audit_log(
        self,
        snapshot_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get audit log for a snapshot"""
        
        async with self.db_manager.get_session_context() as session:
            repo = SnapshotRepository(session)
            logs = await repo.get_audit_log(snapshot_id, limit)
            
            return [
                {
                    "id": str(log.id),
                    "action": log.action.value,
                    "entity_type": log.entity_type,
                    "entity_id": str(log.entity_id) if log.entity_id else None,
                    "user_id": log.user_id,
                    "timestamp": log.timestamp.isoformat(),
                    "details": log.details
                }
                for log in logs
            ]
    
    # Integration methods for simulation engine
    
    def get_baseline_input_from_snapshot(
        self,
        snapshot: PopulationSnapshot
    ) -> Dict[str, Any]:
        """Convert snapshot to baseline_input format for simulation engine"""
        
        workforce_data = {}
        for entry in snapshot.workforce:
            role = entry.role
            level = entry.level
            fte = entry.fte
            
            if level:
                # Leveled role
                if role not in workforce_data:
                    workforce_data[role] = {"levels": {}}
                
                workforce_data[role]["levels"][level] = {
                    "recruitment": {"values": {}},
                    "churn": {"values": {}}
                }
            else:
                # Flat role
                workforce_data[role] = {
                    "recruitment": {"values": {}},
                    "churn": {"values": {}}
                }
        
        return {"global_data": workforce_data}
    
    # Private helper methods
    
    async def _get_current_workforce_data(self, office_id: UUID) -> Dict[str, Any]:
        """Get current workforce data from config service"""
        
        # Convert UUID to string for config service
        office_name = await self._get_office_name_by_id(office_id)
        if not office_name:
            raise ValueError(f"Office with ID {office_id} not found")
        
        config = config_service.get_config()
        if office_name not in config:
            raise ValueError(f"Office '{office_name}' not found in configuration")
        
        office_data = config[office_name]
        roles = office_data.get("roles", {})
        
        workforce_data = {}
        for role_name, role_data in roles.items():
            if isinstance(role_data, dict):
                # Check if it's leveled (has sub-levels) or flat
                has_levels = any(
                    isinstance(level_data, dict) and "fte" in level_data
                    for level_data in role_data.values()
                )
                
                if has_levels:
                    # Leveled role
                    workforce_data[role_name] = {}
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, dict) and "fte" in level_data:
                            workforce_data[role_name][level_name] = level_data["fte"]
                else:
                    # Flat role (treat the whole role as one entry)
                    total_fte = sum(
                        level_data.get("fte", 0) if isinstance(level_data, dict) else 0
                        for level_data in role_data.values()
                    )
                    workforce_data[role_name] = total_fte
        
        return workforce_data
    
    def _extract_workforce_from_simulation(
        self,
        simulation_results: Dict[str, Any],
        office_name: str,
        snapshot_date: str
    ) -> Dict[str, Any]:
        """Extract workforce data from simulation results for a specific date"""
        
        workforce_data = {}
        
        # Navigate simulation results structure: year -> office -> role -> level/month
        year = snapshot_date[:4]
        month_index = int(snapshot_date[4:]) - 1  # Convert to 0-based index
        
        if year not in simulation_results:
            logger.warning(f"Year {year} not found in simulation results")
            return workforce_data
        
        year_data = simulation_results[year]
        if office_name not in year_data:
            logger.warning(f"Office {office_name} not found in simulation results for {year}")
            return workforce_data
        
        office_data = year_data[office_name]["roles"]
        
        for role_name, role_data in office_data.items():
            if isinstance(role_data, dict) and not isinstance(list(role_data.values())[0], list):
                # Leveled role: role -> level -> [month_values]
                workforce_data[role_name] = {}
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, list) and month_index < len(level_data):
                        fte = level_data[month_index]
                        if fte > 0:
                            workforce_data[role_name][level_name] = int(fte)
            
            elif isinstance(role_data, list):
                # Flat role: role -> [month_values]
                if month_index < len(role_data):
                    fte = role_data[month_index]
                    if fte > 0:
                        workforce_data[role_name] = int(fte)
        
        return workforce_data
    
    def _transform_business_plan_to_workforce(
        self,
        business_plan_data: Dict[str, Any],
        snapshot_date: str
    ) -> Dict[str, Any]:
        """Transform business plan data to workforce format"""
        
        # This would depend on the business plan data structure
        # For now, assume it's already in the correct format
        # In practice, this would need to aggregate plan data by role/level
        
        workforce_data = {}
        
        # Extract year and month for filtering
        year = int(snapshot_date[:4])
        month = int(snapshot_date[4:])
        
        for entry in business_plan_data.get("entries", []):
            if entry.get("year") == year and entry.get("month") == month:
                role = entry.get("role")
                level = entry.get("level")
                
                # Use recruitment as base FTE (simplified logic)
                fte = entry.get("recruitment", 0)
                
                if level:
                    # Leveled role
                    if role not in workforce_data:
                        workforce_data[role] = {}
                    workforce_data[role][level] = workforce_data[role].get(level, 0) + fte
                else:
                    # Flat role
                    workforce_data[role] = workforce_data.get(role, 0) + fte
        
        return workforce_data
    
    async def _get_office_id_by_name(self, office_name: str) -> Optional[UUID]:
        """Get office UUID by name from config"""
        
        # In the current system, office names are used as IDs
        # This is a simplified conversion - in a real system,
        # you'd query the offices table
        try:
            return UUID(office_name) if len(office_name) == 36 else None
        except:
            # For now, generate a consistent UUID from office name
            # In production, this should query the database
            return uuid4()  # Placeholder
    
    async def _get_office_name_by_id(self, office_id: UUID) -> Optional[str]:
        """Get office name by UUID"""
        
        # Simplified - in production, query the offices table
        config = config_service.get_config()
        office_names = list(config.keys())
        
        if office_names:
            # Return first office name as placeholder
            # In production, this should query the database
            return office_names[0]
        
        return None
    
    def _calculate_total_fte(self, workforce_data: Dict[str, Any]) -> int:
        """Calculate total FTE from workforce data"""
        
        total = 0
        for role, role_data in workforce_data.items():
            if isinstance(role_data, dict):
                # Leveled role
                total += sum(
                    fte for fte in role_data.values() 
                    if isinstance(fte, (int, float))
                )
            elif isinstance(role_data, (int, float)):
                # Flat role
                total += role_data
        
        return int(total)
    
    def _build_workforce_map(self, snapshot: PopulationSnapshot) -> Dict[Tuple[str, str], int]:
        """Build a map of (role, level) -> FTE for comparison"""
        
        workforce_map = {}
        for entry in snapshot.workforce:
            key = (entry.role, entry.level or "")
            workforce_map[key] = entry.fte
        
        return workforce_map
    
    def _calculate_workforce_changes(
        self,
        workforce_1: Dict[Tuple[str, str], int],
        workforce_2: Dict[Tuple[str, str], int]
    ) -> Dict[str, Any]:
        """Calculate changes between two workforce maps"""
        
        changes = {}
        all_keys = set(workforce_1.keys()) | set(workforce_2.keys())
        
        for role, level in all_keys:
            fte_1 = workforce_1.get((role, level), 0)
            fte_2 = workforce_2.get((role, level), 0)
            
            if fte_1 != fte_2:
                if role not in changes:
                    changes[role] = {}
                
                level_key = level if level else "total"
                changes[role][level_key] = {
                    "from": fte_1,
                    "to": fte_2,
                    "change": fte_2 - fte_1,
                    "percent_change": (
                        ((fte_2 - fte_1) / fte_1 * 100) if fte_1 > 0 else 100.0
                    )
                }
        
        return changes
    
    def _generate_comparison_insights(
        self,
        snapshot_1: PopulationSnapshot,
        snapshot_2: PopulationSnapshot,
        total_fte_delta: int,
        workforce_changes: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from snapshot comparison"""
        
        insights = []
        
        # Overall change insight
        if total_fte_delta > 0:
            insights.append(f"Total workforce increased by {total_fte_delta} FTE")
        elif total_fte_delta < 0:
            insights.append(f"Total workforce decreased by {abs(total_fte_delta)} FTE")
        else:
            insights.append("Total workforce remained unchanged")
        
        # Role-specific insights
        for role, role_changes in workforce_changes.items():
            role_total_change = sum(
                change["change"] for change in role_changes.values()
            )
            
            if role_total_change > 0:
                insights.append(f"{role}: increased by {role_total_change} FTE")
            elif role_total_change < 0:
                insights.append(f"{role}: decreased by {abs(role_total_change)} FTE")
        
        # Time period insight
        date_1 = snapshot_1.snapshot_date
        date_2 = snapshot_2.snapshot_date
        insights.append(
            f"Comparison between {date_1[:4]}-{date_1[4:]} and {date_2[:4]}-{date_2[4:]}"
        )
        
        return insights


# Global service instance
_snapshot_service: Optional[SnapshotService] = None


def get_snapshot_service() -> SnapshotService:
    """Get the global snapshot service instance"""
    global _snapshot_service
    if _snapshot_service is None:
        _snapshot_service = SnapshotService()
    return _snapshot_service