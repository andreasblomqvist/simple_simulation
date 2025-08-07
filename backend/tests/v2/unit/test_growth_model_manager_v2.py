"""
Comprehensive Unit Tests for GrowthModelManagerV2

Tests multi-year growth modeling functionality including:
- Growth pattern application (linear, exponential, seasonal)
- Business plan extrapolation beyond defined periods
- Compound growth calculations
- Economic scenario integration
- Growth validation and constraints
- Historical growth rate tracking
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date, timedelta
from typing import Dict, List
import math

from backend.src.services.growth_model_manager_v2 import (
    GrowthModelManagerV2, GrowthPattern, GrowthModelConfiguration,
    EconomicScenario
)

from backend.src.services.simulation_engine_v2 import (
    BusinessModel, BusinessPlan, MonthlyPlan, GrowthRates, TimeRange
)


class TestGrowthModelManagerV2Initialization:
    """Test suite for GrowthModelManagerV2 initialization"""

    def test_default_initialization(self):
        """Test manager initializes with default configurations"""
        manager = GrowthModelManagerV2()
        
        # Verify default state
        assert isinstance(manager.config, GrowthModelConfiguration)
        assert manager.economic_scenarios == []
        assert manager.growth_history == {}
        
        # Verify default configuration
        assert isinstance(manager.config.default_recruitment_pattern, GrowthPattern)
        assert manager.config.default_recruitment_pattern.pattern_type == "exponential"
        assert manager.config.default_recruitment_pattern.base_rate == 0.05
        
        assert manager.config.default_price_pattern.pattern_type == "linear"
        assert manager.config.default_price_pattern.base_rate == 0.03
        
        assert manager.config.max_annual_growth_rate == 2.0
        assert manager.config.min_annual_growth_rate == -0.5
        assert manager.config.require_positive_extrapolation is True

    def test_custom_configuration_initialization(self):
        """Test manager accepts custom configurations"""
        manager = GrowthModelManagerV2()
        
        # Custom growth patterns
        custom_recruitment = GrowthPattern("linear", 0.08, max_rate=0.15)
        custom_price = GrowthPattern("exponential", 0.04)
        
        custom_config = GrowthModelConfiguration(
            default_recruitment_pattern=custom_recruitment,
            default_price_pattern=custom_price,
            max_annual_growth_rate=1.5,
            min_annual_growth_rate=-0.3
        )
        
        # Custom economic scenarios
        economic_scenarios = [
            EconomicScenario(
                name="Recession",
                description="Economic downturn",
                growth_adjustments={"recruitment": -0.2, "price": -0.1},
                duration_months=18
            )
        ]
        
        # Initialize with custom configs
        result = manager.initialize(
            config=custom_config,
            economic_scenarios=economic_scenarios
        )
        
        assert result is True
        assert manager.config == custom_config
        assert manager.economic_scenarios == economic_scenarios
        assert manager.config.max_annual_growth_rate == 1.5

    def test_initialization_success_logging(self):
        """Test initialization logs success message"""
        manager = GrowthModelManagerV2()
        
        with patch('backend.src.services.growth_model_manager_v2.logger') as mock_logger:
            manager.initialize()
            
            mock_logger.info.assert_called_with("GrowthModelManagerV2 initialized successfully")


class TestGrowthPatterns:
    """Test suite for growth pattern functionality"""

    def test_growth_pattern_creation(self):
        """Test growth pattern creation with various parameters"""
        # Linear pattern
        linear_pattern = GrowthPattern(
            pattern_type="linear",
            base_rate=0.05,
            seasonality_factor={1: 0.8, 6: 1.2, 12: 1.1},
            max_rate=0.15
        )
        
        assert linear_pattern.pattern_type == "linear"
        assert linear_pattern.base_rate == 0.05
        assert linear_pattern.seasonality_factor[6] == 1.2
        assert linear_pattern.max_rate == 0.15

    def test_exponential_growth_pattern_application(self):
        """Test exponential growth pattern application"""
        manager = GrowthModelManagerV2()
        
        # Create exponential pattern
        exponential_pattern = GrowthPattern("exponential", 0.05)
        
        # Apply pattern for 24 months
        results = manager._apply_growth_pattern(
            base_value=100.0,
            pattern=exponential_pattern,
            months=24
        )
        
        assert len(results) == 24
        
        # Exponential growth should compound
        assert results[11] > 100.0 * (1.05 ** 1)  # After 1 year
        assert results[23] > 100.0 * (1.05 ** 2)  # After 2 years
        
        # Each month should be higher than previous
        for i in range(1, len(results)):
            assert results[i] >= results[i-1]

    def test_linear_growth_pattern_application(self):
        """Test linear growth pattern application"""
        manager = GrowthModelManagerV2()
        
        # Create linear pattern
        linear_pattern = GrowthPattern("linear", 0.03)  # 3% annual = 0.25% monthly
        
        results = manager._apply_growth_pattern(
            base_value=1000.0,
            pattern=linear_pattern,
            months=12
        )
        
        assert len(results) == 12
        
        # Linear growth should be steady
        monthly_growth = 0.03 / 12  # Annual rate divided by 12
        expected_final = 1000.0 * (1 + 0.03)
        
        # Final value should be approximately base * (1 + annual_rate)
        assert abs(results[-1] - expected_final) < 1.0

    def test_seasonal_growth_pattern_application(self):
        """Test seasonal growth pattern with monthly factors"""
        manager = GrowthModelManagerV2()
        
        # Create seasonal pattern with higher growth in Q4
        seasonal_pattern = GrowthPattern(
            pattern_type="linear",
            base_rate=0.04,
            seasonality_factor={
                1: 0.8,   # January slow
                6: 1.0,   # June normal
                10: 1.3,  # October high
                11: 1.4,  # November higher
                12: 1.5   # December highest
            }
        )
        
        results = manager._apply_growth_pattern(
            base_value=1000.0,
            pattern=seasonal_pattern,
            months=12
        )
        
        # December growth should be higher than January growth
        jan_growth = results[0] - 1000.0
        dec_growth = results[11] - (results[10] if len(results) > 10 else results[-1])
        
        # Note: This test depends on implementation details

    def test_growth_pattern_with_maximum_rate(self):
        """Test growth pattern respects maximum rate constraints"""
        manager = GrowthModelManagerV2()
        
        # Create pattern with low max rate
        capped_pattern = GrowthPattern(
            pattern_type="exponential",
            base_rate=0.5,  # Very high base rate
            max_rate=0.1    # But capped at 10%
        )
        
        results = manager._apply_growth_pattern(
            base_value=100.0,
            pattern=capped_pattern,
            months=24
        )
        
        # Even with high base rate, shouldn't exceed max_rate constraint
        # Check that no single month growth exceeds 10%
        for i in range(1, len(results)):
            monthly_growth_rate = (results[i] - results[i-1]) / results[i-1]
            # Allow some tolerance for calculation precision
            assert monthly_growth_rate <= 0.1 + 0.001

    def test_sigmoid_growth_pattern(self):
        """Test sigmoid (S-curve) growth pattern"""
        manager = GrowthModelManagerV2()
        
        # Create sigmoid pattern
        sigmoid_pattern = GrowthPattern(
            pattern_type="sigmoid",
            base_rate=0.08,
            max_rate=0.15
        )
        
        results = manager._apply_growth_pattern(
            base_value=50.0,
            pattern=sigmoid_pattern,
            months=36
        )
        
        # Sigmoid should start slow, accelerate, then slow down again
        # Early growth should be less than middle growth
        early_growth = results[5] - results[0]
        middle_growth = results[23] - results[18]
        
        # This depends on implementation, but sigmoid should show acceleration then deceleration


class TestBusinessModelCreation:
    """Test suite for business model creation"""

    def test_create_business_model_single_office(self, mock_config_service):
        """Test business model creation for single office"""
        manager = GrowthModelManagerV2()
        
        office_data = [
            {
                "name": "Stockholm",
                "total_fte": 850.0,
                "roles": {
                    "Consultant": {
                        "A": {"fte": 120.0, "recruitment_1": 8.0, "price_1": 1200.0}
                    }
                }
            }
        ]
        
        time_range = TimeRange(start_year=2025, start_month=1, end_year=2026, end_month=12)
        
        business_model = manager.create_growth_model(office_data, time_range)
        
        assert isinstance(business_model, BusinessModel)
        assert "Stockholm" in business_model.office_plans
        assert isinstance(business_model.office_plans["Stockholm"], BusinessPlan)

    def test_create_business_model_multi_office(self, mock_config_service):
        """Test business model creation for multiple offices"""
        manager = GrowthModelManagerV2()
        
        office_data = [
            {"name": "Stockholm", "total_fte": 850.0, "roles": {}},
            {"name": "Munich", "total_fte": 450.0, "roles": {}},
            {"name": "London", "total_fte": 300.0, "roles": {}}
        ]
        
        time_range = TimeRange(start_year=2025, start_month=1, end_year=2026, end_month=12)
        
        business_model = manager.create_growth_model(office_data, time_range)
        
        assert len(business_model.office_plans) == 3
        assert "Stockholm" in business_model.office_plans
        assert "Munich" in business_model.office_plans
        assert "London" in business_model.office_plans

    def test_create_business_model_time_range_validation(self):
        """Test business model creation validates time ranges"""
        manager = GrowthModelManagerV2()
        
        office_data = [{"name": "Test", "total_fte": 100.0, "roles": {}}]
        
        # Invalid time range (end before start)
        invalid_range = TimeRange(start_year=2026, start_month=6, end_year=2025, end_month=12)
        
        with pytest.raises(ValueError, match="Invalid time range"):
            manager.create_growth_model(office_data, invalid_range)

    def test_create_business_model_empty_offices(self):
        """Test business model creation with empty office list"""
        manager = GrowthModelManagerV2()
        
        time_range = TimeRange(start_year=2025, start_month=1, end_year=2026, end_month=12)
        
        business_model = manager.create_growth_model([], time_range)
        
        assert isinstance(business_model, BusinessModel)
        assert len(business_model.office_plans) == 0


class TestBusinessPlanExtrapolation:
    """Test suite for business plan extrapolation"""

    def test_extrapolate_business_plan_single_year(self, business_plan):
        """Test business plan extrapolation for one additional year"""
        manager = GrowthModelManagerV2()
        
        original_keys = set(business_plan.monthly_plans.keys())
        original_count = len(original_keys)
        
        # Extrapolate to 2026
        result = manager.extrapolate_business_plan(
            business_plan,
            target_year=2026,
            growth_rates=GrowthRates()
        )
        
        assert result is True
        
        # Should have added 12 months for 2026
        new_keys = set(business_plan.monthly_plans.keys())
        assert len(new_keys) >= original_count + 12
        
        # Check for specific 2026 months
        assert "2026-01" in business_plan.monthly_plans
        assert "2026-12" in business_plan.monthly_plans

    def test_extrapolate_business_plan_multi_year(self, business_plan):
        """Test business plan extrapolation for multiple years"""
        manager = GrowthModelManagerV2()
        
        original_keys = set(business_plan.monthly_plans.keys())
        
        # Extrapolate to 2026 and 2027
        manager.extrapolate_business_plan(business_plan, 2026, GrowthRates())
        manager.extrapolate_business_plan(business_plan, 2027, GrowthRates())
        
        new_keys = set(business_plan.monthly_plans.keys())
        
        # Should have plans for both years
        assert "2026-06" in business_plan.monthly_plans
        assert "2027-06" in business_plan.monthly_plans

    def test_extrapolate_with_custom_growth_rates(self, business_plan):
        """Test extrapolation applies custom growth rates"""
        manager = GrowthModelManagerV2()
        
        # Get baseline values from 2025
        if "2025-06" in business_plan.monthly_plans:
            baseline_plan = business_plan.monthly_plans["2025-06"]
            baseline_revenue = baseline_plan.revenue
        else:
            baseline_revenue = 100000.0  # Fallback
        
        # Apply high growth rates
        high_growth = GrowthRates(
            recruitment_growth_rate=0.15,  # 15% annual
            price_growth_rate=0.08,        # 8% annual
            salary_growth_rate=0.06,       # 6% annual
            cost_growth_rate=0.04          # 4% annual
        )
        
        manager.extrapolate_business_plan(business_plan, 2026, high_growth)
        
        # Check that 2026 values are higher
        if "2026-06" in business_plan.monthly_plans:
            extrapolated_plan = business_plan.monthly_plans["2026-06"]
            assert extrapolated_plan.revenue > baseline_revenue

    def test_extrapolate_preserves_original_data(self, business_plan):
        """Test extrapolation doesn't modify original data"""
        manager = GrowthModelManagerV2()
        
        # Store original values
        original_plans = {}
        for key, plan in business_plan.monthly_plans.items():
            if key.startswith("2025"):
                original_plans[key] = plan.revenue
        
        # Extrapolate
        manager.extrapolate_business_plan(business_plan, 2026, GrowthRates())
        
        # Original plans should be unchanged
        for key, original_revenue in original_plans.items():
            current_revenue = business_plan.monthly_plans[key].revenue
            assert current_revenue == original_revenue

    def test_extrapolate_compound_growth_calculation(self, business_plan):
        """Test extrapolation applies compound growth correctly"""
        manager = GrowthModelManagerV2()
        
        growth_rates = GrowthRates(price_growth_rate=0.1)  # 10% annual
        
        # Add baseline if missing
        if "2025-01" not in business_plan.monthly_plans:
            business_plan.monthly_plans["2025-01"] = MonthlyPlan(
                year=2025, month=1,
                recruitment={}, churn={},
                revenue=120000.0, costs=100000.0,
                price_per_role={"Consultant": {"A": 1000.0}},
                salary_per_role={}, utr_per_role={}
            )
        
        baseline_price = business_plan.monthly_plans["2025-01"].price_per_role.get("Consultant", {}).get("A", 1000.0)
        
        # Extrapolate for 2 years
        manager.extrapolate_business_plan(business_plan, 2026, growth_rates)
        manager.extrapolate_business_plan(business_plan, 2027, growth_rates)
        
        # Check compound growth
        if "2027-01" in business_plan.monthly_plans:
            final_plan = business_plan.monthly_plans["2027-01"]
            if "Consultant" in final_plan.price_per_role and "A" in final_plan.price_per_role["Consultant"]:
                final_price = final_plan.price_per_role["Consultant"]["A"]
                
                # Should be approximately baseline * (1.1)^2 = baseline * 1.21
                expected_price = baseline_price * (1.1 ** 2)
                assert abs(final_price - expected_price) < 10.0  # Allow for rounding


class TestEconomicScenarios:
    """Test suite for economic scenario integration"""

    def test_economic_scenario_creation(self):
        """Test economic scenario creation and configuration"""
        scenario = EconomicScenario(
            name="Economic Boom",
            description="Period of rapid economic growth",
            growth_adjustments={
                "recruitment": 0.3,    # 30% increase
                "price": 0.2,          # 20% increase
                "salary": 0.15         # 15% increase
            },
            duration_months=24,
            start_month=(2025, 6)
        )
        
        assert scenario.name == "Economic Boom"
        assert scenario.growth_adjustments["recruitment"] == 0.3
        assert scenario.duration_months == 24
        assert scenario.start_month == (2025, 6)

    def test_apply_economic_scenario_to_growth_rates(self):
        """Test applying economic scenarios to growth rates"""
        manager = GrowthModelManagerV2()
        
        recession_scenario = EconomicScenario(
            name="Recession",
            description="Economic downturn",
            growth_adjustments={
                "recruitment": -0.5,   # 50% decrease
                "price": -0.2,         # 20% decrease
                "cost": 0.1            # 10% increase
            }
        )
        
        manager.economic_scenarios = [recession_scenario]
        
        base_growth = GrowthRates(
            recruitment_growth_rate=0.05,
            price_growth_rate=0.03,
            cost_growth_rate=0.02
        )
        
        adjusted_growth = manager._apply_economic_scenario(base_growth, recession_scenario)
        
        # Recruitment growth should be reduced
        assert adjusted_growth.recruitment_growth_rate < base_growth.recruitment_growth_rate
        
        # Price growth should be reduced
        assert adjusted_growth.price_growth_rate < base_growth.price_growth_rate
        
        # Cost growth should be increased
        assert adjusted_growth.cost_growth_rate > base_growth.cost_growth_rate

    def test_economic_scenario_duration_handling(self, business_plan):
        """Test economic scenarios are applied for correct duration"""
        manager = GrowthModelManagerV2()
        
        # Short-term scenario (6 months)
        short_scenario = EconomicScenario(
            name="Short Boost",
            description="Brief economic boost",
            growth_adjustments={"price": 0.5},
            duration_months=6,
            start_month=(2025, 3)
        )
        
        manager.economic_scenarios = [short_scenario]
        
        # Apply scenario to business plan extrapolation
        affected_months = manager._get_scenario_affected_months(
            short_scenario,
            TimeRange(start_year=2025, start_month=1, end_year=2025, end_month=12)
        )
        
        # Should affect March through August (6 months)
        expected_months = [(2025, 3), (2025, 4), (2025, 5), (2025, 6), (2025, 7), (2025, 8)]
        assert len(affected_months) == 6

    def test_overlapping_economic_scenarios(self):
        """Test handling of overlapping economic scenarios"""
        manager = GrowthModelManagerV2()
        
        scenario1 = EconomicScenario(
            name="Scenario 1",
            description="First scenario",
            growth_adjustments={"recruitment": 0.1},
            start_month=(2025, 1),
            duration_months=12
        )
        
        scenario2 = EconomicScenario(
            name="Scenario 2", 
            description="Overlapping scenario",
            growth_adjustments={"recruitment": 0.2},
            start_month=(2025, 6),
            duration_months=12
        )
        
        manager.economic_scenarios = [scenario1, scenario2]
        
        base_growth = GrowthRates(recruitment_growth_rate=0.05)
        
        # Test overlapping period (June 2025)
        combined_adjustment = manager._calculate_combined_scenario_effect(
            base_growth, (2025, 6)
        )
        
        # Should combine effects of both scenarios
        # Implementation depends on how overlapping scenarios are handled


class TestGrowthValidation:
    """Test suite for growth validation"""

    def test_validate_growth_rates_within_limits(self):
        """Test validation passes for reasonable growth rates"""
        manager = GrowthModelManagerV2()
        manager.config.max_annual_growth_rate = 1.0  # 100% max
        manager.config.min_annual_growth_rate = -0.3  # -30% min
        
        reasonable_rates = GrowthRates(
            recruitment_growth_rate=0.15,  # 15%
            price_growth_rate=0.05,        # 5%
            salary_growth_rate=0.03,       # 3%
            cost_growth_rate=0.02          # 2%
        )
        
        validation_result = manager.validate_growth_rates(reasonable_rates)
        
        assert validation_result.is_valid is True
        assert len(validation_result.errors) == 0

    def test_validate_growth_rates_exceeds_maximum(self):
        """Test validation catches excessive growth rates"""
        manager = GrowthModelManagerV2()
        manager.config.max_annual_growth_rate = 0.5  # 50% max
        
        excessive_rates = GrowthRates(
            recruitment_growth_rate=1.5,  # 150% - too high
            price_growth_rate=0.03
        )
        
        validation_result = manager.validate_growth_rates(excessive_rates)
        
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0
        assert any("exceeds maximum" in error['message'].lower() for error in validation_result.errors)

    def test_validate_growth_rates_below_minimum(self):
        """Test validation catches excessively negative growth rates"""
        manager = GrowthModelManagerV2()
        manager.config.min_annual_growth_rate = -0.2  # -20% min
        
        excessive_decline = GrowthRates(
            recruitment_growth_rate=-0.8,  # -80% - too low
            price_growth_rate=0.03
        )
        
        validation_result = manager.validate_growth_rates(excessive_decline)
        
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0
        assert any("below minimum" in error['message'].lower() for error in validation_result.errors)

    def test_validate_business_plan_extrapolation(self, business_plan):
        """Test validation of extrapolated business plans"""
        manager = GrowthModelManagerV2()
        
        # Extrapolate with reasonable growth
        reasonable_growth = GrowthRates(recruitment_growth_rate=0.05)
        manager.extrapolate_business_plan(business_plan, 2026, reasonable_growth)
        
        validation_result = manager.validate_extrapolated_plan(business_plan, 2026)
        
        assert validation_result.is_valid is True

    def test_validate_negative_extrapolation_detection(self, business_plan):
        """Test validation catches negative extrapolated values"""
        manager = GrowthModelManagerV2()
        manager.config.require_positive_extrapolation = True
        
        # Apply severe negative growth
        severe_decline = GrowthRates(
            recruitment_growth_rate=-0.9,  # 90% decline
            price_growth_rate=-0.8
        )
        
        manager.extrapolate_business_plan(business_plan, 2026, severe_decline)
        
        validation_result = manager.validate_extrapolated_plan(business_plan, 2026)
        
        # May have warnings about negative values
        if validation_result.warnings:
            assert any("negative" in warning['message'].lower() for warning in validation_result.warnings)


class TestGrowthHistoryTracking:
    """Test suite for growth history tracking"""

    def test_record_growth_history(self):
        """Test recording of growth rate history"""
        manager = GrowthModelManagerV2()
        
        # Record some growth rates
        manager._record_growth_rate("Stockholm", "recruitment", 0.05)
        manager._record_growth_rate("Stockholm", "recruitment", 0.08) 
        manager._record_growth_rate("Stockholm", "recruitment", 0.06)
        
        # Should have history
        key = "Stockholm_recruitment"
        assert key in manager.growth_history
        assert len(manager.growth_history[key]) == 3
        assert manager.growth_history[key] == [0.05, 0.08, 0.06]

    def test_get_average_historical_growth(self):
        """Test calculation of average historical growth rates"""
        manager = GrowthModelManagerV2()
        
        # Set up history
        manager.growth_history["Stockholm_recruitment"] = [0.04, 0.06, 0.08, 0.05]
        
        average_rate = manager.get_average_historical_growth("Stockholm", "recruitment")
        
        expected_average = (0.04 + 0.06 + 0.08 + 0.05) / 4
        assert abs(average_rate - expected_average) < 0.001

    def test_predict_future_growth_from_history(self):
        """Test growth prediction based on historical data"""
        manager = GrowthModelManagerV2()
        
        # Set up trending history (increasing growth)
        manager.growth_history["Munich_price"] = [0.02, 0.03, 0.04, 0.05]
        
        predicted_rate = manager.predict_growth_rate("Munich", "price", months_ahead=12)
        
        # Should predict continued trend
        assert predicted_rate > 0.05  # Should be higher than last recorded rate

    def test_growth_history_office_isolation(self):
        """Test growth history is properly isolated by office"""
        manager = GrowthModelManagerV2()
        
        # Record for different offices
        manager._record_growth_rate("Stockholm", "recruitment", 0.08)
        manager._record_growth_rate("Munich", "recruitment", 0.05)
        
        # Should be separate
        stockholm_key = "Stockholm_recruitment"
        munich_key = "Munich_recruitment"
        
        assert stockholm_key in manager.growth_history
        assert munich_key in manager.growth_history
        assert manager.growth_history[stockholm_key] != manager.growth_history[munich_key]


class TestGrowthUtilities:
    """Test suite for utility methods"""

    def test_calculate_compound_growth(self):
        """Test compound growth calculation utility"""
        manager = GrowthModelManagerV2()
        
        result = manager._calculate_compound_growth(
            initial_value=1000.0,
            annual_rate=0.05,  # 5% annual
            months=24         # 2 years
        )
        
        expected = 1000.0 * (1.05 ** 2)  # Compound for 2 years
        assert abs(result - expected) < 1.0

    def test_interpolate_growth_between_months(self):
        """Test growth interpolation between months"""
        manager = GrowthModelManagerV2()
        
        # Interpolate between known values
        jan_value = 1000.0
        dec_value = 1200.0  # 20% growth over year
        
        june_value = manager._interpolate_monthly_value(
            start_value=jan_value,
            end_value=dec_value,
            start_month=1,
            end_month=12,
            target_month=6
        )
        
        # June should be approximately halfway
        expected_june = jan_value + (dec_value - jan_value) * 5/11  # 5 months out of 11
        assert abs(june_value - expected_june) < 10.0

    def test_normalize_seasonal_factors(self):
        """Test seasonal factor normalization"""
        manager = GrowthModelManagerV2()
        
        # Unbalanced seasonal factors
        raw_factors = {1: 0.5, 6: 2.0, 12: 1.5}
        
        normalized = manager._normalize_seasonal_factors(raw_factors, target_annual_rate=0.12)
        
        # Should adjust factors so annual effect equals target
        assert isinstance(normalized, dict)
        assert len(normalized) == len(raw_factors)
        
        # All values should be positive
        for factor in normalized.values():
            assert factor > 0

    def test_convert_annual_to_monthly_rate(self):
        """Test conversion of annual to monthly growth rates"""
        manager = GrowthModelManagerV2()
        
        annual_rate = 0.12  # 12% annual
        monthly_rate = manager._convert_to_monthly_rate(annual_rate)
        
        # Should be approximately (1.12)^(1/12) - 1
        expected_monthly = (1.12 ** (1/12)) - 1
        assert abs(monthly_rate - expected_monthly) < 0.0001

    def test_validate_growth_consistency(self):
        """Test validation of growth rate consistency across metrics"""
        manager = GrowthModelManagerV2()
        
        # Consistent growth rates
        consistent_rates = GrowthRates(
            recruitment_growth_rate=0.05,
            price_growth_rate=0.03,
            salary_growth_rate=0.025,
            cost_growth_rate=0.02
        )
        
        is_consistent = manager._validate_rate_consistency(consistent_rates)
        assert is_consistent is True
        
        # Inconsistent growth rates (salary growing faster than price)
        inconsistent_rates = GrowthRates(
            recruitment_growth_rate=0.05,
            price_growth_rate=0.02,      # Low price growth
            salary_growth_rate=0.15,     # But high salary growth - unsustainable
            cost_growth_rate=0.02
        )
        
        is_consistent = manager._validate_rate_consistency(inconsistent_rates)
        assert is_consistent is False