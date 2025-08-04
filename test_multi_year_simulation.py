#!/usr/bin/env python3
"""
Test script to run a multi-year simulation with comprehensive recruitment/churn values
for multiple levels to verify the system works correctly.
"""

import requests
import json
import sys

def run_multi_year_simulation():
    """Run a simulation with multiple years and comprehensive level data."""
    
    # Create a comprehensive scenario definition
    scenario_definition = {
        "name": "Multi-Year Test with Multiple Levels",
        "description": "Test simulation with 2025-2027 and comprehensive recruitment/churn for all levels",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2027,
            "end_month": 12
        },
        "office_scope": ["Stockholm", "Munich", "Hamburg"],
        "levers": {},
        "baseline_input": {
            "global": {
                "recruitment": {
                    "Consultant": {
                        "levels": {
                            "A": {
                                "recruitment": {
                                    "values": {
                                        "202501": 15.0, "202502": 12.0, "202503": 18.0,
                                        "202504": 14.0, "202505": 16.0, "202506": 13.0,
                                        "202507": 17.0, "202508": 15.0, "202509": 14.0,
                                        "202510": 16.0, "202511": 13.0, "202512": 15.0,
                                        "202601": 20.0, "202602": 18.0, "202603": 22.0,
                                        "202604": 19.0, "202605": 21.0, "202606": 17.0,
                                        "202607": 23.0, "202608": 20.0, "202609": 18.0,
                                        "202610": 22.0, "202611": 19.0, "202612": 21.0,
                                        "202701": 25.0, "202702": 23.0, "202703": 27.0,
                                        "202704": 24.0, "202705": 26.0, "202706": 22.0,
                                        "202707": 28.0, "202708": 25.0, "202709": 23.0,
                                        "202710": 27.0, "202711": 24.0, "202712": 26.0
                                    }
                                },
                                "churn": {
                                    "values": {
                                        "202501": 2.0, "202502": 1.5, "202503": 2.5,
                                        "202504": 2.0, "202505": 1.8, "202506": 2.2,
                                        "202507": 2.3, "202508": 1.9, "202509": 2.1,
                                        "202510": 2.0, "202511": 1.7, "202512": 2.4,
                                        "202601": 3.0, "202602": 2.5, "202603": 3.5,
                                        "202604": 3.0, "202605": 2.8, "202606": 3.2,
                                        "202607": 3.3, "202608": 2.9, "202609": 3.1,
                                        "202610": 3.0, "202611": 2.7, "202612": 3.4,
                                        "202701": 4.0, "202702": 3.5, "202703": 4.5,
                                        "202704": 4.0, "202705": 3.8, "202706": 4.2,
                                        "202707": 4.3, "202708": 3.9, "202709": 4.1,
                                        "202710": 4.0, "202711": 3.7, "202712": 4.4
                                    }
                                }
                            },
                            "AC": {
                                "recruitment": {
                                    "values": {
                                        "202501": 8.0, "202502": 6.0, "202503": 10.0,
                                        "202504": 7.0, "202505": 9.0, "202506": 6.5,
                                        "202507": 10.5, "202508": 8.0, "202509": 7.5,
                                        "202510": 9.5, "202511": 7.0, "202512": 8.5,
                                        "202601": 12.0, "202602": 10.0, "202603": 14.0,
                                        "202604": 11.0, "202605": 13.0, "202606": 10.5,
                                        "202607": 14.5, "202608": 12.0, "202609": 11.5,
                                        "202610": 13.5, "202611": 11.0, "202612": 12.5,
                                        "202701": 16.0, "202702": 14.0, "202703": 18.0,
                                        "202704": 15.0, "202705": 17.0, "202706": 14.5,
                                        "202707": 18.5, "202708": 16.0, "202709": 15.5,
                                        "202710": 17.5, "202711": 15.0, "202712": 16.5
                                    }
                                },
                                "churn": {
                                    "values": {
                                        "202501": 1.0, "202502": 0.8, "202503": 1.2,
                                        "202504": 1.0, "202505": 0.9, "202506": 1.1,
                                        "202507": 1.15, "202508": 0.95, "202509": 1.05,
                                        "202510": 1.0, "202511": 0.85, "202512": 1.2,
                                        "202601": 1.5, "202602": 1.25, "202603": 1.75,
                                        "202604": 1.5, "202605": 1.4, "202606": 1.6,
                                        "202607": 1.65, "202608": 1.45, "202609": 1.55,
                                        "202610": 1.5, "202611": 1.35, "202612": 1.7,
                                        "202701": 2.0, "202702": 1.75, "202703": 2.25,
                                        "202704": 2.0, "202705": 1.9, "202706": 2.1,
                                        "202707": 2.15, "202708": 1.95, "202709": 2.05,
                                        "202710": 2.0, "202711": 1.85, "202712": 2.2
                                    }
                                }
                            },
                            "C": {
                                "recruitment": {
                                    "values": {
                                        "202501": 5.0, "202502": 4.0, "202503": 6.0,
                                        "202504": 4.5, "202505": 5.5, "202506": 4.2,
                                        "202507": 6.2, "202508": 5.0, "202509": 4.8,
                                        "202510": 5.8, "202511": 4.5, "202512": 5.2,
                                        "202601": 7.0, "202602": 6.0, "202603": 8.0,
                                        "202604": 6.5, "202605": 7.5, "202606": 6.2,
                                        "202607": 8.2, "202608": 7.0, "202609": 6.8,
                                        "202610": 7.8, "202611": 6.5, "202612": 7.2,
                                        "202701": 9.0, "202702": 8.0, "202703": 10.0,
                                        "202704": 8.5, "202705": 9.5, "202706": 8.2,
                                        "202707": 10.2, "202708": 9.0, "202709": 8.8,
                                        "202710": 9.8, "202711": 8.5, "202712": 9.2
                                    }
                                },
                                "churn": {
                                    "values": {
                                        "202501": 0.8, "202502": 0.6, "202503": 1.0,
                                        "202504": 0.8, "202505": 0.7, "202506": 0.9,
                                        "202507": 0.95, "202508": 0.75, "202509": 0.85,
                                        "202510": 0.8, "202511": 0.65, "202512": 1.0,
                                        "202601": 1.2, "202602": 1.0, "202603": 1.4,
                                        "202604": 1.2, "202605": 1.1, "202606": 1.3,
                                        "202607": 1.35, "202608": 1.15, "202609": 1.25,
                                        "202610": 1.2, "202611": 1.05, "202612": 1.4,
                                        "202701": 1.6, "202702": 1.4, "202703": 1.8,
                                        "202704": 1.6, "202705": 1.5, "202706": 1.7,
                                        "202707": 1.75, "202708": 1.55, "202709": 1.65,
                                        "202710": 1.6, "202711": 1.45, "202712": 1.8
                                    }
                                }
                            },
                            "SrC": {
                                "recruitment": {
                                    "values": {
                                        "202501": 2.0, "202502": 1.5, "202503": 2.5,
                                        "202504": 2.0, "202505": 1.8, "202506": 2.2,
                                        "202507": 2.3, "202508": 1.9, "202509": 2.1,
                                        "202510": 2.0, "202511": 1.7, "202512": 2.4,
                                        "202601": 3.0, "202602": 2.5, "202603": 3.5,
                                        "202604": 3.0, "202605": 2.8, "202606": 3.2,
                                        "202607": 3.3, "202608": 2.9, "202609": 3.1,
                                        "202610": 3.0, "202611": 2.7, "202612": 3.4,
                                        "202701": 4.0, "202702": 3.5, "202703": 4.5,
                                        "202704": 4.0, "202705": 3.8, "202706": 4.2,
                                        "202707": 4.3, "202708": 3.9, "202709": 4.1,
                                        "202710": 4.0, "202711": 3.7, "202712": 4.4
                                    }
                                },
                                "churn": {
                                    "values": {
                                        "202501": 0.5, "202502": 0.4, "202503": 0.6,
                                        "202504": 0.5, "202505": 0.45, "202506": 0.55,
                                        "202507": 0.58, "202508": 0.48, "202509": 0.52,
                                        "202510": 0.5, "202511": 0.43, "202512": 0.6,
                                        "202601": 0.75, "202602": 0.63, "202603": 0.88,
                                        "202604": 0.75, "202605": 0.7, "202606": 0.8,
                                        "202607": 0.83, "202608": 0.73, "202609": 0.78,
                                        "202610": 0.75, "202611": 0.68, "202612": 0.85,
                                        "202701": 1.0, "202702": 0.88, "202703": 1.13,
                                        "202704": 1.0, "202705": 0.95, "202706": 1.05,
                                        "202707": 1.08, "202708": 0.98, "202709": 1.03,
                                        "202710": 1.0, "202711": 0.93, "202712": 1.1
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "economic_params": {
            "salary_inflation": 0.03,
            "price_inflation": 0.02,
            "utr_target": 0.85
        }
    }

    print("🚀 Running multi-year simulation with comprehensive level data...")
    print(f"📅 Time range: {scenario_definition['time_range']['start_year']}-{scenario_definition['time_range']['end_year']}")
    print(f"🏢 Offices: {', '.join(scenario_definition['office_scope'])}")
    print(f"👥 Levels with recruitment/churn: {list(scenario_definition['baseline_input']['global']['recruitment']['Consultant']['levels'].keys())}")
    
    try:
        # Submit the scenario
        response = requests.post(
            "http://localhost:8000/scenarios/run",
            json={"scenario_definition": scenario_definition}
        )
        
        if response.status_code == 200:
            result = response.json()
            scenario_id = result.get('scenario_id')
            print(f"✅ Simulation completed successfully!")
            print(f"🆔 Scenario ID: {scenario_id}")
            
            # Get the results
            results_response = requests.get(f"http://localhost:8000/scenarios/{scenario_id}/results")
            if results_response.status_code == 200:
                results = results_response.json()
                
                # Analyze the results
                years = results.get('results', {}).get('years', {})
                print(f"\n📊 Results Summary:")
                print(f"📅 Years available: {list(years.keys())}")
                
                for year in sorted(years.keys()):
                    year_data = years[year]
                    print(f"\n📈 {year}:")
                    
                    # Check KPIs
                    if 'kpis' in year_data:
                        kpis = year_data['kpis']
                        if 'financial' in kpis:
                            financial = kpis['financial']
                            print(f"  💰 Net Sales: SEK {financial.get('net_sales', 0):,.0f}")
                            print(f"  💵 EBITDA: SEK {financial.get('ebitda', 0):,.0f}")
                            print(f"  📊 Margin: {financial.get('margin', 0)*100:.1f}%")
                            print(f"  👥 Total Consultants: {financial.get('total_consultants', 0)}")
                    
                    # Check offices
                    if 'offices' in year_data:
                        offices = year_data['offices']
                        print(f"  🏢 Offices: {list(offices.keys())}")
                        
                        # Check first office for detailed data
                        first_office = list(offices.keys())[0] if offices else None
                        if first_office:
                            office_data = offices[first_office]
                            print(f"  📋 {first_office} FTE: {office_data.get('total_fte', 0)}")
                            
                            # Check roles and levels
                            if 'roles' in office_data:
                                roles = office_data['roles']
                                for role_name, role_data in roles.items():
                                    if 'levels' in role_data:
                                        levels = role_data['levels']
                                        for level_name, level_data in levels.items():
                                            if 'monthly_data' in level_data:
                                                monthly_data = level_data['monthly_data']
                                                if monthly_data:
                                                    # Sum recruitment and churn for the year
                                                    total_recruitment = sum(month.get('recruitment', 0) for month in monthly_data)
                                                    total_churn = sum(month.get('churn', 0) for month in monthly_data)
                                                    avg_fte = sum(month.get('fte', 0) for month in monthly_data) / len(monthly_data)
                                                    print(f"    👤 {role_name}.{level_name}: FTE={avg_fte:.1f}, Recruitment={total_recruitment}, Churn={total_churn}")
                
                print(f"\n🌐 Frontend URL: http://localhost:3001/scenarios/{scenario_id}")
                return scenario_id
            else:
                print(f"❌ Failed to get results: {results_response.status_code}")
                return None
        else:
            print(f"❌ Simulation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error running simulation: {e}")
        return None

if __name__ == "__main__":
    scenario_id = run_multi_year_simulation()
    if scenario_id:
        print(f"\n✅ Test completed successfully! Scenario ID: {scenario_id}")
    else:
        print("\n❌ Test failed!")
        sys.exit(1) 