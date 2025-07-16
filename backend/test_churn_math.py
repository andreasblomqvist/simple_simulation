#!/usr/bin/env python3
"""
Test the mathematical correctness of the churn fix
"""

def test_churn_calculation():
    """Test churn calculation with different rates"""
    
    print("Testing churn calculation fix:")
    print("=" * 35)
    
    # Test cases with different churn rates
    test_cases = [
        (0.0015, 100, "Current simulation rate"),
        (0.01, 100, "1% monthly churn"),
        (0.02, 50, "2% monthly churn, 50 FTE"),
        (0.005, 200, "0.5% monthly churn, 200 FTE"),
    ]
    
    for churn_rate, fte, description in test_cases:
        print(f"\n{description}:")
        print(f"  Churn rate: {churn_rate} ({churn_rate*100:.1f}%)")
        print(f"  FTE: {fte}")
        
        # Fixed calculation (no division by 100)
        expected_churn = churn_rate * fte
        actual_churn = int(churn_rate * fte)
        
        print(f"  Expected churn: {expected_churn:.3f} people")
        print(f"  Actual churn (int): {actual_churn} people")
        
        # Show what would happen over multiple months
        months = 8
        total_expected = expected_churn * months
        total_actual = actual_churn * months
        
        print(f"  Over {months} months:")
        print(f"    Expected: {total_expected:.2f} people")
        print(f"    Actual: {total_actual} people")
        
        if total_expected >= 1:
            print(f"    ✓ Should see churn")
        else:
            print(f"    ⚠️ Too low to see churn (need higher rate or more FTE)")

if __name__ == "__main__":
    test_churn_calculation()