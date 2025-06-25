"""
Utility functions for the simulation engine.

This module contains helper functions that support the simulation:
- Configuration validation
- Checksum calculation
- Monthly attribute helpers
"""

from typing import Dict, Any
from datetime import datetime
import json
import hashlib
from copy import deepcopy

from .models import Office, Month


def calculate_configuration_checksum(offices: Dict[str, Office]) -> str:
    """
    Calculates a checksum for the initial office configuration to detect changes.
    This helps in deciding whether to re-run a baseline simulation.
    """
    # Create a deep copy to avoid modifying the original data
    offices_copy = deepcopy(offices)

    # Convert the configuration to a JSON string for hashing
    # Using a custom serializer to handle dataclasses
    def json_default(o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        if isinstance(o, (datetime,)):
            return o.isoformat()
        if isinstance(o, type) and hasattr(o, '__name__') and o.__name__ in ['Month', 'HalfYear', 'Journey', 'OfficeJourney']:
            return o.__name__
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    config_string = json.dumps(
        {name: office for name, office in offices_copy.items()}, 
        sort_keys=True, 
        default=json_default
    )

    return hashlib.md5(config_string.encode('utf-8')).hexdigest()


def validate_configuration_completeness(offices: Dict[str, Office]) -> Dict[str, Any]:
    """
    Validates that the configuration for all offices, roles, and levels is complete.
    Checks for missing rates, salaries, prices, etc. for all 12 months.
    """
    issues = {}
    
    for office_name, office in offices.items():
        office_issues = {}
        for role_name, role_data in office.roles.items():
            role_issues = {}
            if isinstance(role_data, dict): # Leveled roles
                for level_name, level in role_data.items():
                    level_issues = []
                    for i in range(1, 13):
                        for key in ['progression', 'recruitment', 'churn', 'price', 'salary', 'utr']:
                            if not hasattr(level, f'{key}_{i}'):
                                level_issues.append(f"Missing '{key}' for month {i}")
                    if level_issues:
                        role_issues[level_name] = level_issues
            else: # Flat roles
                flat_role_issues = []
                for i in range(1, 13):
                    for key in ['recruitment', 'churn']:
                        if not hasattr(role_data, f'{key}_{i}'):
                            flat_role_issues.append(f"Missing '{key}' for month {i}")
                if flat_role_issues:
                    role_issues['base'] = flat_role_issues
            
            if role_issues:
                office_issues[role_name] = role_issues
        
        if office_issues:
            issues[office_name] = office_issues
            
    return {
        'is_complete': not issues,
        'issues': issues
    }


def get_monthly_attribute(obj, attribute_base: str, month: Month) -> float:
    """Gets a monthly attribute from an object (e.g., price_1, churn_5)"""
    return getattr(obj, f"{attribute_base}_{month.value}", 0.0)


def set_monthly_attribute(obj, attribute_base: str, month: Month, value: float) -> None:
    """Sets a monthly attribute on an object"""
    setattr(obj, f"{attribute_base}_{month.value}", value)


def get_next_level_name(current_level: str, level_order: list) -> str:
    """Get the name of the next level in the progression path"""
    try:
        current_index = level_order.index(current_level)
        if current_index + 1 < len(level_order):
            return level_order[current_index + 1]
        return None
    except ValueError:
        return None


def determine_level_order(config_data: list) -> list:
    """Dynamically determine the level order from configuration."""
    levels = set()
    for office_config in config_data:
        for role_name, role_data in office_config.get('roles', {}).items():
            if role_name != 'Operations':
                levels.update(role_data.keys())
    
    # Use a standard, sorted progression path
    standard_order = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
    
    # Filter and sort found levels according to the standard order
    sorted_levels = [level for level in standard_order if level in levels]
    
    return sorted_levels


def get_journey_for_level(level_name: str) -> str:
    """Get the Journey enum for a given level name."""
    # Simple journey mapping without default config
    if level_name in ['A', 'AC', 'C']:
        return "Journey 1"
    elif level_name in ['SrC', 'AM']:
        return "Journey 2"
    elif level_name in ['M', 'SrM']:
        return "Journey 3"
    elif level_name == 'PiP':
        return "Journey 4"
    else:
        return "Journey 1"

def log_yearly_results(logger, year, yearly_snapshots, monthly_office_metrics, economic_params):
    logger.info("=" * 80)
    logger.info(f"Year: {year}")
    logger.info("=" * 80)
    logger.info("")
    year_str = str(year)
    if year_str not in yearly_snapshots:
        logger.info("No data available for this year")
        return
    year_data = yearly_snapshots[year_str]
    for office_name, office_data in year_data.items():
        logger.info(f"Office: {office_name}")
        logger.info("-" * 50)
        office_levels = office_data.get('levels', {})
        total_office_fte = 0
        for role_name, role_data in office_levels.items():
            if isinstance(role_data, dict):
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, list) and level_data:
                        first_month = level_data[0] if level_data else {}
                        last_month = level_data[-1] if level_data else {}
                        first_fte = first_month.get('total', 0)
                        last_fte = last_month.get('total', 0)
                        fte_change = last_fte - first_fte
                        change_symbol = "+" if fte_change > 0 else ""
                        logger.info(f"  Role: {role_name}")
                        logger.info(f"    Level: {level_name:<8} FTE: {last_fte} (Δ {change_symbol}{fte_change})")
                        total_office_fte += last_fte
                        if fte_change != 0:
                            recruited = sum(month.get('recruited', 0) for month in level_data)
                            churned = sum(month.get('churned', 0) for month in level_data)
                            progressed_out = sum(month.get('progressed_out', 0) for month in level_data)
                            progressed_in = sum(month.get('progressed_in', 0) for month in level_data)
                            logger.info(f"      Recruited: {recruited}, Churned: {churned}, Promoted Out: {progressed_out}, Promoted In: {progressed_in}")
            else:
                if isinstance(role_data, list) and role_data:
                    first_month = role_data[0] if role_data else {}
                    last_month = role_data[-1] if role_data else {}
                    first_fte = first_month.get('total', 0)
                    last_fte = last_month.get('total', 0)
                    fte_change = last_fte - first_fte
                    change_symbol = "+" if fte_change > 0 else ""
                    logger.info(f"  Role: {role_name}")
                    logger.info(f"    FTE: {last_fte} (Δ {change_symbol}{fte_change})")
                    total_office_fte += last_fte
        logger.info("")
        log_office_kpis(logger, office_name, office_data, economic_params)
        logger.info("")
    log_system_kpis(logger, year_data, economic_params)

def log_office_kpis(logger, office_name, office_data, economic_params):
    logger.info(f"KPIs for {office_name}:")
    logger.info("-" * 30)
    office_fte = office_data.get('total_fte', 0)
    office_levels = office_data.get('levels', {})
    working_hours_per_month = economic_params.working_hours_per_month
    unplanned_absence = economic_params.unplanned_absence
    utilization = economic_params.utilization
    total_consultants = 0
    for role_name, role_data in office_levels.items():
        if isinstance(role_data, dict) and role_name == 'Consultant':
            for level_name, level_data in role_data.items():
                if isinstance(level_data, list) and level_data:
                    last_month = level_data[-1]
                    fte_count = last_month.get('total', 0)
                    total_consultants += fte_count
    logger.info(f"  Total Consultants: {total_consultants} FTE")
    logger.info("")
    working_hours = total_consultants * working_hours_per_month * 12
    logger.info(f"  Working Hours (before absence):")
    logger.info(f"    Formula: Consultant FTE × Working Hours/Month × Months")
    logger.info(f"    Calc:   {total_consultants} × {working_hours_per_month} × 12 = {working_hours:,.0f} hours")
    available_hours = working_hours * (1 - unplanned_absence)
    logger.info(f"  Available Working Hours (after unplanned absence):")
    logger.info(f"    Formula: Working Hours × (1 - Unplanned Absence)")
    logger.info(f"    Calc:   {working_hours:,.0f} × (1 - {unplanned_absence:.1%}) = {available_hours:,.0f} hours")
    billable_hours = available_hours * utilization
    logger.info(f"  Billable Hours:")
    logger.info(f"    Formula: Available Hours × Utilization")
    logger.info(f"    Calc:   {available_hours:,.0f} × {utilization:.1%} = {billable_hours:,.0f} hours")
    total_revenue = 0.0
    total_salary_costs = 0.0
    logger.info("  REVENUE (Consultants only):")
    for role_name, role_data in office_levels.items():
        if isinstance(role_data, dict):
            for level_name, level_data in role_data.items():
                if isinstance(level_data, list) and level_data:
                    last_month = level_data[-1]
                    fte_count = last_month.get('total', 0)
                    hourly_rate = last_month.get('price', 0)
                    salary = last_month.get('salary', 0)
                    if fte_count > 0 and role_name == 'Consultant':
                        level_billable_hours = fte_count * working_hours_per_month * (1 - unplanned_absence) * utilization * 12
                        level_revenue = level_billable_hours * hourly_rate
                        total_revenue += level_revenue
                        logger.info(f"    - {role_name} {level_name}: {fte_count} FTE × {hourly_rate} SEK/hr = {level_revenue:,.0f} SEK")
    logger.info("  SALARY COSTS (All roles):")
    for role_name, role_data in office_levels.items():
        if isinstance(role_data, dict):
            for level_name, level_data in role_data.items():
                if isinstance(level_data, list) and level_data:
                    last_month = level_data[-1]
                    fte_count = last_month.get('total', 0)
                    salary = last_month.get('salary', 0)
                    if fte_count > 0:
                        level_salary_cost = fte_count * salary * 12
                        total_salary_costs += level_salary_cost
                        logger.info(f"    - {role_name} {level_name}: {fte_count} FTE × {salary:,.0f} SEK/month = {level_salary_cost:,.0f} SEK")
        elif isinstance(role_data, list) and role_data:
            last_month = role_data[-1]
            fte_count = last_month.get('total', 0)
            salary = last_month.get('salary', 40000.0)
            if fte_count > 0:
                level_salary_cost = fte_count * salary * 12
                total_salary_costs += level_salary_cost
                logger.info(f"    - {role_name}: {fte_count} FTE × {salary:,.0f} SEK/month = {level_salary_cost:,.0f} SEK")
    logger.info(f"  Net Sales:")
    logger.info(f"    Formula: Billable Hours × Average Hourly Rate")
    avg_hourly_rate = total_revenue / billable_hours if billable_hours > 0 else 0
    logger.info(f"    Calc:   {billable_hours:,.0f} × {avg_hourly_rate:.0f} = {total_revenue:,.0f} SEK")
    logger.info(f"  Total Salary Costs:")
    logger.info(f"    Formula: Sum of (FTE × Monthly Salary × 12)")
    logger.info(f"    Calc:   {total_salary_costs:,.0f} SEK")
    employment_cost_rate = economic_params.employment_cost_rate
    total_employment_costs = total_salary_costs * (1 + employment_cost_rate)
    logger.info(f"  Total Employment Costs:")
    logger.info(f"    Formula: Total Salary Costs × (1 + Employment Cost Rate)")
    logger.info(f"    Calc:   {total_salary_costs:,.0f} × (1 + {employment_cost_rate:.1%}) = {total_employment_costs:,.0f} SEK")
    other_expense = economic_params.other_expense
    logger.info(f"  Other Expenses (allocated):")
    logger.info(f"    Formula: (Office FTE / Total System FTE) × Other Expense")
    logger.info(f"    Calc:   Allocated portion of {other_expense:,.0f} SEK")
    total_costs = total_employment_costs
    logger.info(f"  Total Costs:")
    logger.info(f"    Formula: Total Employment Costs + Other Expenses")
    logger.info(f"    Calc:   {total_employment_costs:,.0f} + allocated = {total_costs:,.0f} SEK")
    ebitda = total_revenue - total_costs
    logger.info(f"  EBITDA:")
    logger.info(f"    Formula: Net Sales - Total Costs")
    logger.info(f"    Calc:   {total_revenue:,.0f} - {total_costs:,.0f} = {ebitda:,.0f} SEK")
    margin = (ebitda / total_revenue * 100) if total_revenue > 0 else 0
    logger.info(f"  Margin:")
    logger.info(f"    Formula: (EBITDA / Net Sales) × 100")
    logger.info(f"    Calc:   ({ebitda:,.0f} / {total_revenue:,.0f}) × 100 = {margin:.1f}%")

def log_system_kpis(logger, year_data, economic_params):
    logger.info("SYSTEM-WIDE SUMMARY:")
    logger.info("-" * 50)
    total_fte = sum(office.get('total_fte', 0) for office in year_data.values())
    logger.info(f"Total System FTE: {total_fte}")
    total_revenue = 0.0
    total_costs = 0.0
    for office_name, office_data in year_data.items():
        office_fte = office_data.get('total_fte', 0)
        office_levels = office_data.get('levels', {})
        for role_name, role_data in office_levels.items():
            if isinstance(role_data, dict):
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, list) and level_data and role_name == 'Consultant':
                        last_month = level_data[-1]
                        fte_count = last_month.get('total', 0)
                        hourly_rate = last_month.get('price', 0)
                        if fte_count > 0:
                            billable_hours = fte_count * economic_params.working_hours_per_month * (1 - economic_params.unplanned_absence) * 0.85 * 12
                            office_revenue = billable_hours * hourly_rate
                            total_revenue += office_revenue
    logger.info(f"Total System Revenue: {total_revenue:,.0f} SEK")
    logger.info(f"Average Revenue per FTE: {total_revenue/total_fte if total_fte > 0 else 0:,.0f} SEK")
    logger.info("") 

def log_office_aggregates_per_year(logger, year, year_data, economic_params):
    logger.info("=" * 40)
    logger.info(f"Year: {year}")
    logger.info("-" * 40)
    header = "| Office     | FTE  | Consultants | Revenue      | Salary Cost  | Employment Cost | EBITDA      | Margin  |"
    logger.info(header)
    logger.info("|------------|------|-------------|--------------|--------------|----------------|-------------|---------|")
    for office_name, office_data in year_data.items():
        office_fte = office_data.get('total_fte', 0)
        office_levels = office_data.get('levels', {})
        consultants = 0
        revenue = 0.0
        salary_cost = 0.0
        for role_name, role_data in office_levels.items():
            if isinstance(role_data, dict) and role_name == 'Consultant':
                for level_data in role_data.values():
                    if isinstance(level_data, list) and level_data:
                        last_month = level_data[-1]
                        fte_count = last_month.get('total', 0)
                        hourly_rate = last_month.get('price', 0)
                        salary = last_month.get('salary', 0)
                        consultants += fte_count
                        billable_hours = (
                            fte_count
                            * economic_params.working_hours_per_month
                            * (1 - economic_params.unplanned_absence)
                            * economic_params.utilization
                            * 12
                        )
                        revenue += billable_hours * hourly_rate
                        salary_cost += fte_count * salary * 12
            elif isinstance(role_data, dict) or isinstance(role_data, list):
                # Add salary cost for non-consultant roles
                if isinstance(role_data, dict):
                    for level_data in role_data.values():
                        if isinstance(level_data, list) and level_data:
                            last_month = level_data[-1]
                            fte_count = last_month.get('total', 0)
                            salary = last_month.get('salary', 0)
                            salary_cost += fte_count * salary * 12
                elif isinstance(role_data, list) and role_data:
                    last_month = role_data[-1]
                    fte_count = last_month.get('total', 0)
                    salary = last_month.get('salary', 40000.0)
                    salary_cost += fte_count * salary * 12
        employment_cost = salary_cost * (1 + economic_params.employment_cost_rate)
        ebitda = revenue - employment_cost
        margin = (ebitda / revenue * 100) if revenue > 0 else 0
        logger.info(f"| {office_name:<10} | {office_fte:<4} | {consultants:<11} | {revenue:>12,.0f} | {salary_cost:>12,.0f} | {employment_cost:>14,.0f} | {ebitda:>11,.0f} | {margin:>6.1f}% |")
    logger.info("-" * 40) 