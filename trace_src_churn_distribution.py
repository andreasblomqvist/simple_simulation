#!/usr/bin/env python3
"""
Trace how 7 SrC churn per month gets distributed across all offices.
"""
import json

def trace_src_churn_distribution():
    """Trace the exact distribution of 7 SrC churn per month."""
    
    print("🔍 TRACING SrC CHURN DISTRIBUTION: 7 people/month globally")
    print("=" * 80)
    
    # Load office configuration
    with open('backend/config/office_configuration.json', 'r') as f:
        config = json.load(f)
    
    # Calculate total SrC FTE across all offices
    office_src_ftes = {}
    total_src_fte = 0
    
    for office_name, office_config in config.items():
        src_fte = 0
        if ('roles' in office_config and 
            'Consultant' in office_config['roles'] and
            'SrC' in office_config['roles']['Consultant']):
            src_fte = office_config['roles']['Consultant']['SrC'].get('fte', 0)
        
        office_src_ftes[office_name] = src_fte
        total_src_fte += src_fte
    
    print(f"📊 SrC FTE by Office:")
    print("-" * 40)
    for office_name, src_fte in sorted(office_src_ftes.items()):
        print(f"{office_name:<12}: {src_fte:>3} SrC FTE")
    
    print("-" * 40)
    print(f"{'TOTAL':<12}: {total_src_fte:>3} SrC FTE")
    
    # Apply the exact distribution algorithm from scenario_resolver.py
    print(f"\n🧮 EXACT DISTRIBUTION ALGORITHM:")
    print("=" * 60)
    
    global_src_churn = 7  # 7 SrC churn per month
    
    print(f"Global SrC churn to distribute: {global_src_churn}")
    print(f"Total SrC FTE across all offices: {total_src_fte}")
    
    if total_src_fte == 0:
        print("❌ No SrC FTE found - cannot distribute")
        return
    
    # Step 1: Calculate proportional values and quotas
    print(f"\n📈 STEP 1: PROPORTIONAL CALCULATION")
    print("-" * 60)
    print(f"{'Office':<12} {'SrC FTE':<8} {'Weight':<8} {'Proportional':<12} {'Quota':<6} {'Remainder':<10}")
    print("-" * 60)
    
    office_quotas = {}
    office_remainders = {}
    total_distributed = 0
    
    for office_name, src_fte in sorted(office_src_ftes.items()):
        weight = src_fte / total_src_fte if total_src_fte > 0 else 0
        proportional_value = global_src_churn * weight
        quota = int(proportional_value)  # This is the truncation step!
        remainder = proportional_value - quota
        
        office_quotas[office_name] = quota
        office_remainders[office_name] = remainder
        total_distributed += quota
        
        print(f"{office_name:<12} {src_fte:<8} {weight:<8.4f} {proportional_value:<12.4f} {quota:<6} {remainder:<10.4f}")
    
    print("-" * 60)
    print(f"Total quota distributed: {total_distributed}")
    print(f"Remaining to distribute: {global_src_churn - total_distributed}")
    
    # Step 2: Largest remainder method
    print(f"\n📊 STEP 2: LARGEST REMAINDER METHOD")
    print("-" * 50)
    
    remaining_churn = global_src_churn - total_distributed
    
    # Sort offices by remainder (only those with SrC FTE > 0)
    sorted_offices = sorted(
        [(name, remainder) for name, remainder in office_remainders.items() 
         if office_src_ftes[name] > 0],
        key=lambda x: x[1], reverse=True
    )
    
    print(f"Offices sorted by remainder:")
    for i, (office_name, remainder) in enumerate(sorted_offices):
        print(f"  {i+1}. {office_name}: {remainder:.4f}")
    
    # Distribute remaining churn
    remaining_int = round(remaining_churn)
    print(f"\nDistributing {remaining_int} additional churn to top remainder offices:")
    
    final_distribution = office_quotas.copy()
    
    for i in range(remaining_int):
        if i < len(sorted_offices):
            office_name = sorted_offices[i][0]
            final_distribution[office_name] += 1
            print(f"  +1 to {office_name} (was {office_quotas[office_name]}, now {final_distribution[office_name]})")
    
    # Step 3: Final results
    print(f"\n📋 FINAL SrC CHURN DISTRIBUTION:")
    print("=" * 50)
    print(f"{'Office':<12} {'SrC FTE':<8} {'Monthly Churn':<13} {'Annual Churn'}")
    print("-" * 50)
    
    total_final = 0
    oslo_gets = 0
    
    for office_name in sorted(office_src_ftes.keys()):
        src_fte = office_src_ftes[office_name]
        monthly_churn = final_distribution.get(office_name, 0)
        annual_churn = monthly_churn * 12
        total_final += monthly_churn
        
        if office_name == "Oslo":
            oslo_gets = monthly_churn
        
        marker = " ✅" if monthly_churn > 0 else " ❌" if src_fte > 0 else ""
        print(f"{office_name:<12} {src_fte:<8} {monthly_churn:<13} {annual_churn:<12}{marker}")
    
    print("-" * 50)
    print(f"{'TOTAL':<12} {total_src_fte:<8} {total_final:<13} {total_final * 12}")
    
    # Verification
    print(f"\n🔍 VERIFICATION:")
    print("-" * 30)
    print(f"Expected total distributed: {global_src_churn}")
    print(f"Actual total distributed: {total_final}")
    print(f"Match: {'✅' if total_final == global_src_churn else '❌'}")
    
    print(f"\n🎯 OSLO SPECIFIC:")
    print("-" * 20)
    oslo_src_fte = office_src_ftes.get('Oslo', 0)
    print(f"Oslo SrC FTE: {oslo_src_fte}")
    print(f"Oslo should get: {oslo_gets} SrC churn/month ({oslo_gets * 12} annual)")
    
    if oslo_gets == 0 and oslo_src_fte > 0:
        print("🚨 OSLO GETS 0 CHURN despite having SrC workforce!")
        print("This confirms the distribution algorithm excludes Oslo.")
    elif oslo_gets > 0:
        print("✅ Oslo should receive SrC churn according to distribution.")
    
    # Compare with actual simulation results
    print(f"\n📊 COMPARISON WITH ACTUAL SIMULATION:")
    print("-" * 45)
    print("From simulation results, Oslo SrC level gets 0 churn.")
    print(f"Expected from distribution: {oslo_gets} churn/month")
    print("This shows the distribution algorithm vs. simulation engine mismatch.")

def main():
    """Trace SrC churn distribution."""
    trace_src_churn_distribution()

if __name__ == "__main__":
    main()