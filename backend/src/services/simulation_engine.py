from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import sys
import os
import uuid
import random
import hashlib
from copy import deepcopy
import logging

# Import KPI service
from backend.src.services.kpi import KPIService, EconomicParameters
from backend.src.services.config_service import config_service
from backend.src.services.simulation.workforce import WorkforceManager
from backend.src.services.simulation.office_manager import OfficeManager
from backend.src.services.simulation.models import (
    Office, Level, RoleData, Month, Journey, OfficeJourney, Person
)
from backend.src.services.simulation.utils import log_yearly_results, log_office_aggregates_per_year, calculate_configuration_checksum, validate_configuration_completeness


class SimulationEngine:
    """
    The core simulation engine for SimpleSim.
    This class manages the simulation state and runs the monthly progression,
    recruitment, and churn calculations.
    """

    def __init__(self):
        """
        Initialize the simulation engine.
        This is now a pure function that receives all data as input parameters.
        No config service dependencies are needed.
        """
        print("✅ [ENGINE] SimulationEngine created as pure function.")
        self.offices: Dict[str, Office] = {}
        self.monthly_results: Dict[str, Any] = {}
        self.simulation_results: Optional[Dict[str, Any]] = None
        
        # Set up yearly logging
        self._setup_yearly_logging()

    def _setup_yearly_logging(self):
        """Set up logging for yearly simulation results"""
        # Create logs directory if it doesn't exist
        os.makedirs('backend/logs', exist_ok=True)
        
        # Configure yearly logging
        self.yearly_logger = logging.getLogger('simulation_yearly')
        self.yearly_logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        for handler in self.yearly_logger.handlers[:]:
            self.yearly_logger.removeHandler(handler)
        
        # Create file handler for yearly log
        yearly_handler = logging.FileHandler('backend/logs/simulation_yearly.log', mode='w')
        yearly_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(message)s')
        yearly_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.yearly_logger.addHandler(yearly_handler)
        
        # Prevent propagation to avoid duplicate logs
        self.yearly_logger.propagate = False

    def reinitialize_with_config(self):
        """Re-initialize the engine state. 
        Note: This method is maintained for backward compatibility.
        Since the engine is now a pure function, it just resets the state.
        Offices must be provided via run_simulation_with_offices or run_simulation methods.
        """
        self.reset_simulation_state()

    def reset_simulation_state(self):
        """Reset the simulation state to a clean slate."""
        self.offices = {}
        self.monthly_results = {}
        self.simulation_results = None


    
    def _determine_level_order(self, config_data: List[Dict]) -> List[str]:
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

    def _get_journey_for_level(self, level_name: str) -> Journey:
        """Get the Journey enum for a given level name."""
        # Simple journey mapping without default config
        if level_name in ['A', 'AC', 'C']:
            return Journey.JOURNEY_1
        elif level_name in ['SrC', 'AM']:
            return Journey.JOURNEY_2
        elif level_name in ['M', 'SrM']:
            return Journey.JOURNEY_3
        elif level_name == 'PiP':
            return Journey.JOURNEY_4
        else:
            return Journey.JOURNEY_1

    def _initialize_offices(self):
        """Initializes all offices with default data"""
        self.offices = {}
        for office_name, total_fte in OFFICE_HEADCOUNT.items():
            self.offices[office_name] = Office.create_office(office_name, total_fte)

    def _initialize_roles(self):
        """Initializes roles and levels for all offices"""
        for office in self.offices.values():
            office.roles = {} # Clear existing roles
            # Initialize Consultant role with levels
            office.roles['Consultant'] = {}
            for level_name, level_percentage in CONSULTANT_LEVEL_DISTRIBUTION.items():
                # Get journey for this level
                journey = self._get_journey_for_level(level_name)
                # Progression is handled by CAT-based system
                
                level = Level(
                    name=level_name,
                    journey=journey,
                    **{f'recruitment_{i}': 0.0 for i in range(1, 13)},
                    **{f'churn_{i}': 0.0 for i in range(1, 13)},
                    **{f'price_{i}': BASE_PRICING.get(office.name, {}).get(level_name, 0.0) for i in range(1, 13)},
                    **{f'salary_{i}': BASE_SALARIES.get(office.name, {}).get(level_name, 0.0) for i in range(1, 13)},
                    **{f'utr_{i}': 0.0 for i in range(1, 13)}
                )
                
                # Set initial headcount
                consultant_fte = office.total_fte * ROLE_DISTRIBUTION.get('Consultant', 0.8)
                level_fte = int(consultant_fte * level_percentage)
                # Use a date 2 years before simulation start to ensure people have sufficient tenure
                initialization_date_str = "2023-01"
                for _ in range(level_fte):
                    level.add_new_hire(initialization_date_str, "Consultant", office.name)
                    
                office.roles['Consultant'][level_name] = level
            
            # Initialize other roles (flat structure)
            for role_name in ['Sales', 'Recruitment', 'Operations']:
                role_fte = int(office.total_fte * ROLE_DISTRIBUTION.get(role_name, 0.05))
                role_data = RoleData()
                # Use a date 2 years before simulation start to ensure people have sufficient tenure
                initialization_date_str = "2023-01"
                for _ in range(role_fte):
                    role_data.add_new_hire(initialization_date_str, role_name, office.name)
                office.roles[role_name] = role_data

    def _initialize_roles_with_levers(self, lever_plan: Optional[Dict] = None):
        """Initializes roles and levels, applying any levers from the start."""
        if lever_plan is None:
            self._initialize_roles()
            return
            
        # Global levers (apply to all offices)
        global_levers = lever_plan.get('global', {})
        
        for office in self.offices.values():
            office.roles = {} # Clear existing roles
            
            # Get office-specific levers
            office_levers = lever_plan.get('offices', {}).get(office.name, {})
            
            # Initialize Consultant role with levels
            office.roles['Consultant'] = {}
            for level_name, level_percentage in CONSULTANT_LEVEL_DISTRIBUTION.items():
                journey = self._get_journey_for_level(level_name)
                
                # Combine global, office, and level-specific levers
                level_levers = office_levers.get('Consultant', {}).get(level_name, {})
                global_level_levers = global_levers.get('Consultant', {}).get(level_name, {})

                # Create level with combined levers
                level = Level(
                    name=level_name,
                    journey=journey,
                    **{f'recruitment_{i}': level_levers.get(f'recruitment_{i}', global_level_levers.get(f'recruitment_{i}', 0.0)) for i in range(1, 13)},
                    **{f'churn_{i}': level_levers.get(f'churn_{i}', global_level_levers.get(f'churn_{i}', 0.0)) for i in range(1, 13)},
                    **{f'price_{i}': level_levers.get(f'price_{i}', global_level_levers.get(f'price_{i}', BASE_PRICING.get(office.name, {}).get(level_name, 0.0))) for i in range(1, 13)},
                    **{f'salary_{i}': level_levers.get(f'salary_{i}', global_level_levers.get(f'salary_{i}', BASE_SALARIES.get(office.name, {}).get(level_name, 0.0))) for i in range(1, 13)},
                    **{f'utr_{i}': level_levers.get(f'utr_{i}', global_level_levers.get(f'utr_{i}', 0.0)) for i in range(1, 13)},
                )
                
                # Set initial headcount
                consultant_fte = office.total_fte * ROLE_DISTRIBUTION.get('Consultant', 0.8)
                level_fte = int(consultant_fte * level_percentage)
                # Use a date 2 years before simulation start to ensure people have sufficient tenure
                initialization_date_str = "2023-01"
                for _ in range(level_fte):
                    level.add_new_hire(initialization_date_str, "Consultant", office.name)
                office.roles['Consultant'][level_name] = level
            
            # Initialize other roles
            for role_name in ['Sales', 'Recruitment', 'Operations']:
                role_fte = int(office.total_fte * ROLE_DISTRIBUTION.get(role_name, 0.05))
                role_data = RoleData()
                # Apply levers to flat roles
                role_levers = office_levers.get(role_name, {})
                global_role_levers = global_levers.get(role_name, {})
                for i in range(1, 13):
                    setattr(role_data, f'recruitment_{i}', role_levers.get(f'recruitment_{i}', global_role_levers.get(f'recruitment_{i}', 0.0)))
                    setattr(role_data, f'churn_{i}', role_levers.get(f'churn_{i}', global_role_levers.get(f'churn_{i}', 0.0)))
                
                # Use a date 2 years before simulation start to ensure people have sufficient tenure
                initialization_date_str = "2023-01"
                for _ in range(role_fte):
                    role_data.add_new_hire(initialization_date_str, role_name, office.name)
                office.roles[role_name] = role_data

    def _apply_levers_to_existing_offices(self, lever_plan: Optional[Dict] = None):
        """Applies a lever plan to an already initialized set of offices."""
        if not lever_plan or not self.offices:
            return
            
        global_levers = lever_plan.get('global', {})
        office_levers = lever_plan.get('offices', {})
        
        for office_name, office in self.offices.items():
            current_office_levers = office_levers.get(office_name, {})
            
            for role_name, role_data in office.roles.items():
                if isinstance(role_data, dict): # Leveled roles (Consultant, Sales, Recruitment)
                    for level_name, level in role_data.items():
                        level_levers = current_office_levers.get(role_name, {}).get(level_name, {})
                        global_level_levers = global_levers.get(role_name, {}).get(level_name, {})
                        
                        for i in range(1, 13):
                            # Prioritize office-specific, then global, then default
                            recruitment_rate = level_levers.get(f'recruitment_{i}', global_level_levers.get(f'recruitment_{i}', getattr(level, f'recruitment_{i}')))
                            churn_rate = level_levers.get(f'churn_{i}', global_level_levers.get(f'churn_{i}', getattr(level, f'churn_{i}')))
                            price = level_levers.get(f'price_{i}', global_level_levers.get(f'price_{i}', getattr(level, f'price_{i}')))
                            salary = level_levers.get(f'salary_{i}', global_level_levers.get(f'salary_{i}', getattr(level, f'salary_{i}')))
                            utr = level_levers.get(f'utr_{i}', global_level_levers.get(f'utr_{i}', getattr(level, f'utr_{i}')))
                            
                            setattr(level, f'recruitment_{i}', recruitment_rate)
                            setattr(level, f'churn_{i}', churn_rate)
                            setattr(level, f'price_{i}', price)
                            setattr(level, f'salary_{i}', salary)
                            setattr(level, f'utr_{i}', utr)
                else: # Flat roles (Operations only)
                    flat_role_levers = current_office_levers.get(role_name, {})
                    global_flat_role_levers = global_levers.get(role_name, {})
                    for i in range(1, 13):
                        recruitment_rate = flat_role_levers.get(f'recruitment_{i}', global_flat_role_levers.get(f'recruitment_{i}', getattr(role_data, f'recruitment_{i}')))
                        churn_rate = flat_role_levers.get(f'churn_{i}', global_flat_role_levers.get(f'churn_{i}', getattr(role_data, f'churn_{i}')))
                        setattr(role_data, f'recruitment_{i}', recruitment_rate)
                        setattr(role_data, f'churn_{i}', churn_rate)
                        
    def get_offices_by_journey(self, journey: OfficeJourney) -> List[Office]:
        """Returns a list of offices matching a specific journey type"""
        return [o for o in self.offices.values() if o.journey == journey]

    def _get_monthly_attribute(self, obj, attribute_base: str, month: Month):
        """Gets a monthly attribute from an object (e.g., price_1, churn_5)"""
        return getattr(obj, f"{attribute_base}_{month.value}", 0.0)

    def _set_monthly_attribute(self, obj, attribute_base: str, month: Month, value):
        """Sets a monthly attribute on an object"""
        setattr(obj, f"{attribute_base}_{month.value}", value)
    
    def _recalculate_office_total_fte(self, office: Office) -> int:
        """
        Recalculate the total FTE for an office by summing all roles and levels.
        Updates the office.total_fte field and returns the calculated value.
        """
        total_fte = 0
        
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled roles (Consultant, Sales, Recruitment)
                for level_name, level in role_data.items():
                    total_fte += level.total
            else:  # Flat roles (Operations)
                total_fte += role_data.total
        
        # Update the office's total_fte field
        office.total_fte = total_fte
        return total_fte

    def run_simulation(self, start_year: int, start_month: int, end_year: int, end_month: int,
                      price_increase: float = 0.0, salary_increase: float = 0.0,
                      lever_plan: Optional[Dict] = None,
                      economic_params: Optional[EconomicParameters] = None) -> Dict:
        """
        Run the simulation for the specified period.
        This method now uses the new pure function architecture while maintaining backward compatibility.

        Args:
            start_year: Starting year
            start_month: Starting month (1-12)
            end_year: Ending year
            end_month: Ending month (1-12)
            price_increase: Annual price increase percentage
            salary_increase: Annual salary increase percentage
            lever_plan: Optional lever plan to apply
            economic_params: Optional economic parameters for KPI calculations

        Returns:
            Dictionary containing simulation results
        """
        print(f"🚀 [ENGINE] Starting simulation: {start_year}-{start_month:02d} to {end_year}-{end_month:02d}")
    
        # Import ScenarioService here to avoid circular imports
        from backend.src.services.scenario_service import ScenarioService
        from backend.src.services.config_service import ConfigService

        # Create scenario service to prepare data
        config_service = ConfigService()
        scenario_service = ScenarioService(config_service)
        
        # Resolve scenario data (this handles loading config, applying baseline/levers)
        scenario_data = {}
        if lever_plan:
            # Convert lever plan to scenario format if needed
            scenario_data = {'levers': lever_plan}
        
        resolved_data = scenario_service.resolve_scenario(scenario_data)
        
        # Use the new pure function approach
        return self.run_simulation_with_offices(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
            offices=resolved_data['offices'],
            progression_config=resolved_data['progression_config'],
            cat_curves=resolved_data['cat_curves'],
            price_increase=price_increase,
            salary_increase=salary_increase,
            economic_params=economic_params
        )

    def run_simulation_with_offices(
        self,
        start_year: int,
        start_month: int, 
        end_year: int,
        end_month: int,
        offices: Dict[str, Office],
        progression_config: Dict[str, Any],
        cat_curves: Dict[str, Any],
        price_increase: float = 0.0,
        salary_increase: float = 0.0,
        economic_params: Optional[EconomicParameters] = None
    ) -> Dict[str, Any]:
        """
        Pure function to run simulation with provided offices and progression rules.
        This method accepts all data as input parameters, making it completely testable
        and free from config service dependencies.
        
        Args:
            start_year: Simulation start year
            start_month: Simulation start month (1-12)
            end_year: Simulation end year
            end_month: Simulation end month (1-12)
            offices: Dictionary of Office objects keyed by office name
            progression_config: Progression rules dictionary
            cat_curves: CAT curves dictionary for progression probabilities
            price_increase: Annual price increase rate (0.0-1.0)
            salary_increase: Annual salary increase rate (0.0-1.0)
            economic_params: Economic parameters for KPI calculations
            
        Returns:
            Dictionary containing complete simulation results
        """
        # Validate input parameters
        if not offices:
            raise ValueError("Offices dictionary cannot be empty")
        
        if not progression_config:
            raise ValueError("Progression config cannot be empty")
        
        if not cat_curves:
            raise ValueError("CAT curves cannot be empty")
        
        # Set up the engine state with provided data
        self.offices = offices.copy()  # Use a copy to avoid modifying input
        self.monthly_results = {}
        self.simulation_results = None
        
        # Set up yearly logging
        self._setup_yearly_logging()
        
        # Create workforce manager with the provided offices
        workforce_manager = WorkforceManager(self.offices)
        
        # Run the simulation using the existing logic but with passed progression rules
        return self._run_simulation_core(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
            price_increase=price_increase,
            salary_increase=salary_increase,
            economic_params=economic_params,
            workforce_manager=workforce_manager,
            progression_config=progression_config,
            cat_curves=cat_curves
        )

    def _run_simulation_core(
        self,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
        price_increase: float,
        salary_increase: float,
        economic_params: Optional[EconomicParameters],
        workforce_manager: WorkforceManager,
        progression_config: Dict[str, Any],
        cat_curves: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Core simulation logic that runs the monthly progression, recruitment, and churn calculations.
        This method accepts progression rules as parameters instead of importing them.
        """
        # Initialize KPI service if not provided
        if economic_params is None:
            economic_params = EconomicParameters()
        
        # Initialize monthly results storage
        monthly_office_metrics = {}
        yearly_snapshots = {}
        
        # Calculate total simulation months
        total_months = (end_year - start_year) * 12 + (end_month - start_month + 1)
        
        # Set random seed for deterministic results
        random.seed(42)
        
        # Run simulation month by month
        current_year = start_year
        current_month = start_month
        
        for month_index in range(total_months):
            current_date_str = f"{current_year}-{current_month:02d}"
            
            # Update monthly metrics for all offices
            monthly_office_metrics[current_date_str] = {}
            
            for office_name, office in self.offices.items():
                office_metrics = {}
                
                # Process each role in the office
                for role_name, role_data in office.roles.items():
                    if role_name == 'Operations':
                        # Handle flat role (Operations)
                        role_metrics = self._process_operations_role(
                            role_data, office_name, current_date_str, current_month
                        )
                        office_metrics[role_name] = role_metrics
                    else:
                        # Handle leveled roles (Consultant, Sales, etc.)
                        role_metrics = {}
                        for level_name, level in role_data.items():
                            level_metrics = self._process_level(
                                level, role_name, office_name, current_date_str, 
                                current_month, progression_config, cat_curves
                            )
                            role_metrics[level_name] = level_metrics
                        office_metrics[role_name] = role_metrics
                
                monthly_office_metrics[current_date_str][office_name] = office_metrics
            
            # Move to next month
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
            
            # Store yearly snapshots
            if current_month == 1 or month_index == total_months - 1:
                year_key = str(current_year - 1) if current_month == 1 else str(current_year)
                yearly_snapshots[year_key] = self._get_yearly_snapshot(
                    monthly_office_metrics, year_key, economic_params
                )
        
        # Structure and return results
        return self._structure_yearly_results(
            yearly_snapshots, monthly_office_metrics, start_year, end_year, economic_params
        )

    def _process_operations_role(
        self, 
        role_data: RoleData, 
        office_name: str, 
        current_date_str: str, 
        current_month: int
    ) -> Dict[str, Any]:
        """Process Operations role for a given month."""
        # Get monthly rates
        recruitment_rate = getattr(role_data, f'recruitment_{current_month}', 0.0)
        churn_rate = getattr(role_data, f'churn_{current_month}', 0.0)
        price = getattr(role_data, f'price_{current_month}', 0.0) if hasattr(role_data, f'price_{current_month}') else 0.0
        salary = getattr(role_data, f'salary_{current_month}', 0.0) if hasattr(role_data, f'salary_{current_month}') else 0.0
        utr = getattr(role_data, f'utr_{current_month}', 0.85) if hasattr(role_data, f'utr_{current_month}') else 0.85
        # Calculate absolute numbers
        current_fte = role_data.total
        recruitment_count = int(recruitment_rate * current_fte / 100)
        churn_count = int(churn_rate * current_fte / 100)
        # Apply recruitment and churn
        for _ in range(recruitment_count):
            role_data.add_new_hire(current_date_str, "Operations", office_name)
        churned_people = role_data.apply_churn(churn_count)
        return {
            'fte': role_data.total,
            'recruitment_rate': recruitment_rate,
            'churn_rate': churn_rate,
            'recruitment_count': recruitment_count,
            'churn_count': churn_count,
            'churned_people': len(churned_people),
            'price': price,
            'salary': salary,
            'utr': utr
        }

    def _process_level(
        self, 
        level: Level, 
        role_name: str, 
        office_name: str, 
        current_date_str: str, 
        current_month: int,
        progression_config: Dict[str, Any],
        cat_curves: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a level for a given month."""
        # Get monthly rates
        recruitment_rate = getattr(level, f'recruitment_{current_month}', 0.0)
        churn_rate = getattr(level, f'churn_{current_month}', 0.0)
        price = getattr(level, f'price_{current_month}', 0.0)
        salary = getattr(level, f'salary_{current_month}', 0.0)
        utr = getattr(level, f'utr_{current_month}', 0.85)
        # Calculate absolute numbers
        current_fte = level.total
        recruitment_count = int(recruitment_rate * current_fte / 100)
        churn_count = int(churn_rate * current_fte / 100)
        # Apply recruitment and churn
        for _ in range(recruitment_count):
            level.add_new_hire(current_date_str, role_name, office_name)
        churned_people = level.apply_churn(churn_count)
        # Apply progression using CAT-based system with passed parameters
        promoted_people = level.apply_cat_based_progression(
            current_date_str, progression_config, cat_curves
        )
        return {
            'fte': level.total,
            'recruitment_rate': recruitment_rate,
            'churn_rate': churn_rate,
            'recruitment_count': recruitment_count,
            'churn_count': churn_count,
            'churned_people': len(churned_people),
            'promoted_people': len(promoted_people),
            'price': price,
            'salary': salary,
            'utr': utr
        }

    def _get_yearly_snapshot(
        self, 
        monthly_office_metrics: Dict, 
        year_key: str, 
        economic_params: EconomicParameters
    ) -> Dict[str, Any]:
        """Get a snapshot of all offices for a specific year, including per-office financial KPIs."""
        year_data = {}
        from backend.src.services.kpi.kpi_service import KPIService
        kpi_service = KPIService(economic_params)
        
        # Build the full year snapshot for all offices first
        for office_name, office in self.offices.items():
            office_snapshot = {
                'name': office_name,
                'total_fte': office.total_fte,
                'journey': office.journey.value,
                'levels': self._get_office_level_snapshot(office, monthly_office_metrics, f"{year_key}-01", f"{year_key}-12")
            }
            year_data[office_name] = office_snapshot
        
        # Now, for each office, calculate and attach all KPIs using the detailed office data from the group-level snapshot
        for office_name, office_snapshot in year_data.items():
            office_detailed_data = year_data[office_name]
            office_year_data = {
                'offices': {office_name: office_detailed_data},
                'total_fte': office_detailed_data['total_fte']
            }
            # Calculate all KPIs for this office
            office_kpis = kpi_service.calculate_kpis_for_year(
                {'years': {year_key: office_year_data}},
                target_year=year_key,
                simulation_duration_months=12,
                economic_params=economic_params
            )
            office_snapshot['financial'] = office_kpis.financial
            office_snapshot['growth'] = office_kpis.growth
            office_snapshot['journeys'] = office_kpis.journeys
            # Convert KPI dataclasses to dicts for JSON serialization and structure consistency
            def kpi_to_dict(kpi_obj):
                if hasattr(kpi_obj, 'to_dict'):
                    return kpi_obj.to_dict()
                elif hasattr(kpi_obj, '__dict__'):
                    return dict(kpi_obj.__dict__)
                else:
                    return kpi_obj

            if 'kpis' in office_snapshot:
                for kpi_type in ['financial', 'growth', 'journeys']:
                    if kpi_type in office_snapshot['kpis']:
                        office_snapshot['kpis'][kpi_type] = kpi_to_dict(office_snapshot['kpis'][kpi_type])
        return year_data

    def _structure_yearly_results(self, yearly_snapshots: Dict, monthly_office_metrics: Dict, start_year: int, end_year: int, economic_params: EconomicParameters) -> Dict[str, Any]:
        """
        Structures the final results dictionary with detailed monthly level data for each year.
        """
        yearly_results = {}
        try:
            for year in range(start_year, end_year + 1):
                year_str = str(year)
                # This will contain the structured data for all offices for this year
                yearly_offices_data = {}
                # Use the offices state from the end of the year snapshot
                if not self.offices:
                    print(f"[ENGINE ERROR] No offices found when structuring results for year {year}")
                    continue
                # Use the yearly snapshots if available, otherwise fall back to current office state
                if year_str in yearly_snapshots:
                    yearly_offices_data = yearly_snapshots[year_str]
                else:
                    # Fallback: create from current office state
                    for office_name, office in self.offices.items():
                        try:
                            office_levels = self._get_office_level_snapshot(
                                office, 
                                monthly_office_metrics, 
                                f"{year}-01", 
                                f"{year}-12"
                            )
                            yearly_offices_data[office_name] = {
                                'total_fte': office.total_fte, # End of simulation FTE
                                'name': office.name,
                                'journey': office.journey.value,
                                'levels': office_levels
                            }
                        except Exception as e:
                            print(f"[ENGINE ERROR] Failed to get snapshot for office {office_name}: {e}")
                            # Provide minimal structure if snapshot fails
                            yearly_offices_data[office_name] = {
                                'total_fte': office.total_fte,
                                'name': office.name,
                                'journey': office.journey.value,
                                'levels': {}
                            }
                # First create the basic year structure
                yearly_results[year_str] = {
                    'offices': yearly_offices_data,
                    'total_fte': sum(office_data['total_fte'] for office_data in yearly_offices_data.values())
                }
                # Then calculate complete year-specific KPIs using KPI service
                year_kpis = self._calculate_complete_year_kpis(yearly_results, year_str, economic_params)
                # Add the complete KPI structure to the year
                yearly_results[year_str]['kpis'] = year_kpis
                # --- NEW: Attach per-office KPIs using the same structure as group-level ---
                from backend.src.services.kpi.kpi_service import KPIService
                kpi_service = KPIService(economic_params)
                for office_name in yearly_offices_data:
                    office_detailed_data = yearly_results[year_str]['offices'][office_name]
                    office_year_data = {
                        'offices': {office_name: office_detailed_data},
                        'total_fte': office_detailed_data['total_fte']
                    }
                    office_kpis = kpi_service.calculate_kpis_for_year(
                        {'years': {year_str: office_year_data}},
                        target_year=year_str,
                        simulation_duration_months=12,
                        economic_params=economic_params
                    )
                    # Convert dataclasses to dicts for JSON serialization (matches group-level structure)
                    def to_dict(data):
                        if hasattr(data, '__dataclass_fields__'):
                            return {k: to_dict(getattr(data, k)) for k in data.__dataclass_fields__}
                        elif isinstance(data, dict):
                            return {k: to_dict(v) for k, v in data.items()}
                        elif isinstance(data, list):
                            return [to_dict(i) for i in data]
                        else:
                            return data
                    office_detailed_data['financial'] = to_dict(office_kpis.financial)
                    office_detailed_data['growth'] = to_dict(office_kpis.growth)
                    office_detailed_data['journeys'] = to_dict(office_kpis.journeys)
                # --- END NEW ---
        except Exception as e:
            print(f"[ENGINE ERROR] Failed to structure yearly results: {e}")
            import traceback
            traceback.print_exc()
            # Return minimal structure to prevent total failure
            for year in range(start_year, end_year + 1):
                year_str = str(year)
                yearly_results[year_str] = {
                    'offices': {},
                    'total_fte': 0,
                    'kpis': {
                        'financial': {
                            'net_sales': 0.0,
                            'net_sales_baseline': 0.0,
                            'ebitda': 0.0,
                            'ebitda_baseline': 0.0,
                            'margin': 0.0,
                            'margin_baseline': 0.0,
                            'avg_hourly_rate': 0.0,
                            'avg_hourly_rate_baseline': 0.0,
                            'total_salary_costs': 0.0,
                            'total_salary_costs_baseline': 0.0
                        },
                        'growth': {
                            'total_fte': 0,
                            'baseline_total_fte': 0,
                            'current_total_fte': 0,
                            'non_debit_ratio': 0.0,
                            'non_debit_ratio_baseline': 0.0
                        },
                        'journeys': {
                            'journey_totals': {},
                            'journey_percentages': {},
                            'journey_totals_baseline': {},
                            'journey_percentages_baseline': {}
                        }
                    }
                }
            
        return {'years': yearly_results}

    def _calculate_complete_year_kpis(self, yearly_results: Dict[str, Any], target_year: str, economic_params: EconomicParameters) -> Dict[str, Any]:
        """Calculate complete year-specific KPIs including financial, growth, and journey metrics"""
        try:
            # Create a temporary simulation results structure for the KPI service
            temp_simulation_results = {
                'years': yearly_results
            }
            
            # Use the existing KPI service
            kpi_service = KPIService(economic_params=economic_params)
            year_kpis = kpi_service.calculate_kpis_for_year(
                temp_simulation_results,
                target_year,
                simulation_duration_months=12,  # Always use 12 months for annual calculations
                economic_params=economic_params
            )
            
            # Convert dataclasses to dicts for JSON serialization
            def to_dict(data):
                if hasattr(data, '__dataclass_fields__'):
                    return {k: to_dict(getattr(data, k)) for k in data.__dataclass_fields__}
                elif isinstance(data, dict):
                    return {k: to_dict(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [to_dict(i) for i in data]
                else:
                    return data
            
            # Return the complete KPI structure
            return to_dict(year_kpis)
            
        except Exception as e:
            print(f"[ENGINE ERROR] Failed to calculate complete year KPIs: {e}")
            import traceback
            traceback.print_exc()
            # Return zero values as fallback
            return {
                'financial': {
                    'net_sales': 0.0,
                    'net_sales_baseline': 0.0,
                    'ebitda': 0.0,
                    'ebitda_baseline': 0.0,
                    'margin': 0.0,
                    'margin_baseline': 0.0,
                    'avg_hourly_rate': 0.0,
                    'avg_hourly_rate_baseline': 0.0,
                    'total_salary_costs': 0.0,
                    'total_salary_costs_baseline': 0.0
                },
                'growth': {
                    'total_fte': 0,
                    'baseline_total_fte': 0,
                    'current_total_fte': 0,
                    'non_debit_ratio': 0.0,
                    'non_debit_ratio_baseline': 0.0
                },
                'journeys': {
                    'journey_totals': {},
                    'journey_percentages': {},
                    'journey_totals_baseline': {},
                    'journey_percentages_baseline': {}
                }
            }
        
    def get_simulation_results(self) -> Optional[Dict[str, Any]]:
        """Return the latest simulation results"""
        return self.simulation_results

    def calculate_kpis_for_simulation(
        self, 
        results: Dict[str, Any], 
        simulation_duration_months: int,
        unplanned_absence: float = 0.05,
        other_expense: float = 100000.0
    ) -> Dict[str, Any]:
        """Calculate KPIs using the KPI service"""
        kpi_service = KPIService()
        
        # Convert dataclasses to dicts for JSON serialization
        all_kpis_dataclass = kpi_service.calculate_all_kpis(
            results,
            simulation_duration_months,
            unplanned_absence,
            other_expense
        )
        
        def to_dict(data):
            if hasattr(data, '__dataclass_fields__'):
                return {k: to_dict(getattr(data, k)) for k in data.__dataclass_fields__}
            elif isinstance(data, dict):
                return {k: to_dict(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [to_dict(i) for i in data]
            else:
                return data

        return to_dict(all_kpis_dataclass)

    def _get_next_level_name(self, current_level: str) -> Optional[str]:
        """Get the name of the next level in the progression path"""
        # Determine level order from current offices if available
        if not self.offices:
            # Fallback to standard progression path
            progression_path = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
        else:
            # Extract level order from current offices
            levels = set()
            for office in self.offices.values():
                for role_name, role_data in office.roles.items():
                    if isinstance(role_data, dict):  # Leveled roles
                        levels.update(role_data.keys())
            
            # Use standard progression path filtered by found levels
            standard_order = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
            progression_path = [level for level in standard_order if level in levels]
        
        try:
            current_index = progression_path.index(current_level)
            if current_index + 1 < len(progression_path):
                return progression_path[current_index + 1]
            return None
        except ValueError:
            return None

    def _get_next_level(self, current_level: str, role_name: str, office_roles: Dict[str, Dict[str, 'Level'] or 'RoleData']) -> Optional['Level']:
        """Get the next Level object in the progression path"""
        next_level_name = self._get_next_level_name(current_level)
        if next_level_name and role_name in office_roles and isinstance(office_roles[role_name], dict):
            return office_roles[role_name].get(next_level_name)
        return None

    def _log_yearly_results(self, year: int, yearly_snapshots: Dict, monthly_office_metrics: Dict, economic_params: EconomicParameters):
        year_str = str(year)
        if year_str not in yearly_snapshots:
            self.yearly_logger.info("No data available for this year")
            return
        year_data = yearly_snapshots[year_str]
        log_office_aggregates_per_year(self.yearly_logger, year, year_data, economic_params)
        # Remove or comment out detailed per-office logging
        # for office_name, office_data in year_data.items():
        #     self._log_office_kpis(office_name, office_data, economic_params)
        # self._log_system_kpis(year_data, economic_params)

    def _log_office_kpis(self, office_name: str, office_data: Dict, economic_params: EconomicParameters):
        log_office_kpis(self.yearly_logger, office_name, office_data, economic_params)

    def _log_system_kpis(self, year_data: Dict, economic_params: EconomicParameters):
        log_system_kpis(self.yearly_logger, year_data, economic_params)

    def _get_office_level_snapshot(self, office: Office, monthly_office_metrics: Dict, start_date_str: str, end_date_str: str) -> Dict[str, Any]:
        """
        Gathers and structures the current state data for each level in an office
        for KPI calculations. Converts the monthly_office_metrics structure into arrays.
        """
        level_snapshots = {}
        # Iterate over all dates in monthly_office_metrics
        sorted_dates = sorted(monthly_office_metrics.keys())
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict): # Leveled roles
                level_snapshots[role_name] = {}
                for level_name, _ in role_data.items():
                    monthly_array = []
                    for date_str in sorted_dates:
                        office_data = monthly_office_metrics[date_str].get(office.name, {})
                        level_data = office_data.get(role_name, {}).get(level_name, {})
                        if level_data:
                            monthly_array.append(level_data)
                    level_snapshots[role_name][level_name] = monthly_array
            else: # Flat roles (e.g., Operations)
                monthly_array = []
                for date_str in sorted_dates:
                    office_data = monthly_office_metrics[date_str].get(office.name, {})
                    role_monthly_data = office_data.get(role_name, {})
                    if role_monthly_data:
                        monthly_array.append(role_monthly_data)
                level_snapshots[role_name] = monthly_array
        return level_snapshots

def calculate_configuration_checksum(offices: Dict[str, 'Office']) -> str:
    """
    Calculates a checksum for the initial office configuration to detect changes.
    This helps in deciding whether to re-run a baseline simulation.
    Uses only the raw config data to avoid circular references.
    """
    from backend.src.services.config_service import config_service
    config_data = config_service.get_config()
    config_string = json.dumps(config_data, sort_keys=True)
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
                        for key in ['recruitment', 'churn', 'price', 'salary', 'utr']:
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