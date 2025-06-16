import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.kpi_service import (
    KPIService, 
    FinancialKPIs, 
    GrowthKPIs, 
    JourneyKPIs, 
    AllKPIs
)


class TestKPIDataClasses(unittest.TestCase):
    """Test the KPI dataclasses"""
    
    def test_financial_kpis_creation(self):
        """Test FinancialKPIs dataclass creation"""
        financial_kpis = FinancialKPIs(
            net_sales=1000000.0,
            net_sales_baseline=900000.0,
            ebitda=150000.0,
            ebitda_baseline=135000.0,
            margin=15.0,
            margin_baseline=15.0,
            total_consultants=100,
            total_consultants_baseline=90,
            avg_hourly_rate=1500.0,
            avg_hourly_rate_baseline=1400.0,
            avg_utr=0.85
        )
        
        self.assertEqual(financial_kpis.net_sales, 1000000.0)
        self.assertEqual(financial_kpis.net_sales_baseline, 900000.0)
        self.assertEqual(financial_kpis.ebitda, 150000.0)
        self.assertEqual(financial_kpis.ebitda_baseline, 135000.0)
        self.assertEqual(financial_kpis.margin, 15.0)
        self.assertEqual(financial_kpis.margin_baseline, 15.0)
        self.assertEqual(financial_kpis.total_consultants, 100)
        self.assertEqual(financial_kpis.total_consultants_baseline, 90)
        self.assertEqual(financial_kpis.avg_hourly_rate, 1500.0)
        self.assertEqual(financial_kpis.avg_hourly_rate_baseline, 1400.0)
        self.assertEqual(financial_kpis.avg_utr, 0.85)
    
    def test_growth_kpis_creation(self):
        """Test GrowthKPIs dataclass creation"""
        growth_kpis = GrowthKPIs(
            total_growth_percent=10.5,
            total_growth_absolute=15,
            current_total_fte=150,
            baseline_total_fte=135,
            non_debit_ratio=25.0,
            non_debit_ratio_baseline=23.0,
            non_debit_delta=2.0
        )
        
        self.assertEqual(growth_kpis.total_growth_percent, 10.5)
        self.assertEqual(growth_kpis.total_growth_absolute, 15)
        self.assertEqual(growth_kpis.current_total_fte, 150)
        self.assertEqual(growth_kpis.baseline_total_fte, 135)
    
    def test_journey_kpis_creation(self):
        """Test JourneyKPIs dataclass creation"""
        journey_kpis = JourneyKPIs(
            journey_totals={"Journey 1": 50, "Journey 2": 40},
            journey_percentages={"Journey 1": 55.6, "Journey 2": 44.4},
            journey_deltas={"Journey 1": 2.5, "Journey 2": -2.5}
        )
        
        self.assertEqual(journey_kpis.journey_totals["Journey 1"], 50)
        self.assertEqual(journey_kpis.journey_percentages["Journey 1"], 55.6)
        self.assertEqual(journey_kpis.journey_deltas["Journey 1"], 2.5)

    def test_all_kpis_creation(self):
        """Test AllKPIs dataclass creation"""
        financial = FinancialKPIs(
            net_sales=1000000.0, net_sales_baseline=900000.0,
            ebitda=150000.0, ebitda_baseline=135000.0,
            margin=15.0, margin_baseline=15.0,
            total_consultants=100, total_consultants_baseline=90,
            avg_hourly_rate=1500.0, avg_hourly_rate_baseline=1400.0,
            avg_utr=0.85
        )
        
        growth = GrowthKPIs(
            total_growth_percent=10.5, total_growth_absolute=15,
            current_total_fte=150, baseline_total_fte=135,
            non_debit_ratio=25.0, non_debit_ratio_baseline=23.0,
            non_debit_delta=2.0
        )
        
        journeys = JourneyKPIs(
            journey_totals={"Journey 1": 50},
            journey_percentages={"Journey 1": 100.0},
            journey_deltas={"Journey 1": 0.0}
        )
        
        all_kpis = AllKPIs(financial=financial, growth=growth, journeys=journeys)
        
        self.assertIsInstance(all_kpis.financial, FinancialKPIs)
        self.assertIsInstance(all_kpis.growth, GrowthKPIs)
        self.assertIsInstance(all_kpis.journeys, JourneyKPIs)


class TestKPIService(unittest.TestCase):
    """Test the KPIService class"""
    
    def setUp(self):
        """Set up a KPIService for testing"""
        self.kpi_service = KPIService()
        
        # Mock baseline data
        self.mock_baseline_data = {
            'offices': [
                {
                    'name': 'Stockholm',
                    'roles': {
                        'Consultant': {'A': 10, 'AC': 8, 'C': 12, 'M': 5},
                        'Sales': {'A': 2, 'AC': 1, 'M': 1},
                        'Recruitment': {'A': 1, 'AC': 1},
                        'Operations': 3
                    },
                    'consultants': 35,
                                         'non_consultants': 9,
                    'total': 44
                }
            ],
            'total_consultants': 35,
            'total_non_consultants': 9,
            'total_fte': 44
        }
        
        # Mock simulation results
        self.mock_simulation_results = {
            'offices': {
                'Stockholm': {
                    'levels': {
                        'Consultant': {
                            'A': [{'total': 12, 'price': 1500.0, 'salary': 45000.0}],
                            'AC': [{'total': 10, 'price': 1600.0, 'salary': 47000.0}],
                            'C': [{'total': 15, 'price': 1700.0, 'salary': 50000.0}],
                            'M': [{'total': 8, 'price': 2000.0, 'salary': 70000.0}]
                        },
                        'Sales': {
                            'A': [{'total': 3, 'price': 0.0, 'salary': 40000.0}],
                            'AC': [{'total': 2, 'price': 0.0, 'salary': 42000.0}]
                        },
                        'Recruitment': {
                            'A': [{'total': 2, 'price': 0.0, 'salary': 38000.0}]
                        }
                    },
                    'operations': [{'total': 4, 'price': 0.0, 'salary': 45000.0}],
                    'journeys': {
                        'Journey 1': [{'total': 25}],
                        'Journey 2': [{'total': 20}],
                        'Journey 3': [{'total': 10}],
                        'Journey 4': [{'total': 5}]
                    }
                }
            }
        }
    
    def test_service_initialization(self):
        """Test that KPIService initializes correctly"""
        self.assertEqual(self.kpi_service.working_hours_per_month, 166.4)
        self.assertEqual(self.kpi_service.social_cost_rate, 0.25)
    
    @patch('services.kpi_service.ACTUAL_OFFICE_LEVEL_DATA', {
        'Stockholm': {
            'Consultant': {'A': 10, 'AC': 8, 'C': 12, 'M': 5},
            'Sales': {'A': 2, 'AC': 1, 'M': 1},
            'Recruitment': {'A': 1, 'AC': 1},
            'Operations': 3
        }
    })
    def test_get_baseline_data(self):
        """Test _get_baseline_data method"""
        
        baseline = self.kpi_service._get_baseline_data()
        
        self.assertIn('offices', baseline)
        self.assertIn('total_consultants', baseline)
        self.assertIn('total_non_consultants', baseline)
        self.assertIn('total_fte', baseline)
        
        # Check calculations
        self.assertEqual(baseline['total_consultants'], 35)  # 10+8+12+5
        self.assertEqual(baseline['total_non_consultants'], 9)  # Sales(2+1+1=4) + Recruitment(1+1=2) + Operations(3) = 9
        self.assertEqual(baseline['total_fte'], 44)  # 35+9
    
    def test_get_current_totals(self):
        """Test _get_current_totals method"""
        totals = self.kpi_service._get_current_totals(self.mock_simulation_results['offices'])
        
        expected_consultants = 12 + 10 + 15 + 8  # A+AC+C+M levels
        expected_non_consultants = 3 + 2 + 2 + 4  # Sales + Recruitment + Operations
        expected_total = expected_consultants + expected_non_consultants
        
        self.assertEqual(totals['total_consultants'], expected_consultants)
        self.assertEqual(totals['total_non_consultants'], expected_non_consultants)
        self.assertEqual(totals['total_fte'], expected_total)
    
    def test_get_current_totals_empty_data(self):
        """Test _get_current_totals with empty data"""
        totals = self.kpi_service._get_current_totals({})
        
        self.assertEqual(totals['total_consultants'], 0)
        self.assertEqual(totals['total_non_consultants'], 0)
        self.assertEqual(totals['total_fte'], 0)
    
    def test_calculate_financial_metrics(self):
        """Test _calculate_financial_metrics method"""
        metrics = self.kpi_service._calculate_financial_metrics(
            self.mock_simulation_results['offices'],
            duration_months=12,
            unplanned_absence=0.05,
            other_expense=50000.0
        )
        
        self.assertIn('net_sales', metrics)
        self.assertIn('ebitda', metrics)
        self.assertIn('margin', metrics)
        self.assertIn('total_consultants', metrics)
        self.assertIn('avg_hourly_rate', metrics)
        self.assertIn('avg_utr', metrics)
        
        # Check consultant count
        expected_consultants = 12 + 10 + 15 + 8  # A+AC+C+M levels
        self.assertEqual(metrics['total_consultants'], expected_consultants)
        
        # Check that revenue is positive (consultants generate revenue)
        self.assertGreater(metrics['net_sales'], 0)
        
        # Check that average hourly rate is calculated
        expected_avg_rate = (12*1500 + 10*1600 + 15*1700 + 8*2000) / expected_consultants
        self.assertAlmostEqual(metrics['avg_hourly_rate'], expected_avg_rate, places=2)
    
    def test_calculate_growth_kpis(self):
        """Test _calculate_growth_kpis method"""
        growth_kpis = self.kpi_service._calculate_growth_kpis(
            self.mock_simulation_results,
            self.mock_baseline_data
        )
        
        # Current total: 45 + 11 = 56 (consultants + non-consultants)
        # Baseline total: 44
        expected_growth_absolute = 56 - 44  # 12
        expected_growth_percent = (12 / 44 * 100) if 44 > 0 else 0.0
        
        self.assertIsInstance(growth_kpis, GrowthKPIs)
        self.assertEqual(growth_kpis.baseline_total_fte, 44)
        self.assertEqual(growth_kpis.current_total_fte, 56)
        self.assertEqual(growth_kpis.total_growth_absolute, 12)
        self.assertAlmostEqual(growth_kpis.total_growth_percent, expected_growth_percent, places=1)
    
    def test_calculate_journey_kpis(self):
        """Test _calculate_journey_kpis method"""
        mock_baseline_data = {'total_fte': 40}
        
        journey_kpis = self.kpi_service._calculate_journey_kpis(
            self.mock_simulation_results,
            mock_baseline_data
        )
        
        self.assertIsInstance(journey_kpis, JourneyKPIs)
        
        # Check journey totals
        expected_totals = {"Journey 1": 25, "Journey 2": 20, "Journey 3": 10, "Journey 4": 5}
        self.assertEqual(journey_kpis.journey_totals, expected_totals)
        
        # Check percentages (total = 60)
        total_journey_fte = 25 + 20 + 10 + 5
        expected_percentages = {
            "Journey 1": 25/total_journey_fte * 100,
            "Journey 2": 20/total_journey_fte * 100,
            "Journey 3": 10/total_journey_fte * 100,
            "Journey 4": 5/total_journey_fte * 100
        }
        
        for journey, expected_pct in expected_percentages.items():
            self.assertAlmostEqual(journey_kpis.journey_percentages[journey], expected_pct, places=1)
    
    def test_calculate_journey_kpis_empty_data(self):
        """Test _calculate_journey_kpis with empty data"""
        empty_results = {'offices': {}}
        journey_kpis = self.kpi_service._calculate_journey_kpis(empty_results, self.mock_baseline_data)
        
        expected_zeros = {"Journey 1": 0, "Journey 2": 0, "Journey 3": 0, "Journey 4": 0}
        self.assertEqual(journey_kpis.journey_totals, expected_zeros)
        self.assertEqual(journey_kpis.journey_percentages, expected_zeros)
    
    @patch('backend.config.default_config.BASE_PRICING')
    @patch('backend.config.default_config.BASE_SALARIES')
    def test_calculate_baseline_financial_metrics(self, mock_salaries, mock_pricing):
        """Test _calculate_baseline_financial_metrics method"""
        mock_pricing.get.return_value = {'A': 1400.0, 'AC': 1500.0, 'C': 1600.0, 'M': 1900.0}
        mock_salaries.get.return_value = {'A': 44000.0, 'AC': 46000.0, 'C': 49000.0, 'M': 68000.0, 'Operations': 40000.0}
        
        metrics = self.kpi_service._calculate_baseline_financial_metrics(
            self.mock_baseline_data,
            unplanned_absence=0.05,
            other_expense=50000.0,
            duration_months=12
        )
        
        self.assertIn('net_sales', metrics)
        self.assertIn('ebitda', metrics)
        self.assertIn('margin', metrics)
        self.assertIn('total_consultants', metrics)
        self.assertIn('avg_hourly_rate', metrics)
        self.assertIn('avg_utr', metrics)
        
        # Basic sanity checks
        self.assertGreater(metrics['net_sales'], 0)
        self.assertEqual(metrics['total_consultants'], 35)
        self.assertGreater(metrics['avg_hourly_rate'], 0)
        self.assertEqual(metrics['avg_utr'], 0.85)  # Default UTR
    
    def test_financial_calculations_edge_cases(self):
        """Test financial calculations with edge cases"""
        # Test with zero consultants (must include Consultant section with empty data)
        empty_offices = {
            'Stockholm': {
                'levels': {
                    'Consultant': {
                        'A': [{'total': 0, 'price': 0.0, 'salary': 0.0}]  # Zero consultants
                    },
                    'Sales': {'A': [{'total': 5, 'price': 0.0, 'salary': 40000.0}]},
                    'Recruitment': {'A': [{'total': 2, 'price': 0.0, 'salary': 38000.0}]}
                },
                'operations': [{'total': 3, 'price': 0.0, 'salary': 45000.0}]
            }
        }
        
        metrics = self.kpi_service._calculate_financial_metrics(
            empty_offices,
            duration_months=12,
            unplanned_absence=0.05,
            other_expense=50000.0
        )
        
        # No consultants = no revenue
        self.assertEqual(metrics['net_sales'], 0)
        self.assertEqual(metrics['total_consultants'], 0)
        self.assertEqual(metrics['avg_hourly_rate'], 0.0)
        self.assertEqual(metrics['avg_utr'], 0.0)
        
        # Should still have costs and negative EBITDA
        self.assertLess(metrics['ebitda'], 0)  # Only costs, no revenue
        self.assertEqual(metrics['margin'], 0.0)  # No revenue = 0% margin
    
    @patch.object(KPIService, '_get_baseline_data')
    @patch.object(KPIService, '_calculate_financial_kpis')
    @patch.object(KPIService, '_calculate_growth_kpis')
    @patch.object(KPIService, '_calculate_journey_kpis')
    def test_calculate_all_kpis_integration(self, mock_journey, mock_growth, mock_financial, mock_baseline):
        """Test calculate_all_kpis integration method"""
        # Mock return values
        mock_baseline.return_value = self.mock_baseline_data
        
        mock_financial_result = FinancialKPIs(
            net_sales=1000000.0, net_sales_baseline=900000.0,
            ebitda=150000.0, ebitda_baseline=135000.0,
            margin=15.0, margin_baseline=15.0,
            total_consultants=100, total_consultants_baseline=90,
            avg_hourly_rate=1500.0, avg_hourly_rate_baseline=1400.0,
            avg_utr=0.85
        )
        mock_financial.return_value = mock_financial_result
        
        mock_growth_result = GrowthKPIs(
            total_growth_percent=10.5, total_growth_absolute=15,
            current_total_fte=150, baseline_total_fte=135,
            non_debit_ratio=25.0, non_debit_ratio_baseline=23.0,
            non_debit_delta=2.0
        )
        mock_growth.return_value = mock_growth_result
        
        mock_journey_result = JourneyKPIs(
            journey_totals={"Journey 1": 50, "Journey 2": 40, "Journey 3": 30, "Journey 4": 20},
            journey_percentages={"Journey 1": 35.7, "Journey 2": 28.6, "Journey 3": 21.4, "Journey 4": 14.3},
            journey_deltas={"Journey 1": 0.0, "Journey 2": 0.0, "Journey 3": 0.0, "Journey 4": 0.0}
        )
        mock_journey.return_value = mock_journey_result
        
        # Call the method
        result = self.kpi_service.calculate_all_kpis(
            simulation_results=self.mock_simulation_results,
            simulation_duration_months=12,
            unplanned_absence=0.05,
            other_expense=50000.0
        )
        
        # Verify result structure
        self.assertIsInstance(result, AllKPIs)
        self.assertIsInstance(result.financial, FinancialKPIs)
        self.assertIsInstance(result.growth, GrowthKPIs)
        self.assertIsInstance(result.journeys, JourneyKPIs)
        
        # Verify method calls
        mock_baseline.assert_called_once()
        mock_financial.assert_called_once()
        mock_growth.assert_called_once()
        mock_journey.assert_called_once()


class TestKPIServiceRealWorldScenarios(unittest.TestCase):
    """Test KPIService with more realistic scenarios"""
    
    def setUp(self):
        self.kpi_service = KPIService()
    
    def test_multi_office_scenario(self):
        """Test KPI calculations with multiple offices"""
        multi_office_results = {
            'offices': {
                'Stockholm': {
                    'levels': {
                        'Consultant': {
                            'A': [{'total': 20, 'price': 1400.0, 'salary': 42000.0}],
                            'M': [{'total': 10, 'price': 2000.0, 'salary': 70000.0}]
                        },
                        'Sales': {'A': [{'total': 5, 'price': 0.0, 'salary': 40000.0}]}
                    },
                    'operations': [{'total': 5, 'price': 0.0, 'salary': 45000.0}],
                    'journeys': {
                        'Journey 1': [{'total': 15}],
                        'Journey 2': [{'total': 15}],
                        'Journey 3': [{'total': 8}],
                        'Journey 4': [{'total': 2}]
                    }
                },
                'Munich': {
                    'levels': {
                        'Consultant': {
                            'A': [{'total': 15, 'price': 1300.0, 'salary': 40000.0}],
                            'M': [{'total': 8, 'price': 1900.0, 'salary': 68000.0}]
                        },
                        'Sales': {'A': [{'total': 3, 'price': 0.0, 'salary': 38000.0}]}
                    },
                    'operations': [{'total': 3, 'price': 0.0, 'salary': 43000.0}],
                    'journeys': {
                        'Journey 1': [{'total': 12}],
                        'Journey 2': [{'total': 10}],
                        'Journey 3': [{'total': 6}],
                        'Journey 4': [{'total': 1}]
                    }
                }
            }
        }
        
        # Test current totals calculation
        totals = self.kpi_service._get_current_totals(multi_office_results['offices'])
        
        expected_consultants = (20 + 10) + (15 + 8)  # Stockholm + Munich consultants
        expected_non_consultants = (5 + 5) + (3 + 3)  # Sales + Operations for both offices
        
        self.assertEqual(totals['total_consultants'], expected_consultants)
        self.assertEqual(totals['total_non_consultants'], expected_non_consultants)
        self.assertEqual(totals['total_fte'], expected_consultants + expected_non_consultants)
        
        # Test financial metrics calculation
        metrics = self.kpi_service._calculate_financial_metrics(
            multi_office_results['offices'],
            duration_months=12,
            unplanned_absence=0.05,
            other_expense=100000.0
        )
        
        # Should have positive revenue from consultants
        self.assertGreater(metrics['net_sales'], 0)
        self.assertEqual(metrics['total_consultants'], expected_consultants)
        
        # Average hourly rate should be weighted average
        stockholm_weighted = (20 * 1400.0) + (10 * 2000.0)
        munich_weighted = (15 * 1300.0) + (8 * 1900.0)
        expected_avg_rate = (stockholm_weighted + munich_weighted) / expected_consultants
        
        self.assertAlmostEqual(metrics['avg_hourly_rate'], expected_avg_rate, places=2)


if __name__ == '__main__':
    unittest.main() 