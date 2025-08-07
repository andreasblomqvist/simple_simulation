"""
Snapshot Integration Service - Bridges snapshots with simulation engine and existing services
"""
from typing import Dict, Any, Optional, List
from uuid import UUID
import logging

from .snapshot_service import get_snapshot_service, SnapshotService
from .simulation_engine import SimulationEngine
from .scenario_service import ScenarioService
from .config_service import config_service
from ..database.models import SnapshotSource, SnapshotAction

logger = logging.getLogger(__name__)


class SnapshotIntegrationService:
    """Service for integrating snapshots with simulation engine and other services"""
    
    def __init__(self):
        self.snapshot_service = get_snapshot_service()
        self.simulation_engine = SimulationEngine()
    
    async def create_snapshot_from_scenario_result(
        self,
        scenario_id: str,
        simulation_results: Dict[str, Any],
        snapshot_date: str,
        office_name: str,
        snapshot_name: Optional[str] = None,
        description: Optional[str] = None,
        created_by: str = "system"
    ) -> str:
        """Create a snapshot from scenario simulation results"""
        
        if not snapshot_name:
            snapshot_name = f"Scenario {scenario_id} - {snapshot_date}"
        
        if not description:
            description = f"Snapshot created from scenario {scenario_id} results for {snapshot_date}"
        
        # Create the snapshot using the snapshot service
        from .snapshot_service import SimulationSnapshotRequest
        
        request = SimulationSnapshotRequest(
            office_name=office_name,
            simulation_results=simulation_results,
            snapshot_date=snapshot_date,
            snapshot_name=snapshot_name,
            description=description,
            tags=[f"scenario:{scenario_id}", "simulation", snapshot_date[:4]],  # year tag
            created_by=created_by
        )
        
        try:
            snapshot = await self.snapshot_service.create_snapshot_from_simulation(request)
            
            # Record usage in scenario
            if scenario_id:
                scenario_uuid = UUID(scenario_id) if len(scenario_id) == 36 else None
                if scenario_uuid:
                    await self.snapshot_service.use_snapshot_in_scenario(
                        snapshot_id=snapshot.id,
                        scenario_id=scenario_uuid,
                        user_id=created_by
                    )
            
            logger.info(f"Created snapshot from scenario {scenario_id}: {snapshot.id}")
            return str(snapshot.id)
            
        except Exception as e:
            logger.error(f"Failed to create snapshot from scenario {scenario_id}: {e}")
            raise
    
    async def get_baseline_for_scenario(
        self,
        office_name: str,
        baseline_type: str = "current",
        snapshot_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get baseline data for scenario execution"""
        
        if baseline_type == "snapshot" and snapshot_id:
            # Use specific snapshot as baseline
            snapshot = await self.snapshot_service.get_snapshot(snapshot_id)
            if not snapshot:
                raise ValueError(f"Snapshot {snapshot_id} not found")
            
            return self.snapshot_service.get_baseline_input_from_snapshot(snapshot)
        
        elif baseline_type == "default":
            # Use office default snapshot
            office_id = await self._get_office_id_by_name(office_name)
            if office_id:
                default_snapshot = await self.snapshot_service.get_default_snapshot(office_id)
                if default_snapshot:
                    return self.snapshot_service.get_baseline_input_from_snapshot(default_snapshot)
        
        # Fall back to current config data
        return await self._get_current_baseline(office_name)
    
    async def create_snapshots_from_simulation_timeline(
        self,
        simulation_results: Dict[str, Any],
        office_name: str,
        scenario_id: Optional[str] = None,
        months_to_snapshot: Optional[List[str]] = None,
        created_by: str = "system"
    ) -> List[UUID]:
        """Create multiple snapshots from different points in simulation timeline"""
        
        created_snapshots = []
        
        if not months_to_snapshot:
            # Default to December of each year
            years = list(simulation_results.keys())
            months_to_snapshot = [f"{year}12" for year in years]
        
        for snapshot_date in months_to_snapshot:
            try:
                snapshot_name = f"Timeline {scenario_id} - {snapshot_date}" if scenario_id else f"Simulation {snapshot_date}"
                
                snapshot_id = await self.create_snapshot_from_scenario_result(
                    scenario_id=scenario_id or "timeline",
                    simulation_results=simulation_results,
                    snapshot_date=snapshot_date,
                    office_name=office_name,
                    snapshot_name=snapshot_name,
                    description=f"Timeline snapshot for {snapshot_date}",
                    created_by=created_by
                )
                
                created_snapshots.append(UUID(snapshot_id))
                
            except Exception as e:
                logger.warning(f"Failed to create snapshot for {snapshot_date}: {e}")
                continue
        
        logger.info(f"Created {len(created_snapshots)} timeline snapshots")
        return created_snapshots
    
    async def compare_scenario_snapshots(
        self,
        baseline_snapshot_id: UUID,
        result_snapshot_id: UUID,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compare baseline and result snapshots from a scenario"""
        
        try:
            comparison = await self.snapshot_service.compare_snapshots(
                snapshot_1_id=baseline_snapshot_id,
                snapshot_2_id=result_snapshot_id,
                user_id=user_id
            )
            
            return {
                "baseline_snapshot": {
                    "id": str(comparison.snapshot_1.id),
                    "name": comparison.snapshot_1.snapshot_name,
                    "date": comparison.snapshot_1.snapshot_date,
                    "total_fte": comparison.snapshot_1.total_fte
                },
                "result_snapshot": {
                    "id": str(comparison.snapshot_2.id),
                    "name": comparison.snapshot_2.snapshot_name,
                    "date": comparison.snapshot_2.snapshot_date,
                    "total_fte": comparison.snapshot_2.total_fte
                },
                "total_fte_delta": comparison.total_fte_delta,
                "workforce_changes": comparison.workforce_changes,
                "insights": comparison.insights
            }
            
        except Exception as e:
            logger.error(f"Failed to compare scenario snapshots: {e}")
            raise
    
    async def validate_snapshot_for_simulation(
        self,
        snapshot_id: UUID
    ) -> Dict[str, Any]:
        """Validate that a snapshot can be used for simulation"""
        
        snapshot = await self.snapshot_service.get_snapshot(snapshot_id)
        if not snapshot:
            return {"valid": False, "error": "Snapshot not found"}
        
        # Check if snapshot has workforce data
        if not snapshot.workforce:
            return {"valid": False, "error": "Snapshot has no workforce data"}
        
        # Check if snapshot is approved (optional warning)
        warnings = []
        if not snapshot.is_approved:
            warnings.append("Snapshot is not approved for official use")
        
        # Check data completeness
        roles = set()
        total_fte = 0
        for entry in snapshot.workforce:
            roles.add(entry.role)
            total_fte += entry.fte
        
        if total_fte == 0:
            return {"valid": False, "error": "Snapshot has zero total FTE"}
        
        return {
            "valid": True,
            "warnings": warnings,
            "summary": {
                "total_fte": total_fte,
                "roles_count": len(roles),
                "roles": list(roles),
                "snapshot_date": snapshot.snapshot_date,
                "source": snapshot.source.value
            }
        }
    
    async def get_office_snapshot_history(
        self,
        office_name: str,
        include_simulation_snapshots: bool = True
    ) -> List[Dict[str, Any]]:
        """Get historical snapshots for an office"""
        
        office_id = await self._get_office_id_by_name(office_name)
        if not office_id:
            return []
        
        snapshots = await self.snapshot_service.get_office_snapshots(office_id)
        
        history = []
        for snapshot in snapshots:
            # Filter simulation snapshots if requested
            if not include_simulation_snapshots and snapshot.source == SnapshotSource.SIMULATION:
                continue
            
            history.append({
                "id": str(snapshot.id),
                "name": snapshot.snapshot_name,
                "date": snapshot.snapshot_date,
                "total_fte": snapshot.total_fte,
                "source": snapshot.source.value,
                "is_default": snapshot.is_default,
                "is_approved": snapshot.is_approved,
                "created_at": snapshot.created_at.isoformat(),
                "created_by": snapshot.created_by,
                "tags": snapshot.tag_list
            })
        
        # Sort by date descending
        history.sort(key=lambda x: x["date"], reverse=True)
        return history
    
    # Private helper methods
    
    async def _get_current_baseline(self, office_name: str) -> Dict[str, Any]:
        """Get current baseline from config service"""
        
        config = config_service.get_config()
        if office_name not in config:
            raise ValueError(f"Office '{office_name}' not found in configuration")
        
        office_data = config[office_name]
        roles = office_data.get("roles", {})
        
        # Transform to baseline_input format
        global_data = {}
        
        for role_name, role_data in roles.items():
            if isinstance(role_data, dict):
                # Check if it's leveled or flat
                has_levels = any(
                    isinstance(level_data, dict) and "fte" in level_data
                    for level_data in role_data.values()
                )
                
                if has_levels:
                    # Leveled role
                    global_data[role_name] = {"levels": {}}
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, dict) and "fte" in level_data:
                            global_data[role_name]["levels"][level_name] = {
                                "recruitment": {"values": {}},
                                "churn": {"values": {}}
                            }
                else:
                    # Flat role
                    global_data[role_name] = {
                        "recruitment": {"values": {}},
                        "churn": {"values": {}}
                    }
        
        return {"global_data": global_data}
    
    async def _get_office_id_by_name(self, office_name: str) -> Optional[UUID]:
        """Get office UUID by name"""
        
        # This is a simplified implementation
        # In a real system, this would query the offices table
        from uuid import uuid4
        
        # For now, generate a consistent UUID based on office name
        # In production, this should be replaced with proper database lookup
        config = config_service.get_config()
        if office_name in config:
            # Generate a deterministic UUID from the office name
            import hashlib
            hash_input = office_name.encode('utf-8')
            hash_hex = hashlib.md5(hash_input).hexdigest()
            
            # Convert hash to UUID format
            uuid_str = f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"
            return UUID(uuid_str)
        
        return None


# Global service instance
_integration_service: Optional[SnapshotIntegrationService] = None


def get_snapshot_integration_service() -> SnapshotIntegrationService:
    """Get the global snapshot integration service instance"""
    global _integration_service
    if _integration_service is None:
        _integration_service = SnapshotIntegrationService()
    return _integration_service