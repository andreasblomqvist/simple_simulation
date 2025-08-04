"""
Unit tests for office management models.
"""
import pytest
from datetime import date, datetime
from uuid import uuid4
from pydantic import ValidationError

from backend.src.models.office import (
    OfficeConfig, WorkforceDistribution, WorkforceEntry,
    MonthlyBusinessPlan, MonthlyPlanEntry, ProgressionConfig,
    OfficeBusinessPlanSummary, OfficeJourney, ProgressionCurve,
    EconomicParameters
)


class TestEconomicParameters:
    """Test economic parameters model."""
    
    def test_valid_economic_parameters(self):
        """Test valid economic parameters."""
        params = EconomicParameters(
            cost_of_living=1.2,
            market_multiplier=1.1,
            tax_rate=0.25
        )
        
        assert params.cost_of_living == 1.2
        assert params.market_multiplier == 1.1
        assert params.tax_rate == 0.25
    
    def test_economic_parameters_validation(self):
        """Test economic parameters validation."""
        # Test cost of living bounds
        with pytest.raises(ValidationError):
            EconomicParameters(cost_of_living=0.05)  # Too low
        
        with pytest.raises(ValidationError):
            EconomicParameters(cost_of_living=5.0)   # Too high
        
        # Test market multiplier bounds
        with pytest.raises(ValidationError):
            EconomicParameters(market_multiplier=0.05)  # Too low
        
        # Test tax rate bounds
        with pytest.raises(ValidationError):
            EconomicParameters(tax_rate=-0.1)  # Negative
        
        with pytest.raises(ValidationError):
            EconomicParameters(tax_rate=1.5)   # Too high


class TestOfficeConfig:
    """Test office configuration model."""
    
    def test_valid_office_config(self):
        """Test valid office configuration."""
        config = OfficeConfig(
            name="Stockholm",
            journey=OfficeJourney.MATURE,
            timezone="Europe/Stockholm",
            economic_parameters=EconomicParameters(
                cost_of_living=1.2,
                market_multiplier=1.1,
                tax_rate=0.25
            )
        )
        
        assert config.name == "Stockholm"
        assert config.journey == OfficeJourney.MATURE
        assert config.timezone == "Europe/Stockholm"
        assert config.economic_parameters.cost_of_living == 1.2
    
    def test_office_name_validation(self):
        """Test office name validation."""
        # Empty name
        with pytest.raises(ValidationError):
            OfficeConfig(name="", journey=OfficeJourney.EMERGING)
        
        # Whitespace only
        with pytest.raises(ValidationError):
            OfficeConfig(name="   ", journey=OfficeJourney.EMERGING)
        
        # Valid name with whitespace trimming
        config = OfficeConfig(name="  Stockholm  ", journey=OfficeJourney.EMERGING)
        assert config.name == "Stockholm"
    
    def test_office_defaults(self):
        """Test office configuration defaults."""
        config = OfficeConfig(name="Test Office", journey=OfficeJourney.EMERGING)
        
        assert config.timezone == "UTC"
        assert isinstance(config.economic_parameters, EconomicParameters)


class TestWorkforceEntry:
    """Test workforce entry model."""
    
    def test_valid_workforce_entry(self):
        """Test valid workforce entry."""
        entry = WorkforceEntry(
            role="Consultant",
            level="SrC",
            fte=5,
            notes="Senior consultants"
        )
        
        assert entry.role == "Consultant"
        assert entry.level == "SrC"
        assert entry.fte == 5
        assert entry.notes == "Senior consultants"
    
    def test_workforce_entry_validation(self):
        """Test workforce entry validation."""
        # Negative FTE
        with pytest.raises(ValidationError):
            WorkforceEntry(role="Consultant", level="SrC", fte=-1)
        
        # Empty role
        with pytest.raises(ValidationError):
            WorkforceEntry(role="", level="SrC", fte=5)
        
        # Empty level
        with pytest.raises(ValidationError):
            WorkforceEntry(role="Consultant", level="", fte=5)
    
    def test_workforce_entry_trimming(self):
        """Test role and level trimming."""
        entry = WorkforceEntry(
            role="  Consultant  ",
            level="  SrC  ",
            fte=5
        )
        
        assert entry.role == "Consultant"
        assert entry.level == "SrC"


class TestWorkforceDistribution:
    """Test workforce distribution model."""
    
    def test_valid_workforce_distribution(self):
        """Test valid workforce distribution."""
        office_id = uuid4()
        workforce = WorkforceDistribution(
            office_id=office_id,
            start_date=date(2024, 1, 1),
            workforce=[
                WorkforceEntry(role="Consultant", level="A", fte=25),
                WorkforceEntry(role="Consultant", level="SrC", fte=8),
                WorkforceEntry(role="Sales", level="A", fte=5)
            ]
        )
        
        assert workforce.office_id == office_id
        assert workforce.start_date == date(2024, 1, 1)
        assert len(workforce.workforce) == 3
    
    def test_workforce_duplicate_validation(self):
        """Test duplicate role/level validation."""
        office_id = uuid4()
        
        with pytest.raises(ValidationError):
            WorkforceDistribution(
                office_id=office_id,
                start_date=date(2024, 1, 1),
                workforce=[
                    WorkforceEntry(role="Consultant", level="SrC", fte=5),
                    WorkforceEntry(role="Consultant", level="SrC", fte=3)  # Duplicate
                ]
            )
    
    def test_workforce_calculations(self):
        """Test workforce calculation methods."""
        office_id = uuid4()
        workforce = WorkforceDistribution(
            office_id=office_id,
            start_date=date(2024, 1, 1),
            workforce=[
                WorkforceEntry(role="Consultant", level="A", fte=25),
                WorkforceEntry(role="Consultant", level="SrC", fte=8),
                WorkforceEntry(role="Sales", level="A", fte=5)
            ]
        )
        
        assert workforce.get_total_fte() == 38
        assert workforce.get_fte_by_role("Consultant") == 33
        assert workforce.get_fte_by_role("Sales") == 5
        assert workforce.get_fte_by_level("A") == 30
        assert workforce.get_fte_by_level("SrC") == 8


class TestMonthlyPlanEntry:
    """Test monthly plan entry model."""
    
    def test_valid_monthly_plan_entry(self):
        """Test valid monthly plan entry."""
        entry = MonthlyPlanEntry(
            role="Consultant",
            level="SrC",
            recruitment=2,
            churn=1,
            price=150.0,
            utr=0.75,
            salary=8500.0
        )
        
        assert entry.role == "Consultant"
        assert entry.level == "SrC"
        assert entry.recruitment == 2
        assert entry.churn == 1
        assert entry.price == 150.0
        assert entry.utr == 0.75
        assert entry.salary == 8500.0
    
    def test_monthly_plan_entry_validation(self):
        """Test monthly plan entry validation."""
        # Negative recruitment
        with pytest.raises(ValidationError):
            MonthlyPlanEntry(
                role="Consultant", level="SrC", recruitment=-1,
                churn=0, price=150.0, utr=0.75, salary=8500.0
            )
        
        # Invalid UTR
        with pytest.raises(ValidationError):
            MonthlyPlanEntry(
                role="Consultant", level="SrC", recruitment=2,
                churn=1, price=150.0, utr=1.5, salary=8500.0
            )
        
        # Negative price
        with pytest.raises(ValidationError):
            MonthlyPlanEntry(
                role="Consultant", level="SrC", recruitment=2,
                churn=1, price=-50.0, utr=0.75, salary=8500.0
            )


class TestMonthlyBusinessPlan:
    """Test monthly business plan model."""
    
    def test_valid_monthly_business_plan(self):
        """Test valid monthly business plan."""
        office_id = uuid4()
        plan = MonthlyBusinessPlan(
            office_id=office_id,
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
        
        assert plan.office_id == office_id
        assert plan.year == 2024
        assert plan.month == 3
        assert len(plan.entries) == 2
    
    def test_monthly_plan_duplicate_validation(self):
        """Test duplicate entry validation."""
        office_id = uuid4()
        
        with pytest.raises(ValidationError):
            MonthlyBusinessPlan(
                office_id=office_id,
                year=2024,
                month=3,
                entries=[
                    MonthlyPlanEntry(
                        role="Consultant", level="SrC", recruitment=2,
                        churn=1, price=150.0, utr=0.75, salary=8500.0
                    ),
                    MonthlyPlanEntry(
                        role="Consultant", level="SrC", recruitment=1,  # Duplicate
                        churn=0, price=150.0, utr=0.75, salary=8500.0
                    )
                ]
            )
    
    def test_monthly_plan_calculations(self):
        """Test monthly plan calculation methods."""
        office_id = uuid4()
        plan = MonthlyBusinessPlan(
            office_id=office_id,
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
        
        assert plan.get_total_recruitment() == 3
        assert plan.get_total_churn() == 1
        assert plan.get_net_change() == 2
        
        # Revenue potential: (150 * 0.75 * 160) + (100 * 0.8 * 160) = 18000 + 12800 = 30800
        assert plan.get_revenue_potential() == 30800.0
        
        # Salary cost: 8500 + 5000 = 13500
        assert plan.get_total_salary_cost() == 13500.0


class TestProgressionConfig:
    """Test progression configuration model."""
    
    def test_valid_progression_config(self):
        """Test valid progression configuration."""
        office_id = uuid4()
        config = ProgressionConfig(
            office_id=office_id,
            level="SrC",
            monthly_rate=0.05,
            curve_type=ProgressionCurve.LINEAR
        )
        
        assert config.office_id == office_id
        assert config.level == "SrC"
        assert config.monthly_rate == 0.05
        assert config.curve_type == ProgressionCurve.LINEAR
    
    def test_progression_config_validation(self):
        """Test progression configuration validation."""
        office_id = uuid4()
        
        # Invalid monthly rate
        with pytest.raises(ValidationError):
            ProgressionConfig(
                office_id=office_id,
                level="SrC",
                monthly_rate=1.5  # Too high
            )
        
        # Custom curve without points
        with pytest.raises(ValidationError):
            ProgressionConfig(
                office_id=office_id,
                level="SrC",
                monthly_rate=0.05,
                curve_type=ProgressionCurve.CUSTOM,
                custom_points=[]  # Required for custom curve
            )
    
    def test_progression_rate_calculation(self):
        """Test progression rate calculation for different months."""
        office_id = uuid4()
        
        # Linear progression
        linear_config = ProgressionConfig(
            office_id=office_id,
            level="SrC",
            monthly_rate=0.05,
            curve_type=ProgressionCurve.LINEAR
        )
        
        assert linear_config.get_rate_for_month(1) == 0.05
        assert linear_config.get_rate_for_month(6) == 0.05
        assert linear_config.get_rate_for_month(12) == 0.05
        
        # Exponential progression
        exp_config = ProgressionConfig(
            office_id=office_id,
            level="SrC",
            monthly_rate=0.05,
            curve_type=ProgressionCurve.EXPONENTIAL
        )
        
        # Should be 0.05 * (1.1 ^ 0) = 0.05 for month 1
        assert exp_config.get_rate_for_month(1) == 0.05
        # Should be higher for later months
        assert exp_config.get_rate_for_month(12) > 0.05


class TestOfficeBusinessPlanSummary:
    """Test office business plan summary model."""
    
    def test_office_summary_creation(self):
        """Test office summary creation."""
        office = OfficeConfig(name="Test Office", journey=OfficeJourney.EMERGING)
        office_id = office.id
        
        workforce = WorkforceDistribution(
            office_id=office_id,
            start_date=date(2024, 1, 1),
            workforce=[
                WorkforceEntry(role="Consultant", level="SrC", fte=5)
            ]
        )
        
        plans = [
            MonthlyBusinessPlan(
                office_id=office_id,
                year=2024,
                month=1,
                entries=[
                    MonthlyPlanEntry(
                        role="Consultant", level="SrC", recruitment=2,
                        churn=1, price=150.0, utr=0.75, salary=8500.0
                    )
                ]
            )
        ]
        
        summary = OfficeBusinessPlanSummary(
            office=office,
            workforce_distribution=workforce,
            monthly_plans=plans
        )
        
        assert summary.office.name == "Test Office"
        assert summary.workforce_distribution is not None
        assert len(summary.monthly_plans) == 1
    
    def test_summary_helper_methods(self):
        """Test summary helper methods."""
        office = OfficeConfig(name="Test Office", journey=OfficeJourney.EMERGING)
        office_id = office.id
        
        plans = [
            MonthlyBusinessPlan(
                office_id=office_id,
                year=2024,
                month=1,
                entries=[
                    MonthlyPlanEntry(
                        role="Consultant", level="SrC", recruitment=2,
                        churn=1, price=150.0, utr=0.75, salary=8500.0
                    )
                ]
            ),
            MonthlyBusinessPlan(
                office_id=office_id,
                year=2024,
                month=2,
                entries=[
                    MonthlyPlanEntry(
                        role="Consultant", level="SrC", recruitment=1,
                        churn=2, price=150.0, utr=0.75, salary=8500.0
                    )
                ]
            )
        ]
        
        summary = OfficeBusinessPlanSummary(
            office=office,
            monthly_plans=plans
        )
        
        # Test get_plan_for_month
        jan_plan = summary.get_plan_for_month(2024, 1)
        assert jan_plan is not None
        assert jan_plan.month == 1
        
        # Test get_annual_summary
        annual = summary.get_annual_summary(2024)
        assert annual["year"] == 2024
        assert annual["total_recruitment"] == 3  # 2 + 1
        assert annual["total_churn"] == 3        # 1 + 2
        assert annual["net_change"] == 0         # 3 - 3
        assert annual["months_planned"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])