"""
Office management service for CRUD operations and business logic.
"""
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

try:
    from ..models.office import (
        OfficeConfig, WorkforceDistribution, MonthlyBusinessPlan, 
        ProgressionConfig, OfficeBusinessPlanSummary, OfficeJourney
    )
    from ..validators.office_validators import (
        BusinessPlanValidator, OfficeConfigValidator, validate_complete_office_setup
    )
except ImportError:
    # Fallback for direct execution
    from backend.src.models.office import (
        OfficeConfig, WorkforceDistribution, MonthlyBusinessPlan, 
        ProgressionConfig, OfficeBusinessPlanSummary, OfficeJourney
    )
    from backend.src.validators.office_validators import (
        BusinessPlanValidator, OfficeConfigValidator, validate_complete_office_setup
    )


class OfficeServiceError(Exception):
    """Custom exception for office service errors."""
    pass


class OfficeService:
    """Service class for office management operations."""
    
    def __init__(self, data_dir: str = "data/offices"):
        """Initialize office service with data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different data types
        (self.data_dir / "configs").mkdir(exist_ok=True)
        (self.data_dir / "workforce").mkdir(exist_ok=True)
        (self.data_dir / "business_plans").mkdir(exist_ok=True)
        (self.data_dir / "progressions").mkdir(exist_ok=True)

    # ================================================
    # OFFICE CONFIGURATION OPERATIONS
    # ================================================

    async def create_office(self, office_config: OfficeConfig) -> OfficeConfig:
        """Create a new office configuration."""
        # Validate name uniqueness
        existing_offices = await self.list_offices()
        if not OfficeConfigValidator.validate_office_name_uniqueness(
            office_config.name, existing_offices
        ):
            raise OfficeServiceError(f"Office name '{office_config.name}' already exists")
        
        # Set timestamps
        now = datetime.utcnow()
        office_config.id = uuid4()
        office_config.created_at = now
        office_config.updated_at = now
        
        # Save to file
        config_file = self.data_dir / "configs" / f"{office_config.id}.json"
        with open(config_file, 'w') as f:
            json.dump(office_config.dict(), f, indent=2, default=str)
        
        return office_config

    async def get_office(self, office_id: UUID) -> Optional[OfficeConfig]:
        """Get office configuration by ID."""
        config_file = self.data_dir / "configs" / f"{office_id}.json"
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            return OfficeConfig(**data)
        except (json.JSONDecodeError, ValueError) as e:
            raise OfficeServiceError(f"Error loading office {office_id}: {str(e)}")

    async def get_office_by_name(self, name: str) -> Optional[OfficeConfig]:
        """Get office configuration by name."""
        offices = await self.list_offices()
        for office in offices:
            if office.name.lower() == name.lower():
                return office
        return None

    async def list_offices(self, journey: Optional[OfficeJourney] = None) -> List[OfficeConfig]:
        """List all office configurations, optionally filtered by journey."""
        offices = []
        config_dir = self.data_dir / "configs"
        
        if not config_dir.exists():
            return offices
        
        for config_file in config_dir.glob("*.json"):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                office = OfficeConfig(**data)
                
                if journey is None or office.journey == journey:
                    offices.append(office)
            except (json.JSONDecodeError, ValueError):
                # Skip invalid files
                continue
        
        # Sort by journey and name
        journey_order = {"emerging": 1, "established": 2, "mature": 3}
        offices.sort(key=lambda x: (journey_order.get(x.journey, 0), x.name))
        
        return offices

    async def update_office(self, office_id: UUID, office_config: OfficeConfig) -> Optional[OfficeConfig]:
        """Update office configuration."""
        existing = await self.get_office(office_id)
        if not existing:
            return None
        
        # Validate name uniqueness (excluding current office)
        existing_offices = await self.list_offices()
        if not OfficeConfigValidator.validate_office_name_uniqueness(
            office_config.name, existing_offices, exclude_id=office_id
        ):
            raise OfficeServiceError(f"Office name '{office_config.name}' already exists")
        
        # Preserve ID and creation timestamp, update modification timestamp
        office_config.id = office_id
        office_config.created_at = existing.created_at
        office_config.updated_at = datetime.utcnow()
        
        # Save to file
        config_file = self.data_dir / "configs" / f"{office_id}.json"
        with open(config_file, 'w') as f:
            json.dump(office_config.dict(), f, indent=2, default=str)
        
        return office_config

    async def delete_office(self, office_id: UUID) -> bool:
        """Delete office and all associated data."""
        config_file = self.data_dir / "configs" / f"{office_id}.json"
        
        if not config_file.exists():
            return False
        
        # Delete all associated data
        await self._delete_office_data(office_id)
        
        # Delete office config
        config_file.unlink()
        return True

    async def _delete_office_data(self, office_id: UUID):
        """Delete all data files associated with an office."""
        # Delete workforce distributions
        workforce_dir = self.data_dir / "workforce"
        for file in workforce_dir.glob(f"{office_id}_*.json"):
            file.unlink()
        
        # Delete business plans
        plans_dir = self.data_dir / "business_plans"
        for file in plans_dir.glob(f"{office_id}_*.json"):
            file.unlink()
        
        # Delete progression configs
        progression_dir = self.data_dir / "progressions"
        for file in progression_dir.glob(f"{office_id}_*.json"):
            file.unlink()

    # ================================================
    # WORKFORCE DISTRIBUTION OPERATIONS
    # ================================================

    async def create_workforce_distribution(self, workforce: WorkforceDistribution) -> WorkforceDistribution:
        """Create workforce distribution for an office."""
        # Validate office exists
        office = await self.get_office(workforce.office_id)
        if not office:
            raise OfficeServiceError(f"Office {workforce.office_id} not found")
        
        # Set timestamps
        now = datetime.utcnow()
        workforce.id = uuid4()
        workforce.created_at = now
        workforce.updated_at = now
        
        # Save to file
        workforce_file = self.data_dir / "workforce" / f"{workforce.office_id}_{workforce.start_date}.json"
        with open(workforce_file, 'w') as f:
            json.dump(workforce.dict(), f, indent=2, default=str)
        
        return workforce

    async def get_workforce_distribution(
        self, office_id: UUID, start_date: Optional[date] = None
    ) -> Optional[WorkforceDistribution]:
        """Get workforce distribution for an office."""
        workforce_dir = self.data_dir / "workforce"
        
        if start_date:
            workforce_file = workforce_dir / f"{office_id}_{start_date}.json"
            if workforce_file.exists():
                try:
                    with open(workforce_file, 'r') as f:
                        data = json.load(f)
                    return WorkforceDistribution(**data)
                except (json.JSONDecodeError, ValueError):
                    pass
        else:
            # Get most recent workforce distribution
            files = list(workforce_dir.glob(f"{office_id}_*.json"))
            if files:
                # Sort by date (extracted from filename)
                files.sort(key=lambda x: x.stem.split('_', 1)[1], reverse=True)
                try:
                    with open(files[0], 'r') as f:
                        data = json.load(f)
                    return WorkforceDistribution(**data)
                except (json.JSONDecodeError, ValueError):
                    pass
        
        return None

    async def update_workforce_distribution(
        self, office_id: UUID, start_date: date, workforce: WorkforceDistribution
    ) -> Optional[WorkforceDistribution]:
        """Update workforce distribution."""
        workforce_file = self.data_dir / "workforce" / f"{office_id}_{start_date}.json"
        
        if not workforce_file.exists():
            return None
        
        # Preserve ID and creation timestamp
        existing = await self.get_workforce_distribution(office_id, start_date)
        if existing:
            workforce.id = existing.id
            workforce.created_at = existing.created_at
        
        workforce.office_id = office_id
        workforce.start_date = start_date
        workforce.updated_at = datetime.utcnow()
        
        with open(workforce_file, 'w') as f:
            json.dump(workforce.dict(), f, indent=2, default=str)
        
        return workforce

    # ================================================
    # BUSINESS PLAN OPERATIONS
    # ================================================

    async def create_monthly_business_plan(self, plan: MonthlyBusinessPlan) -> MonthlyBusinessPlan:
        """Create monthly business plan."""
        # Validate office exists
        office = await self.get_office(plan.office_id)
        if not office:
            raise OfficeServiceError(f"Office {plan.office_id} not found")
        
        # Set timestamps
        now = datetime.utcnow()
        plan.id = uuid4()
        plan.created_at = now
        plan.updated_at = now
        
        # Save to file
        plan_file = self.data_dir / "business_plans" / f"{plan.office_id}_{plan.year}_{plan.month:02d}.json"
        with open(plan_file, 'w') as f:
            json.dump(plan.dict(), f, indent=2, default=str)
        
        return plan

    async def get_monthly_business_plan(
        self, office_id: UUID, year: int, month: int
    ) -> Optional[MonthlyBusinessPlan]:
        """Get monthly business plan."""
        plan_file = self.data_dir / "business_plans" / f"{office_id}_{year}_{month:02d}.json"
        
        if not plan_file.exists():
            return None
        
        try:
            with open(plan_file, 'r') as f:
                data = json.load(f)
            return MonthlyBusinessPlan(**data)
        except (json.JSONDecodeError, ValueError) as e:
            raise OfficeServiceError(f"Error loading business plan: {str(e)}")

    async def get_business_plans_for_office(
        self, office_id: UUID, year: Optional[int] = None
    ) -> List[MonthlyBusinessPlan]:
        """Get all business plans for an office."""
        plans = []
        plans_dir = self.data_dir / "business_plans"
        
        if not plans_dir.exists():
            return plans
        
        pattern = f"{office_id}_{year}_*.json" if year else f"{office_id}_*.json"
        
        for plan_file in plans_dir.glob(pattern):
            try:
                with open(plan_file, 'r') as f:
                    data = json.load(f)
                plans.append(MonthlyBusinessPlan(**data))
            except (json.JSONDecodeError, ValueError):
                continue
        
        # Sort by year and month
        plans.sort(key=lambda x: (x.year, x.month))
        return plans

    async def update_monthly_business_plan(
        self, office_id: UUID, year: int, month: int, plan: MonthlyBusinessPlan
    ) -> Optional[MonthlyBusinessPlan]:
        """Update monthly business plan."""
        plan_file = self.data_dir / "business_plans" / f"{office_id}_{year}_{month:02d}.json"
        
        if not plan_file.exists():
            return None
        
        # Preserve ID and creation timestamp
        existing = await self.get_monthly_business_plan(office_id, year, month)
        if existing:
            plan.id = existing.id
            plan.created_at = existing.created_at
        
        plan.office_id = office_id
        plan.year = year
        plan.month = month
        plan.updated_at = datetime.utcnow()
        
        with open(plan_file, 'w') as f:
            json.dump(plan.dict(), f, indent=2, default=str)
        
        return plan

    async def bulk_update_business_plans(
        self, office_id: UUID, plans: List[MonthlyBusinessPlan]
    ) -> List[MonthlyBusinessPlan]:
        """Bulk update multiple business plans."""
        updated_plans = []
        
        for plan in plans:
            plan.office_id = office_id
            updated_plan = await self.update_monthly_business_plan(
                office_id, plan.year, plan.month, plan
            )
            if updated_plan:
                updated_plans.append(updated_plan)
            else:
                # Create new plan if it doesn't exist
                created_plan = await self.create_monthly_business_plan(plan)
                updated_plans.append(created_plan)
        
        return updated_plans

    # ================================================
    # PROGRESSION CONFIG OPERATIONS
    # ================================================

    async def create_progression_config(self, config: ProgressionConfig) -> ProgressionConfig:
        """Create CAT progression configuration."""
        # Validate office exists
        office = await self.get_office(config.office_id)
        if not office:
            raise OfficeServiceError(f"Office {config.office_id} not found")
        
        # Set timestamps
        now = datetime.utcnow()
        config.id = uuid4()
        config.created_at = now
        config.updated_at = now
        
        # Save to file
        config_file = self.data_dir / "progressions" / f"{config.office_id}_{config.level}.json"
        with open(config_file, 'w') as f:
            json.dump(config.dict(), f, indent=2, default=str)
        
        return config

    async def get_progression_configs_for_office(self, office_id: UUID) -> List[ProgressionConfig]:
        """Get all progression configurations for an office."""
        configs = []
        progression_dir = self.data_dir / "progressions"
        
        if not progression_dir.exists():
            return configs
        
        for config_file in progression_dir.glob(f"{office_id}_*.json"):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                configs.append(ProgressionConfig(**data))
            except (json.JSONDecodeError, ValueError):
                continue
        
        # Sort by level
        level_order = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
        configs.sort(key=lambda x: level_order.index(x.level) if x.level in level_order else 999)
        
        return configs

    async def update_progression_config(
        self, office_id: UUID, level: str, config: ProgressionConfig
    ) -> Optional[ProgressionConfig]:
        """Update progression configuration."""
        config_file = self.data_dir / "progressions" / f"{office_id}_{level}.json"
        
        if not config_file.exists():
            return None
        
        # Preserve ID and creation timestamp
        existing_configs = await self.get_progression_configs_for_office(office_id)
        existing = next((c for c in existing_configs if c.level == level), None)
        
        if existing:
            config.id = existing.id
            config.created_at = existing.created_at
        
        config.office_id = office_id
        config.level = level
        config.updated_at = datetime.utcnow()
        
        with open(config_file, 'w') as f:
            json.dump(config.dict(), f, indent=2, default=str)
        
        return config

    # ================================================
    # COMPREHENSIVE OFFICE OPERATIONS
    # ================================================

    async def get_office_summary(self, office_id: UUID) -> Optional[OfficeBusinessPlanSummary]:
        """Get complete office summary with all associated data."""
        office = await self.get_office(office_id)
        if not office:
            return None
        
        workforce = await self.get_workforce_distribution(office_id)
        business_plans = await self.get_business_plans_for_office(office_id)
        progression_configs = await self.get_progression_configs_for_office(office_id)
        
        return OfficeBusinessPlanSummary(
            office=office,
            workforce_distribution=workforce,
            monthly_plans=business_plans,
            progression_configs=progression_configs
        )

    async def validate_office_setup(self, office_id: UUID) -> Dict[str, List[str]]:
        """Validate complete office setup and return validation results."""
        office_summary = await self.get_office_summary(office_id)
        if not office_summary:
            return {"errors": [f"Office {office_id} not found"]}
        
        return validate_complete_office_setup(office_summary)

    async def copy_business_plan_template(
        self, source_office_id: UUID, target_office_id: UUID, year: int
    ) -> List[MonthlyBusinessPlan]:
        """Copy business plan from one office to another."""
        # Validate both offices exist
        source_office = await self.get_office(source_office_id)
        target_office = await self.get_office(target_office_id)
        
        if not source_office:
            raise OfficeServiceError(f"Source office {source_office_id} not found")
        if not target_office:
            raise OfficeServiceError(f"Target office {target_office_id} not found")
        
        # Get source business plans
        source_plans = await self.get_business_plans_for_office(source_office_id, year)
        if not source_plans:
            raise OfficeServiceError(f"No business plans found for source office in year {year}")
        
        # Create new plans for target office
        copied_plans = []
        for source_plan in source_plans:
            new_plan = MonthlyBusinessPlan(
                office_id=target_office_id,
                year=source_plan.year,
                month=source_plan.month,
                entries=source_plan.entries.copy()
            )
            created_plan = await self.create_monthly_business_plan(new_plan)
            copied_plans.append(created_plan)
        
        return copied_plans

    async def get_offices_by_journey(self) -> Dict[str, List[OfficeConfig]]:
        """Get offices grouped by journey."""
        all_offices = await self.list_offices()
        
        grouped = {
            "emerging": [],
            "established": [],
            "mature": []
        }
        
        for office in all_offices:
            grouped[office.journey].append(office)
        
        return grouped