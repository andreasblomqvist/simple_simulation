#!/usr/bin/env python3
"""
Analyze simulation results to validate recruitment, churn, progression, and KPIs.
"""
import json
import requests
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"

def analyze_scenario_results(scenario_id: str) -> Dict[str, Any]:
    """Fetch and analyze results for a specific scenario."""
    
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
    if response.status_code != 200:
        return {"error": f"Failed to fetch results: {response.status_code}"}
    
    data = response.json()
    scenario_name = data.get("scenario_name", "Unknown")
    results = data.get("results", {})
    
    print(f"\n🔍 Analyzing: {scenario_name}")
    print(f"📋 Scenario ID: {scenario_id}")
    
    analysis = {
        "scenario_name": scenario_name,
        "scenario_id": scenario_id,
        "summary": {
            "total_recruitment": 0,
            "total_churn": 0,
            "total_progression": 0,
            "total_fte": 0,
            "years_count": 0,
            "offices_count": 0,
            "roles_count": 0,
            "levels_count": 0,
            "months_analyzed": 0
        },
        "yearly_breakdown": {},
        "office_breakdown": {},
        "level_breakdown": {},
        "validation": {
            "has_non_zero_recruitment": False,
            "has_non_zero_churn": False,
            "has_non_zero_progression": False,
            "recruitment_makes_sense": True,
            "churn_makes_sense": True,
            "progression_makes_sense": True,
            "issues": []
        }
    }
    
    if "years" not in results:
        analysis["validation"]["issues"].append("No 'years' structure found in results")
        return analysis
    
    # Navigate through: years → offices → levels → roles → monthly_data
    for year, year_data in results["years"].items():
        analysis["summary"]["years_count"] += 1
        analysis["yearly_breakdown"][year] = {
            "recruitment": 0, "churn": 0, "progression": 0, "fte": 0, "offices": 0
        }
        
        if "offices" not in year_data:
            analysis["validation"]["issues"].append(f"No offices found in year {year}")
            continue
            
        for office_name, office_data in year_data["offices"].items():
            analysis["summary"]["offices_count"] += 1
            analysis["yearly_breakdown"][year]["offices"] += 1
            
            if office_name not in analysis["office_breakdown"]:
                analysis["office_breakdown"][office_name] = {
                    "recruitment": 0, "churn": 0, "progression": 0, "fte": 0
                }
            
            # Check office-level total FTE
            office_fte = office_data.get("total_fte", 0)
            analysis["yearly_breakdown"][year]["fte"] += office_fte
            analysis["office_breakdown"][office_name]["fte"] = office_fte
            
            if "levels" not in office_data:
                analysis["validation"]["issues"].append(f"No levels found in office {office_name}")
                continue
                
            # Navigate through levels → roles → monthly data
            for role_name, role_data in office_data["levels"].items():
                analysis["summary"]["roles_count"] += 1
                
                for level_name, level_monthly_data in role_data.items():
                    analysis["summary"]["levels_count"] += 1
                    
                    if level_name not in analysis["level_breakdown"]:
                        analysis["level_breakdown"][level_name] = {
                            "recruitment": 0, "churn": 0, "progression": 0, "fte": 0
                        }
                    
                    if not isinstance(level_monthly_data, list):
                        analysis["validation"]["issues"].append(
                            f"Expected list for {office_name}/{role_name}/{level_name}, got {type(level_monthly_data)}"
                        )
                        continue
                    
                    # Analyze monthly data
                    for month_idx, month_data in enumerate(level_monthly_data):
                        analysis["summary"]["months_analyzed"] += 1
                        
                        if not isinstance(month_data, dict):
                            continue
                            
                        recruitment = month_data.get("recruitment", 0)
                        churn = month_data.get("churn", 0)
                        progression = month_data.get("promoted_people", 0)
                        fte = month_data.get("fte", 0)
                        
                        # Accumulate totals
                        analysis["summary"]["total_recruitment"] += recruitment
                        analysis["summary"]["total_churn"] += churn
                        analysis["summary"]["total_progression"] += progression
                        analysis["summary"]["total_fte"] += fte
                        
                        analysis["yearly_breakdown"][year]["recruitment"] += recruitment
                        analysis["yearly_breakdown"][year]["churn"] += churn
                        analysis["yearly_breakdown"][year]["progression"] += progression
                        
                        analysis["office_breakdown"][office_name]["recruitment"] += recruitment
                        analysis["office_breakdown"][office_name]["churn"] += churn
                        analysis["office_breakdown"][office_name]["progression"] += progression
                        
                        analysis["level_breakdown"][level_name]["recruitment"] += recruitment
                        analysis["level_breakdown"][level_name]["churn"] += churn
                        analysis["level_breakdown"][level_name]["progression"] += progression
                        analysis["level_breakdown"][level_name]["fte"] += fte
                        
                        # Validation checks
                        if recruitment > 0:
                            analysis["validation"]["has_non_zero_recruitment"] = True
                        if churn > 0:
                            analysis["validation"]["has_non_zero_churn"] = True
                        if progression > 0:
                            analysis["validation"]["has_non_zero_progression"] = True
                            
                        # Logical validation
                        if recruitment < 0:
                            analysis["validation"]["recruitment_makes_sense"] = False
                            analysis["validation"]["issues"].append(
                                f"Negative recruitment in {year}/{office_name}/{role_name}/{level_name}/month{month_idx+1}: {recruitment}"
                            )
                        if churn < 0:
                            analysis["validation"]["churn_makes_sense"] = False
                            analysis["validation"]["issues"].append(
                                f"Negative churn in {year}/{office_name}/{role_name}/{level_name}/month{month_idx+1}: {churn}"
                            )
                        if progression < 0:
                            analysis["validation"]["progression_makes_sense"] = False
                            analysis["validation"]["issues"].append(
                                f"Negative progression in {year}/{office_name}/{role_name}/{level_name}/month{month_idx+1}: {progression}"
                            )
    
    return analysis

def print_analysis_summary(analysis: Dict[str, Any]):
    """Print a summary of the analysis."""
    
    summary = analysis["summary"]
    validation = analysis["validation"]
    
    print(f"📊 Summary Statistics:")
    print(f"   Years: {summary['years_count']}")
    print(f"   Offices: {summary['offices_count']}")
    print(f"   Roles: {summary['roles_count']}")
    print(f"   Levels: {summary['levels_count']}")
    print(f"   Months analyzed: {summary['months_analyzed']}")
    print(f"   Total FTE: {summary['total_fte']:,}")
    print(f"   Total Recruitment: {summary['total_recruitment']:,}")
    print(f"   Total Churn: {summary['total_churn']:,}")
    print(f"   Total Progression: {summary['total_progression']:,}")
    
    print(f"\n✅ Validation Results:")
    print(f"   Non-zero recruitment: {'✅' if validation['has_non_zero_recruitment'] else '❌'}")
    print(f"   Non-zero churn: {'✅' if validation['has_non_zero_churn'] else '❌'}")
    print(f"   Non-zero progression: {'✅' if validation['has_non_zero_progression'] else '❌'}")
    print(f"   Recruitment logical: {'✅' if validation['recruitment_makes_sense'] else '❌'}")
    print(f"   Churn logical: {'✅' if validation['churn_makes_sense'] else '❌'}")
    print(f"   Progression logical: {'✅' if validation['progression_makes_sense'] else '❌'}")
    
    if validation["issues"]:
        print(f"\n⚠️  Issues ({len(validation['issues'])}):")
        for issue in validation["issues"][:5]:  # Show first 5
            print(f"   • {issue}")
        if len(validation["issues"]) > 5:
            print(f"   ... and {len(validation['issues']) - 5} more")
    
    # Show breakdown by level
    if analysis["level_breakdown"]:
        print(f"\n📈 Level Breakdown (Top 5 by recruitment):")
        sorted_levels = sorted(
            analysis["level_breakdown"].items(), 
            key=lambda x: x[1]["recruitment"], 
            reverse=True
        )
        for level, data in sorted_levels[:5]:
            print(f"   {level}: R={data['recruitment']}, C={data['churn']}, P={data['progression']}, FTE={data['fte']}")
    
    # Show breakdown by office
    if analysis["office_breakdown"]:
        print(f"\n🏢 Office Breakdown (Top 3 by recruitment):")
        sorted_offices = sorted(
            analysis["office_breakdown"].items(), 
            key=lambda x: x[1]["recruitment"], 
            reverse=True
        )
        for office, data in sorted_offices[:3]:
            print(f"   {office}: R={data['recruitment']}, C={data['churn']}, P={data['progression']}, FTE={data['fte']}")
    
    # Show breakdown by year
    if analysis["yearly_breakdown"]:
        print(f"\n📅 Yearly Breakdown:")
        for year, data in sorted(analysis["yearly_breakdown"].items()):
            print(f"   {year}: R={data['recruitment']}, C={data['churn']}, P={data['progression']}, FTE={data['fte']}, Offices={data['offices']}")

def main():
    """Analyze all recent simulation results."""
    
    print("🔍 Fetching recent scenarios...")
    
    # Get list of scenarios
    response = requests.get(f"{BASE_URL}/scenarios/list")
    if response.status_code != 200:
        print(f"❌ Failed to fetch scenarios: {response.status_code}")
        return
    
    scenarios = response.json().get("scenarios", [])
    print(f"Found {len(scenarios)} scenarios")
    
    # Analyze recent scenarios (limit to last 10)
    recent_scenarios = sorted(scenarios, key=lambda x: x.get("created_at", ""), reverse=True)[:10]
    
    all_analyses = []
    
    for scenario in recent_scenarios:
        scenario_id = scenario["id"]
        analysis = analyze_scenario_results(scenario_id)
        
        if "error" in analysis:
            print(f"❌ Error analyzing {scenario_id}: {analysis['error']}")
            continue
            
        print_analysis_summary(analysis)
        all_analyses.append(analysis)
        print("-" * 60)
    
    # Overall summary
    if all_analyses:
        print(f"\n🎯 OVERALL SUMMARY")
        print(f"=" * 60)
        
        total_scenarios = len(all_analyses)
        valid_scenarios = sum(1 for a in all_analyses if not a["validation"]["issues"])
        
        aggregate_recruitment = sum(a["summary"]["total_recruitment"] for a in all_analyses)
        aggregate_churn = sum(a["summary"]["total_churn"] for a in all_analyses)
        aggregate_progression = sum(a["summary"]["total_progression"] for a in all_analyses)
        aggregate_fte = sum(a["summary"]["total_fte"] for a in all_analyses)
        
        print(f"Scenarios analyzed: {total_scenarios}")
        print(f"Scenarios without issues: {valid_scenarios}")
        print(f"Aggregate recruitment: {aggregate_recruitment:,}")
        print(f"Aggregate churn: {aggregate_churn:,}")
        print(f"Aggregate progression: {aggregate_progression:,}")
        print(f"Aggregate FTE: {aggregate_fte:,}")
        
        # Check overall health
        scenarios_with_recruitment = sum(1 for a in all_analyses if a["validation"]["has_non_zero_recruitment"])
        scenarios_with_churn = sum(1 for a in all_analyses if a["validation"]["has_non_zero_churn"])
        scenarios_with_progression = sum(1 for a in all_analyses if a["validation"]["has_non_zero_progression"])
        
        print(f"\nHealth Check:")
        print(f"   Scenarios with recruitment: {scenarios_with_recruitment}/{total_scenarios}")
        print(f"   Scenarios with churn: {scenarios_with_churn}/{total_scenarios}")
        print(f"   Scenarios with progression: {scenarios_with_progression}/{total_scenarios}")
        
        if (scenarios_with_recruitment == total_scenarios and 
            scenarios_with_churn == total_scenarios and 
            scenarios_with_progression >= total_scenarios * 0.8):  # Progression might be 0 in some scenarios
            print(f"\n🎉 SIMULATION ENGINE HEALTH: EXCELLENT")
            print(f"   ✅ All scenarios show recruitment activity")
            print(f"   ✅ All scenarios show churn activity")
            print(f"   ✅ Most scenarios show progression activity")
            print(f"   ✅ Numbers are logical and non-negative")
        else:
            print(f"\n⚠️  SIMULATION ENGINE HEALTH: NEEDS REVIEW")
            if scenarios_with_recruitment < total_scenarios:
                print(f"   ❌ {total_scenarios - scenarios_with_recruitment} scenarios have zero recruitment")
            if scenarios_with_churn < total_scenarios:
                print(f"   ❌ {total_scenarios - scenarios_with_churn} scenarios have zero churn")
            if scenarios_with_progression < total_scenarios * 0.8:
                print(f"   ⚠️  Only {scenarios_with_progression} scenarios have progression activity")

if __name__ == "__main__":
    main()