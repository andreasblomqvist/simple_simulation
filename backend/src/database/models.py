"""
SQLAlchemy ORM models for SimpleSim database
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, 
    JSON, DECIMAL, UniqueConstraint, Index, Enum, Text,
    CheckConstraint, func, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class OfficeJourney(PyEnum):
    EMERGING = "emerging"
    ESTABLISHED = "established"
    MATURE = "mature"


class ProgressionCurve(PyEnum):
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    CUSTOM = "custom"


class CATStage(PyEnum):
    CAT0 = "CAT0"
    CAT6 = "CAT6"
    CAT12 = "CAT12"
    CAT18 = "CAT18"
    CAT24 = "CAT24"
    CAT30 = "CAT30"
    CAT36 = "CAT36"
    CAT42 = "CAT42"
    CAT48 = "CAT48"
    CAT54 = "CAT54"
    CAT60 = "CAT60"


class Level(PyEnum):
    A = "A"
    AC = "AC"
    C = "C"
    SRC = "SrC"
    AM = "AM"
    M = "M"
    SRM = "SrM"
    PI = "Pi"
    P = "P"
    X = "X"
    OPE = "OPE"


class JourneyStage(PyEnum):
    J1 = "J-1"
    J2 = "J-2"
    J3 = "J-3"


class SnapshotSource(PyEnum):
    MANUAL = "manual"
    SIMULATION = "simulation"
    IMPORT = "import"
    BUSINESS_PLAN = "business_plan"
    CURRENT = "current"


class SnapshotAction(PyEnum):
    CREATED = "created"
    MODIFIED = "modified"
    APPROVED = "approved"
    SET_DEFAULT = "set_default"
    USED_IN_SCENARIO = "used_in_scenario"
    USED_IN_PLAN = "used_in_plan"
    USED_IN_SIMULATION = "used_in_simulation"


class Office(Base):
    __tablename__ = 'offices'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, unique=True)
    journey = Column(Enum(OfficeJourney), nullable=False)
    timezone = Column(String(50), default='UTC')
    economic_parameters = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workforce = relationship("OfficeWorkforce", back_populates="office", cascade="all, delete-orphan")
    business_plans = relationship("OfficeBusinessPlan", back_populates="office", cascade="all, delete-orphan")
    progressions = relationship("OfficeProgression", back_populates="office", cascade="all, delete-orphan")
    snapshots = relationship("PopulationSnapshot", back_populates="office", cascade="all, delete-orphan")
    cat_matrices = relationship("CATMatrixConfiguration", back_populates="office", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Office(name='{self.name}', journey='{self.journey}')>"


class OfficeWorkforce(Base):
    __tablename__ = 'office_workforce'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    office_id = Column(UUID(as_uuid=True), ForeignKey('offices.id', ondelete='CASCADE'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    role = Column(String(50), nullable=False)
    level = Column(String(10), nullable=False)
    fte = Column(Integer, nullable=False, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    office = relationship("Office", back_populates="workforce")
    
    __table_args__ = (
        UniqueConstraint('office_id', 'start_date', 'role', 'level'),
        CheckConstraint('fte >= 0', name='check_fte_positive'),
        Index('idx_office_workforce_office_id', 'office_id'),
        Index('idx_office_workforce_role_level', 'role', 'level'),
        Index('idx_office_workforce_start_date', 'start_date'),
    )


class OfficeBusinessPlan(Base):
    __tablename__ = 'office_business_plans'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    office_id = Column(UUID(as_uuid=True), ForeignKey('offices.id', ondelete='CASCADE'), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    role = Column(String(50), nullable=False)
    level = Column(String(10), nullable=False)
    recruitment = Column(Integer, default=0)
    churn = Column(Integer, default=0)
    price = Column(DECIMAL(10, 2))
    utr = Column(DECIMAL(3, 2))
    salary = Column(DECIMAL(10, 2))
    baseline_snapshot_id = Column(UUID(as_uuid=True), ForeignKey('population_snapshots.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    office = relationship("Office", back_populates="business_plans")
    baseline_snapshot = relationship("PopulationSnapshot", back_populates="business_plans")
    
    __table_args__ = (
        UniqueConstraint('office_id', 'year', 'month', 'role', 'level'),
        CheckConstraint('year >= 2020 AND year <= 2050', name='check_year_range'),
        CheckConstraint('month >= 1 AND month <= 12', name='check_month_range'),
        CheckConstraint('recruitment >= 0', name='check_recruitment_positive'),
        CheckConstraint('churn >= 0', name='check_churn_positive'),
        CheckConstraint('price >= 0', name='check_price_positive'),
        CheckConstraint('utr >= 0 AND utr <= 1', name='check_utr_range'),
        CheckConstraint('salary >= 0', name='check_salary_positive'),
        Index('idx_business_plans_office_id', 'office_id'),
        Index('idx_business_plans_year_month', 'year', 'month'),
        Index('idx_business_plans_role_level', 'role', 'level'),
    )


class OfficeProgression(Base):
    __tablename__ = 'office_progressions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    office_id = Column(UUID(as_uuid=True), ForeignKey('offices.id', ondelete='CASCADE'), nullable=False)
    level = Column(String(10), nullable=False)
    monthly_rate = Column(DECIMAL(5, 4))
    curve_type = Column(Enum(ProgressionCurve), default=ProgressionCurve.LINEAR)
    custom_points = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    office = relationship("Office", back_populates="progressions")
    
    __table_args__ = (
        UniqueConstraint('office_id', 'level'),
        CheckConstraint('monthly_rate >= 0 AND monthly_rate <= 1', name='check_monthly_rate_range'),
        Index('idx_office_progressions_office_id', 'office_id'),
        Index('idx_office_progressions_level', 'level'),
    )


class PopulationSnapshot(Base):
    __tablename__ = 'population_snapshots'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    office_id = Column(UUID(as_uuid=True), ForeignKey('offices.id', ondelete='CASCADE'), nullable=False)
    snapshot_date = Column(String(6), nullable=False)  # YYYYMM format
    snapshot_name = Column(String(200), nullable=False)
    description = Column(Text)
    total_fte = Column(Integer, nullable=False)
    is_default = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    source = Column(Enum(SnapshotSource), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=False)
    last_used_at = Column(DateTime)
    snapshot_metadata = Column(JSON, default={})
    
    # Relationships
    office = relationship("Office", back_populates="snapshots")
    workforce = relationship("SnapshotWorkforce", back_populates="snapshot", cascade="all, delete-orphan")
    tags = relationship("SnapshotTag", back_populates="snapshot", cascade="all, delete-orphan")
    business_plans = relationship("OfficeBusinessPlan", back_populates="baseline_snapshot")
    audit_logs = relationship("SnapshotAuditLog", back_populates="snapshot", cascade="all, delete-orphan")
    
    # Comparisons where this snapshot is snapshot_1
    comparisons_as_first = relationship(
        "SnapshotComparison",
        foreign_keys="SnapshotComparison.snapshot_1_id",
        back_populates="snapshot_1",
        cascade="all, delete-orphan"
    )
    
    # Comparisons where this snapshot is snapshot_2
    comparisons_as_second = relationship(
        "SnapshotComparison",
        foreign_keys="SnapshotComparison.snapshot_2_id",
        back_populates="snapshot_2",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        UniqueConstraint('office_id', 'snapshot_name'),
        CheckConstraint('total_fte >= 0', name='check_total_fte_positive'),
        Index('idx_snapshots_office_date', 'office_id', 'snapshot_date'),
        Index('idx_snapshots_office_default', 'office_id', 'is_default'),
        Index('idx_snapshots_approved', 'office_id', 'is_approved'),
    )
    
    @validates('snapshot_date')
    def validate_snapshot_date(self, key, value):
        """Validate snapshot_date is in YYYYMM format"""
        if len(value) != 6 or not value.isdigit():
            raise ValueError("snapshot_date must be in YYYYMM format")
        year = int(value[:4])
        month = int(value[4:])
        if year < 2020 or year > 2050 or month < 1 or month > 12:
            raise ValueError("Invalid year or month in snapshot_date")
        return value
    
    @hybrid_property
    def tag_list(self):
        """Get list of tag names"""
        return [tag.tag for tag in self.tags]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary with workforce data"""
        workforce_data = {}
        for entry in self.workforce:
            if entry.level:
                # Leveled role
                if entry.role not in workforce_data:
                    workforce_data[entry.role] = {}
                workforce_data[entry.role][entry.level] = entry.fte
            else:
                # Flat role
                workforce_data[entry.role] = entry.fte
        
        return {
            'id': str(self.id),
            'office_id': str(self.office_id),
            'snapshot_date': self.snapshot_date,
            'snapshot_name': self.snapshot_name,
            'description': self.description,
            'total_fte': self.total_fte,
            'is_default': self.is_default,
            'is_approved': self.is_approved,
            'source': self.source.value if self.source else None,
            'workforce_data': workforce_data,
            'tags': self.tag_list,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'snapshot_metadata': self.snapshot_metadata
        }


class SnapshotWorkforce(Base):
    __tablename__ = 'snapshot_workforce'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey('population_snapshots.id', ondelete='CASCADE'), nullable=False)
    role = Column(String(50), nullable=False)
    level = Column(String(20))  # NULL for flat roles
    fte = Column(Integer, nullable=False)
    
    # Relationships
    snapshot = relationship("PopulationSnapshot", back_populates="workforce")
    
    __table_args__ = (
        UniqueConstraint('snapshot_id', 'role', 'level'),
        CheckConstraint('fte >= 0', name='check_workforce_fte_positive'),
        Index('idx_snapshot_workforce_snapshot', 'snapshot_id'),
        Index('idx_snapshot_workforce_role', 'role', 'level'),
    )


class SnapshotTag(Base):
    __tablename__ = 'snapshot_tags'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey('population_snapshots.id', ondelete='CASCADE'), nullable=False)
    tag = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    snapshot = relationship("PopulationSnapshot", back_populates="tags")
    
    __table_args__ = (
        UniqueConstraint('snapshot_id', 'tag'),
        Index('idx_snapshot_tags_snapshot', 'snapshot_id'),
        Index('idx_snapshot_tags_tag', 'tag'),
    )


class SnapshotComparison(Base):
    __tablename__ = 'snapshot_comparisons'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    snapshot_1_id = Column(UUID(as_uuid=True), ForeignKey('population_snapshots.id', ondelete='CASCADE'), nullable=False)
    snapshot_2_id = Column(UUID(as_uuid=True), ForeignKey('population_snapshots.id', ondelete='CASCADE'), nullable=False)
    comparison_date = Column(DateTime, default=datetime.utcnow)
    compared_by = Column(String(100))
    delta_data = Column(JSON, nullable=False)
    insights = Column(Text)
    
    # Relationships
    snapshot_1 = relationship("PopulationSnapshot", foreign_keys=[snapshot_1_id], back_populates="comparisons_as_first")
    snapshot_2 = relationship("PopulationSnapshot", foreign_keys=[snapshot_2_id], back_populates="comparisons_as_second")
    
    __table_args__ = (
        CheckConstraint('snapshot_1_id != snapshot_2_id', name='check_different_snapshots'),
        Index('idx_comparisons_snapshots', 'snapshot_1_id', 'snapshot_2_id'),
    )
    
    def calculate_delta(self) -> Dict[str, Any]:
        """Calculate the delta between two snapshots"""
        delta = {
            'total_fte_change': self.snapshot_2.total_fte - self.snapshot_1.total_fte,
            'workforce_changes': {}
        }
        
        # Build workforce maps
        workforce_1 = {}
        workforce_2 = {}
        
        for entry in self.snapshot_1.workforce:
            key = (entry.role, entry.level)
            workforce_1[key] = entry.fte
        
        for entry in self.snapshot_2.workforce:
            key = (entry.role, entry.level)
            workforce_2[key] = entry.fte
        
        # Calculate changes
        all_keys = set(workforce_1.keys()) | set(workforce_2.keys())
        for role, level in all_keys:
            fte_1 = workforce_1.get((role, level), 0)
            fte_2 = workforce_2.get((role, level), 0)
            if fte_1 != fte_2:
                if role not in delta['workforce_changes']:
                    delta['workforce_changes'][role] = {}
                level_key = level if level else 'total'
                delta['workforce_changes'][role][level_key] = {
                    'from': fte_1,
                    'to': fte_2,
                    'change': fte_2 - fte_1
                }
        
        return delta


class SnapshotAuditLog(Base):
    __tablename__ = 'snapshot_audit_log'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey('population_snapshots.id', ondelete='CASCADE'), nullable=False)
    action = Column(Enum(SnapshotAction), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    user_id = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, default={})
    
    # Relationships
    snapshot = relationship("PopulationSnapshot", back_populates="audit_logs")
    
    __table_args__ = (
        Index('idx_audit_snapshot', 'snapshot_id', 'timestamp'),
        Index('idx_audit_action', 'action', 'timestamp'),
    )


class CATMatrixConfiguration(Base):
    __tablename__ = 'cat_matrix_configurations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    office_id = Column(UUID(as_uuid=True), ForeignKey('offices.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Validation tracking
    last_validated_at = Column(DateTime)
    validation_status = Column(String(50), default='pending')
    validation_notes = Column(Text)
    
    # Relationships
    office = relationship("Office", back_populates="cat_matrices")
    level_configurations = relationship("CATLevelConfiguration", back_populates="matrix", cascade="all, delete-orphan")
    progression_probabilities = relationship("CATProgressionProbability", back_populates="matrix", cascade="all, delete-orphan")
    audit_logs = relationship("CATMatrixAuditLog", back_populates="matrix", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('office_id', 'name'),
        CheckConstraint('version > 0', name='check_version_positive'),
        Index('idx_cat_matrix_office_id', 'office_id'),
        Index('idx_cat_matrix_active', 'office_id', 'is_active'),
        Index('idx_cat_matrix_version', 'office_id', 'version'),
    )
    
    def __repr__(self):
        return f"<CATMatrixConfiguration(name='{self.name}', office_id='{self.office_id}')>"


class CATLevelConfiguration(Base):
    __tablename__ = 'cat_level_configurations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    matrix_id = Column(UUID(as_uuid=True), ForeignKey('cat_matrix_configurations.id', ondelete='CASCADE'), nullable=False)
    level = Column(Enum(Level), nullable=False)
    
    # Level-specific progression settings
    start_tenure = Column(Integer, nullable=False, default=0)
    time_on_level = Column(Integer, nullable=False, default=12)
    next_level = Column(Enum(Level))
    journey = Column(Enum(JourneyStage))
    progression_months = Column(ARRAY(Integer), nullable=False, default=[1])
    base_progression_rate = Column(DECIMAL(5, 4), nullable=False, default=0.0)
    
    # CAT curve configuration
    use_cat_curve = Column(Boolean, default=True)
    curve_type = Column(Enum(ProgressionCurve), default=ProgressionCurve.CUSTOM)
    custom_curve_data = Column(JSON, default={})
    
    # Metadata
    notes = Column(Text)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    matrix = relationship("CATMatrixConfiguration", back_populates="level_configurations")
    
    __table_args__ = (
        UniqueConstraint('matrix_id', 'level'),
        CheckConstraint('start_tenure >= 0', name='check_start_tenure_positive'),
        CheckConstraint('time_on_level > 0', name='check_time_on_level_positive'),
        CheckConstraint('base_progression_rate >= 0 AND base_progression_rate <= 1', name='check_base_progression_rate_range'),
        Index('idx_cat_levels_matrix_id', 'matrix_id'),
        Index('idx_cat_levels_level', 'level'),
        Index('idx_cat_levels_enabled', 'matrix_id', 'is_enabled'),
    )
    
    def __repr__(self):
        return f"<CATLevelConfiguration(matrix_id='{self.matrix_id}', level='{self.level}')>"


class CATProgressionProbability(Base):
    __tablename__ = 'cat_progression_probabilities'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    matrix_id = Column(UUID(as_uuid=True), ForeignKey('cat_matrix_configurations.id', ondelete='CASCADE'), nullable=False)
    level = Column(Enum(Level), nullable=False)
    cat_stage = Column(Enum(CATStage), nullable=False)
    probability = Column(DECIMAL(6, 4), nullable=False, default=0.0)
    
    # Optional overrides
    effective_from_month = Column(Integer)
    effective_to_month = Column(Integer)
    seasonal_adjustment = Column(DECIMAL(5, 4), default=0.0)
    
    # Metadata
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    matrix = relationship("CATMatrixConfiguration", back_populates="progression_probabilities")
    
    __table_args__ = (
        UniqueConstraint('matrix_id', 'level', 'cat_stage'),
        CheckConstraint('probability >= 0 AND probability <= 1', name='check_probability_range'),
        CheckConstraint(
            '(effective_from_month IS NULL AND effective_to_month IS NULL) OR '
            '(effective_from_month IS NOT NULL AND effective_to_month IS NOT NULL AND '
            'effective_from_month >= 1 AND effective_from_month <= 12 AND '
            'effective_to_month >= 1 AND effective_to_month <= 12)',
            name='check_effective_months'
        ),
        Index('idx_cat_probabilities_matrix_id', 'matrix_id'),
        Index('idx_cat_probabilities_level', 'level'),
        Index('idx_cat_probabilities_stage', 'cat_stage'),
        Index('idx_cat_probabilities_active', 'matrix_id', 'is_active'),
        Index('idx_cat_probabilities_lookup', 'matrix_id', 'level', 'cat_stage'),
    )
    
    def __repr__(self):
        return f"<CATProgressionProbability(level='{self.level}', cat_stage='{self.cat_stage}', probability='{self.probability}')>"


class CATMatrixAuditLog(Base):
    __tablename__ = 'cat_matrix_audit_log'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    matrix_id = Column(UUID(as_uuid=True), ForeignKey('cat_matrix_configurations.id', ondelete='CASCADE'), nullable=False)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)  # 'matrix', 'level', 'probability'
    entity_id = Column(UUID(as_uuid=True))
    old_values = Column(JSON, default={})
    new_values = Column(JSON, default={})
    user_id = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    matrix = relationship("CATMatrixConfiguration", back_populates="audit_logs")
    
    __table_args__ = (
        CheckConstraint(
            "action IN ('created', 'updated', 'deleted', 'activated', 'deactivated', "
            "'copied_from', 'reset_to_default', 'validated', 'bulk_updated')",
            name='check_action_valid'
        ),
        Index('idx_cat_audit_matrix_id', 'matrix_id', 'timestamp'),
        Index('idx_cat_audit_action', 'action', 'timestamp'),
        Index('idx_cat_audit_user', 'user_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<CATMatrixAuditLog(matrix_id='{self.matrix_id}', action='{self.action}', timestamp='{self.timestamp}')>"