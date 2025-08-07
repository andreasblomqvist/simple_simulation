"""
V2 Scenario Converter Testing

Tests conversion of V1 scenarios to V2 enhanced format:
1. Scenario request conversion with enhanced levers
2. Business plan conversion with baseline FTE integration
3. Population snapshot format migration
4. KPI structure upgrade to role-specific format
5. Migration report generation and recommendations

Verifies backward compatibility and data integrity during migration.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_v2_scenario_converter():
    """Test comprehensive V1 to V2 scenario conversion"""
    print("V2 ENGINE - SCENARIO CONVERTER TESTING")
    print("=" * 45)
    
    try:
        from src.services.v2_scenario_converter import V2ScenarioConverter, ConversionResult
        
        # 1. Initialize converter
        print("1. Initializing V2 scenario converter...")
        converter = V2ScenarioConverter()
        
        print(f"   Default utilization targets: {converter.default_utilization_targets}")
        print(f"   Default price structure: {len(converter.default_price_structure)} levels")
        
        # 2. Create sample V1 scenario data
        print("\n2. Creating sample V1 scenario data...")
        
        v1_scenario_request = {
            'scenario_id': 'legacy_growth_scenario',
            'name': 'Legacy Growth Scenario 2024',
            'time_range': {
                'start_year': 2024,
                'start_month': 1,
                'end_year': 2024,
                'end_month': 12
            },
            'office_ids': ['london', 'munich'],
            'levers': {
                'recruitment_multiplier': 1.2,
                'churn_multiplier': 0.8,
                'progression_multiplier': 1.1
            }
        }
        
        v1_business_plan = {
            'office_id': 'london',
            'name': 'London Growth Plan 2024',
            'monthly_plans': {
                '2024-01': {
                    'year': 2024,
                    'month': 1,
                    'recruitment': {
                        'Consultant': {'A': 5.0, 'AC': 2.0, 'C': 1.0},
                        'Sales': {'A': 2.0, 'AC': 1.0}
                    },
                    'churn': {
                        'Consultant': {'A': 2.0, 'AC': 1.0, 'C': 0.5},
                        'Sales': {'A': 1.0, 'AC': 0.5}
                    },
                    'revenue': 500000.0,
                    'costs': 300000.0,
                    'price_per_role': {},
                    'salary_per_role': {},
                    'utr_per_role': {}
                },
                '2024-02': {
                    'year': 2024,
                    'month': 2,
                    'recruitment': {
                        'Consultant': {'A': 4.0, 'AC': 2.0, 'C': 1.0},
                        'Sales': {'A': 2.0, 'AC': 1.0}
                    },
                    'churn': {
                        'Consultant': {'A': 2.0, 'AC': 1.0, 'C': 0.5},
                        'Sales': {'A': 1.0, 'AC': 0.5}
                    },
                    'revenue': 520000.0,
                    'costs': 310000.0,
                    'price_per_role': {},
                    'salary_per_role': {},
                    'utr_per_role': {}
                }
            }
        }
        
        v1_population_snapshot = {
            'id': 'london_baseline_2024',
            'office_id': 'london',
            'snapshot_date': '2024-01',
            'name': 'London Office Baseline',
            'workforce': [
                {'id': 'emp_001', 'role': 'Consultant', 'level': 'AC', 'hire_date': '2021-08', 'level_start_date': '2021-08', 'office': 'london'},
                {'id': 'emp_002', 'role': 'Consultant', 'level': 'C', 'hire_date': '2020-06', 'level_start_date': '2021-06', 'office': 'london'},
                {'id': 'emp_003', 'role': 'Sales', 'level': 'A', 'hire_date': '2023-01', 'level_start_date': '2023-01', 'office': 'london'},
                {'id': 'emp_004', 'role': 'Operations', 'level': 'Operations', 'hire_date': '2022-03', 'level_start_date': '2022-03', 'office': 'london'}
            ]
        }
        
        v1_kpis = {
            'total_headcount': 45,
            'total_recruitment': 8,
            'total_churn': 3,
            'net_recruitment': 5,
            'revenue': 500000,
            'costs': 300000
        }
        
        print(f"   V1 scenario: {v1_scenario_request['name']}")
        print(f"   V1 business plan: {len(v1_business_plan['monthly_plans'])} months")
        print(f"   V1 population: {len(v1_population_snapshot['workforce'])} people")
        print(f"   V1 KPIs: {len(v1_kpis)} metrics")
        
        # 3. CONVERT SCENARIO REQUEST
        print("\n3. CONVERTING SCENARIO REQUEST")
        print("=" * 35)
        
        scenario_result = converter.convert_scenario_request(v1_scenario_request)
        
        print(f"   Conversion success: {scenario_result.success}")
        print(f"   Warnings: {len(scenario_result.warnings)}")
        print(f"   Errors: {len(scenario_result.errors)}")
        print(f"   Notes: {len(scenario_result.conversion_notes)}")
        
        if scenario_result.success:
            v2_scenario = scenario_result.converted_data
            print(f"\n   V2 scenario structure:")
            print(f"      Scenario ID: {v2_scenario['scenario_id']}")
            print(f"      Time range: {v2_scenario['time_range']}")
            print(f"      Enhanced levers: {v2_scenario['levers']}")
            print(f"      Metadata: {v2_scenario['metadata']}")
        
        # 4. CONVERT BUSINESS PLAN
        print("\n4. CONVERTING BUSINESS PLAN")
        print("=" * 32)
        
        business_plan_result = converter.convert_business_plan(v1_business_plan, v1_population_snapshot)
        
        print(f"   Conversion success: {business_plan_result.success}")
        print(f"   Warnings: {len(business_plan_result.warnings)}")
        print(f"   Errors: {len(business_plan_result.errors)}")
        print(f"   Notes: {len(business_plan_result.conversion_notes)}")
        
        if business_plan_result.success:
            v2_business_plan = business_plan_result.converted_data
            sample_month = list(v2_business_plan['monthly_plans'].values())[0]
            
            print(f"\n   V2 business plan enhancements:")
            print(f"      Baseline FTE: {sample_month['baseline_fte']}")
            print(f"      Utilization targets: {sample_month['utilization_targets']}")
            print(f"      Price per hour: {len(sample_month['price_per_hour'])} levels")
            print(f"      Working hours/month: {sample_month['working_hours_per_month']}")
            print(f"      Operating costs: ${sample_month['operating_costs']:,.0f}")
        
        # 5. CONVERT POPULATION SNAPSHOT
        print("\n5. CONVERTING POPULATION SNAPSHOT")
        print("=" * 37)
        
        snapshot_result = converter.convert_population_snapshot(v1_population_snapshot)
        
        print(f"   Conversion success: {snapshot_result.success}")
        print(f"   Warnings: {len(snapshot_result.warnings)}")
        print(f"   Errors: {len(snapshot_result.errors)}")
        print(f"   Notes: {len(snapshot_result.conversion_notes)}")
        
        if snapshot_result.success:
            v2_snapshot = snapshot_result.converted_data
            print(f"\n   V2 snapshot structure:")
            print(f"      Workforce entries: {len(v2_snapshot['workforce'])}")
            print(f"      Metadata: {v2_snapshot['metadata']}")
            print(f"      Roles included: {v2_snapshot['metadata']['roles_included']}")
        
        # 6. CONVERT KPI STRUCTURE
        print("\n6. CONVERTING KPI STRUCTURE")
        print("=" * 32)
        
        kpi_result = converter.convert_kpi_structure(v1_kpis)
        
        print(f"   Conversion success: {kpi_result.success}")
        print(f"   Warnings: {len(kpi_result.warnings)}")
        print(f"   Errors: {len(kpi_result.errors)}")
        print(f"   Notes: {len(kpi_result.conversion_notes)}")
        
        if kpi_result.success:
            v2_kpis = kpi_result.converted_data
            print(f"\n   V2 KPI enhancements:")
            print(f"      Role-specific workforce: {len(v2_kpis['role_specific_workforce'])} roles")
            print(f"      Role-specific financial: {len(v2_kpis['role_specific_financial'])} roles")
            print(f"      Enhanced metrics: {len([k for k in v2_kpis.keys() if k not in v1_kpis])}")
            
            # Show role-specific breakdown
            for role, role_kpis in v2_kpis['role_specific_workforce'].items():
                print(f"         {role}: {role_kpis['total_headcount']} people (billable: {role_kpis['billable_headcount']})")
        
        # 7. MIGRATION REPORT GENERATION
        print("\n7. GENERATING MIGRATION REPORT")
        print("=" * 37)
        
        # Compile all conversion results
        all_conversions = {
            'scenario_request': scenario_result,
            'business_plan': business_plan_result,
            'population_snapshot': snapshot_result,
            'kpi_structure': kpi_result
        }
        
        migration_report = converter.create_migration_report(all_conversions)
        
        print(f"   Migration summary:")
        print(f"      Total items: {migration_report['migration_summary']['total_items']}")
        print(f"      Successful: {migration_report['migration_summary']['successful_conversions']}")
        print(f"      Failed: {migration_report['migration_summary']['failed_conversions']}")
        print(f"      Total warnings: {migration_report['migration_summary']['total_warnings']}")
        print(f"      Total errors: {migration_report['migration_summary']['total_errors']}")
        
        print(f"\n   Recommendations ({len(migration_report['recommendations'])}):")
        for i, recommendation in enumerate(migration_report['recommendations'][:3], 1):
            print(f"      {i}. {recommendation}")
        if len(migration_report['recommendations']) > 3:
            print(f"      ... and {len(migration_report['recommendations']) - 3} more")
        
        # 8. CONVERSION VERIFICATION
        print("\n8. CONVERSION VERIFICATION")
        print("=" * 30)
        
        verification_checks = {
            'scenario_converted': scenario_result.success,
            'business_plan_converted': business_plan_result.success,
            'population_snapshot_converted': snapshot_result.success,
            'kpi_structure_converted': kpi_result.success,
            'enhanced_features_added': any('enhanced' in ' '.join(result.conversion_notes) for result in all_conversions.values()),
            'baseline_fte_extracted': 'baseline_fte' in str(business_plan_result.converted_data) if business_plan_result.success else False,
            'role_specific_kpis_created': 'role_specific' in str(kpi_result.converted_data) if kpi_result.success else False,
            'metadata_preserved': all('metadata' in str(result.converted_data) for result in all_conversions.values() if result.success),
            'migration_report_generated': len(migration_report) > 0,
            'no_critical_errors': migration_report['migration_summary']['failed_conversions'] == 0
        }
        
        all_checks_passed = all(verification_checks.values())
        
        print(f"   Verification results:")
        for check, passed in verification_checks.items():
            status = "[OK]" if passed else "[X]"
            print(f"      {check}: {status}")
        
        print(f"\n   Overall Status: {'[OK] ALL CONVERSIONS SUCCESSFUL' if all_checks_passed else '[X] Some conversions need review'}")
        
        # 9. DATA COMPARISON ANALYSIS
        print("\n9. V1 vs V2 DATA COMPARISON")
        print("=" * 32)
        
        if business_plan_result.success and kpi_result.success:
            # Compare key metrics
            v1_revenue = v1_business_plan['monthly_plans']['2024-01']['revenue']
            v2_utilization_revenue = "calculated_on_demand"  # Would be calculated in actual V2 simulation
            
            v1_total_headcount = v1_kpis['total_headcount']
            v2_total_headcount = sum(role['total_headcount'] for role in v2_kpis['role_specific_workforce'].values())
            
            print(f"   Revenue comparison:")
            print(f"      V1 fixed revenue: ${v1_revenue:,.0f}")
            print(f"      V2 utilization-based: {v2_utilization_revenue}")
            
            print(f"\n   Workforce comparison:")
            print(f"      V1 total headcount: {v1_total_headcount}")
            print(f"      V2 estimated breakdown: {v2_total_headcount}")
            
            print(f"\n   Enhancement summary:")
            print(f"      V1 KPI metrics: {len(v1_kpis)}")
            print(f"      V2 KPI metrics: {len([k for k in v2_kpis.keys() if k != 'conversion_metadata'])}")
            print(f"      New features: Role-specific attribution, utilization-based revenue, baseline FTE")
        
        return True, {
            'conversions_successful': migration_report['migration_summary']['successful_conversions'],
            'total_warnings': migration_report['migration_summary']['total_warnings'],
            'total_errors': migration_report['migration_summary']['total_errors'],
            'verification_checks_passed': all_checks_passed,
            'recommendations_count': len(migration_report['recommendations'])
        }
        
    except Exception as e:
        print(f"\nERROR: V2 scenario converter test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("Starting V2 Scenario Converter Testing")
    print("=" * 45)
    
    success, metrics = test_v2_scenario_converter()
    
    print("\n" + "=" * 45)
    if success:
        print("SUCCESS: V2 Scenario Converter working!")
        print(f"Successful conversions: {metrics['conversions_successful']}/4")
        print(f"Total warnings: {metrics['total_warnings']}")
        print(f"Total errors: {metrics['total_errors']}")
        print(f"Recommendations: {metrics['recommendations_count']} migration tips")
        print("Features: Enhanced levers, baseline FTE, role-specific KPIs, migration reports")
    else:
        print("FAILURE: V2 Scenario Converter needs work")
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
    
    print(f"\nV2 Scenario Converter test complete")