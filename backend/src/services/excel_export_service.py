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
            self._create_summary_sheet(kpis, simulation_results, writer)
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

    def _create_summary_sheet(self, kpis: Dict[str, Any], simulation_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create Summary sheet with key metrics"""
        # Get first year KPIs for summary
        first_year_kpis = None
        if 'yearly_kpis' in kpis:
            first_year = list(kpis['yearly_kpis'].keys())[0]
            first_year_kpis = kpis['yearly_kpis'][first_year]
        
        if not first_year_kpis:
            return
        
        # Create summary data with correct field access
        summary_data = {
            'Metric': [
                'Total Consultants',
                'Growth (%)',
                'Growth (Absolute)',
                'EBITDA',
                'EBITDA Margin (%)',
                'Net Sales',
                'Average Hourly Rate',
                'Average UTR',
                'Non-Debit Ratio (%)'
            ],
            'Current': [
                first_year_kpis.get('total_consultants', 0),
                0,  # Growth percent - not available in this format
                0,  # Growth absolute - not available in this format  
                first_year_kpis['ebitda'],
                first_year_kpis['margin'] * 100,
                first_year_kpis['net_sales'],
                first_year_kpis['avg_hourly_rate'],
                0,  # Average UTR - not available in this format
                0   # Non-Debit Ratio - not available in this format
            ]
        }
        
        # Create DataFrame and write to Excel
        df = pd.DataFrame(summary_data)
        df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Summary']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _create_financial_kpis_sheet(self, kpis: Dict[str, Any], simulation_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create Financial KPIs sheet with detailed financial metrics"""
        yearly_data = []
        
        # Extract yearly KPIs from the top-level KPIs structure
        if 'yearly_kpis' in kpis:
            for year_str, year_kpis in kpis['yearly_kpis'].items():
                yearly_data.append({
                    'Year': year_str,
                    'Net Sales': year_kpis['net_sales'],
                    'Net Sales Baseline': year_kpis.get('net_sales_baseline', 'N/A'),
                    'EBITDA': year_kpis['ebitda'],
                    'EBITDA Baseline': year_kpis.get('ebitda_baseline', 'N/A'),
                    'EBITDA Margin (%)': year_kpis['margin'] * 100,
                    'EBITDA Margin Baseline (%)': year_kpis.get('margin_baseline', 0) * 100,
                    'Total Consultants': year_kpis.get('total_consultants', 0),
                    'Total Consultants Baseline': year_kpis.get('total_consultants_baseline', 'N/A'),
                    'Average Hourly Rate': year_kpis['avg_hourly_rate'],
                    'Average Hourly Rate Baseline': year_kpis.get('avg_hourly_rate_baseline', 'N/A'),
                    'Average UTR': year_kpis['avg_utr'],
                    'Total Salary Costs': year_kpis.get('total_salary_costs', 'N/A'),
                    'Total Salary Costs Baseline': year_kpis.get('total_salary_costs_baseline', 'N/A')
                })
        
        if not yearly_data:
            return
        
        # Create DataFrame and write to Excel
        df = pd.DataFrame(yearly_data)
        df.to_excel(writer, sheet_name='Financial_KPIs', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Financial_KPIs']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
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
        """Create Journey Analysis sheet with journey breakdowns"""
        journey_data = []
        
        # Extract yearly KPIs from the top-level KPIs structure
        if 'yearly_kpis' in kpis:
            for year_str, year_kpis in kpis['yearly_kpis'].items():
                # Journey data is not available in the current flat structure
                # Create a simple placeholder with available data
                journey_data.append({
                    'Year': year_str,
                    'Total Consultants': year_kpis.get('total_consultants', 0),
                    'Total Consultants Baseline': year_kpis.get('total_consultants_baseline', 'N/A'),
                    'Growth (%)': year_kpis.get('total_growth_percent', 0),
                    'Growth (Absolute)': year_kpis.get('total_growth_absolute', 0),
                    'Note': 'Detailed journey breakdown not available in current data structure'
                })
        
        if not journey_data:
            return
        
        # Create DataFrame and write to Excel
        df = pd.DataFrame(journey_data)
        df.to_excel(writer, sheet_name='Journey_Analysis', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Journey_Analysis']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _create_movement_logs_sheet(self, simulation_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create Movement Logs sheet with available growth data"""
        movement_data = []
        
        # Since detailed monthly movement data isn't available in the current structure,
        # we'll create a summary based on available data
        for year, year_data in simulation_results['years'].items():
            if 'summary' in year_data:
                summary = year_data['summary']
                
                # Create a summary row for the year
                movement_data.append({
                    'Year': year,
                    'Period': 'Year Summary',
                    'Total FTE': summary.get('total_fte', 0),
                    'Total Revenue': summary.get('total_revenue', 0),
                    'Total Costs': summary.get('total_costs', 0),
                    'Total Profit': summary.get('total_profit', 0),
                    'Average Margin': round(summary.get('average_margin', 0) * 100, 2),
                    'Growth Rate': round(summary.get('growth_rate', 0) * 100, 2),
                    'Note': 'Detailed monthly movement data not available in current simulation structure'
                })
                
                # Add monthly entries showing the months simulated
                months = year_data.get('months', [])
                for i, month in enumerate(months):
                    movement_data.append({
                        'Year': year,
                        'Period': f'Month {i+1} ({month})',
                        'Total FTE': None,
                        'Total Revenue': None,
                        'Total Costs': None,
                        'Total Profit': None,
                        'Average Margin': None,
                        'Growth Rate': None,
                        'Note': 'Month processed in simulation'
                    })
        
        df_movements = pd.DataFrame(movement_data)
        self._safe_to_excel(df_movements, writer, 'Movement_Logs')
    
    def _create_baseline_comparison_sheet(self, kpis: Dict[str, Any], simulation_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create Baseline Comparison sheet comparing simulation results with baseline"""
        comparison_data = []
        
        # Extract yearly KPIs from the top-level KPIs structure
        if 'yearly_kpis' in kpis:
            for year_str, year_kpis in kpis['yearly_kpis'].items():
                # Get baseline values safely with defaults
                net_sales_baseline = year_kpis.get('net_sales_baseline', None)
                ebitda_baseline = year_kpis.get('ebitda_baseline', None)
                margin_baseline = year_kpis.get('margin_baseline', None)
                baseline_total_fte = year_kpis.get('total_consultants_baseline', None)
                non_debit_ratio_baseline = year_kpis.get('non_debit_ratio_baseline', None)
                
                # Calculate baseline comparisons using the available data
                net_sales_vs_baseline = (
                    (year_kpis['net_sales'] / net_sales_baseline - 1) * 100 
                    if net_sales_baseline else None
                )
                ebitda_vs_baseline = (
                    (year_kpis['ebitda'] / ebitda_baseline - 1) * 100 
                    if ebitda_baseline else None
                )
                margin_vs_baseline = (
                    (year_kpis['margin'] - margin_baseline) * 100 
                    if margin_baseline else None
                )
                fte_vs_baseline = (
                    (year_kpis['total_consultants'] / baseline_total_fte - 1) * 100 
                    if baseline_total_fte else None
                )
                non_debit_vs_baseline = (
                    (year_kpis['non_debit_ratio'] - non_debit_ratio_baseline) * 100 
                    if non_debit_ratio_baseline else None
                )
                
                comparison_data.append({
                    'Year': year_str,
                    'Net Sales Current': year_kpis['net_sales'],
                    'Net Sales Baseline': net_sales_baseline or 'N/A',
                    'Net Sales vs Baseline (%)': round(net_sales_vs_baseline, 2) if net_sales_vs_baseline else 'N/A',
                    'EBITDA Current': year_kpis['ebitda'],
                    'EBITDA Baseline': ebitda_baseline or 'N/A',
                    'EBITDA vs Baseline (%)': round(ebitda_vs_baseline, 2) if ebitda_vs_baseline else 'N/A',
                    'Margin Current (%)': round(year_kpis['margin'] * 100, 2),
                    'Margin Baseline (%)': round(margin_baseline * 100, 2) if margin_baseline else 'N/A',
                    'Margin vs Baseline (pp)': round(margin_vs_baseline, 2) if margin_vs_baseline else 'N/A',
                    'Total Consultants Current': year_kpis['total_consultants'],
                    'Total Consultants Baseline': baseline_total_fte or 'N/A',
                    'Total Consultants vs Baseline (%)': round(fte_vs_baseline, 2) if fte_vs_baseline else 'N/A',
                    'Non-Debit Ratio Current (%)': round(year_kpis['non_debit_ratio'] * 100, 2),
                    'Non-Debit Ratio Baseline (%)': round(non_debit_ratio_baseline * 100, 2) if non_debit_ratio_baseline else 'N/A',
                    'Non-Debit Ratio vs Baseline (pp)': round(non_debit_vs_baseline, 2) if non_debit_vs_baseline else 'N/A'
                })
        
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            df.to_excel(writer, sheet_name='Baseline_Comparison', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Baseline_Comparison']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width 