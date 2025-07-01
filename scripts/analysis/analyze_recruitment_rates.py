#!/usr/bin/env python3
"""
Deep Analysis of Recruitment and Churn Rates
Analyze why FTE is declining despite high recruitment rates
"""

import json
from collections import defaultdict

def analyze_recruitment_churn_rates():
    """Deep analysis of recruitment vs churn rates"""
    
    print("🔍 DEEP ANALYSIS: Recruitment vs Churn Rates")
    print("=" * 60)
    
    # Load configuration
    with open('backend/config/office_configuration.json', 'r') as f:
        config = json.load(f)
    
    # Analysis containers
    level_analysis = defaultdict(lambda: {
        'total_fte': 0,
        'total_recruitment': 0.0,
        'total_churn': 0.0,
        'offices': 0,
        'net_growth_rate': 0.0
    })
    
    office_analysis = {}
    
    # Analyze each office
    for office_name, office_data in config.items():
        print(f"\n📊 {office_name}:")
        print(f"   Total FTE: {office_data.get('total_fte', 0)}")
        
        office_total_fte = 0
        office_total_recruitment = 0.0
        office_total_churn = 0.0
        
        roles = office_data.get('roles', {})
        
        for role_name, role_data in roles.items():
            if isinstance(role_data, dict):
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, dict) and 'fte' in level_data:
                        fte = level_data.get('fte', 0)
                        recruitment = level_data.get('recruitment_1', 0.0)
                        churn = level_data.get('churn_1', 0.0)
                        
                        net_growth = recruitment - churn
                        annual_recruitment = recruitment * 12
                        annual_churn = churn * 12
                        annual_net = net_growth * 12
                        
                        print(f"   {role_name} {level_name}: {fte} FTE")
                        print(f"     Monthly: Rec={recruitment:.3f}, Churn={churn:.3f}, Net={net_growth:.3f}")
                        print(f"     Annual:  Rec={annual_recruitment:.1f}%, Churn={annual_churn:.1f}%, Net={annual_net:.1f}%")
                        
                        # Aggregate by level
                        level_key = f"{role_name}_{level_name}"
                        level_analysis[level_key]['total_fte'] += fte
                        level_analysis[level_key]['total_recruitment'] += recruitment * fte
                        level_analysis[level_key]['total_churn'] += churn * fte
                        level_analysis[level_key]['offices'] += 1
                        
                        office_total_fte += fte
                        office_total_recruitment += recruitment * fte
                        office_total_churn += churn * fte
        
        # Calculate office-level averages
        if office_total_fte > 0:
            avg_recruitment = office_total_recruitment / office_total_fte
            avg_churn = office_total_churn / office_total_fte
            net_growth = avg_recruitment - avg_churn
            
            office_analysis[office_name] = {
                'total_fte': office_total_fte,
                'avg_recruitment': avg_recruitment,
                'avg_churn': avg_churn,
                'net_growth': net_growth,
                'annual_net_growth': net_growth * 12
            }
            
            print(f"   📈 Office Summary:")
            print(f"     Avg Monthly: Rec={avg_recruitment:.3f}, Churn={avg_churn:.3f}, Net={net_growth:.3f}")
            print(f"     Annual Net Growth: {net_growth * 12:.1f}%")
    
    # Level-by-level analysis
    print(f"\n" + "=" * 60)
    print("📊 LEVEL-BY-LEVEL ANALYSIS")
    print("=" * 60)
    
    for level_key, data in level_analysis.items():
        if data['total_fte'] > 0:
            avg_recruitment = data['total_recruitment'] / data['total_fte']
            avg_churn = data['total_churn'] / data['total_fte']
            net_growth = avg_recruitment - avg_churn
            
            print(f"\n{level_key}:")
            print(f"  Total FTE: {data['total_fte']} across {data['offices']} offices")
            print(f"  Monthly: Rec={avg_recruitment:.3f}, Churn={avg_churn:.3f}, Net={net_growth:.3f}")
            print(f"  Annual:  Rec={avg_recruitment * 12:.1f}%, Churn={avg_churn * 12:.1f}%, Net={net_growth * 12:.1f}%")
            
            if net_growth < 0:
                print(f"  ⚠️  NEGATIVE GROWTH - This level is declining!")
            elif net_growth > 0.02:  # >2% monthly
                print(f"  🚀 HIGH GROWTH - This level is growing rapidly!")
    
    # Overall system analysis
    print(f"\n" + "=" * 60)
    print("🌍 OVERALL SYSTEM ANALYSIS")
    print("=" * 60)
    
    total_system_fte = sum(office['total_fte'] for office in office_analysis.values())
    total_system_recruitment = sum(office['avg_recruitment'] * office['total_fte'] for office in office_analysis.values())
    total_system_churn = sum(office['avg_churn'] * office['total_fte'] for office in office_analysis.values())
    
    if total_system_fte > 0:
        system_avg_recruitment = total_system_recruitment / total_system_fte
        system_avg_churn = total_system_churn / total_system_fte
        system_net_growth = system_avg_recruitment - system_avg_churn
        
        print(f"Total System FTE: {total_system_fte}")
        print(f"System Average Monthly:")
        print(f"  Recruitment: {system_avg_recruitment:.3f} ({system_avg_recruitment * 12:.1f}% annually)")
        print(f"  Churn:       {system_avg_churn:.3f} ({system_avg_churn * 12:.1f}% annually)")
        print(f"  Net Growth:  {system_net_growth:.3f} ({system_net_growth * 12:.1f}% annually)")
        
        if system_net_growth > 0:
            print(f"✅ System should be GROWING by {system_net_growth * 12:.1f}% annually")
        else:
            print(f"❌ System is DECLINING by {abs(system_net_growth * 12):.1f}% annually")
    
    # Check for potential issues
    print(f"\n" + "=" * 60)
    print("🔍 POTENTIAL ISSUES TO INVESTIGATE")
    print("=" * 60)
    
    print("1. Check if simulation is using the correct configuration")
    print("2. Verify baseline FTE calculation in KPI service")
    print("3. Check if progression is working correctly")
    print("4. Verify recruitment logic in simulation engine")
    print("5. Check if there are any initialization issues")
    
    return {
        'office_analysis': office_analysis,
        'level_analysis': dict(level_analysis),
        'system_totals': {
            'total_fte': total_system_fte,
            'avg_recruitment': system_avg_recruitment if total_system_fte > 0 else 0,
            'avg_churn': system_avg_churn if total_system_fte > 0 else 0,
            'net_growth': system_net_growth if total_system_fte > 0 else 0
        }
    }

if __name__ == "__main__":
    analyze_recruitment_churn_rates() 