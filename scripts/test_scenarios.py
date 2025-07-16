#!/usr/bin/env python3
"""
Test Scenarios
=============

This file contains all test scenario definitions that can be imported
and used by various test scripts. This keeps the test scripts clean
and focused on testing logic rather than scenario data.

All scenarios include everything the engine needs:
- Complete baseline_input with offices, roles, levels
- All required economic_params
- Recruitment and churn for all months (1-12)
- Proper CAT curves
- All required fields for validation
"""

from datetime import datetime

def generate_monthly_recruitment_churn(base_recruitment, base_churn, months=12):
    """Generate recruitment and churn values for all months."""
    recruitment = {}
    churn = {}
    
    for month in range(1, months + 1):
        recruitment[f"recruitment_abs_{month}"] = base_recruitment
        churn[f"churn_abs_{month}"] = base_churn
    
    return recruitment, churn

def get_minimal_scenario():
    """Get a minimal scenario for basic testing."""
    recruitment, churn = generate_monthly_recruitment_churn(5, 2)
    
    return {
        "name": "Minimal Test Scenario",
        "description": "Minimal scenario for basic testing",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12
        },
        "office_scope": ["Stockholm"],
        "levers": {},
        "economic_params": {
            "working_hours_per_month": 160.0,
            "employment_cost_rate": 0.3,
            "unplanned_absence": 0.05,
            "other_expense": 1000000.0
        },
        "baseline_input": {
            "offices": {
                "Stockholm": {
                    "name": "Stockholm",
                    "total_fte": 100,
                    "journey": "Mature Office",
                    "roles": {
                        "Consultant": {
                            "A": {
                                "fte": 50.0,
                                "price_1": 1200.0,
                                "salary_1": 45000.0,
                                "utr_1": 0.85,
                                **recruitment,
                                **churn
                            }
                        },
                        "Operations": {
                            "fte": 50.0,
                            "price_1": 80.0,
                            "salary_1": 35000.0,
                            "utr_1": 0.85,
                            **generate_monthly_recruitment_churn(2, 1)[0],
                            **generate_monthly_recruitment_churn(2, 1)[1]
                        }
                    }
                }
            }
        },
        "cat_curves": get_default_cat_curves()
    }

def get_recruitment_churn_test_scenario():
    """Get a scenario specifically for testing recruitment and churn."""
    recruitment, churn = generate_monthly_recruitment_churn(5, 2)
    ops_recruitment, ops_churn = generate_monthly_recruitment_churn(2, 1)
    
    return {
        "name": "Recruitment Churn Test",
        "description": "Scenario to test recruitment and churn with absolute values",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2027,
            "end_month": 12
        },
        "office_scope": ["Stockholm"],
        "levers": {},
        "economic_params": {
            "working_hours_per_month": 160.0,
            "employment_cost_rate": 0.3,
            "unplanned_absence": 0.05,
            "other_expense": 1000000.0
        },
        "baseline_input": {
            "offices": {
                "Stockholm": {
                    "name": "Stockholm",
                    "total_fte": 100,
                    "journey": "Mature Office",
                    "roles": {
                        "Consultant": {
                            "A": {
                                "fte": 50.0,
                                "price_1": 1200.0,
                                "salary_1": 45000.0,
                                "utr_1": 0.85,
                                **recruitment,
                                **churn
                            }
                        },
                        "Operations": {
                            "fte": 50.0,
                            "price_1": 80.0,
                            "salary_1": 35000.0,
                            "utr_1": 0.85,
                            **ops_recruitment,
                            **ops_churn
                        }
                    }
                }
            }
        },
        "cat_curves": get_default_cat_curves()
    }

def get_complete_scenario():
    """Get a complete scenario with all offices and roles."""
    return {
        "name": "Complete Test Scenario",
        "description": "Complete scenario with all offices and roles for comprehensive testing",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2027,
            "end_month": 12
        },
        "office_scope": ["Stockholm", "Gothenburg", "Amsterdam", "Frankfurt", "Zurich", "Cologne", "Toronto"],
        "levers": {},
        "economic_params": {
            "working_hours_per_month": 160.0,
            "employment_cost_rate": 0.3,
            "unplanned_absence": 0.05,
            "other_expense": 1000000.0
        },
        "baseline_input": {
            "offices": {
                "Stockholm": {
                    "name": "Stockholm",
                    "total_fte": 821,
                    "journey": "Mature Office",
                    "roles": {
                        "Consultant": {
                            "A": {
                                "fte": 69.0, 
                                "price_1": 1200.0, 
                                "salary_1": 45000.0, 
                                "utr_1": 0.85,
                                **generate_monthly_recruitment_churn(8, 3)[0],
                                **generate_monthly_recruitment_churn(8, 3)[1]
                            },
                            "AC": {
                                "fte": 45.0, 
                                "price_1": 1300.0, 
                                "salary_1": 52000.0, 
                                "utr_1": 0.85,
                                **generate_monthly_recruitment_churn(5, 2)[0],
                                **generate_monthly_recruitment_churn(5, 2)[1]
                            },
                            "C": {
                                "fte": 12.0, 
                                "price_1": 1400.0, 
                                "salary_1": 65000.0, 
                                "utr_1": 0.85,
                                **generate_monthly_recruitment_churn(2, 1)[0],
                                **generate_monthly_recruitment_churn(2, 1)[1]
                            },
                            "SrC": {
                                "fte": 8.0, 
                                "price_1": 1500.0, 
                                "salary_1": 75000.0, 
                                "utr_1": 0.85,
                                **generate_monthly_recruitment_churn(1, 1)[0],
                                **generate_monthly_recruitment_churn(1, 1)[1]
                            },
                            "AM": {
                                "fte": 4.0, 
                                "price_1": 1600.0, 
                                "salary_1": 85000.0, 
                                "utr_1": 0.85,
                                **generate_monthly_recruitment_churn(1, 0)[0],
                                **generate_monthly_recruitment_churn(1, 0)[1]
                            },
                            "M": {
                                "fte": 2.0, 
                                "price_1": 1700.0, 
                                "salary_1": 95000.0, 
                                "utr_1": 0.85,
                                **generate_monthly_recruitment_churn(0, 0)[0],
                                **generate_monthly_recruitment_churn(0, 0)[1]
                            }
                        },
                        "Operations": {
                            "fte": 12.0, 
                            "price_1": 80.0, 
                            "salary_1": 35000.0, 
                            "utr_1": 0.85,
                            **generate_monthly_recruitment_churn(2, 1)[0],
                            **generate_monthly_recruitment_churn(2, 1)[1]
                        }
                    }
                },
                "Gothenburg": {
                    "name": "Gothenburg",
                    "total_fte": 245,
                    "journey": "Established Office",
                    "roles": {
                        "Consultant": {
                            "A": {
                                "fte": 25.0, 
                                "price_1": 1100.0, 
                                "salary_1": 42000.0, 
                                "utr_1": 0.85,
                                **generate_monthly_recruitment_churn(3, 1)[0],
                                **generate_monthly_recruitment_churn(3, 1)[1]
                            },
                            "AC": {
                                "fte": 15.0, 
                                "price_1": 1200.0, 
                                "salary_1": 48000.0, 
                                "utr_1": 0.85,
                                **generate_monthly_recruitment_churn(2, 1)[0],
                                **generate_monthly_recruitment_churn(2, 1)[1]
                            },
                            "C": {
                                "fte": 5.0, 
                                "price_1": 1300.0, 
                                "salary_1": 60000.0, 
                                "utr_1": 0.85,
                                **generate_monthly_recruitment_churn(1, 0)[0],
                                **generate_monthly_recruitment_churn(1, 0)[1]
                            }
                        },
                        "Operations": {
                            "fte": 8.0, 
                            "price_1": 75.0, 
                            "salary_1": 32000.0, 
                            "utr_1": 0.85,
                            **generate_monthly_recruitment_churn(1, 1)[0],
                            **generate_monthly_recruitment_churn(1, 1)[1]
                        }
                    }
                }
            }
        },
        "cat_curves": get_default_cat_curves()
    }

def get_no_progression_scenario():
    """Get a scenario with zero CAT curves to test without progression."""
    return {
        "name": "No Progression Test",
        "description": "Scenario with zero CAT curves to test without progression effects",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12
        },
        "office_scope": ["Stockholm"],
        "levers": {},
        "economic_params": {
            "working_hours_per_month": 160.0,
            "employment_cost_rate": 0.3,
            "unplanned_absence": 0.05,
            "other_expense": 1000000.0
        },
        "baseline_input": {
            "offices": {
                "Stockholm": {
                    "name": "Stockholm",
                    "total_fte": 100,
                    "journey": "Mature Office",
                    "roles": {
                        "Consultant": {
                            "A": {
                                "fte": 50.0,
                                "price_1": 1200.0,
                                "salary_1": 45000.0,
                                "utr_1": 0.85,
                                **generate_monthly_recruitment_churn(5, 2)[0],
                                **generate_monthly_recruitment_churn(5, 2)[1]
                            }
                        },
                        "Operations": {
                            "fte": 50.0,
                            "price_1": 80.0,
                            "salary_1": 35000.0,
                            "utr_1": 0.85,
                            **generate_monthly_recruitment_churn(2, 1)[0],
                            **generate_monthly_recruitment_churn(2, 1)[1]
                        }
                    }
                }
            }
        },
        "cat_curves": get_zero_cat_curves()
    }

def get_default_cat_curves():
    """Get default CAT curves for all levels."""
    return {
        "A": {"CAT0": 0.0, "CAT6": 0.919, "CAT12": 0.85, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0},
        "AC": {"CAT0": 0.0, "CAT6": 0.054, "CAT12": 0.759, "CAT18": 0.400, "CAT24": 0.0, "CAT30": 0.0},
        "C": {"CAT0": 0.0, "CAT6": 0.050, "CAT12": 0.442, "CAT18": 0.597, "CAT24": 0.278, "CAT30": 0.643, "CAT36": 0.200, "CAT42": 0.0},
        "SrC": {"CAT0": 0.0, "CAT6": 0.206, "CAT12": 0.438, "CAT18": 0.317, "CAT24": 0.211, "CAT30": 0.206, "CAT36": 0.167, "CAT42": 0.0, "CAT48": 0.0, "CAT54": 0.0, "CAT60": 0.0},
        "AM": {"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.189, "CAT24": 0.197, "CAT30": 0.234, "CAT36": 0.048, "CAT42": 0.0, "CAT48": 0.0, "CAT54": 0.0, "CAT60": 0.0},
        "M": {"CAT0": 0.0, "CAT6": 0.00, "CAT12": 0.01, "CAT18": 0.02, "CAT24": 0.03, "CAT30": 0.04, "CAT36": 0.05, "CAT42": 0.06, "CAT48": 0.07, "CAT54": 0.08, "CAT60": 0.10},
        "SrM": {"CAT0": 0.0, "CAT6": 0.00, "CAT12": 0.005, "CAT18": 0.01, "CAT24": 0.015, "CAT30": 0.02, "CAT36": 0.025, "CAT42": 0.03, "CAT48": 0.04, "CAT54": 0.05, "CAT60": 0.06},
        "Pi": {"CAT0": 0.0},
        "P": {"CAT0": 0.0},
        "X": {"CAT0": 0.0},
        "OPE": {"CAT0": 0.0}
    }

def get_zero_cat_curves():
    """Get zero CAT curves for all levels (no progression)."""
    return {
        "A": {"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0},
        "AC": {"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0},
        "C": {"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0, "CAT36": 0.0, "CAT42": 0.0},
        "SrC": {"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0, "CAT36": 0.0, "CAT42": 0.0, "CAT48": 0.0, "CAT54": 0.0, "CAT60": 0.0},
        "AM": {"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0, "CAT36": 0.0, "CAT42": 0.0, "CAT48": 0.0, "CAT54": 0.0, "CAT60": 0.0},
        "M": {"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0, "CAT36": 0.0, "CAT42": 0.0, "CAT48": 0.0, "CAT54": 0.0, "CAT60": 0.0},
        "SrM": {"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0, "CAT36": 0.0, "CAT42": 0.0, "CAT48": 0.0, "CAT54": 0.0, "CAT60": 0.0},
        "Pi": {"CAT0": 0.0},
        "P": {"CAT0": 0.0},
        "X": {"CAT0": 0.0},
        "OPE": {"CAT0": 0.0}
    }

def get_scenario_by_name(name):
    """Get a scenario by name."""
    scenarios = {
        "minimal": get_minimal_scenario,
        "recruitment_churn": get_recruitment_churn_test_scenario,
        "complete": get_complete_scenario,
        "no_progression": get_no_progression_scenario
    }
    
    if name in scenarios:
        return scenarios[name]()
    else:
        raise ValueError(f"Unknown scenario name: {name}. Available: {list(scenarios.keys())}")

def list_available_scenarios():
    """List all available scenario names."""
    return ["minimal", "recruitment_churn", "complete", "no_progression"]

def validate_scenario(scenario):
    """Validate that a scenario has all required fields."""
    required_fields = [
        "name", "description", "time_range", "office_scope", 
        "levers", "economic_params", "baseline_input", "cat_curves"
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in scenario:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")
    
    # Validate economic_params
    required_economic_params = [
        "working_hours_per_month", "employment_cost_rate", 
        "unplanned_absence", "other_expense"
    ]
    
    missing_economic_params = []
    for param in required_economic_params:
        if param not in scenario["economic_params"]:
            missing_economic_params.append(param)
    
    if missing_economic_params:
        raise ValueError(f"Missing required economic_params: {missing_economic_params}")
    
    return True 