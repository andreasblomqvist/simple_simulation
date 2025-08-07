"""
Repository for snapshot comparison data operations
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import logging

from sqlalchemy import select, delete, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import SnapshotComparison, PopulationSnapshot

logger = logging.getLogger(__name__)


class ComparisonRepository:
    """Repository for snapshot comparison operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_comparison(
        self,
        snapshot_1_id: UUID,
        snapshot_2_id: UUID,
        delta_data: Dict[str, Any],
        compared_by: Optional[str] = None,
        insights: Optional[str] = None
    ) -> SnapshotComparison:
        """Create a new snapshot comparison record"""
        
        comparison = SnapshotComparison(
            id=uuid4(),
            snapshot_1_id=snapshot_1_id,
            snapshot_2_id=snapshot_2_id,
            delta_data=delta_data,
            compared_by=compared_by,
            insights=insights
        )
        
        self.session.add(comparison)
        await self.session.flush()
        
        logger.info(f"Created comparison between snapshots {snapshot_1_id} and {snapshot_2_id}")
        return comparison
    
    async def get_comparison(self, comparison_id: UUID) -> Optional[SnapshotComparison]:
        """Get a comparison by ID with related snapshots"""
        query = (
            select(SnapshotComparison)
            .options(
                joinedload(SnapshotComparison.snapshot_1).selectinload(PopulationSnapshot.workforce),
                joinedload(SnapshotComparison.snapshot_1).selectinload(PopulationSnapshot.tags),
                joinedload(SnapshotComparison.snapshot_2).selectinload(PopulationSnapshot.workforce),
                joinedload(SnapshotComparison.snapshot_2).selectinload(PopulationSnapshot.tags),
            )
            .where(SnapshotComparison.id == comparison_id)
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_comparisons_by_snapshot(
        self,
        snapshot_id: UUID,
        limit: int = 50
    ) -> List[SnapshotComparison]:
        """Get all comparisons involving a specific snapshot"""
        query = (
            select(SnapshotComparison)
            .options(
                joinedload(SnapshotComparison.snapshot_1),
                joinedload(SnapshotComparison.snapshot_2)
            )
            .where(
                and_(
                    (SnapshotComparison.snapshot_1_id == snapshot_id) |
                    (SnapshotComparison.snapshot_2_id == snapshot_id)
                )
            )
            .order_by(SnapshotComparison.comparison_date.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def find_existing_comparison(
        self,
        snapshot_1_id: UUID,
        snapshot_2_id: UUID
    ) -> Optional[SnapshotComparison]:
        """Find existing comparison between two snapshots (in either order)"""
        query = (
            select(SnapshotComparison)
            .options(
                joinedload(SnapshotComparison.snapshot_1),
                joinedload(SnapshotComparison.snapshot_2)
            )
            .where(
                or_(
                    and_(
                        SnapshotComparison.snapshot_1_id == snapshot_1_id,
                        SnapshotComparison.snapshot_2_id == snapshot_2_id
                    ),
                    and_(
                        SnapshotComparison.snapshot_1_id == snapshot_2_id,
                        SnapshotComparison.snapshot_2_id == snapshot_1_id
                    )
                )
            )
            .order_by(SnapshotComparison.comparison_date.desc())
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def delete_comparison(self, comparison_id: UUID) -> bool:
        """Delete a comparison"""
        stmt = delete(SnapshotComparison).where(SnapshotComparison.id == comparison_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def delete_comparisons_by_snapshot(self, snapshot_id: UUID) -> int:
        """Delete all comparisons involving a specific snapshot"""
        stmt = (
            delete(SnapshotComparison)
            .where(
                (SnapshotComparison.snapshot_1_id == snapshot_id) |
                (SnapshotComparison.snapshot_2_id == snapshot_id)
            )
        )
        
        result = await self.session.execute(stmt)
        return result.rowcount