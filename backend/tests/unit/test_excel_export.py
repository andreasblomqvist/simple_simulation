import pytest
import pandas as pd
import os
from backend.src.services.excel_export_service import ExcelExportService
from backend.src.services.kpi_service import AllKPIs, FinancialKPIs, GrowthKPIs, JourneyKPIs, YearlyKPIs
from dataclasses import asdict
from backend.src.services.simulation.models import Month

@pytest.fixture
def sample_kpis():
    """Create sample KPIs for testing"""
    financial = FinancialKPIs(
        net_sales=1000000.0,
        net_sales_baseline=900000.0,
        ebitda=200000.0,
        ebitda_baseline=180000.0,
        margin=20.0,
        margin_baseline=18.0,
        total_consultants=100,
        total_consultants_baseline=90,
        avg_hourly_rate=150.0,
        avg_hourly_rate_baseline=140.0,
        avg_utr=0.85,
        total_salary_costs=500000.0,
        total_salary_costs_baseline=500000.0
    )
    
    growth = GrowthKPIs(
        total_growth_percent=10.0,
        total_growth_absolute=10,
        current_total_fte=110,
        baseline_total_fte=100,
        non_debit_ratio=0.15,
        non_debit_ratio_baseline=0.14,
        non_debit_delta=0.01
    )
    
    journeys = JourneyKPIs(
        journey_totals={
            'Journey 1': 40,
            'Journey 2': 30,
            'Journey 3': 20,
            'Journey 4': 10
        },
        journey_percentages={
            'Journey 1': 40.0,
            'Journey 2': 30.0,
            'Journey 3': 20.0,
            'Journey 4': 10.0
        },
        journey_deltas={
            'Journey 1': 5.0,
            'Journey 2': 2.0,
            'Journey 3': -1.0,
            'Journey 4': 0.0
        },
        journey_totals_baseline={
            'Journey 1': 40,
            'Journey 2': 30,
            'Journey 3': 20,
            'Journey 4': 10
        },
        journey_percentages_baseline={
            'Journey 1': 40.0,
            'Journey 2': 30.0,
            'Journey 3': 20.0,
            'Journey 4': 10.0
        }
    )
    
    yearly_kpis = {
        '2025': YearlyKPIs(
            year='2025',
            financial=financial,
            growth=growth,
            journeys=journeys,
            year_over_year_growth=10.0,
            year_over_year_margin_change=2.0
        )
    }
    
    return AllKPIs(
        financial=financial,
        growth=growth,
        journeys=journeys,
        yearly_kpis=yearly_kpis
    )

@pytest.fixture
def sample_simulation_results():
    """Create sample simulation results for testing"""
    from backend.src.services.simulation_engine import Office, OfficeJourney, Level, Journey, RoleData, Person
    
    # Create a sample office
    office = Office.create_office("Stockholm", 110)
    
    # Create sample consultant levels
    consultant_levels = {
        'A': Level(
            name='A',
            journey=Journey.JOURNEY_1,
            # Progression fields
            progression_months=[Month.MAY, Month.NOV],
            progression_1=0.0, progression_2=0.0, progression_3=0.0, progression_4=0.0,
            progression_5=0.1, progression_6=0.0, progression_7=0.0, progression_8=0.0,
            progression_9=0.0, progression_10=0.0, progression_11=0.1, progression_12=0.0,
            # Recruitment fields
            recruitment_1=0.0, recruitment_2=0.0, recruitment_3=0.0,
            recruitment_4=0.0, recruitment_5=0.0, recruitment_6=0.0,
            recruitment_7=0.0, recruitment_8=0.0, recruitment_9=0.0,
            recruitment_10=0.0, recruitment_11=0.0, recruitment_12=0.0,
            # Churn fields
            churn_1=0.0, churn_2=0.0, churn_3=0.0,
            churn_4=0.0, churn_5=0.0, churn_6=0.0,
            churn_7=0.0, churn_8=0.0, churn_9=0.0,
            churn_10=0.0, churn_11=0.0, churn_12=0.0,
            # Price fields
            price_1=0.0, price_2=0.0, price_3=0.0,
            price_4=0.0, price_5=0.0, price_6=0.0,
            price_7=0.0, price_8=0.0, price_9=0.0,
            price_10=0.0, price_11=0.0, price_12=0.0,
            # Salary fields
            salary_1=0.0, salary_2=0.0, salary_3=0.0,
            salary_4=0.0, salary_5=0.0, salary_6=0.0,
            salary_7=0.0, salary_8=0.0, salary_9=0.0,
            salary_10=0.0, salary_11=0.0, salary_12=0.0,
            # UTR fields
            utr_1=1.0, utr_2=1.0, utr_3=1.0,
            utr_4=1.0, utr_5=1.0, utr_6=1.0,
            utr_7=1.0, utr_8=1.0, utr_9=1.0,
            utr_10=1.0, utr_11=1.0, utr_12=1.0
        )
    }
    
    # Create sample roles
    office.roles = {
        'Consultant': consultant_levels,
        'Sales': RoleData(),
        'Recruitment': RoleData(),
        'Operations': RoleData()
    }
    
    # Add some people to each role
    for _ in range(40):
        consultant_levels['A'].add_new_hire('2025-01', 'Consultant', 'Stockholm')
    for role in ['Sales', 'Recruitment', 'Operations']:
        for _ in range(10):
            office.roles[role].add_new_hire('2025-01', role, 'Stockholm')
    
    # Create sample monthly data
    month_data = {
        'recruitment': 5,
        'churn': 2,
        'progressions': 3,
        'net_change': 3
    }
    
    return {
        'years': {
            '2025': {
                'offices': {
                    'Stockholm': office
                },
                'month_1': month_data,
                'month_2': month_data,
                'month_3': month_data
            }
        }
    }

def test_excel_export_service(sample_kpis, sample_simulation_results, tmp_path):
    """Test the ExcelExportService functionality"""
    # Create service instance
    service = ExcelExportService()
    
    # Create temporary output file
    output_path = os.path.join(tmp_path, 'test_export.xlsx')
    
    # Convert sample_kpis to a dict with keys 'financial', 'growth', 'journeys' (extract from sample_kpis)
    kpis_dict = {
        'financial': asdict(sample_kpis.financial),
        'growth': asdict(sample_kpis.growth),
        'journeys': asdict(sample_kpis.journeys)
    }
    
    # Before calling export_simulation_results, convert Office objects in sample_simulation_results['years']['2025']['offices'] to dicts using asdict().
    for office_name, office_obj in sample_simulation_results['years']['2025']['offices'].items():
        if hasattr(office_obj, '__dataclass_fields__'):
            sample_simulation_results['years']['2025']['offices'][office_name] = asdict(office_obj)
    
    # Export data
    service.export_simulation_results(sample_simulation_results, kpis_dict, output_path)
    
    # Verify file exists
    assert os.path.exists(output_path)
    
    # Read Excel file and verify sheets
    with pd.ExcelFile(output_path) as excel_file:
        # Check all sheets exist
        expected_sheets = [
            'Summary',
            'Financial_KPIs',
            'Office_Details',
            'Journey_Analysis',
            'Movement_Logs',
            'Baseline_Comparison'
        ]
        assert all(sheet in excel_file.sheet_names for sheet in expected_sheets)
        
        # Check Summary sheet
        df_summary = pd.read_excel(excel_file, 'Summary')
        assert 'Metric' in df_summary.columns
        assert 'Current' in df_summary.columns
        assert 'Baseline' in df_summary.columns
        assert len(df_summary) == 9  # Number of metrics
        
        # Check Financial KPIs sheet
        df_financial = pd.read_excel(excel_file, 'Financial_KPIs')
        assert 'Year' in df_financial.columns
        assert 'Net Sales' in df_financial.columns
        assert 'EBITDA' in df_financial.columns
        assert len(df_financial) == 1  # One year of data
        
        # Check Office Details sheet
        df_offices = pd.read_excel(excel_file, 'Office_Details')
        assert 'Year' in df_offices.columns
        assert 'Office' in df_offices.columns
        assert 'Journey Stage' in df_offices.columns
        assert len(df_offices) == 1  # One office
        
        # Check Journey Analysis sheet
        df_journeys = pd.read_excel(excel_file, 'Journey_Analysis')
        assert 'Year' in df_journeys.columns
        assert 'Journey 1 Total' in df_journeys.columns
        assert 'Journey 1 %' in df_journeys.columns
        assert len(df_journeys) == 1  # One year of data
        
        # Check Movement Logs sheet
        df_movements = pd.read_excel(excel_file, 'Movement_Logs')
        assert 'Year' in df_movements.columns
        assert 'Month' in df_movements.columns
        assert 'Recruitment' in df_movements.columns
        assert len(df_movements) == 3  # Three months of data
        
        # Check Baseline Comparison sheet
        df_comparison = pd.read_excel(excel_file, 'Baseline_Comparison')
        assert 'Year' in df_comparison.columns
        assert 'Net Sales vs Baseline (%)' in df_comparison.columns
        assert 'EBITDA vs Baseline (%)' in df_comparison.columns
        assert len(df_comparison) == 1  # One year of data 