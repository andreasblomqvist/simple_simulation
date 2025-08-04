#!/usr/bin/env python3
"""
Comprehensive simulation engine testing script.
Tests recruitment, churn, progression, and KPIs across multiple years, roles, and offices.
"""
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"

def create_test_scenario(name: str, start_year: int, end_year: int, offices: List[str], 
                        recruitment_levels: Dict[str, int], churn_levels: Dict[str, int],
                        levers: Dict[str, Dict[str, float]] = None) -> Dict[str, Any]:
    """Create a test scenario with specific parameters."""
    
    if levers is None:
        levers = {
            "recruitment": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
            "churn": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
            "progression": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0}
        }
    
    # Create monthly baseline data structure
    months = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            months.append(f"{year}{month:02d}")
    
    # Build the baseline input structure
    levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P']
    
    consultantLevels = {}
    for level in levels:
        # Create monthly values
        monthly_values = {}
        for month in months:
            monthly_values[month] = recruitment_levels.get(level, 0) if level in recruitment_levels else 0
        
        consultantLevels[level] = {
            "recruitment": {"values": monthly_values},
            "churn": {"values": {month: churn_levels.get(level, 0) for month in months}}
        }
    
    baseline_input = {
        "global": {
            "recruitment": {
                "Consultant": {
                    "levels": consultantLevels
                }
            },
            "churn": {
                "Consultant": {
                    "levels": consultantLevels
                }
            }
        }
    }
    
    return {
        "name": name,
        "description": f"Test scenario: {name}",
        "time_range": {
            "start_year": start_year,
            "start_month": 1,
            "end_year": end_year,
            "end_month": 12
        },
        "office_scope": offices,
        "baseline_input": baseline_input,
        "levers": levers,
        "progression_config": None,
        "cat_curves": None
    }

def run_simulation(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Run a simulation and return the results."""
    payload = {"scenario_definition": scenario}
    
    print(f"🔄 Running simulation: {scenario['name']}")
    print(f"   Time range: {scenario['time_range']['start_year']}-{scenario['time_range']['end_year']}")
    print(f"   Offices: {', '.join(scenario['office_scope'])}")
    
    response = requests.post(f"{BASE_URL}/scenarios/run", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Simulation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None
    
    result = response.json()
    if result.get("status") != "success":
        print(f"❌ Simulation error: {result.get('error_message', 'Unknown error')}")
        return None
    
    print(f"✅ Simulation completed in {result.get('execution_time', 0):.2f}s")
    return result

def analyze_results(result: Dict[str, Any], scenario_name: str) -> Dict[str, Any]:
    """Analyze simulation results and validate numbers."""
    
    print(f"\n📊 Analyzing results for: {scenario_name}")
    
    if not result or not result.get("results"):
        print("❌ No results data found")
        return {"valid": False, "errors": ["No results data"]}
    
    results_data = result["results"]
    analysis = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "summary": {
            "total_recruitment": 0,
            "total_churn": 0,
            "total_progression": 0,
            "years_analyzed": 0,
            "offices_analyzed": 0,
            "roles_analyzed": 0,
            "levels_analyzed": 0
        },
        "detailed_analysis": {}
    }
    
    # Navigate through the results structure
    if "years" in results_data:
        for year, year_data in results_data["years"].items():
            analysis["summary"]["years_analyzed"] += 1
            
            if "offices" in year_data:
                for office_name, office_data in year_data["offices"].items():
                    analysis["summary"]["offices_analyzed"] += 1
                    
                    if "roles" in office_data:
                        for role_name, role_data in office_data["roles"].items():
                            analysis["summary"]["roles_analyzed"] += 1
                            
                            if "levels" in role_data:
                                for level_name, level_data in role_data["levels"].items():
                                    analysis["summary"]["levels_analyzed"] += 1
                                    
                                    # Analyze monthly data
                                    if isinstance(level_data, list):
                                        for month_idx, month_data in enumerate(level_data):
                                            if isinstance(month_data, dict):
                                                recruitment = month_data.get("recruitment", 0)
                                                churn = month_data.get("churn", 0)
                                                progression = month_data.get("promoted_people", 0)
                                                
                                                analysis["summary"]["total_recruitment"] += recruitment
                                                analysis["summary"]["total_churn"] += churn
                                                analysis["summary"]["total_progression"] += progression
                                                
                                                # Validate numbers are logical
                                                if recruitment < 0:
                                                    analysis["errors"].append(f"Negative recruitment in {year}/{office_name}/{role_name}/{level_name}/month{month_idx+1}: {recruitment}")
                                                if churn < 0:
                                                    analysis["errors"].append(f"Negative churn in {year}/{office_name}/{role_name}/{level_name}/month{month_idx+1}: {churn}")
                                                if progression < 0:
                                                    analysis["errors"].append(f"Negative progression in {year}/{office_name}/{role_name}/{level_name}/month{month_idx+1}: {progression}")
    
    # Validate that we have meaningful numbers
    if analysis["summary"]["total_recruitment"] == 0:
        analysis["warnings"].append("Total recruitment is zero across all simulated periods")
    
    if analysis["summary"]["total_churn"] == 0:
        analysis["warnings"].append("Total churn is zero across all simulated periods")
    
    if analysis["summary"]["total_progression"] == 0:
        analysis["warnings"].append("Total progression is zero across all simulated periods")
    
    # Check if we have reasonable data structure
    if analysis["summary"]["years_analyzed"] == 0:
        analysis["errors"].append("No years found in results")
    
    if analysis["summary"]["offices_analyzed"] == 0:
        analysis["errors"].append("No offices found in results")
    
    if analysis["summary"]["roles_analyzed"] == 0:
        analysis["errors"].append("No roles found in results")
    
    if analysis["summary"]["levels_analyzed"] == 0:
        analysis["errors"].append("No levels found in results")
    
    # Set validity based on errors
    analysis["valid"] = len(analysis["errors"]) == 0
    
    # Print summary
    print(f"   📈 Summary:")
    print(f"      Years: {analysis['summary']['years_analyzed']}")
    print(f"      Offices: {analysis['summary']['offices_analyzed']}")
    print(f"      Roles: {analysis['summary']['roles_analyzed']}")
    print(f"      Levels: {analysis['summary']['levels_analyzed']}")
    print(f"      Total Recruitment: {analysis['summary']['total_recruitment']}")
    print(f"      Total Churn: {analysis['summary']['total_churn']}")
    print(f"      Total Progression: {analysis['summary']['total_progression']}")
    
    if analysis["errors"]:
        print(f"   ❌ Errors: {len(analysis['errors'])}")
        for error in analysis["errors"][:5]:  # Show first 5 errors
            print(f"      • {error}")
    
    if analysis["warnings"]:
        print(f"   ⚠️  Warnings: {len(analysis['warnings'])}")
        for warning in analysis["warnings"][:5]:  # Show first 5 warnings
            print(f"      • {warning}")
    
    return analysis

def main():
    """Run comprehensive simulation engine tests."""
    
    print("🚀 Starting comprehensive simulation engine testing")
    print("=" * 60)
    
    # Test scenarios
    test_scenarios = [
        # Test 1: Single year, single office, moderate recruitment/churn
        create_test_scenario(
            "Single Year - Stockholm Only",
            2024, 2024,
            ["Stockholm"],
            {"A": 10, "AC": 5, "C": 2, "SrC": 1, "AM": 1},
            {"A": 2, "AC": 3, "C": 1, "SrC": 0, "AM": 0}
        ),
        
        # Test 2: Multi-year, multiple offices, high recruitment
        create_test_scenario(
            "Multi-Year - High Growth",
            2024, 2026,
            ["Stockholm", "Munich", "Amsterdam"],
            {"A": 20, "AC": 10, "C": 5, "SrC": 2, "AM": 1, "M": 1},
            {"A": 5, "AC": 7, "C": 3, "SrC": 1, "AM": 1, "M": 0}
        ),
        
        # Test 3: Single year, all offices, balanced scenario
        create_test_scenario(
            "All Offices - Balanced",
            2024, 2024,
            ["Stockholm", "Munich", "Hamburg", "Helsinki", "Oslo", "Berlin", "Copenhagen", "Zurich", "Frankfurt", "Amsterdam", "Cologne", "Toronto"],
            {"A": 15, "AC": 8, "C": 4, "SrC": 2, "AM": 1, "M": 1, "SrM": 0, "Pi": 0, "P": 0},
            {"A": 3, "AC": 4, "C": 2, "SrC": 1, "AM": 1, "M": 0, "SrM": 0, "Pi": 0, "P": 0}
        ),
        
        # Test 4: Multi-year with leverage effects
        create_test_scenario(
            "Multi-Year with Levers",
            2024, 2025,
            ["Stockholm", "Munich"],
            {"A": 12, "AC": 6, "C": 3, "SrC": 1, "AM": 1},
            {"A": 2, "AC": 3, "C": 1, "SrC": 0, "AM": 0},
            {
                "recruitment": {"A": 1.5, "AC": 1.2, "C": 1.1, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
                "churn": {"A": 0.8, "AC": 0.9, "C": 0.9, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
                "progression": {"A": 1.2, "AC": 1.1, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0}
            }
        )
    ]
    
    # Run all test scenarios
    all_results = []
    for scenario in test_scenarios:
        print(f"\n{'='*40}")
        result = run_simulation(scenario)
        
        if result:
            analysis = analyze_results(result, scenario["name"])
            all_results.append({
                "scenario": scenario["name"],
                "result": result,
                "analysis": analysis
            })
        else:
            all_results.append({
                "scenario": scenario["name"],
                "result": None,
                "analysis": {"valid": False, "errors": ["Simulation failed"]}
            })
    
    # Final summary
    print(f"\n{'='*60}")
    print("🎯 FINAL SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results if r["analysis"]["valid"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    
    print(f"\n📋 Test Results:")
    for result in all_results:
        status = "✅ PASS" if result["analysis"]["valid"] else "❌ FAIL"
        print(f"  {status} {result['scenario']}")
        if not result["analysis"]["valid"]:
            for error in result["analysis"]["errors"][:3]:
                print(f"    • {error}")
    
    # Aggregate statistics
    total_recruitment = sum(r["analysis"]["summary"]["total_recruitment"] for r in all_results if r["analysis"]["valid"])
    total_churn = sum(r["analysis"]["summary"]["total_churn"] for r in all_results if r["analysis"]["valid"])
    total_progression = sum(r["analysis"]["summary"]["total_progression"] for r in all_results if r["analysis"]["valid"])
    
    print(f"\n📊 Aggregate Statistics (from valid tests):")
    print(f"  Total Recruitment: {total_recruitment}")
    print(f"  Total Churn: {total_churn}")
    print(f"  Total Progression: {total_progression}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 All tests passed! Simulation engine is working correctly.")
    else:
        print(f"\n⚠️  {failed_tests} tests failed. Please review the simulation engine.")
    
    return all_results

if __name__ == "__main__":
    main()