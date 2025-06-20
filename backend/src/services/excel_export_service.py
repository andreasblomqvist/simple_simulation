from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
from backend.src.services.kpi_service import KPIService, AllKPIs, YearlyKPIs

class ExcelExportService:
    """Service for exporting simulation results to Excel format"""
    
    def __init__(self):
        self.kpi_service = KPIService()
    
    def export_simulation_results(
        self,
        simulation_results: Dict[str, Any],
        kpis: Dict[str, Any],  # Changed from AllKPIs to Dict[str, Any]
        output_path: str
    ) -> None:
        """
        Export simulation results to Excel with multiple sheets
        
        Args:
            simulation_results: Raw simulation results dictionary
            kpis: Calculated KPIs dictionary from simulation engine
            output_path: Path where the Excel file should be saved
        """
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Generate each sheet
            self._create_summary_sheet(kpis, writer)
            self._create_financial_kpis_sheet(kpis, simulation_results, writer)
            self._create_office_details_sheet(simulation_results, writer)
            self._create_journey_analysis_sheet(kpis, simulation_results, writer)
            self._create_movement_logs_sheet(simulation_results, writer)
            self._create_baseline_comparison_sheet(kpis, simulation_results, writer)
    
    def _safe_to_excel(self, df, writer, sheet_name):
        if df.empty:
            pd.DataFrame({'Info': ['No data available']}).to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    def _create_summary_sheet(self, kpis: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create Summary sheet with high-level KPIs"""
        summary_data = {
            'Metric': [
                'Total FTE',
                'Total Growth (%)',
                'Total Growth (Absolute)',
                'EBITDA',
                'EBITDA Margin (%)',
                'Net Sales',
                'Average Hourly Rate',
                'Average UTR',
                'Non-Debit Ratio'
            ],
            'Current': [
                kpis['growth']['current_total_fte'],
                kpis['growth']['total_growth_percent'],
                kpis['growth']['total_growth_absolute'],
                kpis['financial']['current_ebitda'],
                kpis['financial']['current_margin'],
                kpis['financial']['current_net_sales'],
                kpis['financial']['avg_hourly_rate'],
                kpis['financial']['avg_utr'],
                kpis['growth']['non_debit_ratio']
            ],
            'Baseline': [
                kpis['growth']['baseline_total_fte'],
                None,  # No baseline for growth percentage
                None,  # No baseline for absolute growth
                kpis['financial']['baseline_ebitda'],
                kpis['financial']['baseline_margin'],
                kpis['financial']['baseline_net_sales'],
                kpis['financial']['avg_hourly_rate_baseline'],
                None,  # No baseline for UTR
                kpis['growth']['non_debit_ratio_baseline']
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        self._safe_to_excel(df_summary, writer, 'Summary')
    
    def _create_financial_kpis_sheet(self, kpis: Dict[str, Any], simulation_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create Financial KPIs sheet with year-by-year breakdown"""
        yearly_data = []
        
        # Extract yearly KPIs from simulation results
        for year_str, year_data in simulation_results['years'].items():
            if 'kpis' in year_data:
                year_kpis = year_data['kpis']
                yearly_data.append({
                    'Year': year_str,
                    'Net Sales': year_kpis['financial']['net_sales'],
                    'EBITDA': year_kpis['financial']['ebitda'],
                    'EBITDA Margin (%)': year_kpis['financial']['margin'],
                    'Total Consultants': year_kpis['financial']['total_consultants'],
                    'Average Hourly Rate': year_kpis['financial']['avg_hourly_rate'],
                    'Average UTR': year_kpis['financial']['avg_utr'],
                    'YoY Growth (%)': year_kpis['year_over_year']['growth_percent'],
                    'YoY Margin Change': year_kpis['year_over_year']['margin_change']
                })
        
        df_financial = pd.DataFrame(yearly_data)
        self._safe_to_excel(df_financial, writer, 'Financial_KPIs')
    
    def _sum_total_recursive(self, obj):
        if isinstance(obj, dict):
            total = 0
            for v in obj.values():
                total += self._sum_total_recursive(v)
            if 'total' in obj and isinstance(obj['total'], (int, float)):
                total += obj['total']
            return total
        elif isinstance(obj, list):
            return sum(self._sum_total_recursive(item) for item in obj)
        else:
            return 0

    def _get_role_total(self, office, role_name):
        levels = office.get('levels', {}).get(role_name, None)
        return self._sum_total_recursive(levels)

    def _get_role_total_from_results(self, office_data, role_name):
        """Get total FTE for a role from the simulation results structure"""
        if 'levels' not in office_data or role_name not in office_data['levels']:
            return 0
        
        role_data = office_data['levels'][role_name]
        
        if isinstance(role_data, dict):
            # Roles with levels (Consultant, Sales, Recruitment)
            total = 0
            for level_name, level_list in role_data.items():
                if level_list and len(level_list) > 0:
                    # Get the latest month's data
                    latest_data = level_list[-1]
                    total += latest_data.get('total', 0)
            return total
        elif isinstance(role_data, list):
            # Flat roles (Operations)
            if role_data and len(role_data) > 0:
                # Get the latest month's data
                latest_data = role_data[-1]
                return latest_data.get('total', 0)
        return 0
    
    def _calculate_journey_stage(self, total_fte):
        """Calculate journey stage based on total FTE"""
        if total_fte >= 500:
            return "Mature Office"
        elif total_fte >= 200:
            return "Established Office"
        elif total_fte >= 25:
            return "Emerging Office"
        else:
            return "New Office"

    def _create_office_details_sheet(self, simulation_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create Office Details sheet with office-specific metrics"""
        office_data = []
        
        for year, year_data in simulation_results['years'].items():
            for office_name, office in year_data['offices'].items():
                # Calculate total FTE across all roles
                total_fte = (
                    self._get_role_total_from_results(office, 'Consultant') +
                    self._get_role_total_from_results(office, 'Sales') +
                    self._get_role_total_from_results(office, 'Recruitment') +
                    self._get_role_total_from_results(office, 'Operations')
                )
                
                # Calculate journey stage based on total FTE
                journey_stage = self._calculate_journey_stage(total_fte)
                
                office_data.append({
                    'Year': year,
                    'Office': office_name,
                    'Journey Stage': journey_stage,
                    'Total FTE': total_fte,
                    'Consultants': self._get_role_total_from_results(office, 'Consultant'),
                    'Sales': self._get_role_total_from_results(office, 'Sales'),
                    'Recruitment': self._get_role_total_from_results(office, 'Recruitment'),
                    'Operations': self._get_role_total_from_results(office, 'Operations')
                })
        
        df_offices = pd.DataFrame(office_data)
        self._safe_to_excel(df_offices, writer, 'Office_Details')
    
    def _create_journey_analysis_sheet(self, kpis: Dict[str, Any], simulation_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create Journey Analysis sheet with journey distribution metrics"""
        journey_data = []
        
        # Extract journey data from simulation results
        for year_str, year_data in simulation_results['years'].items():
            if 'kpis' in year_data:
                year_kpis = year_data['kpis']
                journey_totals = year_kpis['journeys']['journey_totals']
                journey_percentages = year_kpis['journeys']['journey_percentages']
                
                journey_data.append({
                    'Year': year_str,
                    'Journey 1 Total': journey_totals.get('Journey 1', 0),
                    'Journey 1 %': journey_percentages.get('Journey 1', 0),
                    'Journey 2 Total': journey_totals.get('Journey 2', 0),
                    'Journey 2 %': journey_percentages.get('Journey 2', 0),
                    'Journey 3 Total': journey_totals.get('Journey 3', 0),
                    'Journey 3 %': journey_percentages.get('Journey 3', 0),
                    'Journey 4 Total': journey_totals.get('Journey 4', 0),
                    'Journey 4 %': journey_percentages.get('Journey 4', 0)
                })
        
        df_journeys = pd.DataFrame(journey_data)
        df_journeys.to_excel(writer, sheet_name='Journey_Analysis', index=False)
    
    def _create_movement_logs_sheet(self, simulation_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create Movement Logs sheet with recruitment, churn, and progression data"""
        movement_data = []
        
        for year, year_data in simulation_results['years'].items():
            for month in range(1, 13):
                if f'month_{month}' in year_data:
                    month_data = year_data[f'month_{month}']
                    movement_data.append({
                        'Year': year,
                        'Month': month,
                        'Recruitment': month_data.get('recruitment', 0),
                        'Churn': month_data.get('churn', 0),
                        'Progressions': month_data.get('progressions', 0),
                        'Net Change': month_data.get('net_change', 0)
                    })
        
        df_movements = pd.DataFrame(movement_data)
        self._safe_to_excel(df_movements, writer, 'Movement_Logs')
    
    def _create_baseline_comparison_sheet(self, kpis: Dict[str, Any], simulation_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create Baseline Comparison sheet comparing simulation results with baseline"""
        comparison_data = []
        
        # Extract yearly KPIs from simulation results
        for year_str, year_data in simulation_results['years'].items():
            if 'kpis' in year_data:
                year_kpis = year_data['kpis']
                
                # Calculate baseline comparisons
                net_sales_vs_baseline = (
                    (year_kpis['financial']['net_sales'] / kpis['financial']['baseline_net_sales'] - 1) * 100 
                    if kpis['financial']['baseline_net_sales'] else None
                )
                ebitda_vs_baseline = (
                    (year_kpis['financial']['ebitda'] / kpis['financial']['baseline_ebitda'] - 1) * 100 
                    if kpis['financial']['baseline_ebitda'] else None
                )
                margin_vs_baseline = year_kpis['financial']['margin'] - kpis['financial']['baseline_margin']
                headcount_vs_baseline = (
                    (year_kpis['growth']['current_total_fte'] / kpis['growth']['baseline_total_fte'] - 1) * 100 
                    if kpis['growth']['baseline_total_fte'] else None
                )
                non_debit_vs_baseline = year_kpis['growth']['non_debit_ratio'] - kpis['growth']['non_debit_ratio_baseline']
                
                comparison_data.append({
                    'Year': year_str,
                    'Net Sales vs Baseline (%)': net_sales_vs_baseline,
                    'EBITDA vs Baseline (%)': ebitda_vs_baseline,
                    'Margin vs Baseline (pp)': margin_vs_baseline,
                    'Headcount vs Baseline (%)': headcount_vs_baseline,
                    'Non-Debit Ratio vs Baseline (pp)': non_debit_vs_baseline
                })
        
        df_comparison = pd.DataFrame(comparison_data)
        df_comparison.to_excel(writer, sheet_name='Baseline_Comparison', index=False) 