#!/usr/bin/env python3
"""
Test script for simulation verification

This script demonstrates how to use the verification system to check simulation results.
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from scripts.analysis.verify_simulation_results import SimulationVerifier


def test_verification_with_new_simulation():
    """Test verification with a fresh simulation run"""
    print("🧪 Testing verification with new simulation...")
    print("=" * 60)
    
    # Create verifier (will run new simulation)
    verifier = SimulationVerifier()
    
    # Run verification
    if verifier.load_results():
        results = verifier.verify_all()
        verifier.print_results()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"test_verification_results_{timestamp}.json"
        verifier.save_results(output_file)
        
        print(f"\n✅ Verification test completed!")
        print(f"📊 Results saved to: {output_file}")
        
        return results['summary']['errors'] == 0
    else:
        print("❌ Verification test failed - could not load results")
        return False


def test_verification_with_existing_file(results_file: str):
    """Test verification with an existing results file"""
    print(f"🧪 Testing verification with existing file: {results_file}")
    print("=" * 60)
    
    if not os.path.exists(results_file):
        print(f"❌ Results file not found: {results_file}")
        return False
    
    # Create verifier with existing file
    verifier = SimulationVerifier(results_file)
    
    # Run verification
    if verifier.load_results():
        results = verifier.verify_all()
        verifier.print_results()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"verification_results_{timestamp}.json"
        verifier.save_results(output_file)
        
        print(f"\n✅ Verification test completed!")
        print(f"📊 Results saved to: {output_file}")
        
        return results['summary']['errors'] == 0
    else:
        print("❌ Verification test failed - could not load results")
        return False


def main():
    """Main test function"""
    print("🚀 Simulation Verification Test Suite")
    print("=" * 60)
    
    # Test 1: New simulation
    print("\n1️⃣ Testing with new simulation...")
    success1 = test_verification_with_new_simulation()
    
    # Test 2: Check for existing results files
    print("\n2️⃣ Checking for existing results files...")
    possible_files = [
        "comprehensive_simulation_results.json",
        "simulation_export.json",
        "test_simulation_results.json"
    ]
    
    existing_file = None
    for file in possible_files:
        if os.path.exists(file):
            existing_file = file
            break
    
    if existing_file:
        print(f"📁 Found existing results file: {existing_file}")
        success2 = test_verification_with_existing_file(existing_file)
    else:
        print("📁 No existing results files found")
        success2 = True  # Not a failure, just no file to test
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ New simulation test: {'PASSED' if success1 else 'FAILED'}")
    print(f"✅ Existing file test: {'PASSED' if success2 else 'FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All verification tests passed!")
        return 0
    else:
        print("\n❌ Some verification tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 