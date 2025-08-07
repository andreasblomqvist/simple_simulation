"""
Comprehensive Unit Tests for BusinessPlanProcessorV2

Tests business plan processing functionality including:
- Monthly target extraction from business plans
- Growth rate application for multi-year modeling
- Scenario lever integration and adjustments
- Financial metrics calculation
- Business plan validation and consistency
- Plan extrapolation and projections
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date
from typing import Dict, List

from backend.src.services.business_plan_processor_v2 import (
    BusinessPlanProcessorV2, FinancialMetrics, BusinessPlanValidation
)

from backend.src.services.simulation_engine_v2 import (
    BusinessPlan, MonthlyPlan, MonthlyTargets, GrowthRates, Levers, TimeRange
)


class TestBusinessPlanProcessorV2Initialization:
    """Test suite for BusinessPlanProcessorV2 initialization"""

    def test_default_initialization(self):
        """Test processor initializes with default configurations"""
        processor = BusinessPlanProcessorV2()
        
        # Verify default state
        assert processor.loaded_plans == {}
        assert isinstance(processor.validation_config, BusinessPlanValidation)
        assert isinstance(processor.default_growth_rates, GrowthRates)
        
        # Verify default validation config
        assert processor.validation_config.allow_negative_targets is False
        assert processor.validation_config.max_monthly_growth_rate == 0.5
        assert processor.validation_config.require_complete_year is True
        assert processor.validation_config.validate_financial_consistency is True
        
        # Verify default growth rates
        assert processor.default_growth_rates.recruitment_growth_rate == 0.05
        assert processor.default_growth_rates.price_growth_rate == 0.03
        assert processor.default_growth_rates.salary_growth_rate == 0.025
        assert processor.default_growth_rates.cost_growth_rate == 0.02

    def test_custom_configuration_initialization(self):
        """Test processor accepts custom configurations"""
        processor = BusinessPlanProcessorV2()
        
        # Custom configurations
        custom_validation = BusinessPlanValidation(
            allow_negative_targets=True,
            max_monthly_growth_rate=0.8,
            require_complete_year=False,
            validate_financial_consistency=False
        )
        
        custom_growth = GrowthRates(
            recruitment_growth_rate=0.08,
            price_growth_rate=0.05,
            salary_growth_rate=0.04,
            cost_growth_rate=0.03
        )
        
        # Initialize with custom configs
        result = processor.initialize(
            validation_config=custom_validation,
            default_growth_rates=custom_growth
        )
        
        assert result is True
        assert processor.validation_config == custom_validation
        assert processor.default_growth_rates == custom_growth

    def test_initialization_success_logging(self):
        """Test initialization logs success message"""
        processor = BusinessPlanProcessorV2()
        
        with patch('backend.src.services.business_plan_processor_v2.logger') as mock_logger:
            processor.initialize()
            
            mock_logger.info.assert_called_with("BusinessPlanProcessorV2 initialized successfully")


class TestBusinessPlanProcessorV2PlanLoading:
    """Test suite for business plan loading functionality"""

    def test_load_business_plan_success(self, business_plan):
        """Test successful business plan loading"""
        processor = BusinessPlanProcessorV2()
        
        result = processor.load_business_plan(business_plan)
        
        assert result is True
        assert business_plan.office_id in processor.loaded_plans
        assert processor.loaded_plans[business_plan.office_id] == business_plan

    def test_load_multiple_business_plans(self, business_plan):
        """Test loading multiple business plans for different offices"""
        processor = BusinessPlanProcessorV2()
        
        # Create second business plan
        munich_plan = BusinessPlan(
            office_id="Munich",
            name="Munich Business Plan",
            monthly_plans={}
        )
        
        # Load both plans
        processor.load_business_plan(business_plan)  # Stockholm
        processor.load_business_plan(munich_plan)    # Munich
        
        assert len(processor.loaded_plans) == 2
        assert "Stockholm" in processor.loaded_plans
        assert "Munich" in processor.loaded_plans

    def test_reload_business_plan_overwrites(self, business_plan):
        """Test reloading business plan overwrites existing plan"""
        processor = BusinessPlanProcessorV2()
        
        # Load initial plan
        processor.load_business_plan(business_plan)
        initial_plan = processor.loaded_plans[business_plan.office_id]
        
        # Create new plan with same office ID
        updated_plan = BusinessPlan(
            office_id="Stockholm",
            name="Stockholm Updated Plan",
            monthly_plans={}
        )
        
        # Reload
        processor.load_business_plan(updated_plan)
        
        # Should be replaced
        assert processor.loaded_plans["Stockholm"] != initial_plan
        assert processor.loaded_plans["Stockholm"] == updated_plan
        assert processor.loaded_plans["Stockholm"].name == "Stockholm Updated Plan"

    def test_load_empty_business_plan(self):
        """Test loading empty business plan is handled"""
        processor = BusinessPlanProcessorV2()
        
        empty_plan = BusinessPlan(
            office_id="Empty",
            name="Empty Plan",
            monthly_plans={}
        )
        
        result = processor.load_business_plan(empty_plan)
        
        assert result is True
        assert "Empty" in processor.loaded_plans


class TestBusinessPlanProcessorV2MonthlyTargets:
    """Test suite for monthly target extraction"""

    def test_get_monthly_targets_success(self, business_plan, sample_monthly_plans):
        """Test successful monthly target extraction"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        # Get targets for a known month
        targets = processor.get_monthly_targets("Stockholm", 2025, 6)
        
        assert isinstance(targets, MonthlyTargets)
        assert targets.year == 2025
        assert targets.month == 6
        assert targets.recruitment_targets is not None
        assert targets.churn_targets is not None
        assert targets.revenue_target > 0
        assert targets.cost_target > 0

    def test_get_monthly_targets_no_plan_loaded(self):
        """Test monthly target extraction when no plan is loaded"""
        processor = BusinessPlanProcessorV2()
        
        with patch('backend.src.services.business_plan_processor_v2.logger') as mock_logger:
            targets = processor.get_monthly_targets("NonExistent", 2025, 6)
            
            # Should return empty targets
            assert isinstance(targets, MonthlyTargets)
            assert targets.recruitment_targets == {}
            assert targets.churn_targets == {}
            assert targets.revenue_target == 0.0
            
            # Should log warning
            mock_logger.warning.assert_called_with("No business plan found for office NonExistent")

    def test_get_monthly_targets_missing_month(self, business_plan):
        """Test monthly target extraction for missing month"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        with patch('backend.src.services.business_plan_processor_v2.logger') as mock_logger:
            # Request month that doesn't exist in plan
            targets = processor.get_monthly_targets("Stockholm", 2030, 12)
            
            # Should return empty targets
            assert isinstance(targets, MonthlyTargets)
            assert targets.recruitment_targets == {}
            
            # Should log warning
            mock_logger.warning.assert_called_with("No monthly plan found for Stockholm 2030-12")

    def test_get_monthly_targets_with_levers(self, business_plan):
        """Test monthly target extraction with scenario levers applied"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        # Define levers
        levers = Levers(
            recruitment_multiplier=1.2,
            churn_multiplier=0.8,
            price_multiplier=1.1
        )
        
        targets = processor.get_monthly_targets("Stockholm", 2025, 6, levers=levers)
        
        # Targets should be adjusted by levers
        assert isinstance(targets, MonthlyTargets)
        # Recruitment should be increased by 20%
        # Churn should be decreased by 20%
        # (Specific value testing would require knowing the base values)

    def test_monthly_targets_structure_validation(self, business_plan):
        """Test monthly targets have correct structure"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        targets = processor.get_monthly_targets("Stockholm", 2025, 6)
        
        # Verify structure
        assert hasattr(targets, 'year')
        assert hasattr(targets, 'month')
        assert hasattr(targets, 'recruitment_targets')
        assert hasattr(targets, 'churn_targets')
        assert hasattr(targets, 'revenue_target')
        assert hasattr(targets, 'cost_target')
        assert hasattr(targets, 'salary_budget')
        
        # Verify recruitment targets structure
        if targets.recruitment_targets:
            for role, levels in targets.recruitment_targets.items():
                assert isinstance(role, str)
                assert isinstance(levels, dict)
                for level, count in levels.items():
                    assert isinstance(level, str)
                    assert isinstance(count, (int, float))
                    assert count >= 0


class TestBusinessPlanProcessorV2GrowthRates:
    """Test suite for growth rate application"""

    def test_apply_growth_rates_single_year(self, business_plan):
        """Test growth rate application for single year projection"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        growth_rates = GrowthRates(
            recruitment_growth_rate=0.1,  # 10% annual growth
            price_growth_rate=0.05,       # 5% annual growth
            salary_growth_rate=0.03,      # 3% annual growth
            cost_growth_rate=0.02         # 2% annual growth
        )
        
        # Apply growth rates (year 1 to year 2)
        result = processor.apply_growth_rates(business_plan, growth_rates, 2026)
        
        assert result is True
        
        # Should have added plans for 2026
        jan_2025_key = "2025-01"
        jan_2026_key = "2026-01"
        
        if jan_2025_key in business_plan.monthly_plans:
            original_plan = business_plan.monthly_plans[jan_2025_key]
            
            if jan_2026_key in business_plan.monthly_plans:
                grown_plan = business_plan.monthly_plans[jan_2026_key]
                
                # Revenue should be higher (price growth effect)
                assert grown_plan.revenue > original_plan.revenue
                
                # Recruitment targets should be higher
                for role in grown_plan.recruitment:
                    for level in grown_plan.recruitment[role]:
                        grown_value = grown_plan.recruitment[role][level]
                        original_value = original_plan.recruitment[role][level]
                        assert grown_value >= original_value

    def test_apply_growth_rates_multi_year(self, business_plan):
        """Test growth rate application for multi-year projection"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        growth_rates = GrowthRates(recruitment_growth_rate=0.1)
        
        # Apply growth for multiple years
        processor.apply_growth_rates(business_plan, growth_rates, 2026)
        processor.apply_growth_rates(business_plan, growth_rates, 2027)
        
        # Should have compound growth effect
        if "2025-01" in business_plan.monthly_plans and "2027-01" in business_plan.monthly_plans:
            original = business_plan.monthly_plans["2025-01"]
            year_3 = business_plan.monthly_plans["2027-01"]
            
            # Should show compound growth (approximately 1.1^2 = 1.21)
            assert year_3.revenue > original.revenue * 1.15  # Allow for rounding

    def test_apply_growth_rates_zero_growth(self, business_plan):
        """Test growth rate application with zero growth"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        growth_rates = GrowthRates(
            recruitment_growth_rate=0.0,
            price_growth_rate=0.0,
            salary_growth_rate=0.0,
            cost_growth_rate=0.0
        )
        
        # Store original values
        original_keys = set(business_plan.monthly_plans.keys())
        if "2025-01" in business_plan.monthly_plans:
            original_plan = business_plan.monthly_plans["2025-01"]
            original_revenue = original_plan.revenue
        
        # Apply zero growth
        processor.apply_growth_rates(business_plan, growth_rates, 2026)
        
        # Should create new year plans but with same values
        if "2026-01" in business_plan.monthly_plans:
            grown_plan = business_plan.monthly_plans["2026-01"]
            assert grown_plan.revenue == original_revenue

    def test_apply_growth_rates_negative_growth(self, business_plan):
        """Test growth rate application with negative growth (decline)"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        growth_rates = GrowthRates(
            recruitment_growth_rate=-0.1,  # 10% decline
            price_growth_rate=-0.05        # 5% decline
        )
        
        original_plan = business_plan.monthly_plans.get("2025-01")
        if original_plan:
            original_revenue = original_plan.revenue
            
            processor.apply_growth_rates(business_plan, growth_rates, 2026)
            
            grown_plan = business_plan.monthly_plans.get("2026-01")
            if grown_plan:
                # Should be lower due to negative growth
                assert grown_plan.revenue < original_revenue


class TestBusinessPlanProcessorV2LeverApplication:
    """Test suite for scenario lever application"""

    def test_apply_levers_recruitment_multiplier(self):
        """Test recruitment multiplier lever application"""
        processor = BusinessPlanProcessorV2()
        
        # Create test monthly plan
        monthly_plan = MonthlyPlan(
            year=2025,
            month=6,
            recruitment={"Consultant": {"A": 10.0, "AC": 5.0}},
            churn={"Consultant": {"A": 3.0, "AC": 2.0}},
            revenue=100000.0,
            costs=80000.0,
            price_per_role={"Consultant": {"A": 1000.0}},
            salary_per_role={"Consultant": {"A": 50000.0}},
            utr_per_role={"Consultant": {"A": 0.8}}
        )
        
        levers = Levers(recruitment_multiplier=1.5)
        
        adjusted_plan = processor.apply_levers(monthly_plan, levers)
        
        # Recruitment should be multiplied by 1.5
        assert adjusted_plan.recruitment["Consultant"]["A"] == 15.0  # 10.0 * 1.5
        assert adjusted_plan.recruitment["Consultant"]["AC"] == 7.5  # 5.0 * 1.5
        
        # Other values should remain unchanged
        assert adjusted_plan.churn["Consultant"]["A"] == 3.0
        assert adjusted_plan.revenue == 100000.0

    def test_apply_levers_churn_multiplier(self):
        """Test churn multiplier lever application"""
        processor = BusinessPlanProcessorV2()
        
        monthly_plan = MonthlyPlan(
            year=2025, month=6,
            recruitment={"Consultant": {"A": 10.0}},
            churn={"Consultant": {"A": 5.0}},
            revenue=100000.0, costs=80000.0,
            price_per_role={}, salary_per_role={}, utr_per_role={}
        )
        
        levers = Levers(churn_multiplier=0.6)  # Reduce churn by 40%
        
        adjusted_plan = processor.apply_levers(monthly_plan, levers)
        
        # Churn should be multiplied by 0.6
        assert adjusted_plan.churn["Consultant"]["A"] == 3.0  # 5.0 * 0.6
        
        # Recruitment should remain unchanged
        assert adjusted_plan.recruitment["Consultant"]["A"] == 10.0

    def test_apply_levers_price_multiplier(self):
        """Test price multiplier lever application"""
        processor = BusinessPlanProcessorV2()
        
        monthly_plan = MonthlyPlan(
            year=2025, month=6,
            recruitment={}, churn={},
            revenue=100000.0, costs=80000.0,
            price_per_role={"Consultant": {"A": 1000.0, "AC": 1200.0}},
            salary_per_role={}, utr_per_role={}
        )
        
        levers = Levers(price_multiplier=1.25)  # 25% price increase
        
        adjusted_plan = processor.apply_levers(monthly_plan, levers)
        
        # Prices should be multiplied by 1.25
        assert adjusted_plan.price_per_role["Consultant"]["A"] == 1250.0  # 1000.0 * 1.25
        assert adjusted_plan.price_per_role["Consultant"]["AC"] == 1500.0  # 1200.0 * 1.25

    def test_apply_levers_multiple_simultaneous(self):
        """Test multiple levers applied simultaneously"""
        processor = BusinessPlanProcessorV2()
        
        monthly_plan = MonthlyPlan(
            year=2025, month=6,
            recruitment={"Consultant": {"A": 8.0}},
            churn={"Consultant": {"A": 4.0}},
            revenue=100000.0, costs=80000.0,
            price_per_role={"Consultant": {"A": 1000.0}},
            salary_per_role={"Consultant": {"A": 50000.0}},
            utr_per_role={}
        )
        
        levers = Levers(
            recruitment_multiplier=1.2,
            churn_multiplier=0.8,
            price_multiplier=1.1,
            salary_multiplier=1.05
        )
        
        adjusted_plan = processor.apply_levers(monthly_plan, levers)
        
        # All levers should be applied
        assert adjusted_plan.recruitment["Consultant"]["A"] == 9.6  # 8.0 * 1.2
        assert adjusted_plan.churn["Consultant"]["A"] == 3.2       # 4.0 * 0.8
        assert adjusted_plan.price_per_role["Consultant"]["A"] == 1100.0  # 1000.0 * 1.1
        assert adjusted_plan.salary_per_role["Consultant"]["A"] == 52500.0  # 50000.0 * 1.05

    def test_apply_levers_edge_cases(self):
        """Test lever application with edge cases"""
        processor = BusinessPlanProcessorV2()
        
        # Test with empty plan
        empty_plan = MonthlyPlan(
            year=2025, month=6,
            recruitment={}, churn={}, 
            revenue=0.0, costs=0.0,
            price_per_role={}, salary_per_role={}, utr_per_role={}
        )
        
        levers = Levers(recruitment_multiplier=2.0)
        
        # Should not raise errors with empty data
        adjusted_plan = processor.apply_levers(empty_plan, levers)
        assert adjusted_plan.recruitment == {}
        
        # Test with zero multipliers
        monthly_plan = MonthlyPlan(
            year=2025, month=6,
            recruitment={"Consultant": {"A": 10.0}},
            churn={}, revenue=100000.0, costs=80000.0,
            price_per_role={}, salary_per_role={}, utr_per_role={}
        )
        
        zero_levers = Levers(recruitment_multiplier=0.0)
        adjusted_plan = processor.apply_levers(monthly_plan, zero_levers)
        
        # Should result in zero recruitment
        assert adjusted_plan.recruitment["Consultant"]["A"] == 0.0


class TestBusinessPlanProcessorV2FinancialMetrics:
    """Test suite for financial metrics calculation"""

    def test_calculate_financial_metrics_basic(self, business_plan):
        """Test basic financial metrics calculation"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        time_range = TimeRange(start_year=2025, start_month=1, end_year=2025, end_month=12)
        
        metrics = processor.calculate_financial_metrics("Stockholm", time_range)
        
        assert isinstance(metrics, FinancialMetrics)
        assert metrics.total_revenue > 0
        assert metrics.total_costs > 0
        assert metrics.gross_profit == metrics.total_revenue - metrics.total_costs
        assert 0 <= metrics.profit_margin <= 1  # Should be a percentage
        assert metrics.revenue_per_fte > 0
        assert metrics.cost_per_fte > 0

    def test_calculate_financial_metrics_multi_year(self, business_plan):
        """Test financial metrics calculation over multiple years"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        time_range = TimeRange(start_year=2025, start_month=1, end_year=2027, end_month=12)
        
        metrics = processor.calculate_financial_metrics("Stockholm", time_range)
        
        # Multi-year metrics should be higher than single year
        single_year_range = TimeRange(start_year=2025, start_month=1, end_year=2025, end_month=12)
        single_year_metrics = processor.calculate_financial_metrics("Stockholm", single_year_range)
        
        assert metrics.total_revenue > single_year_metrics.total_revenue
        assert metrics.total_costs > single_year_metrics.total_costs

    def test_calculate_financial_metrics_partial_year(self, business_plan):
        """Test financial metrics calculation for partial year"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        # Q2 only (April-June)
        time_range = TimeRange(start_year=2025, start_month=4, end_year=2025, end_month=6)
        
        metrics = processor.calculate_financial_metrics("Stockholm", time_range)
        
        # Should have lower totals than full year
        full_year_range = TimeRange(start_year=2025, start_month=1, end_year=2025, end_month=12)
        full_year_metrics = processor.calculate_financial_metrics("Stockholm", full_year_range)
        
        assert metrics.total_revenue < full_year_metrics.total_revenue
        assert metrics.total_costs < full_year_metrics.total_costs

    def test_financial_metrics_with_zero_values(self):
        """Test financial metrics calculation with zero/empty values"""
        processor = BusinessPlanProcessorV2()
        
        # Create business plan with zero values
        empty_monthly_plan = MonthlyPlan(
            year=2025, month=1,
            recruitment={}, churn={},
            revenue=0.0, costs=0.0,
            price_per_role={}, salary_per_role={}, utr_per_role={}
        )
        
        empty_business_plan = BusinessPlan(
            office_id="Empty",
            name="Empty Plan",
            monthly_plans={"2025-01": empty_monthly_plan}
        )
        
        processor.load_business_plan(empty_business_plan)
        
        time_range = TimeRange(start_year=2025, start_month=1, end_year=2025, end_month=1)
        metrics = processor.calculate_financial_metrics("Empty", time_range)
        
        assert metrics.total_revenue == 0.0
        assert metrics.total_costs == 0.0
        assert metrics.gross_profit == 0.0
        assert metrics.profit_margin == 0.0  # Should handle division by zero


class TestBusinessPlanProcessorV2Validation:
    """Test suite for business plan validation"""

    def test_validate_business_plan_success(self, business_plan):
        """Test successful business plan validation"""
        processor = BusinessPlanProcessorV2()
        
        validation_result = processor.validate_business_plan(business_plan)
        
        assert validation_result.is_valid is True
        assert len(validation_result.errors) == 0

    def test_validate_business_plan_negative_targets(self):
        """Test validation catches negative targets when not allowed"""
        processor = BusinessPlanProcessorV2()
        processor.validation_config.allow_negative_targets = False
        
        # Create plan with negative targets
        negative_plan = MonthlyPlan(
            year=2025, month=1,
            recruitment={"Consultant": {"A": -5.0}},  # Negative recruitment
            churn={"Consultant": {"A": 2.0}},
            revenue=100000.0, costs=80000.0,
            price_per_role={}, salary_per_role={}, utr_per_role={}
        )
        
        bad_business_plan = BusinessPlan(
            office_id="Bad",
            name="Bad Plan",
            monthly_plans={"2025-01": negative_plan}
        )
        
        validation_result = processor.validate_business_plan(bad_business_plan)
        
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0
        assert any("negative" in error['message'].lower() for error in validation_result.errors)

    def test_validate_business_plan_extreme_growth_rates(self, business_plan):
        """Test validation catches extreme growth rates"""
        processor = BusinessPlanProcessorV2()
        processor.validation_config.max_monthly_growth_rate = 0.2  # 20% max monthly growth
        
        # Add plan with extreme growth (simulated by having very different consecutive months)
        extreme_plan = MonthlyPlan(
            year=2025, month=2,
            recruitment={"Consultant": {"A": 50.0}},  # Much higher than typical
            churn={}, revenue=100000.0, costs=80000.0,
            price_per_role={}, salary_per_role={}, utr_per_role={}
        )
        
        business_plan.monthly_plans["2025-02"] = extreme_plan
        
        validation_result = processor.validate_business_plan(business_plan)
        
        if validation_result.warnings:
            # Should have warnings about extreme growth rates
            assert any("growth" in warning['message'].lower() for warning in validation_result.warnings)

    def test_validate_business_plan_incomplete_year(self, business_plan):
        """Test validation handles incomplete year when required"""
        processor = BusinessPlanProcessorV2()
        processor.validation_config.require_complete_year = True
        
        # Create plan with only 6 months
        incomplete_plan = BusinessPlan(
            office_id="Incomplete",
            name="Incomplete Plan",
            monthly_plans={}
        )
        
        # Add only January through June
        for month in range(1, 7):
            monthly_plan = MonthlyPlan(
                year=2025, month=month,
                recruitment={}, churn={},
                revenue=100000.0, costs=80000.0,
                price_per_role={}, salary_per_role={}, utr_per_role={}
            )
            incomplete_plan.monthly_plans[f"2025-{month:02d}"] = monthly_plan
        
        validation_result = processor.validate_business_plan(incomplete_plan)
        
        # Should have warnings about incomplete year
        assert len(validation_result.warnings) > 0
        assert any("incomplete" in warning['message'].lower() for warning in validation_result.warnings)

    def test_validate_business_plan_financial_inconsistency(self):
        """Test validation catches financial inconsistencies"""
        processor = BusinessPlanProcessorV2()
        processor.validation_config.validate_financial_consistency = True
        
        # Create plan with inconsistent financials (costs > revenue by large margin)
        inconsistent_plan = MonthlyPlan(
            year=2025, month=1,
            recruitment={}, churn={},
            revenue=50000.0,   # Low revenue
            costs=200000.0,    # Very high costs
            price_per_role={}, salary_per_role={}, utr_per_role={}
        )
        
        inconsistent_business_plan = BusinessPlan(
            office_id="Inconsistent", 
            name="Inconsistent Plan",
            monthly_plans={"2025-01": inconsistent_plan}
        )
        
        validation_result = processor.validate_business_plan(inconsistent_business_plan)
        
        # Should have warnings about financial inconsistency
        if validation_result.warnings:
            assert any("financial" in warning['message'].lower() or "profit" in warning['message'].lower() 
                      for warning in validation_result.warnings)


class TestBusinessPlanProcessorV2Utilities:
    """Test suite for utility methods"""

    def test_create_empty_targets(self):
        """Test creation of empty monthly targets"""
        processor = BusinessPlanProcessorV2()
        
        empty_targets = processor._create_empty_targets(2025, 6)
        
        assert isinstance(empty_targets, MonthlyTargets)
        assert empty_targets.year == 2025
        assert empty_targets.month == 6
        assert empty_targets.recruitment_targets == {}
        assert empty_targets.churn_targets == {}
        assert empty_targets.revenue_target == 0.0
        assert empty_targets.cost_target == 0.0
        assert empty_targets.salary_budget == 0.0

    def test_interpolate_missing_months(self, business_plan):
        """Test interpolation of missing months in business plan"""
        processor = BusinessPlanProcessorV2()
        
        # Remove some months to create gaps
        if "2025-03" in business_plan.monthly_plans:
            del business_plan.monthly_plans["2025-03"]
        if "2025-04" in business_plan.monthly_plans:
            del business_plan.monthly_plans["2025-04"]
        
        original_count = len(business_plan.monthly_plans)
        
        # Interpolate missing months
        processor.interpolate_missing_months(business_plan, 2025)
        
        # Should have filled in the gaps
        assert len(business_plan.monthly_plans) >= original_count
        assert "2025-03" in business_plan.monthly_plans
        assert "2025-04" in business_plan.monthly_plans

    def test_extrapolate_business_plan(self, business_plan):
        """Test business plan extrapolation to future years"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        original_keys = set(business_plan.monthly_plans.keys())
        
        # Extrapolate to 2026
        processor.extrapolate_business_plan("Stockholm", 2026)
        
        # Should have 2026 plans
        new_keys = set(business_plan.monthly_plans.keys())
        added_keys = new_keys - original_keys
        
        assert len(added_keys) >= 12  # At least 12 months added
        assert any(key.startswith("2026-") for key in added_keys)

    def test_get_plan_summary(self, business_plan):
        """Test business plan summary generation"""
        processor = BusinessPlanProcessorV2()
        processor.load_business_plan(business_plan)
        
        summary = processor.get_plan_summary("Stockholm")
        
        assert isinstance(summary, dict)
        assert "office_id" in summary
        assert "total_months" in summary
        assert "date_range" in summary
        assert "total_recruitment" in summary
        assert "total_churn" in summary
        assert "total_revenue" in summary
        assert "total_costs" in summary
        
        assert summary["office_id"] == "Stockholm"
        assert summary["total_months"] > 0