#!/usr/bin/env python3
"""
Run Simulation and Verify Results

This script runs a simulation and then automatically verifies the results
to ensure they are correct and reasonable.

Usage:
    python scripts/run_and_verify_simulation.py
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi import EconomicParameters
from scripts.analysis.verify_simulation_results import SimulationVerifier


def run_simulation_with_verification():
    """Run a simulation and verify the results"""
    print("🚀 Running Simulation with Verification")
    print("=" * 60)
    
    try:
        # Step 1: Run simulation
        print("\n1️⃣ Running simulation...")
        engine = SimulationEngine()
        
        # Run a 3-year simulation with typical parameters
        results = engine.run_simulation(
            start_year=2025,
            start_month=1,
            end_year=2027,
            end_month=12,
            price_increase=0.05,  # 5% annual price increase
            salary_increase=0.03   # 3% annual salary increase
        )
        
        print("✅ Simulation completed successfully")
        
        # Step 2: Save results to file
        print("\n2️⃣ Saving simulation results...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"simulation_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"✅ Results saved to: {results_file}")
        
        # Step 3: Verify results
        print("\n3️⃣ Verifying simulation results...")
        verifier = SimulationVerifier(results_file)
        
        if verifier.load_results():
            verification_results = verifier.verify_all()
            verifier.print_results()
            
            # Step 4: Save verification results
            print("\n4️⃣ Saving verification results...")
            verification_file = f"verification_results_{timestamp}.json"
            verifier.save_results(verification_file)
            
            print(f"✅ Verification results saved to: {verification_file}")
            
            # Step 5: Summary
            print("\n" + "=" * 60)
            print("📊 FINAL SUMMARY")
            print("=" * 60)
            
            summary = verification_results['summary']
            print(f"📈 Simulation Results: {results_file}")
            print(f"🔍 Verification Results: {verification_file}")
            print(f"✅ Passed Checks: {summary['passed']}")
            print(f"⚠️  Warnings: {summary['warnings']}")
            print(f"❌ Errors: {summary['errors']}")
            print(f"📊 Success Rate: {summary['success_rate']:.1f}%")
            
            if summary['errors'] == 0:
                print("\n🎉 SUCCESS: All critical checks passed!")
                return True
            else:
                print("\n⚠️  WARNING: Some critical issues found!")
                return False
        else:
            print("❌ Failed to load results for verification")
            return False
            
    except Exception as e:
        print(f"❌ Error during simulation or verification: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    success = run_simulation_with_verification()
    
    if success:
        print("\n✅ Process completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Process completed with issues!")
        sys.exit(1)


if __name__ == "__main__":
    main() 