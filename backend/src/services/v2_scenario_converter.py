"""
V2 Scenario Converter - Migration Utility

Converts existing V1 scenarios to V2 format with enhanced data structures:
- Upgrades scenario requests to new V2 format
- Converts business plan data to enhanced structure
- Migrates population snapshots to V2 format
- Updates KPI structures and calculation methods
- Provides backward compatibility utilities

Enables smooth migration from V1 to V2 simulation engine.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, date
from dataclasses import dataclass, asdict
import logging
import json
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Result of scenario conversion process"""
    success: bool
    converted_data: Optional[Dict[str, Any]] = None
    warnings: List[str] = None
    errors: List[str] = None
    conversion_notes: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
        if self.conversion_notes is None:
            self.conversion_notes = []


class V2ScenarioConverter:
    """
    Converts V1 scenarios to V2 format with enhanced data structures
    
    Key capabilities:
    - Convert scenario requests with enhanced levers and time ranges
    - Upgrade business plan data to include baseline FTE and utilization
    - Migrate population snapshots to V2 format
    - Update KPI structures for role-specific calculations
    - Provide compatibility mapping for legacy APIs
    """
    
    def __init__(self):
        self.default_utilization_targets = {
            'Consultant': 0.85,
            'Sales': 0.0,
            'Recruitment': 0.0,
            'Operations': 0.0
        }
        self.default_price_structure = {
            'A': 150.0, 'AC': 200.0, 'C': 250.0, 
            'SrC': 300.0, 'AM': 350.0, 'M': 400.0,
            'SrM': 450.0, 'Pi': 500.0, 'P': 600.0
        }
        
    def convert_scenario_request(self, v1_scenario: Dict[str, Any]) -> ConversionResult:
        """Convert V1 scenario request to V2 format"""
        result = ConversionResult(success=True)
        
        try:
            # Extract V1 scenario components
            scenario_id = v1_scenario.get('scenario_id', f"migrated_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            name = v1_scenario.get('name', 'Migrated Scenario')
            
            # Convert time range
            v2_time_range = self._convert_time_range(v1_scenario.get('time_range', {}), result)
            
            # Convert office IDs (straightforward)
            office_ids = v1_scenario.get('office_ids', [])
            if isinstance(office_ids, str):
                office_ids = [office_ids]
            
            # Convert levers to enhanced V2 format
            v2_levers = self._convert_levers(v1_scenario.get('levers', {}), result)
            
            # Create V2 scenario structure
            v2_scenario = {
                'scenario_id': scenario_id,
                'name': name,
                'time_range': v2_time_range,
                'office_ids': office_ids,
                'levers': v2_levers,
                'metadata': {
                    'converted_from_v1': True,
                    'conversion_date': datetime.now().isoformat(),
                    'original_format_version': '1.0'
                }
            }
            
            result.converted_data = v2_scenario
            result.conversion_notes.append(f"Successfully converted scenario '{name}' to V2 format")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to convert scenario request: {str(e)}")
            logger.error(f"Scenario conversion error: {str(e)}")
        
        return result
    
    def convert_business_plan(self, v1_business_plan: Dict[str, Any], 
                            population_snapshot: Optional[Dict[str, Any]] = None) -> ConversionResult:
        """Convert V1 business plan to enhanced V2 format with baseline FTE"""
        result = ConversionResult(success=True)
        
        try:
            office_id = v1_business_plan.get('office_id', 'unknown_office')
            name = v1_business_plan.get('name', f'Converted Business Plan - {office_id}')
            
            # Extract baseline FTE from population snapshot if available
            baseline_fte = {}
            if population_snapshot and 'workforce' in population_snapshot:
                baseline_fte = self._extract_baseline_fte(population_snapshot['workforce'])
                result.conversion_notes.append("Extracted baseline FTE from population snapshot")
            else:
                result.warnings.append("No population snapshot provided - baseline FTE will be empty")
            
            # Convert monthly plans to enhanced V2 format
            v1_monthly_plans = v1_business_plan.get('monthly_plans', {})
            v2_monthly_plans = {}
            
            for month_key, v1_monthly_plan in v1_monthly_plans.items():
                v2_monthly_plan = self._convert_monthly_plan(v1_monthly_plan, baseline_fte, result)
                v2_monthly_plans[month_key] = v2_monthly_plan
            
            # Create enhanced V2 business plan
            v2_business_plan = {
                'office_id': office_id,
                'name': f"{name} (Enhanced V2)",
                'monthly_plans': v2_monthly_plans,
                'metadata': {
                    'converted_from_v1': True,
                    'conversion_date': datetime.now().isoformat(),
                    'baseline_fte_source': 'population_snapshot' if baseline_fte else 'empty',
                    'enhanced_features': ['baseline_fte', 'utilization_targets', 'price_per_hour', 'cost_breakdown']
                }
            }
            
            result.converted_data = v2_business_plan
            result.conversion_notes.append(f"Converted {len(v2_monthly_plans)} monthly plans to enhanced V2 format")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to convert business plan: {str(e)}")
            logger.error(f"Business plan conversion error: {str(e)}")
        
        return result
    
    def convert_population_snapshot(self, v1_snapshot: Dict[str, Any]) -> ConversionResult:
        """Convert V1 population snapshot to V2 format"""
        result = ConversionResult(success=True)
        
        try:
            # V1 to V2 population snapshot is mostly straightforward
            # Main differences are in metadata and validation
            
            v2_snapshot = {
                'id': v1_snapshot.get('id', f"migrated_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                'office_id': v1_snapshot.get('office_id', 'unknown_office'),
                'snapshot_date': v1_snapshot.get('snapshot_date', '2024-01'),
                'name': v1_snapshot.get('name', 'Migrated Population Snapshot'),
                'workforce': self._convert_workforce_entries(v1_snapshot.get('workforce', []), result),
                'metadata': {
                    'converted_from_v1': True,
                    'conversion_date': datetime.now().isoformat(),
                    'total_workforce': len(v1_snapshot.get('workforce', [])),
                    'roles_included': list(set(entry.get('role') for entry in v1_snapshot.get('workforce', []))),
                    'validation_status': 'converted_pending_validation'
                }
            }
            
            result.converted_data = v2_snapshot
            result.conversion_notes.append(f"Converted population snapshot with {len(v2_snapshot['workforce'])} workforce entries")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to convert population snapshot: {str(e)}")
            logger.error(f"Population snapshot conversion error: {str(e)}")
        
        return result
    
    def convert_kpi_structure(self, v1_kpis: Dict[str, Any]) -> ConversionResult:
        """Convert V1 KPI structure to V2 role-specific format"""
        result = ConversionResult(success=True)
        
        try:
            # Convert basic workforce KPIs
            v2_kpis = {
                'total_headcount': v1_kpis.get('total_headcount', 0),
                'total_recruitment': v1_kpis.get('total_recruitment', 0),
                'total_churn': v1_kpis.get('total_churn', 0),
                'net_recruitment': v1_kpis.get('net_recruitment', 0),
                
                # Enhanced V2 KPIs
                'role_specific_workforce': self._create_role_specific_workforce_kpis(v1_kpis),
                'role_specific_financial': self._create_role_specific_financial_kpis(v1_kpis),
                
                # Financial KPIs with enhanced calculations
                'net_sales': v1_kpis.get('revenue', 0),  # Will be recalculated in V2
                'total_costs': v1_kpis.get('costs', 0),
                'gross_profit': v1_kpis.get('revenue', 0) - v1_kpis.get('costs', 0),
                'ebitda': v1_kpis.get('revenue', 0) - v1_kpis.get('costs', 0),  # Simplified
                
                'conversion_metadata': {
                    'converted_from_v1': True,
                    'conversion_date': datetime.now().isoformat(),
                    'enhanced_features': ['role_specific_breakdown', 'financial_attribution'],
                    'recalculation_needed': True
                }
            }
            
            result.converted_data = v2_kpis
            result.conversion_notes.append("Converted KPIs to V2 role-specific format")
            result.warnings.append("V2 KPIs will be recalculated during first simulation run")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to convert KPI structure: {str(e)}")
            logger.error(f"KPI conversion error: {str(e)}")
        
        return result
    
    def create_migration_report(self, conversions: Dict[str, ConversionResult]) -> Dict[str, Any]:
        """Create comprehensive migration report"""
        report = {
            'migration_summary': {
                'total_items': len(conversions),
                'successful_conversions': sum(1 for r in conversions.values() if r.success),
                'failed_conversions': sum(1 for r in conversions.values() if not r.success),
                'total_warnings': sum(len(r.warnings) for r in conversions.values()),
                'total_errors': sum(len(r.errors) for r in conversions.values()),
                'migration_date': datetime.now().isoformat()
            },
            'conversion_details': {},
            'recommendations': self._generate_migration_recommendations(conversions)
        }
        
        # Add detailed results for each conversion
        for item_name, result in conversions.items():
            report['conversion_details'][item_name] = {
                'success': result.success,
                'warnings_count': len(result.warnings),
                'errors_count': len(result.errors),
                'notes_count': len(result.conversion_notes),
                'warnings': result.warnings,
                'errors': result.errors,
                'notes': result.conversion_notes
            }
        
        return report
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _convert_time_range(self, v1_time_range: Dict[str, Any], result: ConversionResult) -> Dict[str, Any]:
        """Convert V1 time range to V2 format"""
        # V2 format is more structured
        return {
            'start_year': v1_time_range.get('start_year', 2024),
            'start_month': v1_time_range.get('start_month', 1),
            'end_year': v1_time_range.get('end_year', 2024),
            'end_month': v1_time_range.get('end_month', 12),
            'total_months': self._calculate_total_months(
                v1_time_range.get('start_year', 2024), v1_time_range.get('start_month', 1),
                v1_time_range.get('end_year', 2024), v1_time_range.get('end_month', 12)
            )
        }
    
    def _convert_levers(self, v1_levers: Dict[str, Any], result: ConversionResult) -> Dict[str, Any]:
        """Convert V1 levers to enhanced V2 format"""
        v2_levers = {
            'recruitment_multiplier': v1_levers.get('recruitment_multiplier', 1.0),
            'churn_multiplier': v1_levers.get('churn_multiplier', 1.0),
            'progression_multiplier': v1_levers.get('progression_multiplier', 1.0),
            
            # Enhanced V2 levers
            'price_multiplier': v1_levers.get('price_multiplier', 1.0),
            'salary_multiplier': v1_levers.get('salary_multiplier', 1.0),
            'utilization_multiplier': v1_levers.get('utilization_multiplier', 1.0)  # New in V2
        }
        
        if any(lever != 1.0 for lever in [v2_levers['price_multiplier'], v2_levers['salary_multiplier'], v2_levers['utilization_multiplier']]):
            result.conversion_notes.append("Enhanced V2 levers (price, salary, utilization) detected or added")
        
        return v2_levers
    
    def _convert_monthly_plan(self, v1_monthly_plan: Dict[str, Any], 
                            baseline_fte: Dict[str, Dict[str, int]], result: ConversionResult) -> Dict[str, Any]:
        """Convert single monthly plan to V2 enhanced format"""
        v2_monthly_plan = {
            'year': v1_monthly_plan.get('year', 2024),
            'month': v1_monthly_plan.get('month', 1),
            'recruitment': v1_monthly_plan.get('recruitment', {}),
            'churn': v1_monthly_plan.get('churn', {}),
            'revenue': v1_monthly_plan.get('revenue', 0.0),
            'costs': v1_monthly_plan.get('costs', 0.0),
            
            # Enhanced V2 fields
            'baseline_fte': baseline_fte,
            'utilization_targets': self.default_utilization_targets.copy(),
            'price_per_hour': self.default_price_structure.copy(),
            'working_hours_per_month': 160,
            'operating_costs': v1_monthly_plan.get('costs', 0.0) * 0.3,  # Estimate 30%
            'total_costs': v1_monthly_plan.get('costs', 0.0),
            
            # Existing fields with defaults
            'price_per_role': v1_monthly_plan.get('price_per_role', {}),
            'salary_per_role': v1_monthly_plan.get('salary_per_role', {}),
            'utr_per_role': v1_monthly_plan.get('utr_per_role', {})
        }
        
        return v2_monthly_plan
    
    def _extract_baseline_fte(self, workforce_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """Extract baseline FTE counts from workforce data"""
        baseline_fte = {}
        
        for entry in workforce_data:
            role = entry.get('role', 'Unknown')
            level = entry.get('level', 'Unknown')
            
            if role not in baseline_fte:
                baseline_fte[role] = {}
            if level not in baseline_fte[role]:
                baseline_fte[role][level] = 0
            
            baseline_fte[role][level] += 1
        
        return baseline_fte
    
    def _convert_workforce_entries(self, v1_workforce: List[Dict[str, Any]], result: ConversionResult) -> List[Dict[str, Any]]:
        """Convert workforce entries to V2 format"""
        v2_workforce = []
        
        for entry in v1_workforce:
            # V2 format is largely compatible, just add validation
            v2_entry = {
                'id': entry.get('id', f"migrated_{len(v2_workforce)}"),
                'role': entry.get('role', 'Unknown'),
                'level': entry.get('level', 'Unknown'),
                'hire_date': entry.get('hire_date', '2024-01'),
                'level_start_date': entry.get('level_start_date', entry.get('hire_date', '2024-01')),
                'office': entry.get('office', 'unknown_office')
            }
            
            # Validate required fields
            if v2_entry['role'] == 'Unknown':
                result.warnings.append(f"Workforce entry {v2_entry['id']} missing role information")
            
            v2_workforce.append(v2_entry)
        
        return v2_workforce
    
    def _create_role_specific_workforce_kpis(self, v1_kpis: Dict[str, Any]) -> Dict[str, Any]:
        """Create role-specific workforce KPIs from V1 data"""
        # This is a simplified conversion - real V2 KPIs are calculated during simulation
        total_headcount = v1_kpis.get('total_headcount', 0)
        
        # Estimate role distribution (will be recalculated in V2)
        return {
            'Consultant': {
                'total_headcount': int(total_headcount * 0.6),  # Estimate 60%
                'billable_headcount': int(total_headcount * 0.6),
                'progression_eligible': True
            },
            'Sales': {
                'total_headcount': int(total_headcount * 0.25),  # Estimate 25%
                'billable_headcount': 0,
                'progression_eligible': True
            },
            'Recruitment': {
                'total_headcount': int(total_headcount * 0.1),   # Estimate 10%
                'billable_headcount': 0,
                'progression_eligible': True
            },
            'Operations': {
                'total_headcount': int(total_headcount * 0.05),  # Estimate 5%
                'billable_headcount': 0,
                'progression_eligible': False
            }
        }
    
    def _create_role_specific_financial_kpis(self, v1_kpis: Dict[str, Any]) -> Dict[str, Any]:
        """Create role-specific financial KPIs from V1 data"""
        total_revenue = v1_kpis.get('revenue', 0)
        total_costs = v1_kpis.get('costs', 0)
        
        # In V2, only Consultants generate revenue
        return {
            'Consultant': {
                'revenue': total_revenue,  # All revenue attributed to consultants
                'costs': total_costs * 0.6,  # Estimate 60% of costs
                'profit': total_revenue - (total_costs * 0.6),
                'generates_revenue': True
            },
            'Sales': {
                'revenue': 0,  # No direct revenue in V2 business model
                'costs': total_costs * 0.25,  # Estimate 25% of costs
                'profit': -(total_costs * 0.25),  # Cost center
                'generates_revenue': False
            },
            'Recruitment': {
                'revenue': 0,  # No direct revenue in V2 business model
                'costs': total_costs * 0.1,   # Estimate 10% of costs
                'profit': -(total_costs * 0.1),   # Cost center
                'generates_revenue': False
            },
            'Operations': {
                'revenue': 0,  # No direct revenue in V2 business model
                'costs': total_costs * 0.05,  # Estimate 5% of costs
                'profit': -(total_costs * 0.05),  # Cost center
                'generates_revenue': False
            }
        }
    
    def _calculate_total_months(self, start_year: int, start_month: int, end_year: int, end_month: int) -> int:
        """Calculate total months between start and end dates"""
        return (end_year - start_year) * 12 + (end_month - start_month) + 1
    
    def _generate_migration_recommendations(self, conversions: Dict[str, ConversionResult]) -> List[str]:
        """Generate recommendations based on conversion results"""
        recommendations = []
        
        # Check for common issues
        failed_conversions = [name for name, result in conversions.items() if not result.success]
        if failed_conversions:
            recommendations.append(f"Review and fix {len(failed_conversions)} failed conversions before proceeding")
        
        total_warnings = sum(len(result.warnings) for result in conversions.values())
        if total_warnings > 0:
            recommendations.append(f"Address {total_warnings} warnings to ensure data quality")
        
        # Check for missing features
        if any('baseline_fte' in ' '.join(result.warnings) for result in conversions.values()):
            recommendations.append("Consider providing population snapshots for more accurate baseline FTE data")
        
        recommendations.extend([
            "Run V2 simulation tests after migration to validate converted data",
            "Compare V1 and V2 simulation results to verify conversion accuracy",
            "Update any custom integrations to use V2 API endpoints and data structures",
            "Consider gradual rollout with parallel V1/V2 operation during transition period"
        ])
        
        return recommendations


# ============================================================================
# Utility Functions
# ============================================================================

def migrate_v1_scenario_file(file_path: str, output_path: Optional[str] = None) -> ConversionResult:
    """Migrate a complete V1 scenario file to V2 format"""
    converter = V2ScenarioConverter()
    
    try:
        # Load V1 scenario file
        with open(file_path, 'r') as f:
            v1_data = json.load(f)
        
        # Convert all components
        conversions = {}
        
        if 'scenario' in v1_data:
            conversions['scenario'] = converter.convert_scenario_request(v1_data['scenario'])
        
        if 'business_plans' in v1_data:
            for office_id, business_plan in v1_data['business_plans'].items():
                pop_snapshot = v1_data.get('population_snapshots', {}).get(office_id)
                conversions[f'business_plan_{office_id}'] = converter.convert_business_plan(business_plan, pop_snapshot)
        
        if 'population_snapshots' in v1_data:
            for office_id, snapshot in v1_data['population_snapshots'].items():
                conversions[f'population_snapshot_{office_id}'] = converter.convert_population_snapshot(snapshot)
        
        # Create migration report
        migration_report = converter.create_migration_report(conversions)
        
        # Compile converted data
        v2_data = {
            'format_version': '2.0',
            'migration_info': migration_report['migration_summary'],
            'converted_data': {}
        }
        
        for item_name, result in conversions.items():
            if result.success:
                v2_data['converted_data'][item_name] = result.converted_data
        
        v2_data['migration_report'] = migration_report
        
        # Save converted data
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(v2_data, f, indent=2, default=str)
        
        overall_result = ConversionResult(
            success=all(result.success for result in conversions.values()),
            converted_data=v2_data,
            conversion_notes=[f"Migrated V1 scenario file to V2 format with {len(conversions)} components"]
        )
        
        return overall_result
        
    except Exception as e:
        return ConversionResult(
            success=False,
            errors=[f"Failed to migrate scenario file: {str(e)}"]
        )


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    'V2ScenarioConverter',
    'ConversionResult', 
    'migrate_v1_scenario_file'
]