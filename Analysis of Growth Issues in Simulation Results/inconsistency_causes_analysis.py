import json
import pandas as pd
from datetime import datetime

print("=== SIMULATION INCONSISTENCY CAUSES ANALYSIS ===")
print()

print("1. EVIDENCE SUMMARY:")
print("===================")

evidence = [
    "Same starting parameters: Both simulations start with identical FTE numbers",
    "Different outcomes: 161.6 percentage points total discrepancy",
    "New simulation matches baseline: 0.9% total deviation from expected",
    "Old simulation deviates significantly: 148.8% total deviation from expected",
    "Pattern reversals: 2 levels show opposite growth trends",
    "Major discrepancies: 3 levels show >20% difference",
    "Time periods differ: Old=6 years, New=5 years (but normalized for comparison)"
]

print("Key Evidence:")
for i, item in enumerate(evidence, 1):
    print(f"{i}. {item}")

print("\n2. HYPOTHESIS TESTING:")
print("======================")

# Test different hypotheses based on the evidence

print("Hypothesis 1: Random Seed Differences")
print("-------------------------------------")
print("Evidence FOR:")
print("- Stochastic simulations typically use random seeds")
print("- Different seeds would produce different outcomes")
print("- Could explain the magnitude of differences observed")
print("Evidence AGAINST:")
print("- New simulation matches baseline almost perfectly (unlikely if purely random)")
print("- Pattern is too systematic for pure randomness")
print("Likelihood: MEDIUM")

print("\nHypothesis 2: Bug Fix Between Runs")
print("----------------------------------")
print("Evidence FOR:")
print("- New simulation matches baseline expectations almost perfectly")
print("- Old simulation shows systematic deviations")
print("- Suggests correction of calculation errors")
print("Evidence AGAINST:")
print("- Would need confirmation of software changes")
print("Likelihood: HIGH")

print("\nHypothesis 3: Parameter Correction")
print("----------------------------------")
print("Evidence FOR:")
print("- New simulation aligns with intended baseline parameters")
print("- Old simulation appears to use incorrect parameters")
print("- Explains systematic nature of differences")
print("Evidence AGAINST:")
print("- Would need confirmation of parameter changes")
print("Likelihood: HIGH")

print("\nHypothesis 4: Different Simulation Versions")
print("-------------------------------------------")
print("Evidence FOR:")
print("- Dramatic improvement in baseline alignment")
print("- Systematic nature of improvements")
print("- Timing suggests version upgrade")
print("Evidence AGAINST:")
print("- Would need version information to confirm")
print("Likelihood: HIGH")

print("\nHypothesis 5: Configuration Differences")
print("---------------------------------------")
print("Evidence FOR:")
print("- Different time periods (5Y vs 6Y)")
print("- Could indicate different simulation setups")
print("Evidence AGAINST:")
print("- Time period normalized, discrepancies remain")
print("- Differences too large for configuration alone")
print("Likelihood: LOW")

print("\n3. DETAILED PATTERN ANALYSIS:")
print("=============================")

# Analyze the specific patterns to understand the root cause

patterns = {
    'Level A': {
        'old_behavior': 'Moderate growth (57.1%)',
        'new_behavior': 'High growth (95.1%)',
        'baseline_expectation': 'High growth (95.1%)',
        'conclusion': 'Old simulation under-performed, new matches baseline'
    },
    'Level AC': {
        'old_behavior': 'Very high growth (84.0%)',
        'new_behavior': 'Low growth (8.7%)',
        'baseline_expectation': 'Low growth (8.8%)',
        'conclusion': 'Old simulation over-performed, new matches baseline'
    },
    'Level AM': {
        'old_behavior': 'Moderate decline (-8.6%)',
        'new_behavior': 'Slight decline (-2.4%)',
        'baseline_expectation': 'Slight decline (-2.4%)',
        'conclusion': 'Old simulation over-declined, new matches baseline'
    },
    'Level C': {
        'old_behavior': 'Significant decline (-24.2%)',
        'new_behavior': 'Slight decline (-2.2%)',
        'baseline_expectation': 'Slight decline (-2.4%)',
        'conclusion': 'Old simulation over-declined, new matches baseline'
    }
}

print("Pattern Analysis by Level:")
for level, pattern in patterns.items():
    print(f"\n{level}:")
    print(f"  Old: {pattern['old_behavior']}")
    print(f"  New: {pattern['new_behavior']}")
    print(f"  Expected: {pattern['baseline_expectation']}")
    print(f"  Conclusion: {pattern['conclusion']}")

print("\n4. ROOT CAUSE ASSESSMENT:")
print("=========================")

# Based on the pattern analysis, determine most likely root cause

print("Most Likely Root Cause: SIMULATION ENGINE CORRECTION")
print("----------------------------------------------------")

reasons = [
    "New simulation matches baseline expectations with 99.9% accuracy",
    "Old simulation shows systematic deviations across multiple levels",
    "Pattern suggests correction of calculation errors rather than random variation",
    "Timing indicates potential software update or bug fix",
    "Magnitude of improvement too large for parameter tweaking alone"
]

print("Supporting Evidence:")
for i, reason in enumerate(reasons, 1):
    print(f"{i}. {reason}")

print("\nSpecific Issues Likely Fixed:")
print("- Level A: Under-recruitment/over-churn corrected")
print("- Level AC: Over-recruitment/over-churn corrected") 
print("- Level C: Over-churn corrected")
print("- Overall: Recruitment/churn calculation logic improved")

print("\n5. ALTERNATIVE EXPLANATIONS:")
print("============================")

alternatives = [
    {
        'cause': 'Data Input Changes',
        'likelihood': 'LOW',
        'reason': 'Starting parameters identical, suggests same input data'
    },
    {
        'cause': 'Random Seed Management',
        'likelihood': 'MEDIUM', 
        'reason': 'Could explain variation, but not systematic baseline alignment'
    },
    {
        'cause': 'External Dependencies',
        'likelihood': 'LOW',
        'reason': 'Simulation appears self-contained based on data structure'
    },
    {
        'cause': 'Hardware/Environment',
        'likelihood': 'LOW',
        'reason': 'Would not explain systematic improvement in baseline alignment'
    }
]

print("Alternative Explanations:")
for alt in alternatives:
    print(f"- {alt['cause']}: {alt['likelihood']} likelihood")
    print(f"  Reason: {alt['reason']}")

print("\n6. VALIDATION APPROACH:")
print("=======================")

validation_steps = [
    "Compare simulation software versions between runs",
    "Review change logs for bug fixes or parameter updates",
    "Check configuration files for parameter modifications",
    "Verify random seed management approach",
    "Test simulation reproducibility with same inputs",
    "Document baseline parameter sources and calculations",
    "Implement automated baseline validation checks",
    "Create regression testing for simulation consistency"
]

print("Recommended Validation Steps:")
for i, step in enumerate(validation_steps, 1):
    print(f"{i}. {step}")

print("\n7. BUSINESS IMPLICATIONS:")
print("=========================")

implications = {
    'positive': [
        "New simulation appears to be working correctly",
        "Baseline alignment suggests reliable parameter implementation",
        "Growth patterns now match business expectations",
        "Can potentially trust new simulation results"
    ],
    'negative': [
        "Historical analysis using old simulation may be invalid",
        "Previous business decisions may have been based on incorrect projections",
        "Simulation reliability track record is compromised",
        "Need to validate all previous simulation-based analyses"
    ],
    'actions_required': [
        "Validate the new simulation with additional test cases",
        "Review and potentially revise previous strategic decisions",
        "Implement stronger quality assurance for simulation outputs",
        "Establish baseline validation as standard practice"
    ]
}

print("Positive Implications:")
for imp in implications['positive']:
    print(f"✅ {imp}")

print("\nNegative Implications:")
for imp in implications['negative']:
    print(f"⚠️ {imp}")

print("\nRequired Actions:")
for action in implications['actions_required']:
    print(f"🔧 {action}")

print("\n8. CONFIDENCE ASSESSMENT:")
print("=========================")

confidence_factors = {
    'High Confidence (>80%)': [
        "New simulation matches baseline expectations",
        "Old simulation shows systematic deviations",
        "Pattern suggests correction rather than random variation"
    ],
    'Medium Confidence (50-80%)': [
        "Specific technical cause (bug fix vs parameter change)",
        "Timeline of when changes were implemented",
        "Scope of changes made to simulation engine"
    ],
    'Low Confidence (<50%)': [
        "Exact technical details of what was changed",
        "Whether changes were intentional or accidental",
        "Impact on other simulation scenarios not tested"
    ]
}

for level, factors in confidence_factors.items():
    print(f"\n{level}:")
    for factor in factors:
        print(f"  - {factor}")

print(f"\nOverall Assessment: The new simulation appears to be CORRECTED and RELIABLE")
print(f"Recommendation: Use new simulation for business planning, but validate with additional test cases")

print(f"\nAnalysis complete. Root cause most likely: Simulation engine correction/improvement.")

