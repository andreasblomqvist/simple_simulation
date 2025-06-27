import pytest
import random
import math
from datetime import datetime, timedelta
from backend.src.services.simulation.models import Person, Level, Office
from backend.config.default_config import DEFAULT_RATES

def create_realistic_test_config():
    """Create a realistic test configuration with multiple levels and FTEs, all with 3% progression"""
    config = {
        "TestOffice": {
            "name": "TestOffice",
            "total_fte": 2500,
            "journey": "Mature Office",
            "roles": {
                "Consultant": {
                    "A": {
                        "fte": 500,
                        "salary": 45000,
                        "price_1": 1200,
                        "progression_1": 0.03,
                        "progression_6": 0.03,
                        "recruitment_1": 0.05,
                        "recruitment_6": 0.05,
                        "churn_1": 0.02,
                        "churn_6": 0.02
                    },
                    "AC": {
                        "fte": 400,
                        "salary": 50000,
                        "price_1": 1300,
                        "progression_1": 0.03,
                        "progression_6": 0.03,
                        "recruitment_1": 0.04,
                        "recruitment_6": 0.04,
                        "churn_1": 0.015,
                        "churn_6": 0.015
                    },
                    "C": {
                        "fte": 350,
                        "salary": 55000,
                        "price_1": 1400,
                        "progression_1": 0.03,
                        "progression_6": 0.03,
                        "recruitment_1": 0.03,
                        "recruitment_6": 0.03,
                        "churn_1": 0.01,
                        "churn_6": 0.01
                    },
                    "SrC": {
                        "fte": 300,
                        "salary": 60000,
                        "price_1": 1500,
                        "progression_1": 0.03,
                        "progression_6": 0.03,
                        "recruitment_1": 0.02,
                        "recruitment_6": 0.02,
                        "churn_1": 0.008,
                        "churn_6": 0.008
                    },
                    "AM": {
                        "fte": 250,
                        "salary": 70000,
                        "price_1": 1600,
                        "progression_1": 0.03,
                        "progression_6": 0.03,
                        "recruitment_1": 0.015,
                        "recruitment_6": 0.015,
                        "churn_1": 0.006,
                        "churn_6": 0.006
                    },
                    "M": {
                        "fte": 200,
                        "salary": 80000,
                        "price_1": 1700,
                        "progression_1": 0.03,
                        "progression_6": 0.03,
                        "recruitment_1": 0.01,
                        "recruitment_6": 0.01,
                        "churn_1": 0.005,
                        "churn_6": 0.005
                    },
                    "SrM": {
                        "fte": 150,
                        "salary": 90000,
                        "price_1": 1800,
                        "progression_1": 0.03,
                        "progression_6": 0.03,
                        "recruitment_1": 0.008,
                        "recruitment_6": 0.008,
                        "churn_1": 0.004,
                        "churn_6": 0.004
                    },
                    "PiP": {
                        "fte": 100,
                        "salary": 100000,
                        "price_1": 2000,
                        "progression_1": 0.03,
                        "progression_6": 0.03,
                        "recruitment_1": 0.005,
                        "recruitment_6": 0.005,
                        "churn_1": 0.003,
                        "churn_6": 0.003
                    }
                }
            }
        }
    }
    return config

def create_people_with_varied_tenure(level_name, fte, base_date="2025-01"):
    """Create people with varied tenure to test different CAT categories"""
    people = []
    base_dt = datetime.strptime(base_date, "%Y-%m")
    
    # Distribute people across different CAT categories
    cat_distribution = {
        6: 0.25,   # 25% CAT6 (6-12 months)
        12: 0.30,  # 30% CAT12 (12-18 months)
        18: 0.25,  # 25% CAT18 (18-24 months)
        24: 0.15,  # 15% CAT24 (24-30 months)
        30: 0.05   # 5% CAT30+ (30+ months)
    }
    
    person_id = 0
    for cat_months, percentage in cat_distribution.items():
        num_people = int(fte * percentage)
        for i in range(num_people):
            # Calculate level start date to achieve desired CAT
            level_start_dt = base_dt - timedelta(days=cat_months * 30)
            level_start = level_start_dt.strftime("%Y-%m")
            
            person = Person(
                id=f"{level_name}_{person_id}",
                career_start="2020-01",
                current_level=level_name,
                level_start=level_start,
                role="Consultant",
                office="TestOffice"
            )
            people.append(person)
            person_id += 1
    
    # Add remaining people to CAT6 if any rounding occurred
    while len(people) < fte:
        person = Person(
            id=f"{level_name}_{person_id}",
            career_start="2020-01",
            current_level=level_name,
            level_start=(base_dt - timedelta(days=6 * 30)).strftime("%Y-%m"),
            role="Consultant",
            office="TestOffice"
        )
        people.append(person)
        person_id += 1
    
    return people[:fte]  # Ensure exact FTE count

def calculate_expected_progressions(level_name, fte, progression_rate, cat_distribution):
    """Calculate expected number of progressions based on CAT distribution"""
    cat_curves = DEFAULT_RATES['progression']['cat_curves'].get(level_name, {})
    expected_total = 0
    
    for cat_months, percentage in cat_distribution.items():
        cat_category = f"CAT{cat_months}"
        cat_multiplier = cat_curves.get(cat_category, 0.0)
        num_people = int(fte * percentage)
        expected_prob = min(progression_rate * cat_multiplier, 1.0)
        expected_total += num_people * expected_prob
    
    return expected_total

def run_multi_year_simulation(config, years=3):
    """Run simulation for multiple years and track progression statistics"""
    # Create office with realistic configuration
    office_data = config["TestOffice"]
    office = Office(
        name=office_data["name"],
        journey=office_data["journey"],
        total_fte=office_data["total_fte"],
        roles={}
    )
    
    # Create levels and people
    for role_name, role_data in office_data["roles"].items():
        office.roles[role_name] = {}
        for level_name, level_data in role_data.items():
            fte = level_data["fte"]
            people = create_people_with_varied_tenure(level_name, fte)
            
            level = Level(
                name=level_name,
                journey=None,
                progression_months=[1, 6],
                progression_1=level_data["progression_1"],
                progression_2=0.0,
                progression_3=0.0,
                progression_4=0.0,
                progression_5=0.0,
                progression_6=level_data["progression_6"],
                progression_7=0.0,
                progression_8=0.0,
                progression_9=0.0,
                progression_10=0.0,
                progression_11=0.0,
                progression_12=0.0,
                recruitment_1=level_data["recruitment_1"],
                recruitment_2=0.0,
                recruitment_3=0.0,
                recruitment_4=0.0,
                recruitment_5=0.0,
                recruitment_6=level_data["recruitment_6"],
                recruitment_7=0.0,
                recruitment_8=0.0,
                recruitment_9=0.0,
                recruitment_10=0.0,
                recruitment_11=0.0,
                recruitment_12=0.0,
                churn_1=level_data["churn_1"],
                churn_2=0.0,
                churn_3=0.0,
                churn_4=0.0,
                churn_5=0.0,
                churn_6=level_data["churn_6"],
                churn_7=0.0,
                churn_8=0.0,
                churn_9=0.0,
                churn_10=0.0,
                churn_11=0.0,
                churn_12=0.0,
                price_1=level_data["price_1"],
                price_2=level_data["price_1"],
                price_3=level_data["price_1"],
                price_4=level_data["price_1"],
                price_5=level_data["price_1"],
                price_6=level_data["price_1"],
                price_7=level_data["price_1"],
                price_8=level_data["price_1"],
                price_9=level_data["price_1"],
                price_10=level_data["price_1"],
                price_11=level_data["price_1"],
                price_12=level_data["price_1"],
                salary_1=level_data["salary"],
                salary_2=level_data["salary"],
                salary_3=level_data["salary"],
                salary_4=level_data["salary"],
                salary_5=level_data["salary"],
                salary_6=level_data["salary"],
                salary_7=level_data["salary"],
                salary_8=level_data["salary"],
                salary_9=level_data["salary"],
                salary_10=level_data["salary"],
                salary_11=level_data["salary"],
                salary_12=level_data["salary"],
                utr_1=1.0,
                utr_2=1.0,
                utr_3=1.0,
                utr_4=1.0,
                utr_5=1.0,
                utr_6=1.0,
                utr_7=1.0,
                utr_8=1.0,
                utr_9=1.0,
                utr_10=1.0,
                utr_11=1.0,
                utr_12=1.0
            )
            level.people = people
            office.roles[role_name][level_name] = level
    
    # Track progression statistics over years
    progression_stats = {}
    
    for year in range(2025, 2025 + years):
        for month in [1, 6]:  # Progression months
            current_date = f"{year}-{month:02d}"
            
            # Track progressions for each level
            for role_name, role_data in office.roles.items():
                for level_name, level in role_data.items():
                    if level_name not in progression_stats:
                        progression_stats[level_name] = []
                    
                    # Get progression rate for this month
                    progression_rate = level.progression_1 if month == 1 else level.progression_6
                    
                    # Count people before progression
                    people_before = len(level.people)
                    
                    # Apply progression
                    progressed_people = []
                    for person in level.people:
                        prob = person.get_progression_probability(current_date, progression_rate, level_name)
                        if random.random() < prob:
                            progressed_people.append(person)
                    
                    # Record statistics
                    progression_stats[level_name].append({
                        'date': current_date,
                        'fte_before': people_before,
                        'progressions': len(progressed_people),
                        'progression_rate': progression_rate,
                        'actual_rate': len(progressed_people) / people_before if people_before > 0 else 0
                    })
                    
                    # Remove progressed people (in real simulation they'd move to next level)
                    for person in progressed_people:
                        level.people.remove(person)
    
    return progression_stats

def test_comprehensive_cat_progression():
    """Comprehensive test of CAT progression with realistic populations over multiple years"""
    print("\n" + "="*80)
    print("COMPREHENSIVE CAT PROGRESSION TEST")
    print("="*80)
    
    # Set random seed for reproducible results
    random.seed(42)
    
    # Create realistic test configuration
    config = create_realistic_test_config()
    
    # Run multi-year simulation
    progression_stats = run_multi_year_simulation(config, years=3)
    
    # Analyze results
    print("\nPROGRESSION STATISTICS OVER 3 YEARS:")
    print("-" * 80)
    
    results_table = []
    total_tests = 0
    passed_tests = 0
    
    for level_name, stats in progression_stats.items():
        print(f"\n{level_name} Level:")
        print(f"{'Date':<10} {'FTE':<6} {'Progressions':<12} {'Expected':<10} {'Actual Rate':<12} {'Status':<6}")
        print("-" * 60)
        
        for stat in stats:
            # Get expected progressions based on CAT distribution
            cat_distribution = {6: 0.25, 12: 0.30, 18: 0.25, 24: 0.15, 30: 0.05}
            expected = calculate_expected_progressions(
                level_name, 
                stat['fte_before'], 
                stat['progression_rate'], 
                cat_distribution
            )
            
            # Calculate statistical range with adjusted thresholds for small FTEs
            if expected > 0:
                stddev = math.sqrt(stat['fte_before'] * (expected/stat['fte_before']) * (1 - expected/stat['fte_before']))
                
                # Adjust confidence interval based on FTE size
                if stat['fte_before'] < 50:
                    sigma_multiplier = 4  # ±4σ for very small populations
                elif stat['fte_before'] < 100:
                    sigma_multiplier = 3  # ±3σ for small populations
                else:
                    sigma_multiplier = 2  # ±2σ for larger populations
                
                lower_bound = max(0, expected - sigma_multiplier * stddev)
                upper_bound = min(stat['fte_before'], expected + sigma_multiplier * stddev)
                in_range = lower_bound <= stat['progressions'] <= upper_bound
            else:
                in_range = stat['progressions'] == 0
                lower_bound = upper_bound = 0
            
            status = "✅" if in_range else "❌"
            if in_range:
                passed_tests += 1
            total_tests += 1
            
            print(f"{stat['date']:<10} {stat['fte_before']:<6} {stat['progressions']:<12} {expected:<10.1f} {stat['actual_rate']:<12.3f} {status:<6}")
            
            results_table.append({
                'level': level_name,
                'date': stat['date'],
                'fte': stat['fte_before'],
                'progressions': stat['progressions'],
                'expected': expected,
                'range': f"({lower_bound:.1f}, {upper_bound:.1f})",
                'status': status
            })
    
    # Summary statistics
    print(f"\n" + "="*80)
    print(f"SUMMARY: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    print("="*80)
    
    # Verify key assertions
    assert passed_tests / total_tests >= 0.95, f"Too many tests failed: {passed_tests}/{total_tests}"
    
    # Test specific scenarios
    print("\nSPECIFIC SCENARIO TESTS:")
    print("-" * 40)
    
    # Test 1: Junior levels should have higher progression rates
    junior_levels = ['A', 'AC', 'C']
    senior_levels = ['SrM', 'PiP']
    
    avg_junior_rate = sum(
        stat['actual_rate'] for stat in progression_stats['A'] + progression_stats['AC'] + progression_stats['C']
    ) / len(progression_stats['A'] + progression_stats['AC'] + progression_stats['C'])
    
    avg_senior_rate = sum(
        stat['actual_rate'] for stat in progression_stats['SrM'] + progression_stats['PiP']
    ) / len(progression_stats['SrM'] + progression_stats['PiP'])
    
    print(f"Average junior level progression rate: {avg_junior_rate:.3f}")
    print(f"Average senior level progression rate: {avg_senior_rate:.3f}")
    assert avg_junior_rate > avg_senior_rate, "Junior levels should have higher progression rates"
    print("✅ Junior levels have higher progression rates than senior levels")
    
    # Test 2: Progression should be consistent over time
    for level_name in ['A', 'C', 'AM']:
        rates = [stat['actual_rate'] for stat in progression_stats[level_name]]
        variance = sum((r - sum(rates)/len(rates))**2 for r in rates) / len(rates)
        print(f"{level_name} level progression variance: {variance:.6f}")
        assert variance < 0.01, f"{level_name} level progression too inconsistent"
        print(f"✅ {level_name} level progression is consistent over time")
    
    # Test 3: Large populations should show statistical accuracy
    large_level_stats = [stat for stat in progression_stats['A'] if stat['fte_before'] > 400]
    if large_level_stats:
        avg_error = sum(abs(stat['progressions'] - stat['expected']) / stat['fte_before'] 
                       for stat in large_level_stats) / len(large_level_stats)
        print(f"Average error rate for large populations: {avg_error:.3f}")
        assert avg_error < 0.05, "Large populations should show accurate progression rates"
        print("✅ Large populations show accurate progression rates")
    
    print(f"\n🎉 All comprehensive CAT progression tests passed!")
    return results_table

if __name__ == "__main__":
    test_comprehensive_cat_progression() 