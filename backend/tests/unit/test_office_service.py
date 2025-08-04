"""
Unit tests for office service.
"""
import pytest
import asyncio
import tempfile
import shutil
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from backend.src.models.office import (
    OfficeConfig, WorkforceDistribution, WorkforceEntry,
    MonthlyBusinessPlan, MonthlyPlanEntry, ProgressionConfig,
    OfficeJourney, ProgressionCurve
)
from backend.src.services.office_service import OfficeService, OfficeServiceError


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def office_service(temp_data_dir):
    """Create office service with temporary data directory."""
    return OfficeService(data_dir=temp_data_dir)


@pytest.fixture
def sample_office():
    """Create a sample office configuration."""
    return OfficeConfig(
        name="Test Office",
        journey=OfficeJourney.EMERGING,
        timezone="UTC"
    )


@pytest.fixture
def sample_workforce(sample_office):
    """Create a sample workforce distribution."""
    return WorkforceDistribution(
        office_id=sample_office.id,
        start_date=date(2024, 1, 1),
        workforce=[
            WorkforceEntry(role="Consultant", level="A", fte=25),
            WorkforceEntry(role="Consultant", level="SrC", fte=8),
            WorkforceEntry(role="Sales", level="A", fte=5)
        ]
    )


@pytest.fixture
def sample_business_plan(sample_office):
    """Create a sample business plan."""
    return MonthlyBusinessPlan(
        office_id=sample_office.id,
        year=2024,
        month=3,
        entries=[
            MonthlyPlanEntry(
                role="Consultant", level="SrC", recruitment=2,
                churn=1, price=150.0, utr=0.75, salary=8500.0
            ),
            MonthlyPlanEntry(
                role="Sales", level="A", recruitment=1,
                churn=0, price=100.0, utr=0.8, salary=5000.0
            )
        ]
    )


class TestOfficeService:
    """Test office service operations."""
    
    @pytest.mark.asyncio
    async def test_create_office(self, office_service, sample_office):
        """Test office creation."""
        created_office = await office_service.create_office(sample_office)
        
        assert created_office.id is not None
        assert created_office.name == "Test Office"
        assert created_office.journey == OfficeJourney.EMERGING
        assert created_office.created_at is not None
        assert created_office.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_create_duplicate_office(self, office_service, sample_office):
        """Test creating office with duplicate name."""
        await office_service.create_office(sample_office)
        
        # Try to create another office with same name
        duplicate_office = OfficeConfig(
            name="Test Office",  # Same name
            journey=OfficeJourney.MATURE
        )
        
        with pytest.raises(OfficeServiceError):
            await office_service.create_office(duplicate_office)
    
    @pytest.mark.asyncio
    async def test_get_office(self, office_service, sample_office):
        """Test getting office by ID."""
        created_office = await office_service.create_office(sample_office)
        
        retrieved_office = await office_service.get_office(created_office.id)
        
        assert retrieved_office is not None
        assert retrieved_office.id == created_office.id
        assert retrieved_office.name == created_office.name
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_office(self, office_service):
        """Test getting nonexistent office."""
        nonexistent_id = uuid4()
        office = await office_service.get_office(nonexistent_id)
        assert office is None
    
    @pytest.mark.asyncio
    async def test_get_office_by_name(self, office_service, sample_office):
        """Test getting office by name."""
        await office_service.create_office(sample_office)
        
        retrieved_office = await office_service.get_office_by_name("Test Office")
        
        assert retrieved_office is not None
        assert retrieved_office.name == "Test Office"
        
        # Test case insensitive
        retrieved_office = await office_service.get_office_by_name("test office")
        assert retrieved_office is not None
    
    @pytest.mark.asyncio
    async def test_list_offices(self, office_service):
        """Test listing offices."""
        # Create multiple offices
        offices = [
            OfficeConfig(name="Emerging Office", journey=OfficeJourney.EMERGING),
            OfficeConfig(name="Established Office", journey=OfficeJourney.ESTABLISHED),
            OfficeConfig(name="Mature Office", journey=OfficeJourney.MATURE)
        ]
        
        for office in offices:
            await office_service.create_office(office)
        
        # Test listing all offices
        all_offices = await office_service.list_offices()
        assert len(all_offices) == 3
        
        # Test filtering by journey
        emerging_offices = await office_service.list_offices(OfficeJourney.EMERGING)
        assert len(emerging_offices) == 1
        assert emerging_offices[0].name == "Emerging Office"
    
    @pytest.mark.asyncio
    async def test_update_office(self, office_service, sample_office):
        """Test updating office."""
        created_office = await office_service.create_office(sample_office)
        
        # Update office
        created_office.name = "Updated Office"
        created_office.journey = OfficeJourney.MATURE
        
        updated_office = await office_service.update_office(created_office.id, created_office)
        
        assert updated_office is not None
        assert updated_office.name == "Updated Office"
        assert updated_office.journey == OfficeJourney.MATURE
        assert updated_office.updated_at > updated_office.created_at
    
    @pytest.mark.asyncio
    async def test_delete_office(self, office_service, sample_office):
        """Test deleting office."""
        created_office = await office_service.create_office(sample_office)
        
        # Delete office
        success = await office_service.delete_office(created_office.id)
        assert success is True
        
        # Verify deletion
        retrieved_office = await office_service.get_office(created_office.id)
        assert retrieved_office is None
    
    @pytest.mark.asyncio
    async def test_get_offices_by_journey(self, office_service):
        """Test getting offices grouped by journey."""
        # Create offices in different journeys
        offices = [
            OfficeConfig(name="Emerging 1", journey=OfficeJourney.EMERGING),
            OfficeConfig(name="Emerging 2", journey=OfficeJourney.EMERGING),
            OfficeConfig(name="Established 1", journey=OfficeJourney.ESTABLISHED),
            OfficeConfig(name="Mature 1", journey=OfficeJourney.MATURE)
        ]
        
        for office in offices:
            await office_service.create_office(office)
        
        grouped = await office_service.get_offices_by_journey()
        
        assert len(grouped["emerging"]) == 2
        assert len(grouped["established"]) == 1
        assert len(grouped["mature"]) == 1


class TestWorkforceService:
    """Test workforce distribution operations."""
    
    @pytest.mark.asyncio
    async def test_create_workforce_distribution(self, office_service, sample_office, sample_workforce):
        """Test creating workforce distribution."""
        await office_service.create_office(sample_office)
        
        created_workforce = await office_service.create_workforce_distribution(sample_workforce)
        
        assert created_workforce.id is not None
        assert created_workforce.office_id == sample_office.id
        assert len(created_workforce.workforce) == 3
        assert created_workforce.get_total_fte() == 38
    
    @pytest.mark.asyncio
    async def test_get_workforce_distribution(self, office_service, sample_office, sample_workforce):
        """Test getting workforce distribution."""
        await office_service.create_office(sample_office)
        await office_service.create_workforce_distribution(sample_workforce)
        
        retrieved_workforce = await office_service.get_workforce_distribution(sample_office.id)
        
        assert retrieved_workforce is not None
        assert retrieved_workforce.office_id == sample_office.id
        assert len(retrieved_workforce.workforce) == 3
    
    @pytest.mark.asyncio
    async def test_update_workforce_distribution(self, office_service, sample_office, sample_workforce):
        """Test updating workforce distribution."""
        await office_service.create_office(sample_office)
        await office_service.create_workforce_distribution(sample_workforce)
        
        # Update workforce
        sample_workforce.workforce.append(
            WorkforceEntry(role="Operations", level="A", fte=3)
        )
        
        updated_workforce = await office_service.update_workforce_distribution(
            sample_office.id, sample_workforce.start_date, sample_workforce
        )
        
        assert updated_workforce is not None
        assert len(updated_workforce.workforce) == 4
        assert updated_workforce.get_total_fte() == 41


class TestBusinessPlanService:
    """Test business plan operations."""
    
    @pytest.mark.asyncio
    async def test_create_business_plan(self, office_service, sample_office, sample_business_plan):
        """Test creating business plan."""
        await office_service.create_office(sample_office)
        
        created_plan = await office_service.create_monthly_business_plan(sample_business_plan)
        
        assert created_plan.id is not None
        assert created_plan.office_id == sample_office.id
        assert created_plan.year == 2024
        assert created_plan.month == 3
        assert len(created_plan.entries) == 2
    
    @pytest.mark.asyncio
    async def test_get_business_plan(self, office_service, sample_office, sample_business_plan):
        """Test getting business plan."""
        await office_service.create_office(sample_office)
        await office_service.create_monthly_business_plan(sample_business_plan)
        
        retrieved_plan = await office_service.get_monthly_business_plan(
            sample_office.id, 2024, 3
        )
        
        assert retrieved_plan is not None
        assert retrieved_plan.year == 2024
        assert retrieved_plan.month == 3
        assert len(retrieved_plan.entries) == 2
    
    @pytest.mark.asyncio
    async def test_get_business_plans_for_office(self, office_service, sample_office):
        """Test getting all business plans for office."""
        await office_service.create_office(sample_office)
        
        # Create multiple plans
        plans = []
        for month in [1, 2, 3]:
            plan = MonthlyBusinessPlan(
                office_id=sample_office.id,
                year=2024,
                month=month,
                entries=[
                    MonthlyPlanEntry(
                        role="Consultant", level="SrC", recruitment=2,
                        churn=1, price=150.0, utr=0.75, salary=8500.0
                    )
                ]
            )
            plans.append(await office_service.create_monthly_business_plan(plan))
        
        # Get all plans
        all_plans = await office_service.get_business_plans_for_office(sample_office.id)
        assert len(all_plans) == 3
        
        # Get plans for specific year
        year_plans = await office_service.get_business_plans_for_office(sample_office.id, 2024)
        assert len(year_plans) == 3
        
        # Verify sorting
        assert year_plans[0].month == 1
        assert year_plans[1].month == 2
        assert year_plans[2].month == 3
    
    @pytest.mark.asyncio
    async def test_bulk_update_business_plans(self, office_service, sample_office):
        """Test bulk updating business plans."""
        await office_service.create_office(sample_office)
        
        # Create initial plans
        plans = []
        for month in [1, 2, 3]:
            plan = MonthlyBusinessPlan(
                office_id=sample_office.id,
                year=2024,
                month=month,
                entries=[
                    MonthlyPlanEntry(
                        role="Consultant", level="SrC", recruitment=1,
                        churn=0, price=150.0, utr=0.75, salary=8500.0
                    )
                ]
            )
            plans.append(plan)
        
        # Create plans
        for plan in plans:
            await office_service.create_monthly_business_plan(plan)
        
        # Update all plans
        for plan in plans:
            plan.entries[0].recruitment = 3  # Change recruitment
        
        updated_plans = await office_service.bulk_update_business_plans(sample_office.id, plans)
        
        assert len(updated_plans) == 3
        for plan in updated_plans:
            assert plan.entries[0].recruitment == 3
    
    @pytest.mark.asyncio
    async def test_copy_business_plan_template(self, office_service):
        """Test copying business plan template."""
        # Create source and target offices
        source_office = OfficeConfig(name="Source Office", journey=OfficeJourney.MATURE)
        target_office = OfficeConfig(name="Target Office", journey=OfficeJourney.EMERGING)
        
        await office_service.create_office(source_office)
        await office_service.create_office(target_office)
        
        # Create business plans in source office
        source_plans = []
        for month in [1, 2, 3]:
            plan = MonthlyBusinessPlan(
                office_id=source_office.id,
                year=2024,
                month=month,
                entries=[
                    MonthlyPlanEntry(
                        role="Consultant", level="SrC", recruitment=2,
                        churn=1, price=150.0, utr=0.75, salary=8500.0
                    )
                ]
            )
            source_plans.append(await office_service.create_monthly_business_plan(plan))
        
        # Copy plans to target office
        copied_plans = await office_service.copy_business_plan_template(
            source_office.id, target_office.id, 2024
        )
        
        assert len(copied_plans) == 3
        for plan in copied_plans:
            assert plan.office_id == target_office.id
            assert plan.year == 2024
            assert len(plan.entries) == 1


class TestProgressionService:
    """Test progression configuration operations."""
    
    @pytest.mark.asyncio
    async def test_create_progression_config(self, office_service, sample_office):
        """Test creating progression configuration."""
        await office_service.create_office(sample_office)
        
        config = ProgressionConfig(
            office_id=sample_office.id,
            level="SrC",
            monthly_rate=0.05,
            curve_type=ProgressionCurve.LINEAR
        )
        
        created_config = await office_service.create_progression_config(config)
        
        assert created_config.id is not None
        assert created_config.office_id == sample_office.id
        assert created_config.level == "SrC"
        assert created_config.monthly_rate == 0.05
    
    @pytest.mark.asyncio
    async def test_get_progression_configs(self, office_service, sample_office):
        """Test getting progression configurations."""
        await office_service.create_office(sample_office)
        
        # Create configs for multiple levels
        levels = ["A", "AC", "C", "SrC"]
        for level in levels:
            config = ProgressionConfig(
                office_id=sample_office.id,
                level=level,
                monthly_rate=0.05,
                curve_type=ProgressionCurve.LINEAR
            )
            await office_service.create_progression_config(config)
        
        configs = await office_service.get_progression_configs_for_office(sample_office.id)
        
        assert len(configs) == 4
        # Should be sorted by level order
        assert configs[0].level == "A"
        assert configs[1].level == "AC"


class TestOfficeSummaryService:
    """Test office summary operations."""
    
    @pytest.mark.asyncio
    async def test_get_office_summary(self, office_service, sample_office, sample_workforce, sample_business_plan):
        """Test getting complete office summary."""
        # Create office and associated data
        await office_service.create_office(sample_office)
        await office_service.create_workforce_distribution(sample_workforce)
        await office_service.create_monthly_business_plan(sample_business_plan)
        
        # Create progression config
        config = ProgressionConfig(
            office_id=sample_office.id,
            level="SrC",
            monthly_rate=0.05,
            curve_type=ProgressionCurve.LINEAR
        )
        await office_service.create_progression_config(config)
        
        # Get summary
        summary = await office_service.get_office_summary(sample_office.id)
        
        assert summary is not None
        assert summary.office.id == sample_office.id
        assert summary.workforce_distribution is not None
        assert len(summary.monthly_plans) == 1
        assert len(summary.progression_configs) == 1
    
    @pytest.mark.asyncio
    async def test_validate_office_setup(self, office_service, sample_office, sample_workforce, sample_business_plan):
        """Test office setup validation."""
        # Create office and associated data
        await office_service.create_office(sample_office)
        await office_service.create_workforce_distribution(sample_workforce)
        await office_service.create_monthly_business_plan(sample_business_plan)
        
        # Validate setup
        validation_results = await office_service.validate_office_setup(sample_office.id)
        
        assert "errors" in validation_results
        assert "warnings" in validation_results
        assert "info" in validation_results
        
        # Should have some info about the setup
        info_messages = validation_results["info"]
        assert any("Total workforce:" in msg for msg in info_messages)
        assert any("Business plans:" in msg for msg in info_messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])