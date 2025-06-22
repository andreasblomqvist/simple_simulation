import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

class ExcelExportService:
    """Service for exporting simulation results to Excel format."""

    def export_simulation_results(
        self,
        simulation_results: Dict[str, Any],
        kpis: Dict[str, Any],
        output_path: str,
    ) -> None:
        """
        Export simulation results to an Excel file with multiple sheets.
        Safely handles missing data by skipping empty sheets and creating a fallback if no data is available.
        """
        sheets_to_write = {
            "Summary": self._create_summary_df(kpis),
            "Financial_KPIs": self._create_financial_kpis_df(kpis),
            "Baseline_Comparison": self._create_baseline_comparison_df(kpis),
            "Office_Details": self._create_office_details_df(simulation_results),
            "Monthly_Level_Details": self._create_monthly_level_details_df(simulation_results),
            "Monthly_Movement_Summary": self._create_monthly_movement_summary_df(simulation_results),
            "Level_Change_Metrics": self._create_level_change_metrics_df(simulation_results),
            "Journey_Analysis": self._create_journey_analysis_df(simulation_results),
            "Movement_Logs": self._create_movement_logs_df(simulation_results),
        }

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            sheets_created = 0
            for sheet_name, df in sheets_to_write.items():
                if df is not None and not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    self._auto_adjust_column_widths(writer, sheet_name)
                    sheets_created += 1

            if sheets_created == 0:
                fallback_df = pd.DataFrame({
                    "Info": [
                        "Simulation Export",
                        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        "No data was available to generate any of the standard export sheets.",
                    ]
                })
                fallback_df.to_excel(writer, sheet_name="Export_Info", index=False)
                self._auto_adjust_column_widths(writer, "Export_Info")

    def _create_summary_df(self, kpis: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Creates a DataFrame for the Summary sheet."""
        summary_kpis = kpis.get("summary")
        if not summary_kpis:
            return None

        data = {
            "Metric": list(summary_kpis.keys()),
            "Value": list(summary_kpis.values()),
        }
        return pd.DataFrame(data)

    def _create_financial_kpis_df(self, kpis: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Creates a DataFrame for the Financial_KPIs sheet."""
        if not kpis:
            return None

        financial_data = []
        
        # Extract main financial KPIs
        financial = kpis.get("financial", {})
        growth = kpis.get("growth", {})
        journeys = kpis.get("journeys", {})
        
        # Create comprehensive financial KPI overview
        financial_data.extend([
            {"Metric": "Net Sales (SEK)", "Current": financial.get("net_sales", 0), "Baseline": financial.get("net_sales_baseline", 0)},
            {"Metric": "EBITDA (SEK)", "Current": financial.get("ebitda", 0), "Baseline": financial.get("ebitda_baseline", 0)},
            {"Metric": "Margin (%)", "Current": financial.get("margin", 0) * 100, "Baseline": financial.get("margin_baseline", 0) * 100},
            {"Metric": "Total Consultants", "Current": financial.get("total_consultants", 0), "Baseline": financial.get("total_consultants_baseline", 0)},
            {"Metric": "Total Salary Costs (SEK)", "Current": financial.get("total_salary_costs", 0), "Baseline": financial.get("total_salary_costs_baseline", 0)},
            {"Metric": "Avg Hourly Rate (SEK)", "Current": financial.get("avg_hourly_rate", 0), "Baseline": financial.get("avg_hourly_rate_baseline", 0)},
            {"Metric": "Total Growth (%)", "Current": growth.get("total_growth_percent", 0), "Baseline": 0},
            {"Metric": "Total Growth (Absolute)", "Current": growth.get("current_total_fte", 0), "Baseline": growth.get("baseline_total_fte", 0)},
            {"Metric": "Non-Debit Ratio (%)", "Current": growth.get("non_debit_ratio", 0), "Baseline": growth.get("non_debit_ratio_baseline", 0)},
        ])
        
        # Add journey metrics
        journey_totals = journeys.get("journey_totals", {})
        journey_percentages = journeys.get("journey_percentages", {})
        journey_deltas = journeys.get("journey_deltas", {})
        
        for journey_name in ["Journey 1", "Journey 2", "Journey 3", "Journey 4"]:
            financial_data.extend([
                {"Metric": f"{journey_name} Total FTE", "Current": journey_totals.get(journey_name, 0), "Baseline": journey_deltas.get(journey_name, 0)},
                {"Metric": f"{journey_name} Percentage", "Current": journey_percentages.get(journey_name, 0), "Baseline": 0},
            ])
        
        df = pd.DataFrame(financial_data)
        
        # Calculate Difference column after DataFrame creation
        df['Difference'] = df['Current'] - df['Baseline']
        
        # Reorder columns
        df = df[["Metric", "Current", "Baseline", "Difference"]]
        
        return df

    def _create_baseline_comparison_df(self, kpis: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Creates a DataFrame for the Baseline_Comparison sheet."""
        baseline_kpis = kpis.get("baseline_comparison")
        if not baseline_kpis:
            return None

        comparison_data = []
        for metric, values in baseline_kpis.items():
            comparison_data.append({
                "Metric": metric.replace("_", " ").title(),
                "Simulation": values.get("simulation"),
                "Baseline": values.get("baseline"),
                "Difference": values.get("difference"),
                "Difference (%)": values.get("difference_percent"),
            })
        return pd.DataFrame(comparison_data)

    def _create_office_details_df(self, simulation_results: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Creates a DataFrame for the Office_Details sheet."""
        years_data = simulation_results.get("years")
        if not years_data:
            return None

        office_details = []
        for year, year_data in years_data.items():
            for office_name, office_data in year_data.get("offices", {}).items():
                # Calculate office-level metrics from the levels data
                office_revenue = 0.0
                office_salary_costs = 0.0
                office_consultants = 0
                office_total_fte = office_data.get("total_fte", 0)
                
                # Extract data from the levels structure
                office_levels = office_data.get("levels", {})
                for role_name, role_data in office_levels.items():
                    if isinstance(role_data, dict):
                        # Role with levels (Consultant, Sales, Recruitment)
                        for level_name, level_data in role_data.items():
                            if isinstance(level_data, list) and level_data:
                                # Get the last month's data (December)
                                last_month_data = level_data[-1]
                                fte_count = last_month_data.get('total', 0)
                                hourly_rate = last_month_data.get('price', 0)
                                salary = last_month_data.get('salary', 0)
                                utr = last_month_data.get('utr', 0.85)
                                
                                if fte_count > 0:
                                    # Only consultants generate revenue
                                    if role_name == 'Consultant':
                                        # Calculate revenue (same logic as KPI service)
                                        working_hours_per_month = 166.4
                                        unplanned_absence = 0.05
                                        available_hours = working_hours_per_month * (1 - unplanned_absence)
                                        billable_hours = available_hours * utr
                                        monthly_revenue_per_person = hourly_rate * billable_hours
                                        level_total_revenue = fte_count * monthly_revenue_per_person * 12  # 12 months
                                        office_revenue += level_total_revenue
                                        office_consultants += fte_count
                                    
                                    # All roles have salary costs
                                    base_salary_cost = fte_count * salary * 12  # 12 months
                                    office_salary_costs += base_salary_cost
                    
                    elif isinstance(role_data, list) and role_data:
                        # Flat role (Operations)
                        last_month_data = role_data[-1]
                        fte_count = last_month_data.get('total', 0)
                        salary = last_month_data.get('salary', 40000)  # Default operations salary
                        
                        if fte_count > 0:
                            base_salary_cost = fte_count * salary * 12  # 12 months
                            office_salary_costs += base_salary_cost
                
                # Calculate office-level financial metrics
                total_employment_cost_rate = 0.34  # 34% overhead on salaries
                office_total_employment_cost = office_salary_costs * (1 + total_employment_cost_rate)
                
                # Calculate proportional other expenses (same logic as KPI service)
                # Total other expense is 120,000 SEK/month for the entire system
                total_other_expense_per_month = 120000
                total_system_fte = year_data.get("total_fte", 1)  # Avoid division by zero
                office_other_expense = (office_total_fte / total_system_fte) * total_other_expense_per_month * 12  # 12 months
                office_total_costs = office_total_employment_cost + office_other_expense
                
                office_ebitda = office_revenue - office_total_costs
                office_margin = (office_ebitda / office_revenue * 100) if office_revenue > 0 else 0
                
                office_details.append({
                    "Year": year,
                    "Office": office_name,
                    "Total FTE": office_total_fte,
                    "Net Sales": office_revenue,
                    "EBITDA": office_ebitda,
                    "Margin (%)": office_margin,
                    "Consultants": office_consultants,
                    "Total Costs": office_total_costs,
                    "Salary Costs": office_salary_costs,
                    "Other Expenses": office_other_expense,
                })
        return pd.DataFrame(office_details)

    def _create_monthly_level_details_df(self, simulation_results: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Creates a comprehensive DataFrame with monthly details for all levels."""
        years_data = simulation_results.get("years")
        if not years_data:
            return None

        monthly_details = []
        
        for year, year_data in years_data.items():
            for office_name, office_data in year_data.get("offices", {}).items():
                office_levels = office_data.get("levels", {})
                
                for role_name, role_data in office_levels.items():
                    if isinstance(role_data, dict):
                        # Role with levels (Consultant, Sales, Recruitment)
                        for level_name, level_data in role_data.items():
                            if isinstance(level_data, list):
                                for month_data in level_data:
                                    monthly_details.append({
                                        "Year": year,
                                        "Office": office_name,
                                        "Role": role_name,
                                        "Level": level_name,
                                        "Month": month_data.get("month", ""),
                                        "Total_FTE": month_data.get("total", 0),
                                        "Recruited": month_data.get("recruited", 0),
                                        "Churned": month_data.get("churned", 0),
                                        "Promoted_Out": month_data.get("progressed_out", 0),
                                        "Price_SEK_per_hour": month_data.get("price", 0),
                                        "Salary_SEK_per_month": month_data.get("salary", 0),
                                        "UTR": month_data.get("utr", 0),
                                        "Net_Change": month_data.get("recruited", 0) - month_data.get("churned", 0) - month_data.get("progressed_out", 0),
                                    })
                    elif isinstance(role_data, list):
                        # Flat role (Operations)
                        for month_data in role_data:
                            monthly_details.append({
                                "Year": year,
                                "Office": office_name,
                                "Role": role_name,
                                "Level": "N/A",
                                "Month": month_data.get("month", ""),
                                "Total_FTE": month_data.get("total", 0),
                                "Recruited": month_data.get("recruited", 0),
                                "Churned": month_data.get("churned", 0),
                                "Promoted_Out": month_data.get("progressed_out", 0),
                                "Price_SEK_per_hour": month_data.get("price", 0),
                                "Salary_SEK_per_month": month_data.get("salary", 0),
                                "UTR": month_data.get("utr", 0),
                                "Net_Change": month_data.get("recruited", 0) - month_data.get("churned", 0) - month_data.get("progressed_out", 0),
                            })
        
        return pd.DataFrame(monthly_details) if monthly_details else None

    def _create_monthly_movement_summary_df(self, simulation_results: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Creates a summary DataFrame of monthly movements by office and role."""
        years_data = simulation_results.get("years")
        if not years_data:
            return None

        movement_summary = []
        
        for year, year_data in years_data.items():
            for office_name, office_data in year_data.get("offices", {}).items():
                office_levels = office_data.get("levels", {})
                
                # Group by month for office-level summaries
                monthly_office_data = {}
                
                for role_name, role_data in office_levels.items():
                    if isinstance(role_data, dict):
                        # Role with levels
                        for level_name, level_data in role_data.items():
                            if isinstance(level_data, list):
                                for month_data in level_data:
                                    month = month_data.get("month", "")
                                    if month not in monthly_office_data:
                                        monthly_office_data[month] = {
                                            "total_recruited": 0,
                                            "total_churned": 0,
                                            "total_promoted_out": 0,
                                            "total_fte": 0,
                                            "roles": {}
                                        }
                                    
                                    recruited = month_data.get("recruited", 0)
                                    churned = month_data.get("churned", 0)
                                    promoted_out = month_data.get("promoted_out", 0)
                                    total_fte = month_data.get("total", 0)
                                    
                                    monthly_office_data[month]["total_recruited"] += recruited
                                    monthly_office_data[month]["total_churned"] += churned
                                    monthly_office_data[month]["total_promoted_out"] += promoted_out
                                    monthly_office_data[month]["total_fte"] += total_fte
                                    
                                    # Track by role
                                    if role_name not in monthly_office_data[month]["roles"]:
                                        monthly_office_data[month]["roles"][role_name] = {
                                            "recruited": 0, "churned": 0, "promoted_out": 0, "fte": 0
                                        }
                                    
                                    monthly_office_data[month]["roles"][role_name]["recruited"] += recruited
                                    monthly_office_data[month]["roles"][role_name]["churned"] += churned
                                    monthly_office_data[month]["roles"][role_name]["promoted_out"] += promoted_out
                                    monthly_office_data[month]["roles"][role_name]["fte"] += total_fte
                    
                    elif isinstance(role_data, list):
                        # Flat role (Operations)
                        for month_data in role_data:
                            month = month_data.get("month", "")
                            if month not in monthly_office_data:
                                monthly_office_data[month] = {
                                    "total_recruited": 0,
                                    "total_churned": 0,
                                    "total_promoted_out": 0,
                                    "total_fte": 0,
                                    "roles": {}
                                }
                            
                            recruited = month_data.get("recruited", 0)
                            churned = month_data.get("churned", 0)
                            promoted_out = month_data.get("promoted_out", 0)
                            total_fte = month_data.get("total", 0)
                            
                            monthly_office_data[month]["total_recruited"] += recruited
                            monthly_office_data[month]["total_churned"] += churned
                            monthly_office_data[month]["total_promoted_out"] += promoted_out
                            monthly_office_data[month]["total_fte"] += total_fte
                            
                            # Track by role
                            if role_name not in monthly_office_data[month]["roles"]:
                                monthly_office_data[month]["roles"][role_name] = {
                                    "recruited": 0, "churned": 0, "promoted_out": 0, "fte": 0
                                }
                            
                            monthly_office_data[month]["roles"][role_name]["recruited"] += recruited
                            monthly_office_data[month]["roles"][role_name]["churned"] += churned
                            monthly_office_data[month]["roles"][role_name]["promoted_out"] += promoted_out
                            monthly_office_data[month]["roles"][role_name]["fte"] += total_fte
                
                # Convert to summary records
                for month, data in monthly_office_data.items():
                    net_change = data["total_recruited"] - data["total_churned"] - data["total_promoted_out"]
                    
                    movement_summary.append({
                        "Year": year,
                        "Office": office_name,
                        "Month": month,
                        "Total_FTE": data["total_fte"],
                        "Total_Recruited": data["total_recruited"],
                        "Total_Churned": data["total_churned"],
                        "Total_Promoted_Out": data["total_promoted_out"],
                        "Net_Change": net_change,
                        "Consultant_FTE": data["roles"].get("Consultant", {}).get("fte", 0),
                        "Consultant_Recruited": data["roles"].get("Consultant", {}).get("recruited", 0),
                        "Consultant_Churned": data["roles"].get("Consultant", {}).get("churned", 0),
                        "Sales_FTE": data["roles"].get("Sales", {}).get("fte", 0),
                        "Sales_Recruited": data["roles"].get("Sales", {}).get("recruited", 0),
                        "Sales_Churned": data["roles"].get("Sales", {}).get("churned", 0),
                        "Recruitment_FTE": data["roles"].get("Recruitment", {}).get("fte", 0),
                        "Recruitment_Recruited": data["roles"].get("Recruitment", {}).get("recruited", 0),
                        "Recruitment_Churned": data["roles"].get("Recruitment", {}).get("churned", 0),
                        "Operations_FTE": data["roles"].get("Operations", {}).get("fte", 0),
                        "Operations_Recruited": data["roles"].get("Operations", {}).get("recruited", 0),
                        "Operations_Churned": data["roles"].get("Operations", {}).get("churned", 0),
                    })
        
        return pd.DataFrame(movement_summary) if movement_summary else None

    def _create_level_change_metrics_df(self, simulation_results: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Creates a DataFrame focusing on level-by-level change metrics and progression flows."""
        years_data = simulation_results.get("years")
        if not years_data:
            return None

        level_changes = []
        
        for year, year_data in years_data.items():
            for office_name, office_data in year_data.get("offices", {}).items():
                office_levels = office_data.get("levels", {})
                
                for role_name, role_data in office_levels.items():
                    if isinstance(role_data, dict):
                        # Role with levels - track progression between levels
                        for level_name, level_data in role_data.items():
                            if isinstance(level_data, list) and len(level_data) > 1:
                                # Calculate month-over-month changes
                                for i in range(1, len(level_data)):
                                    prev_month = level_data[i-1]
                                    curr_month = level_data[i]
                                    
                                    prev_total = prev_month.get("total", 0)
                                    curr_total = curr_month.get("total", 0)
                                    recruited = curr_month.get("recruited", 0)
                                    churned = curr_month.get("churned", 0)
                                    promoted_out = curr_month.get("promoted_out", 0)
                                    
                                    # Calculate implied promotions in (reverse engineer from the numbers)
                                    expected_total = prev_total + recruited - churned - promoted_out
                                    promoted_in = curr_total - expected_total
                                    
                                    actual_change = curr_total - prev_total
                                    
                                    level_changes.append({
                                        "Year": year,
                                        "Office": office_name,
                                        "Role": role_name,
                                        "Level": level_name,
                                        "Month": curr_month.get("month", ""),
                                        "Previous_FTE": prev_total,
                                        "Current_FTE": curr_total,
                                        "Recruited": recruited,
                                        "Churned": churned,
                                        "Promoted_Out": promoted_out,
                                        "Promoted_In": max(0, promoted_in),  # Can't be negative
                                        "Expected_Change": recruited - churned - promoted_out + max(0, promoted_in),
                                        "Actual_Change": actual_change,
                                        "Variance": actual_change - (recruited - churned - promoted_out + max(0, promoted_in)),
                                        "Churn_Rate": (churned / prev_total * 100) if prev_total > 0 else 0,
                                        "Recruitment_Rate": (recruited / prev_total * 100) if prev_total > 0 else 0,
                                        "Promotion_Out_Rate": (promoted_out / prev_total * 100) if prev_total > 0 else 0,
                                    })
        
        return pd.DataFrame(level_changes) if level_changes else None

    def _create_journey_analysis_df(self, simulation_results: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Creates a DataFrame for the Journey_Analysis sheet."""
        years_data = simulation_results.get("years")
        if not years_data:
            return None

        journey_data = []
        for year, year_data in years_data.items():
            for journey_name, journey_metrics in year_data.get("journeys", {}).items():
                latest_metrics = journey_metrics[-1] if journey_metrics else {}
                journey_data.append({
                    "Year": year,
                    "Journey": journey_name,
                    "Total FTE": latest_metrics.get("total_fte", 0),
                    "Net Sales": latest_metrics.get("net_sales", 0),
                    "EBITDA": latest_metrics.get("ebitda", 0),
                    "Margin (%)": latest_metrics.get("margin", 0) * 100,
                })
        return pd.DataFrame(journey_data)

    def _create_movement_logs_df(self, simulation_results: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Creates a DataFrame for the Movement_Logs sheet."""
        logs = simulation_results.get("logs")
        if not logs:
            return None
        return pd.DataFrame(logs)

    def _auto_adjust_column_widths(self, writer: pd.ExcelWriter, sheet_name: str):
        """Auto-adjusts column widths for a given sheet."""
        worksheet = writer.sheets[sheet_name]
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max(max_length, len(str(column[0].value))) + 2, 60)
            worksheet.column_dimensions[column_letter].width = adjusted_width