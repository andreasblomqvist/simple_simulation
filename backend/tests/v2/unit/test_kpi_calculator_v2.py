"""
Comprehensive Unit Tests for KPICalculatorV2

Tests KPI calculation functionality including:
- Workforce metrics (headcount, turnover, progression rates)
- Financial metrics (revenue, costs, profitability)  
- Business intelligence (utilization, efficiency, growth rates)
- Comparative analysis (vs targets, vs previous periods)
- Executive summary generation
- Trend analysis and forecasting
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date, timedelta
from typing import Dict, List
import statistics

from backend.src.services.kpi_calculator_v2 import (
    KPICalculatorV2, WorkforceKPIs, FinancialKPIs, BusinessIntelligenceKPIs,
    ComparativeKPIs, ExecutiveSummary
)

from backend.src.services.simulation_engine_v2 import (
    SimulationResults, BusinessModel, PersonEvent, EventType, MonthlyResults,
    Person, OfficeState, MonthlyTargets
)


class TestKPICalculatorV2Initialization:
    """Test suite for KPICalculatorV2 initialization"""

    def test_default_initialization(self):
        """Test calculator initializes with default configurations"""
        calculator = KPICalculatorV2()
        
        # Verify default state
        assert calculator.calculation_cache == {}
        assert calculator.benchmark_data == {}
        assert isinstance(calculator.calculation_methods, dict)
        assert len(calculator.calculation_methods) > 0

    def test_custom_configuration_initialization(self):
        """Test calculator accepts custom configurations"""
        calculator = KPICalculatorV2()
        
        custom_config = {
            'cache_enabled': False,
            'precision_decimals': 4,
            'benchmark_source': 'industry_data',
            'calculation_mode': 'detailed'
        }
        
        result = calculator.initialize(**custom_config)
        
        assert result is True
        assert calculator.cache_enabled is False
        assert calculator.precision_decimals == 4

    def test_initialization_success_logging(self):
        """Test initialization logs success message"""
        calculator = KPICalculatorV2()
        
        with patch('backend.src.services.kpi_calculator_v2.logger') as mock_logger:
            calculator.initialize()
            
            mock_logger.info.assert_called_with("KPICalculatorV2 initialized successfully")

    def test_calculation_methods_setup(self):
        """Test calculation methods are properly registered"""
        calculator = KPICalculatorV2()
        
        expected_methods = [
            'workforce_kpis', 'financial_kpis', 'business_intelligence_kpis',
            'comparative_kpis', 'executive_summary'
        ]
        
        for method in expected_methods:
            assert method in calculator.calculation_methods
            assert callable(calculator.calculation_methods[method])


class TestKPICalculatorV2WorkforceMetrics:
    """Test suite for workforce KPI calculations"""

    def test_calculate_workforce_kpis_basic(self, test_person_factory):
        """Test basic workforce KPI calculations"""
        calculator = KPICalculatorV2()
        
        # Create test persons
        persons = [
            test_person_factory(role="Consultant", level="A", office="Stockholm"),
            test_person_factory(role="Consultant", level="AC", office="Stockholm"),
            test_person_factory(role="Operations", level="Junior", office="Stockholm")
        ]
        
        # Create test events
        events = [
            PersonEvent(
                date=date(2025, 6, 15),
                event_type=EventType.HIRED,
                details={"role": "Consultant", "level": "A"},
                simulation_month=5
            ),
            PersonEvent(
                date=date(2025, 6, 20),
                event_type=EventType.CHURNED,
                details={"role": "Operations", "level": "Junior"},
                simulation_month=5
            )
        ]
        
        workforce_kpis = calculator.calculate_workforce_kpis(persons, events, 6)
        
        assert isinstance(workforce_kpis, WorkforceKPIs)
        assert workforce_kpis.total_headcount == 3
        assert workforce_kpis.total_recruitment == 1
        assert workforce_kpis.total_churn == 1
        assert workforce_kpis.net_recruitment == 0
        assert workforce_kpis.headcount_by_role["Consultant"] == 2
        assert workforce_kpis.headcount_by_role["Operations"] == 1

    def test_calculate_workforce_kpis_empty_data(self):
        """Test workforce KPI calculation with empty data"""
        calculator = KPICalculatorV2()
        
        workforce_kpis = calculator.calculate_workforce_kpis([], [], 1)
        
        assert workforce_kpis.total_headcount == 0
        assert workforce_kpis.total_recruitment == 0
        assert workforce_kpis.total_churn == 0
        assert workforce_kpis.net_recruitment == 0
        assert workforce_kpis.churn_rate == 0.0
        assert workforce_kpis.recruitment_rate == 0.0

    def test_calculate_headcount_by_role(self, test_person_factory):
        """Test headcount calculation by role"""
        calculator = KPICalculatorV2()
        
        persons = [
            test_person_factory(role="Consultant", level="A"),
            test_person_factory(role="Consultant", level="AC"),
            test_person_factory(role="Consultant", level="C"),
            test_person_factory(role="Operations", level="Junior"),
            test_person_factory(role="Operations", level="Senior"),
            test_person_factory(role="Marketing", level="Specialist")
        ]
        
        headcount_by_role = calculator._calculate_headcount_by_role(persons)
        
        assert headcount_by_role["Consultant"] == 3
        assert headcount_by_role["Operations"] == 2
        assert headcount_by_role["Marketing"] == 1

    def test_calculate_headcount_by_level(self, test_person_factory):
        """Test headcount calculation by level"""
        calculator = KPICalculatorV2()
        
        persons = [
            test_person_factory(role="Consultant", level="A"),
            test_person_factory(role="Consultant", level="A"),
            test_person_factory(role="Consultant", level="AC"),
            test_person_factory(role="Operations", level="Junior"),
            test_person_factory(role="Operations", level="Senior")
        ]
        
        headcount_by_level = calculator._calculate_headcount_by_level(persons)
        
        assert headcount_by_level["A"] == 2
        assert headcount_by_level["AC"] == 1
        assert headcount_by_level["Junior"] == 1
        assert headcount_by_level["Senior"] == 1

    def test_calculate_recruitment_metrics(self):
        """Test recruitment metrics calculation from events"""
        calculator = KPICalculatorV2()
        
        events = [
            PersonEvent(date=date(2025, 6, 1), event_type=EventType.HIRED, 
                       details={"role": "Consultant", "level": "A"}, simulation_month=5),
            PersonEvent(date=date(2025, 6, 5), event_type=EventType.HIRED,
                       details={"role": "Consultant", "level": "AC"}, simulation_month=5),
            PersonEvent(date=date(2025, 6, 10), event_type=EventType.HIRED,
                       details={"role": "Operations", "level": "Junior"}, simulation_month=5),
            PersonEvent(date=date(2025, 6, 15), event_type=EventType.CHURNED,
                       details={"role": "Consultant", "level": "C"}, simulation_month=5)
        ]
        
        total_recruitment, recruitment_by_role = calculator._calculate_recruitment_metrics(events)
        
        assert total_recruitment == 3
        assert recruitment_by_role["Consultant"] == 2
        assert recruitment_by_role["Operations"] == 1

    def test_calculate_churn_metrics(self):
        """Test churn metrics calculation from events"""
        calculator = KPICalculatorV2()
        
        events = [
            PersonEvent(date=date(2025, 6, 1), event_type=EventType.CHURNED,
                       details={"role": "Consultant", "level": "A"}, simulation_month=5),
            PersonEvent(date=date(2025, 6, 5), event_type=EventType.CHURNED,
                       details={"role": "Consultant", "level": "C"}, simulation_month=5),
            PersonEvent(date=date(2025, 6, 10), event_type=EventType.HIRED,
                       details={"role": "Operations", "level": "Junior"}, simulation_month=5)
        ]
        
        total_churn, churn_by_role = calculator._calculate_churn_metrics(events)
        
        assert total_churn == 2
        assert churn_by_role["Consultant"] == 2
        assert churn_by_role.get("Operations", 0) == 0

    def test_calculate_promotion_metrics(self):
        """Test promotion metrics calculation from events"""
        calculator = KPICalculatorV2()
        
        events = [
            PersonEvent(date=date(2025, 6, 1), event_type=EventType.PROMOTED,
                       details={"from_level": "A", "to_level": "AC", "role": "Consultant"}, simulation_month=5),
            PersonEvent(date=date(2025, 6, 5), event_type=EventType.PROMOTED,
                       details={"from_level": "AC", "to_level": "C", "role": "Consultant"}, simulation_month=5),
            PersonEvent(date=date(2025, 6, 10), event_type=EventType.HIRED,
                       details={"role": "Operations", "level": "Junior"}, simulation_month=5)
        ]
        
        total_promotions, promotion_by_level = calculator._calculate_promotion_metrics(events)
        
        assert total_promotions == 2
        assert promotion_by_level["AC"] == 1  # Promoted to AC
        assert promotion_by_level["C"] == 1   # Promoted to C

    def test_calculate_tenure_metrics(self, test_person_factory):
        """Test tenure metrics calculation"""
        calculator = KPICalculatorV2()
        
        # Create persons with different hire dates
        current_date = date(2025, 6, 15)
        persons = [
            test_person_factory(hire_date="2024-01"),  # ~17 months tenure
            test_person_factory(hire_date="2024-10"),  # ~8 months tenure
            test_person_factory(hire_date="2025-03"),  # ~3 months tenure
        ]
        
        avg_tenure, tenure_dist = calculator._calculate_tenure_metrics(persons, current_date)
        
        assert avg_tenure > 0
        assert isinstance(tenure_dist, dict)
        assert "0-6" in tenure_dist
        assert "6-12" in tenure_dist
        assert "12+" in tenure_dist


class TestKPICalculatorV2FinancialMetrics:
    """Test suite for financial KPI calculations"""

    def test_calculate_financial_kpis_basic(self):
        """Test basic financial KPI calculations"""
        calculator = KPICalculatorV2()
        
        # Mock monthly results with financial data
        monthly_results = {
            "2025-06": MonthlyResults(
                year=2025, month=6,
                office_results={
                    "Stockholm": {
                        "revenue": 850000.0,
                        "costs": 650000.0,
                        "salary_costs": 450000.0,
                        "total_fte": 850
                    }
                },
                aggregate_kpis={},
                events_summary={}
            )
        }
        
        # Mock previous period for comparison
        previous_results = {
            "2025-05": MonthlyResults(
                year=2025, month=5,
                office_results={
                    "Stockholm": {
                        "revenue": 800000.0,
                        "costs": 620000.0,
                        "salary_costs": 430000.0,
                        "total_fte": 840
                    }
                },
                aggregate_kpis={},
                events_summary={}
            )
        }
        
        financial_kpis = calculator.calculate_financial_kpis(monthly_results, previous_results)
        
        assert isinstance(financial_kpis, FinancialKPIs)
        assert financial_kpis.total_revenue == 850000.0
        assert financial_kpis.total_costs == 650000.0
        assert financial_kpis.gross_profit == 200000.0  # 850k - 650k
        assert abs(financial_kpis.profit_margin - 0.235) < 0.01  # 200k/850k
        assert financial_kpis.revenue_growth_rate > 0  # Should show growth from previous month

    def test_calculate_financial_kpis_zero_revenue(self):
        """Test financial KPI calculation with zero revenue"""
        calculator = KPICalculatorV2()
        
        monthly_results = {
            "2025-06": MonthlyResults(
                year=2025, month=6,
                office_results={
                    "EmptyOffice": {
                        "revenue": 0.0,
                        "costs": 1000.0,
                        "salary_costs": 500.0,
                        "total_fte": 0
                    }
                },
                aggregate_kpis={},
                events_summary={}
            )
        }
        
        financial_kpis = calculator.calculate_financial_kpis(monthly_results, {})
        
        assert financial_kpis.total_revenue == 0.0
        assert financial_kpis.profit_margin == 0.0  # Should handle division by zero
        assert financial_kpis.revenue_per_fte == 0.0

    def test_calculate_multi_office_financial_kpis(self):
        """Test financial KPI calculation across multiple offices"""
        calculator = KPICalculatorV2()
        
        monthly_results = {
            "2025-06": MonthlyResults(
                year=2025, month=6,
                office_results={
                    "Stockholm": {
                        "revenue": 850000.0,
                        "costs": 650000.0,
                        "salary_costs": 450000.0,
                        "total_fte": 850
                    },
                    "Munich": {
                        "revenue": 450000.0,
                        "costs": 350000.0,
                        "salary_costs": 250000.0,
                        "total_fte": 450
                    }
                },
                aggregate_kpis={},
                events_summary={}
            )
        }
        
        financial_kpis = calculator.calculate_financial_kpis(monthly_results, {})
        
        # Should aggregate across offices
        assert financial_kpis.total_revenue == 1300000.0  # 850k + 450k
        assert financial_kpis.total_costs == 1000000.0    # 650k + 350k
        assert financial_kpis.gross_profit == 300000.0    # 1300k - 1000k

    def test_calculate_revenue_growth_rate(self):
        """Test revenue growth rate calculation"""
        calculator = KPICalculatorV2()
        
        current_revenue = 1000000.0
        previous_revenue = 900000.0
        
        growth_rate = calculator._calculate_growth_rate(current_revenue, previous_revenue)
        
        expected_growth = (1000000 - 900000) / 900000  # ~11.11%
        assert abs(growth_rate - expected_growth) < 0.001

    def test_calculate_operating_efficiency(self):
        """Test operating efficiency calculation"""
        calculator = KPICalculatorV2()
        
        revenue = 1000000.0
        operating_costs = 750000.0
        
        efficiency = calculator._calculate_operating_efficiency(revenue, operating_costs)
        
        expected_efficiency = revenue / operating_costs  # ~1.33
        assert abs(efficiency - expected_efficiency) < 0.01

    def test_calculate_per_fte_metrics(self):
        """Test per-FTE metrics calculation"""
        calculator = KPICalculatorV2()
        
        total_revenue = 850000.0
        total_costs = 650000.0
        total_fte = 850
        
        revenue_per_fte = calculator._calculate_revenue_per_fte(total_revenue, total_fte)
        cost_per_fte = calculator._calculate_cost_per_fte(total_costs, total_fte)
        
        assert revenue_per_fte == 1000.0  # 850k / 850
        assert cost_per_fte == 764.71    # 650k / 850 (rounded)


class TestKPICalculatorV2BusinessIntelligence:
    """Test suite for business intelligence KPI calculations"""

    def test_calculate_business_intelligence_kpis(self):
        """Test basic business intelligence KPI calculations"""
        calculator = KPICalculatorV2()
        
        # Mock data with utilization rates
        monthly_results = {
            "2025-06": MonthlyResults(
                year=2025, month=6,
                office_results={
                    "Stockholm": {
                        "utilization_by_role": {
                            "Consultant": {"A": 0.75, "AC": 0.80, "C": 0.85},
                            "Operations": {"Junior": 0.70, "Senior": 0.85}
                        },
                        "efficiency_metrics": {
                            "projects_completed": 25,
                            "avg_project_duration": 3.2,
                            "client_satisfaction": 4.2
                        }
                    }
                },
                aggregate_kpis={},
                events_summary={}
            )
        }
        
        bi_kpis = calculator.calculate_business_intelligence_kpis(monthly_results)
        
        assert isinstance(bi_kpis, BusinessIntelligenceKPIs)
        assert bi_kpis.average_utilization_rate > 0.7
        assert "Consultant" in bi_kpis.utilization_by_role
        assert "Operations" in bi_kpis.utilization_by_role

    def test_calculate_average_utilization_rate(self):
        """Test average utilization rate calculation"""
        calculator = KPICalculatorV2()
        
        utilization_data = {
            "Consultant": {"A": 0.75, "AC": 0.80, "C": 0.85},
            "Operations": {"Junior": 0.70, "Senior": 0.90}
        }
        
        avg_utilization = calculator._calculate_average_utilization(utilization_data)
        
        # Should be average of all individual utilization rates
        all_rates = [0.75, 0.80, 0.85, 0.70, 0.90]
        expected_avg = sum(all_rates) / len(all_rates)
        assert abs(avg_utilization - expected_avg) < 0.01

    def test_calculate_role_efficiency_metrics(self):
        """Test role-based efficiency metrics calculation"""
        calculator = KPICalculatorV2()
        
        role_data = {
            "Consultant": {
                "billable_hours": 1200,
                "total_hours": 1440,  # 30 days * 8 hours * 6 people
                "revenue_generated": 240000
            }
        }
        
        efficiency_metrics = calculator._calculate_role_efficiency(role_data)
        
        assert "billability_rate" in efficiency_metrics["Consultant"]
        assert "revenue_per_hour" in efficiency_metrics["Consultant"]
        
        expected_billability = 1200 / 1440  # 83.33%
        assert abs(efficiency_metrics["Consultant"]["billability_rate"] - expected_billability) < 0.01

    def test_calculate_project_metrics(self):
        """Test project-related metrics calculation"""
        calculator = KPICalculatorV2()
        
        project_data = {
            "total_projects": 15,
            "completed_projects": 12,
            "avg_duration_days": 45,
            "budget_variance": -0.05  # 5% under budget
        }
        
        project_metrics = calculator._calculate_project_metrics(project_data)
        
        assert "completion_rate" in project_metrics
        assert "average_duration" in project_metrics
        assert "budget_performance" in project_metrics
        
        expected_completion_rate = 12 / 15  # 80%
        assert abs(project_metrics["completion_rate"] - expected_completion_rate) < 0.01

    def test_calculate_client_satisfaction_metrics(self):
        """Test client satisfaction metrics calculation"""
        calculator = KPICalculatorV2()
        
        satisfaction_data = {
            "ratings": [4.5, 4.2, 4.8, 4.1, 4.6, 4.3],
            "repeat_clients": 8,
            "total_clients": 12,
            "referrals": 3
        }
        
        satisfaction_metrics = calculator._calculate_satisfaction_metrics(satisfaction_data)
        
        assert "average_rating" in satisfaction_metrics
        assert "retention_rate" in satisfaction_metrics
        assert "referral_rate" in satisfaction_metrics
        
        expected_avg_rating = statistics.mean(satisfaction_data["ratings"])
        assert abs(satisfaction_metrics["average_rating"] - expected_avg_rating) < 0.01


class TestKPICalculatorV2ComparativeAnalysis:
    """Test suite for comparative analysis functionality"""

    def test_calculate_comparative_kpis_vs_targets(self):
        """Test comparative KPI calculation against targets"""
        calculator = KPICalculatorV2()
        
        actual_kpis = {
            "total_recruitment": 25,
            "total_churn": 12,
            "revenue": 850000,
            "profit_margin": 0.24
        }
        
        targets = {
            "recruitment_target": 20,
            "churn_target": 15,
            "revenue_target": 800000,
            "profit_target": 0.20
        }
        
        comparative_kpis = calculator.calculate_comparative_kpis(actual_kpis, targets)
        
        assert isinstance(comparative_kpis, ComparativeKPIs)
        assert comparative_kpis.vs_targets["recruitment"]["variance"] > 0  # Above target
        assert comparative_kpis.vs_targets["churn"]["variance"] < 0       # Below target (good)
        assert comparative_kpis.vs_targets["revenue"]["variance"] > 0     # Above target

    def test_calculate_comparative_kpis_vs_previous_period(self):
        """Test comparative KPI calculation against previous period"""
        calculator = KPICalculatorV2()
        
        current_kpis = {
            "total_headcount": 850,
            "revenue": 1000000,
            "churn_rate": 0.08
        }
        
        previous_kpis = {
            "total_headcount": 820,
            "revenue": 950000,
            "churn_rate": 0.10
        }
        
        comparative_kpis = calculator.calculate_comparative_kpis(current_kpis, previous_period=previous_kpis)
        
        assert comparative_kpis.vs_previous["headcount"]["growth_rate"] > 0  # Growth
        assert comparative_kpis.vs_previous["revenue"]["growth_rate"] > 0    # Growth
        assert comparative_kpis.vs_previous["churn_rate"]["change"] < 0      # Improvement

    def test_calculate_variance_metrics(self):
        """Test variance calculation between actual and target"""
        calculator = KPICalculatorV2()
        
        actual = 125
        target = 100
        
        variance_pct, status = calculator._calculate_variance(actual, target)
        
        assert variance_pct == 0.25  # 25% above target
        assert status == "above_target"
        
        # Test below target
        actual = 85
        target = 100
        
        variance_pct, status = calculator._calculate_variance(actual, target)
        
        assert variance_pct == -0.15  # 15% below target
        assert status == "below_target"

    def test_calculate_trend_analysis(self):
        """Test trend analysis over multiple periods"""
        calculator = KPICalculatorV2()
        
        historical_data = [
            {"period": "2025-01", "revenue": 750000},
            {"period": "2025-02", "revenue": 780000},
            {"period": "2025-03", "revenue": 820000},
            {"period": "2025-04", "revenue": 840000},
            {"period": "2025-05", "revenue": 880000},
            {"period": "2025-06", "revenue": 900000}
        ]
        
        trend_analysis = calculator._calculate_trend_analysis(historical_data, "revenue")
        
        assert "trend_direction" in trend_analysis
        assert "growth_rate_monthly" in trend_analysis
        assert "volatility" in trend_analysis
        
        assert trend_analysis["trend_direction"] == "increasing"
        assert trend_analysis["growth_rate_monthly"] > 0


class TestKPICalculatorV2ExecutiveSummary:
    """Test suite for executive summary generation"""

    def test_generate_executive_summary(self):
        """Test executive summary generation"""
        calculator = KPICalculatorV2()
        
        # Mock comprehensive KPI data
        workforce_kpis = WorkforceKPIs(
            total_headcount=850, headcount_by_role={"Consultant": 680, "Operations": 170},
            headcount_by_level={}, headcount_by_office={"Stockholm": 850},
            total_recruitment=25, recruitment_by_role={}, recruitment_rate=0.029,
            total_churn=12, churn_by_role={}, churn_rate=0.014,
            net_recruitment=13, growth_rate=0.015,
            total_promotions=8, promotion_rate=0.009, promotion_by_level={},
            average_tenure_months=18.5, tenure_distribution={}
        )
        
        financial_kpis = FinancialKPIs(
            total_revenue=850000, revenue_growth_rate=0.06, revenue_per_fte=1000,
            total_costs=650000, cost_growth_rate=0.04, cost_per_fte=765,
            gross_profit=200000, profit_margin=0.235,
            total_salary_costs=450000, salary_per_fte=529,
            operating_efficiency=1.31, fte_productivity=1000
        )
        
        summary = calculator.generate_executive_summary(workforce_kpis, financial_kpis)
        
        assert isinstance(summary, ExecutiveSummary)
        assert summary.period is not None
        assert len(summary.key_highlights) > 0
        assert len(summary.key_concerns) >= 0
        assert len(summary.recommendations) > 0
        assert summary.overall_health_score > 0

    def test_generate_key_highlights(self):
        """Test generation of key highlights"""
        calculator = KPICalculatorV2()
        
        kpi_data = {
            "revenue_growth": 0.12,      # 12% growth - highlight
            "profit_margin": 0.28,       # 28% margin - highlight
            "churn_rate": 0.05,          # 5% churn - good
            "recruitment_rate": 0.08     # 8% recruitment - good
        }
        
        highlights = calculator._generate_key_highlights(kpi_data)
        
        assert isinstance(highlights, list)
        assert len(highlights) > 0
        assert any("revenue" in highlight.lower() for highlight in highlights)
        assert any("profit" in highlight.lower() for highlight in highlights)

    def test_generate_key_concerns(self):
        """Test generation of key concerns"""
        calculator = KPICalculatorV2()
        
        kpi_data = {
            "churn_rate": 0.18,          # 18% churn - concerning
            "profit_margin": 0.08,       # 8% margin - low
            "utilization_rate": 0.62,    # 62% utilization - low
            "revenue_growth": -0.05      # -5% growth - concerning
        }
        
        concerns = calculator._generate_key_concerns(kpi_data)
        
        assert isinstance(concerns, list)
        assert len(concerns) > 0
        assert any("churn" in concern.lower() for concern in concerns)
        assert any("revenue" in concern.lower() or "growth" in concern.lower() for concern in concerns)

    def test_generate_recommendations(self):
        """Test generation of actionable recommendations"""
        calculator = KPICalculatorV2()
        
        analysis_data = {
            "high_churn_roles": ["Consultant_A"],
            "low_utilization_offices": ["Munich"],
            "growth_opportunities": ["price_optimization", "market_expansion"],
            "efficiency_gaps": ["project_management", "resource_allocation"]
        }
        
        recommendations = calculator._generate_recommendations(analysis_data)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)

    def test_calculate_health_score(self):
        """Test overall health score calculation"""
        calculator = KPICalculatorV2()
        
        # Good performance metrics
        good_metrics = {
            "revenue_growth": 0.10,      # 10% growth
            "profit_margin": 0.25,       # 25% margin
            "churn_rate": 0.08,          # 8% churn
            "utilization_rate": 0.82,    # 82% utilization
            "employee_satisfaction": 4.2  # 4.2/5 rating
        }
        
        health_score = calculator._calculate_health_score(good_metrics)
        
        assert 0 <= health_score <= 100
        assert health_score > 70  # Should be high for good metrics
        
        # Poor performance metrics
        poor_metrics = {
            "revenue_growth": -0.05,     # -5% decline
            "profit_margin": 0.05,       # 5% margin
            "churn_rate": 0.25,          # 25% churn
            "utilization_rate": 0.58,    # 58% utilization
            "employee_satisfaction": 2.8  # 2.8/5 rating
        }
        
        poor_health_score = calculator._calculate_health_score(poor_metrics)
        
        assert poor_health_score < health_score  # Should be lower
        assert poor_health_score < 50           # Should be below average


class TestKPICalculatorV2CachingAndPerformance:
    """Test suite for caching and performance optimization"""

    def test_calculation_caching(self):
        """Test KPI calculation results are cached appropriately"""
        calculator = KPICalculatorV2()
        calculator.cache_enabled = True
        
        # Mock data
        persons = []
        events = []
        
        # First calculation
        result1 = calculator.calculate_workforce_kpis(persons, events, 6)
        cache_key = calculator._generate_cache_key("workforce_kpis", persons, events, 6)
        
        assert cache_key in calculator.calculation_cache
        assert calculator.calculation_cache[cache_key] == result1
        
        # Second calculation should use cache
        with patch.object(calculator, '_calculate_workforce_kpis_impl') as mock_calc:
            result2 = calculator.calculate_workforce_kpis(persons, events, 6)
            
            # Should not call implementation (used cache)
            mock_calc.assert_not_called()
            assert result2 == result1

    def test_cache_invalidation(self):
        """Test cache invalidation when data changes"""
        calculator = KPICalculatorV2()
        calculator.cache_enabled = True
        
        # Initial calculation
        persons1 = []
        events1 = []
        result1 = calculator.calculate_workforce_kpis(persons1, events1, 6)
        
        # Different data should not use cache
        persons2 = [Mock()]  # Different persons
        with patch.object(calculator, '_calculate_workforce_kpis_impl') as mock_calc:
            mock_calc.return_value = Mock()
            result2 = calculator.calculate_workforce_kpis(persons2, events1, 6)
            
            # Should call implementation (cache miss)
            mock_calc.assert_called_once()

    def test_cache_size_limits(self):
        """Test cache respects size limits"""
        calculator = KPICalculatorV2()
        calculator.cache_enabled = True
        calculator.max_cache_size = 2  # Small limit for testing
        
        # Fill cache beyond limit
        for i in range(5):
            persons = [Mock(id=f"person-{i}")]  # Different data for each
            calculator.calculate_workforce_kpis(persons, [], i)
        
        # Cache should not exceed limit
        assert len(calculator.calculation_cache) <= calculator.max_cache_size

    def test_performance_optimization_large_dataset(self, large_workforce_entries):
        """Test performance optimization with large datasets"""
        calculator = KPICalculatorV2()
        
        # Create large dataset
        persons = [calculator._convert_entry_to_person(entry) for entry in large_workforce_entries[:1000]]
        events = []
        
        # Time the calculation
        import time
        start_time = time.time()
        
        result = calculator.calculate_workforce_kpis(persons, events, 6)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete in reasonable time (adjust threshold as needed)
        assert execution_time < 5.0  # 5 seconds max
        assert result.total_headcount == 1000


class TestKPICalculatorV2UtilityMethods:
    """Test suite for utility methods"""

    def test_generate_cache_key(self):
        """Test cache key generation"""
        calculator = KPICalculatorV2()
        
        key1 = calculator._generate_cache_key("test_method", "param1", "param2")
        key2 = calculator._generate_cache_key("test_method", "param1", "param2")
        key3 = calculator._generate_cache_key("test_method", "param1", "param3")
        
        # Same parameters should generate same key
        assert key1 == key2
        
        # Different parameters should generate different keys
        assert key1 != key3

    def test_format_percentage(self):
        """Test percentage formatting utility"""
        calculator = KPICalculatorV2()
        
        assert calculator._format_percentage(0.1234) == "12.34%"
        assert calculator._format_percentage(0.05) == "5.00%"
        assert calculator._format_percentage(1.5) == "150.00%"

    def test_format_currency(self):
        """Test currency formatting utility"""
        calculator = KPICalculatorV2()
        
        assert calculator._format_currency(1234.56) == "$1,234.56"
        assert calculator._format_currency(1000000) == "$1,000,000.00"
        assert calculator._format_currency(0) == "$0.00"

    def test_round_to_precision(self):
        """Test value rounding to specified precision"""
        calculator = KPICalculatorV2()
        calculator.precision_decimals = 3
        
        assert calculator._round_to_precision(1.23456789) == 1.235
        assert calculator._round_to_precision(1.0) == 1.0
        assert calculator._round_to_precision(0.999999) == 1.0

    def test_data_validation(self):
        """Test input data validation"""
        calculator = KPICalculatorV2()
        
        # Valid data
        valid_persons = [Mock(id="p1", role="Consultant")]
        valid_events = [Mock(event_type=EventType.HIRED)]
        
        is_valid = calculator._validate_input_data(valid_persons, valid_events)
        assert is_valid is True
        
        # Invalid data
        with pytest.raises(ValueError):
            calculator._validate_input_data(None, valid_events)
        
        with pytest.raises(ValueError):
            calculator._validate_input_data(valid_persons, None)