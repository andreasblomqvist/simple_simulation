"""
Repository pattern for population snapshot data access
"""
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime
import logging

from sqlalchemy import select, delete, update, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import (
    PopulationSnapshot, SnapshotWorkforce, SnapshotTag, 
    SnapshotComparison, SnapshotAuditLog, SnapshotSource, SnapshotAction
)

logger = logging.getLogger(__name__)


class SnapshotRepository:
    """Repository for population snapshot data operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_snapshot(
        self,
        office_id: UUID,
        snapshot_name: str,
        snapshot_date: str,
        total_fte: int,
        source: SnapshotSource,
        created_by: str,
        description: Optional[str] = None,
        workforce_data: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_default: bool = False,
        is_approved: bool = False
    ) -> PopulationSnapshot:
        """Create a new population snapshot"""
        
        # Create the snapshot
        snapshot = PopulationSnapshot(
            id=uuid4(),
            office_id=office_id,
            snapshot_name=snapshot_name,
            snapshot_date=snapshot_date,
            description=description,
            total_fte=total_fte,
            source=source,
            created_by=created_by,
            metadata=metadata or {},
            is_default=is_default,
            is_approved=is_approved
        )
        
        self.session.add(snapshot)
        await self.session.flush()  # Get the ID
        
        # Add workforce data if provided
        if workforce_data:
            await self._add_workforce_data(snapshot.id, workforce_data)
        
        # Add tags if provided
        if tags:
            await self._add_tags(snapshot.id, tags)
        
        # Log creation
        await self._log_action(
            snapshot.id,
            SnapshotAction.CREATED,
            created_by,
            {"source": source.value, "total_fte": total_fte}
        )
        
        logger.info(f"Created snapshot '{snapshot_name}' for office {office_id}")
        return snapshot
    
    async def get_snapshot_by_id(self, snapshot_id: UUID) -> Optional[PopulationSnapshot]:
        """Get snapshot by ID with all related data"""
        query = (
            select(PopulationSnapshot)
            .options(
                selectinload(PopulationSnapshot.workforce),
                selectinload(PopulationSnapshot.tags),
                joinedload(PopulationSnapshot.office)
            )
            .where(PopulationSnapshot.id == snapshot_id)
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_snapshots_by_office(
        self,
        office_id: UUID,
        include_unapproved: bool = True,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[PopulationSnapshot]:
        """Get all snapshots for an office"""
        query = (
            select(PopulationSnapshot)
            .options(
                selectinload(PopulationSnapshot.workforce),
                selectinload(PopulationSnapshot.tags)
            )
            .where(PopulationSnapshot.office_id == office_id)
        )
        
        if not include_unapproved:
            query = query.where(PopulationSnapshot.is_approved == True)
        
        query = query.order_by(PopulationSnapshot.snapshot_date.desc(), PopulationSnapshot.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_default_snapshot(self, office_id: UUID) -> Optional[PopulationSnapshot]:
        """Get the default snapshot for an office"""
        query = (
            select(PopulationSnapshot)
            .options(
                selectinload(PopulationSnapshot.workforce),
                selectinload(PopulationSnapshot.tags)
            )
            .where(
                and_(
                    PopulationSnapshot.office_id == office_id,
                    PopulationSnapshot.is_default == True
                )
            )
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
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
        
        # Base query
        query = select(PopulationSnapshot).options(
            selectinload(PopulationSnapshot.workforce),
            selectinload(PopulationSnapshot.tags),
            joinedload(PopulationSnapshot.office)
        )
        
        # Apply filters
        filters = []
        
        if office_id:
            filters.append(PopulationSnapshot.office_id == office_id)
        
        if source:
            filters.append(PopulationSnapshot.source == source)
        
        if date_from:
            filters.append(PopulationSnapshot.snapshot_date >= date_from)
        
        if date_to:
            filters.append(PopulationSnapshot.snapshot_date <= date_to)
        
        if approved_only:
            filters.append(PopulationSnapshot.is_approved == True)
        
        if search_term:
            search_filter = or_(
                PopulationSnapshot.snapshot_name.ilike(f"%{search_term}%"),
                PopulationSnapshot.description.ilike(f"%{search_term}%")
            )
            filters.append(search_filter)
        
        if tags:
            # Join with tags table to filter by tags
            query = query.join(SnapshotTag).where(SnapshotTag.tag.in_(tags))
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count(PopulationSnapshot.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        
        total_result = await self.session.execute(count_query)
        total_count = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(
            PopulationSnapshot.snapshot_date.desc(),
            PopulationSnapshot.created_at.desc()
        ).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        snapshots = result.scalars().all()
        
        return snapshots, total_count
    
    async def update_snapshot(
        self,
        snapshot_id: UUID,
        updates: Dict[str, Any],
        updated_by: Optional[str] = None
    ) -> Optional[PopulationSnapshot]:
        """Update snapshot properties"""
        
        # Build update statement
        update_data = {}
        for key, value in updates.items():
            if hasattr(PopulationSnapshot, key):
                update_data[key] = value
        
        if not update_data:
            return await self.get_snapshot_by_id(snapshot_id)
        
        # Execute update
        stmt = (
            update(PopulationSnapshot)
            .where(PopulationSnapshot.id == snapshot_id)
            .values(**update_data)
            .returning(PopulationSnapshot)
        )
        
        result = await self.session.execute(stmt)
        snapshot = result.scalar_one_or_none()
        
        if snapshot and updated_by:
            await self._log_action(
                snapshot_id,
                SnapshotAction.MODIFIED,
                updated_by,
                {"updates": list(update_data.keys())}
            )
        
        return snapshot
    
    async def set_default_snapshot(
        self,
        snapshot_id: UUID,
        user_id: Optional[str] = None
    ) -> bool:
        """Set a snapshot as the default for its office"""
        
        # Get the snapshot to find the office
        snapshot = await self.get_snapshot_by_id(snapshot_id)
        if not snapshot:
            return False
        
        # Clear other defaults for this office (handled by database trigger)
        # Update this snapshot to be default
        await self.update_snapshot(
            snapshot_id,
            {"is_default": True},
            user_id
        )
        
        if user_id:
            await self._log_action(
                snapshot_id,
                SnapshotAction.SET_DEFAULT,
                user_id,
                {"office_id": str(snapshot.office_id)}
            )
        
        return True
    
    async def approve_snapshot(
        self,
        snapshot_id: UUID,
        user_id: Optional[str] = None
    ) -> bool:
        """Approve a snapshot for official use"""
        
        result = await self.update_snapshot(
            snapshot_id,
            {"is_approved": True},
            user_id
        )
        
        if result and user_id:
            await self._log_action(
                snapshot_id,
                SnapshotAction.APPROVED,
                user_id,
                {}
            )
        
        return result is not None
    
    async def delete_snapshot(self, snapshot_id: UUID) -> bool:
        """Delete a snapshot and all related data"""
        
        stmt = delete(PopulationSnapshot).where(PopulationSnapshot.id == snapshot_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def update_workforce_data(
        self,
        snapshot_id: UUID,
        workforce_data: Dict[str, Any]
    ) -> bool:
        """Update workforce data for a snapshot"""
        
        # Delete existing workforce data
        await self.session.execute(
            delete(SnapshotWorkforce).where(SnapshotWorkforce.snapshot_id == snapshot_id)
        )
        
        # Add new workforce data
        await self._add_workforce_data(snapshot_id, workforce_data)
        
        # Update total FTE
        total_fte = await self._calculate_total_fte(workforce_data)
        await self.update_snapshot(snapshot_id, {"total_fte": total_fte})
        
        return True
    
    async def update_tags(
        self,
        snapshot_id: UUID,
        tags: List[str]
    ) -> bool:
        """Update tags for a snapshot"""
        
        # Delete existing tags
        await self.session.execute(
            delete(SnapshotTag).where(SnapshotTag.snapshot_id == snapshot_id)
        )
        
        # Add new tags
        await self._add_tags(snapshot_id, tags)
        return True
    
    async def record_usage(
        self,
        snapshot_id: UUID,
        action: SnapshotAction,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """Record snapshot usage in scenarios/plans"""
        
        # Update last used timestamp
        await self.update_snapshot(snapshot_id, {"last_used_at": datetime.utcnow()})
        
        # Log the usage
        await self._log_action(
            snapshot_id,
            action,
            user_id,
            {
                "entity_type": entity_type,
                "entity_id": str(entity_id) if entity_id else None
            }
        )
        
        return True
    
    async def get_audit_log(
        self,
        snapshot_id: UUID,
        limit: int = 50
    ) -> List[SnapshotAuditLog]:
        """Get audit log for a snapshot"""
        
        query = (
            select(SnapshotAuditLog)
            .where(SnapshotAuditLog.snapshot_id == snapshot_id)
            .order_by(SnapshotAuditLog.timestamp.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    # Private helper methods
    
    async def _add_workforce_data(
        self,
        snapshot_id: UUID,
        workforce_data: Dict[str, Any]
    ) -> None:
        """Add workforce data entries for a snapshot"""
        
        workforce_entries = []
        
        for role, role_data in workforce_data.items():
            if isinstance(role_data, dict):
                # Leveled role
                for level, fte in role_data.items():
                    if fte > 0:
                        workforce_entries.append(
                            SnapshotWorkforce(
                                snapshot_id=snapshot_id,
                                role=role,
                                level=level,
                                fte=int(fte)
                            )
                        )
            elif isinstance(role_data, (int, float)):
                # Flat role
                if role_data > 0:
                    workforce_entries.append(
                        SnapshotWorkforce(
                            snapshot_id=snapshot_id,
                            role=role,
                            level=None,
                            fte=int(role_data)
                        )
                    )
        
        if workforce_entries:
            self.session.add_all(workforce_entries)
    
    async def _add_tags(self, snapshot_id: UUID, tags: List[str]) -> None:
        """Add tags for a snapshot"""
        
        tag_entries = [
            SnapshotTag(snapshot_id=snapshot_id, tag=tag.strip())
            for tag in tags
            if tag.strip()
        ]
        
        if tag_entries:
            self.session.add_all(tag_entries)
    
    async def _log_action(
        self,
        snapshot_id: UUID,
        action: SnapshotAction,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an action in the audit trail"""
        
        log_entry = SnapshotAuditLog(
            snapshot_id=snapshot_id,
            action=action,
            user_id=user_id,
            details=details or {}
        )
        
        self.session.add(log_entry)
    
    async def _calculate_total_fte(self, workforce_data: Dict[str, Any]) -> int:
        """Calculate total FTE from workforce data"""
        
        total = 0
        for role, role_data in workforce_data.items():
            if isinstance(role_data, dict):
                # Leveled role
                total += sum(fte for fte in role_data.values() if isinstance(fte, (int, float)))
            elif isinstance(role_data, (int, float)):
                # Flat role
                total += role_data
        
        return int(total)