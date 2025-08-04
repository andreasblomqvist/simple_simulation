#!/usr/bin/env python3
"""
Test a 3-year positive growth scenario with detailed KPI output for each year.
"""
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def create_3_year_growth_scenario():
    """Create a 3-year positive growth scenario."""
    
    scenario = {
        "name": "3-Year Positive Growth Scenario",
        "description": "Strategic growth plan with increasing recruitment and controlled churn",
        "time_range": {
            "start_year": 2024,
            "start_month": 1,
            "end_year": 2026,
            "end_month": 12
        },
        "office_scope": ["Stockholm", "Munich", "Amsterdam"],
        "baseline_input": {
            "global": {
                "recruitment": {
                    "Consultant": {
                        "levels": {
                            # Year 1: Moderate growth
                            "A": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 8 for m in range(1, 13)},  # 8 per month
                                    **{f"2025{m:02d}": 12 for m in range(1, 13)}, # 12 per month
                                    **{f"2026{m:02d}": 15 for m in range(1, 13)}  # 15 per month
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 2 for m in range(1, 13)},  # 2 per month
                                    **{f"2025{m:02d}": 3 for m in range(1, 13)},  # 3 per month
                                    **{f"2026{m:02d}": 4 for m in range(1, 13)}   # 4 per month
                                }}
                            },
                            "AC": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 5 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 8 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 10 for m in range(1, 13)}
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 2 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 3 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 3 for m in range(1, 13)}
                                }}
                            },
                            "C": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 3 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 5 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 7 for m in range(1, 13)}
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 1 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 1 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 2 for m in range(1, 13)}
                                }}
                            },
                            "SrC": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 2 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 3 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 4 for m in range(1, 13)}
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 1 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 1 for m in range(1, 13)}
                                }}
                            },
                            "AM": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 1 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 2 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 3 for m in range(1, 13)}
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 1 for m in range(1, 13)}
                                }}
                            },
                            # Senior levels - minimal recruitment, low churn
                            "M": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 1 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 1 for m in range(1, 13)}
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 0 for m in range(1, 13)}
                                }}
                            },
                            "SrM": {
                                "recruitment": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}},
                                "churn": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}}
                            },
                            "Pi": {
                                "recruitment": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}},
                                "churn": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}}
                            },
                            "P": {
                                "recruitment": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}},
                                "churn": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}}
                            }
                        }
                    }
                },
                "churn": {
                    "Consultant": {
                        "levels": {
                            # Same structure as recruitment for churn baseline
                            "A": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 8 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 12 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 15 for m in range(1, 13)}
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 2 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 3 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 4 for m in range(1, 13)}
                                }}
                            },
                            "AC": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 5 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 8 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 10 for m in range(1, 13)}
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 2 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 3 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 3 for m in range(1, 13)}
                                }}
                            },
                            "C": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 3 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 5 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 7 for m in range(1, 13)}
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 1 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 1 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 2 for m in range(1, 13)}
                                }}
                            },
                            "SrC": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 2 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 3 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 4 for m in range(1, 13)}
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 1 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 1 for m in range(1, 13)}
                                }}
                            },
                            "AM": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 1 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 2 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 3 for m in range(1, 13)}
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 1 for m in range(1, 13)}
                                }}
                            },
                            "M": {
                                "recruitment": {"values": {
                                    **{f"2024{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 1 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 1 for m in range(1, 13)}
                                }},
                                "churn": {"values": {
                                    **{f"2024{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2025{m:02d}": 0 for m in range(1, 13)},
                                    **{f"2026{m:02d}": 0 for m in range(1, 13)}
                                }}
                            },
                            "SrM": {
                                "recruitment": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}},
                                "churn": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}}
                            },
                            "Pi": {
                                "recruitment": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}},
                                "churn": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}}
                            },
                            "P": {
                                "recruitment": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}},
                                "churn": {"values": {f"{year}{m:02d}": 0 for year in [2024, 2025, 2026] for m in range(1, 13)}}
                            }
                        }
                    }
                }
            }
        },
        "levers": {
            "recruitment": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
            "churn": {"A": 0.8, "AC": 0.8, "C": 0.7, "SrC": 0.6, "AM": 0.5, "M": 0.4, "SrM": 0.3, "Pi": 0.3, "P": 0.3},  # Reduced churn
            "progression": {"A": 1.2, "AC": 1.2, "C": 1.1, "SrC": 1.1, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0}  # Slight progression boost
        },
        "progression_config": None,
        "cat_curves": None
    }
    
    return scenario

def run_growth_scenario():
    """Run the 3-year growth scenario."""
    
    print("🚀 Running 3-Year Positive Growth Scenario")
    print("=" * 70)
    
    scenario = create_3_year_growth_scenario()
    payload = {"scenario_definition": scenario}
    
    print("📊 Scenario Parameters:")
    print(f"   Time Range: 2024-2026 (3 years)")
    print(f"   Offices: Stockholm, Munich, Amsterdam")
    print(f"   Growth Pattern: Increasing recruitment each year")
    print(f"   Churn Control: Reduced churn through levers")
    print(f"   Expected Net Growth: ~70-80 FTE per year")
    
    response = requests.post(f"{BASE_URL}/scenarios/run", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Simulation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    result = response.json()
    if result.get("status") != "success":
        print(f"❌ Simulation error: {result.get('error_message', 'Unknown error')}")
        return None
    
    print(f"✅ Simulation completed in {result.get('execution_time', 0):.2f}s")
    return result

def analyze_yearly_kpis(result: Dict[str, Any]):
    """Analyze and output detailed KPIs for each year."""
    
    if not result or not result.get("results"):
        print("❌ No results data found")
        return
    
    scenario_id = result.get("scenario_id")
    print(f"\n📋 Scenario ID: {scenario_id}")
    
    results_data = result["results"]
    
    if "years" not in results_data:
        print("❌ No years data found in results")
        return
    
    print(f"\n🎯 YEARLY KPI ANALYSIS")
    print("=" * 70)
    
    yearly_kpis = {}
    
    # Analyze each year
    for year in sorted(results_data["years"].keys()):
        year_data = results_data["years"][year]
        
        yearly_kpis[year] = {
            "total_fte": 0,
            "total_revenue": 0,
            "total_cost": 0,
            "total_recruitment": 0,
            "total_churn": 0,
            "total_progression": 0,
            "offices": {},
            "levels": {},
            "months_data": 12,
            "average_utr": 0,
            "utr_values": []
        }
        
        # Analyze each office
        for office_name, office_data in year_data.get("offices", {}).items():
            yearly_kpis[year]["offices"][office_name] = {
                "fte": 0, "revenue": 0, "cost": 0, "recruitment": 0, "churn": 0, "progression": 0
            }
            
            # Analyze each role and level
            for role_name, role_data in office_data.get("levels", {}).items():
                for level_name, level_monthly_data in role_data.items():
                    if level_name not in yearly_kpis[year]["levels"]:
                        yearly_kpis[year]["levels"][level_name] = {
                            "fte": 0, "revenue": 0, "cost": 0, "recruitment": 0, "churn": 0, "progression": 0
                        }
                    
                    if isinstance(level_monthly_data, list):
                        for month_data in level_monthly_data:
                            if isinstance(month_data, dict):
                                fte = month_data.get("fte", 0)
                                price = month_data.get("price", 0)
                                salary = month_data.get("salary", 0)
                                recruitment = month_data.get("recruitment", 0)
                                churn = month_data.get("churn", 0)
                                progression = month_data.get("promoted_people", 0)
                                utr = month_data.get("utr", 0)
                                
                                monthly_revenue = fte * price
                                monthly_cost = fte * salary
                                
                                # Accumulate yearly totals
                                yearly_kpis[year]["total_fte"] += fte
                                yearly_kpis[year]["total_revenue"] += monthly_revenue
                                yearly_kpis[year]["total_cost"] += monthly_cost
                                yearly_kpis[year]["total_recruitment"] += recruitment
                                yearly_kpis[year]["total_churn"] += churn
                                yearly_kpis[year]["total_progression"] += progression
                                
                                if utr > 0:
                                    yearly_kpis[year]["utr_values"].append(utr)
                                
                                # Accumulate office totals
                                yearly_kpis[year]["offices"][office_name]["fte"] += fte
                                yearly_kpis[year]["offices"][office_name]["revenue"] += monthly_revenue
                                yearly_kpis[year]["offices"][office_name]["cost"] += monthly_cost
                                yearly_kpis[year]["offices"][office_name]["recruitment"] += recruitment
                                yearly_kpis[year]["offices"][office_name]["churn"] += churn
                                yearly_kpis[year]["offices"][office_name]["progression"] += progression
                                
                                # Accumulate level totals
                                yearly_kpis[year]["levels"][level_name]["fte"] += fte
                                yearly_kpis[year]["levels"][level_name]["revenue"] += monthly_revenue
                                yearly_kpis[year]["levels"][level_name]["cost"] += monthly_cost
                                yearly_kpis[year]["levels"][level_name]["recruitment"] += recruitment
                                yearly_kpis[year]["levels"][level_name]["churn"] += churn
                                yearly_kpis[year]["levels"][level_name]["progression"] += progression
        
        # Calculate averages
        if yearly_kpis[year]["utr_values"]:
            yearly_kpis[year]["average_utr"] = sum(yearly_kpis[year]["utr_values"]) / len(yearly_kpis[year]["utr_values"])
    
    # Output detailed yearly analysis
    for year in sorted(yearly_kpis.keys()):
        kpis = yearly_kpis[year]
        
        print(f"\n📅 YEAR {year} DETAILED KPIs")
        print("-" * 50)
        
        # Overall metrics
        total_profit = kpis["total_revenue"] - kpis["total_cost"]
        profit_margin = (total_profit / kpis["total_revenue"]) * 100 if kpis["total_revenue"] > 0 else 0
        net_growth = kpis["total_recruitment"] - kpis["total_churn"]
        
        print(f"📊 Overall Performance:")
        print(f"   Total FTE: {kpis['total_fte']:,.0f}")
        print(f"   Total Revenue: ${kpis['total_revenue']:,.0f}")
        print(f"   Total Cost: ${kpis['total_cost']:,.0f}")
        print(f"   Total Profit: ${total_profit:,.0f}")
        print(f"   Profit Margin: {profit_margin:.1f}%")
        print(f"   Average UTR: {kpis['average_utr']:.2f}")
        
        print(f"\n🔄 Growth Metrics:")
        print(f"   Total Recruitment: {kpis['total_recruitment']:,}")
        print(f"   Total Churn: {kpis['total_churn']:,}")
        print(f"   Net Growth: {net_growth:,}")
        print(f"   Total Progression: {kpis['total_progression']:,}")
        
        # Business KPIs
        if kpis["total_fte"] > 0:
            revenue_per_fte = kpis["total_revenue"] / kpis["total_fte"]
            cost_per_fte = kpis["total_cost"] / kpis["total_fte"]
            print(f"\n💼 Business KPIs:")
            print(f"   Revenue per FTE: ${revenue_per_fte:,.0f}")
            print(f"   Cost per FTE: ${cost_per_fte:,.0f}")
            
            if kpis["total_recruitment"] > 0:
                cost_per_hire = (kpis["total_cost"] * 0.05) / kpis["total_recruitment"]  # 5% of cost for recruitment
                print(f"   Cost per hire (est.): ${cost_per_hire:,.0f}")
            
            if kpis["total_churn"] > 0:
                churn_rate = (kpis["total_churn"] / kpis["total_fte"]) * 100
                print(f"   Annual churn rate: {churn_rate:.1f}%")
        
        # Office breakdown
        print(f"\n🏢 Office Performance:")
        for office_name, office_kpis in kpis["offices"].items():
            office_profit = office_kpis["revenue"] - office_kpis["cost"]
            office_margin = (office_profit / office_kpis["revenue"]) * 100 if office_kpis["revenue"] > 0 else 0
            office_net_growth = office_kpis["recruitment"] - office_kpis["churn"]
            
            print(f"   {office_name}:")
            print(f"      FTE: {office_kpis['fte']:,.0f} | Revenue: ${office_kpis['revenue']:,.0f} | Profit: ${office_profit:,.0f} ({office_margin:.1f}%)")
            print(f"      Recruitment: {office_kpis['recruitment']:,} | Churn: {office_kpis['churn']:,} | Net: {office_net_growth:+,}")
        
        # Level breakdown (top 5 by FTE)
        print(f"\n📊 Level Performance (Top 5 by FTE):")
        sorted_levels = sorted(kpis["levels"].items(), key=lambda x: x[1]["fte"], reverse=True)
        for level_name, level_kpis in sorted_levels[:5]:
            level_profit = level_kpis["revenue"] - level_kpis["cost"]
            level_net_growth = level_kpis["recruitment"] - level_kpis["churn"]
            
            print(f"   {level_name}:")
            print(f"      FTE: {level_kpis['fte']:,.0f} | Revenue: ${level_kpis['revenue']:,.0f} | Profit: ${level_profit:,.0f}")
            print(f"      Recruitment: {level_kpis['recruitment']:,} | Churn: {level_kpis['churn']:,} | Net: {level_net_growth:+,}")
    
    # Year-over-year comparison
    print(f"\n📈 YEAR-OVER-YEAR GROWTH ANALYSIS")
    print("=" * 70)
    
    years_list = sorted(yearly_kpis.keys())
    for i in range(1, len(years_list)):
        current_year = years_list[i]
        previous_year = years_list[i-1]
        
        current = yearly_kpis[current_year]
        previous = yearly_kpis[previous_year]
        
        # Calculate growth rates
        fte_growth = ((current["total_fte"] - previous["total_fte"]) / previous["total_fte"]) * 100 if previous["total_fte"] > 0 else 0
        revenue_growth = ((current["total_revenue"] - previous["total_revenue"]) / previous["total_revenue"]) * 100 if previous["total_revenue"] > 0 else 0
        recruitment_growth = ((current["total_recruitment"] - previous["total_recruitment"]) / previous["total_recruitment"]) * 100 if previous["total_recruitment"] > 0 else 0
        
        print(f"\n{previous_year} → {current_year} Growth:")
        print(f"   FTE Growth: {fte_growth:+.1f}% ({previous['total_fte']:,.0f} → {current['total_fte']:,.0f})")
        print(f"   Revenue Growth: {revenue_growth:+.1f}% (${previous['total_revenue']:,.0f} → ${current['total_revenue']:,.0f})")
        print(f"   Recruitment Growth: {recruitment_growth:+.1f}% ({previous['total_recruitment']:,} → {current['total_recruitment']:,})")
    
    # 3-year summary
    first_year = years_list[0]
    last_year = years_list[-1]
    first_kpis = yearly_kpis[first_year]
    last_kpis = yearly_kpis[last_year]
    
    total_fte_growth = ((last_kpis["total_fte"] - first_kpis["total_fte"]) / first_kpis["total_fte"]) * 100 if first_kpis["total_fte"] > 0 else 0
    total_revenue_growth = ((last_kpis["total_revenue"] - first_kpis["total_revenue"]) / first_kpis["total_revenue"]) * 100 if first_kpis["total_revenue"] > 0 else 0
    
    print(f"\n🎯 3-YEAR SUMMARY ({first_year}-{last_year})")
    print("=" * 70)
    print(f"📊 Total Growth:")
    print(f"   FTE: {first_kpis['total_fte']:,.0f} → {last_kpis['total_fte']:,.0f} ({total_fte_growth:+.1f}%)")
    print(f"   Revenue: ${first_kpis['total_revenue']:,.0f} → ${last_kpis['total_revenue']:,.0f} ({total_revenue_growth:+.1f}%)")
    print(f"   Net Recruitment: {sum(yearly_kpis[year]['total_recruitment'] for year in years_list):,}")
    print(f"   Net Churn: {sum(yearly_kpis[year]['total_churn'] for year in years_list):,}")
    print(f"   Total Net Growth: {sum(yearly_kpis[year]['total_recruitment'] - yearly_kpis[year]['total_churn'] for year in years_list):,}")

def main():
    """Run the 3-year growth scenario test."""
    
    result = run_growth_scenario()
    if result:
        analyze_yearly_kpis(result)
    else:
        print("❌ Failed to run growth scenario")

if __name__ == "__main__":
    main()