"""
Unit tests for ScenarioResolver service.
"""
import pytest
from unittest.mock import Mock, patch
from src.services.scenario_resolver import ScenarioResolver


class TestScenarioResolver:
    """Test cases for ScenarioResolver service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config_service = Mock()
        self.resolver = ScenarioResolver(self.mock_config_service)
    
    def test_resolve_scenario_empty_data(self):
        """Test resolving empty scenario data."""
        scenario_data = {}
        
        result = self.resolver.resolve_scenario(scenario_data)
        
        assert 'offices_config' in result
        assert 'progression_config' in result
        assert 'cat_curves' in result
        assert result['offices_config'] == {}
        assert result['progression_config'] == {}
        assert result['cat_curves'] == {}
    
    def test_resolve_scenario_with_baseline_input_global(self):
        """Test resolving scenario with global baseline input."""
        # Mock config service to return office config
        self.mock_config_service.get_office_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0},
                        "AC": {"fte": 30.0, "price_1": 1300.0}
                    }
                }
            }
        }
        
        scenario_data = {
            "baseline_input": {
                "global": {
                    "recruitment": {
                        "Consultant": {
                            "recruitment_1": {"A": 5.0, "AC": 3.0},
                            "recruitment_2": {"A": 4.0, "AC": 2.5}
                        }
                    },
                    "churn": {
                        "Consultant": {
                            "churn_1": {"A": 0.02, "AC": 0.015},
                            "churn_2": {"A": 0.025, "AC": 0.02}
                        }
                    }
                }
            }
        }
        
        result = self.resolver.resolve_scenario(scenario_data)
        
        # Verify offices config contains the baseline input
        offices_config = result['offices_config']
        assert "Stockholm" in offices_config
        
        stockholm_config = offices_config["Stockholm"]
        assert "recruitment_abs_A" in stockholm_config["roles"]["Consultant"]["A"]
        assert "recruitment_abs_AC" in stockholm_config["roles"]["Consultant"]["AC"]
        assert "churn_abs_A" in stockholm_config["roles"]["Consultant"]["A"]
        assert "churn_abs_AC" in stockholm_config["roles"]["Consultant"]["AC"]
        
        # Verify absolute values are set correctly
        assert stockholm_config["roles"]["Consultant"]["A"]["recruitment_abs_A"] == 5.0
        assert stockholm_config["roles"]["Consultant"]["AC"]["recruitment_abs_AC"] == 3.0
        assert stockholm_config["roles"]["Consultant"]["A"]["churn_abs_A"] == 0.02
        assert stockholm_config["roles"]["Consultant"]["AC"]["churn_abs_AC"] == 0.015
    
    def test_resolve_scenario_with_baseline_input_offices(self):
        """Test resolving scenario with office-specific baseline input."""
        # Mock config service to return office config
        self.mock_config_service.get_office_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0},
                        "AC": {"fte": 30.0, "price_1": 1300.0}
                    }
                }
            }
        }
        
        scenario_data = {
            "baseline_input": {
                "offices": {
                    "Stockholm": {
                        "recruitment": {
                            "Consultant": {
                                "recruitment_1": {"A": 6.0, "AC": 4.0}
                            }
                        },
                        "churn": {
                            "Consultant": {
                                "churn_1": {"A": 0.03, "AC": 0.02}
                            }
                        }
                    }
                }
            }
        }
        
        result = self.resolver.resolve_scenario(scenario_data)
        
        # Verify offices config contains the office-specific baseline input
        offices_config = result['offices_config']
        assert "Stockholm" in offices_config
        
        stockholm_config = offices_config["Stockholm"]
        assert stockholm_config["roles"]["Consultant"]["A"]["recruitment_abs_A"] == 6.0
        assert stockholm_config["roles"]["Consultant"]["AC"]["recruitment_abs_AC"] == 4.0
        assert stockholm_config["roles"]["Consultant"]["A"]["churn_abs_A"] == 0.03
        assert stockholm_config["roles"]["Consultant"]["AC"]["churn_abs_AC"] == 0.02
    
    def test_resolve_scenario_with_levers_global(self):
        """Test resolving scenario with global levers."""
        # Mock config service to return office config
        self.mock_config_service.get_office_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0, "cat_curve": 0.1},
                        "AC": {"fte": 30.0, "price_1": 1300.0, "cat_curve": 0.08}
                    }
                }
            }
        }
        
        scenario_data = {
            "levers": {
                "global": {
                    "recruitment": {"A": 1.2, "AC": 1.1},
                    "churn": {"A": 0.8, "AC": 0.9},
                    "progression": {"A": 1.1, "AC": 1.05},
                    "price": {"A": 1.1, "AC": 1.05},
                    "salary": {"A": 1.05, "AC": 1.02},
                    "utr": {"A": 1.1, "AC": 1.05}
                }
            }
        }
        
        result = self.resolver.resolve_scenario(scenario_data)
        
        # Verify offices config contains the lever multipliers
        offices_config = result['offices_config']
        assert "Stockholm" in offices_config
        
        stockholm_config = offices_config["Stockholm"]
        consultant_a = stockholm_config["roles"]["Consultant"]["A"]
        consultant_ac = stockholm_config["roles"]["Consultant"]["AC"]
        
        # Verify lever multipliers are applied
        assert consultant_a["recruitment_multiplier"] == 1.2
        assert consultant_ac["recruitment_multiplier"] == 1.1
        assert consultant_a["churn_multiplier"] == 0.8
        assert consultant_ac["churn_multiplier"] == 0.9
        assert consultant_a["price_multiplier"] == 1.1
        assert consultant_ac["price_multiplier"] == 1.05
        assert consultant_a["salary_multiplier"] == 1.05
        assert consultant_ac["salary_multiplier"] == 1.02
        assert consultant_a["utr_multiplier"] == 1.1
        assert consultant_ac["utr_multiplier"] == 1.05
        
        # Verify progression lever affects CAT curve
        assert consultant_a["cat_curve"] == 0.11  # 0.1 * 1.1
        assert consultant_ac["cat_curve"] == 0.084  # 0.08 * 1.05
    
    def test_resolve_scenario_with_levers_offices(self):
        """Test resolving scenario with office-specific levers."""
        # Mock config service to return office config
        self.mock_config_service.get_office_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0, "cat_curve": 0.1},
                        "AC": {"fte": 30.0, "price_1": 1300.0, "cat_curve": 0.08}
                    }
                }
            }
        }
        
        scenario_data = {
            "levers": {
                "offices": {
                    "Stockholm": {
                        "recruitment": {"A": 1.3, "AC": 1.2},
                        "progression": {"A": 1.2, "AC": 1.1}
                    }
                }
            }
        }
        
        result = self.resolver.resolve_scenario(scenario_data)
        
        # Verify offices config contains the office-specific lever multipliers
        offices_config = result['offices_config']
        assert "Stockholm" in offices_config
        
        stockholm_config = offices_config["Stockholm"]
        consultant_a = stockholm_config["roles"]["Consultant"]["A"]
        consultant_ac = stockholm_config["roles"]["Consultant"]["AC"]
        
        # Verify office-specific lever multipliers are applied
        assert consultant_a["recruitment_multiplier"] == 1.3
        assert consultant_ac["recruitment_multiplier"] == 1.2
        assert consultant_a["cat_curve"] == 0.12  # 0.1 * 1.2
        assert consultant_ac["cat_curve"] == 0.088  # 0.08 * 1.1
    
    def test_resolve_scenario_with_office_scope(self):
        """Test resolving scenario with office scope filtering."""
        # Mock config service to return multiple offices
        self.mock_config_service.get_office_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0}
                    }
                }
            },
            "Gothenburg": {
                "name": "Gothenburg",
                "total_fte": 80,
                "journey": "Emerging Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 40.0, "price_1": 1100.0}
                    }
                }
            },
            "Malmö": {
                "name": "Malmö",
                "total_fte": 60,
                "journey": "New Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 30.0, "price_1": 1000.0}
                    }
                }
            }
        }
        
        scenario_data = {
            "office_scope": ["Stockholm", "Gothenburg"]
        }
        
        result = self.resolver.resolve_scenario(scenario_data)
        
        # Verify only specified offices are included
        offices_config = result['offices_config']
        assert "Stockholm" in offices_config
        assert "Gothenburg" in offices_config
        assert "Malmö" not in offices_config
    
    def test_resolve_scenario_progression_cap(self):
        """Test that progression lever is capped at 1.0."""
        # Mock config service to return office config
        self.mock_config_service.get_office_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0, "cat_curve": 0.1}
                    }
                }
            }
        }
        
        scenario_data = {
            "levers": {
                "global": {
                    "progression": {"A": 1.5}  # Should be capped at 1.0
                }
            }
        }
        
        result = self.resolver.resolve_scenario(scenario_data)
        
        # Verify CAT curve is capped at 1.0
        offices_config = result['offices_config']
        stockholm_config = offices_config["Stockholm"]
        consultant_a = stockholm_config["roles"]["Consultant"]["A"]
        
        assert consultant_a["cat_curve"] == 0.1  # Should remain at original value (capped)
    
    def test_resolve_scenario_complex_combination(self):
        """Test resolving scenario with complex combination of baseline and levers."""
        # Mock config service to return office config
        self.mock_config_service.get_office_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0, "cat_curve": 0.1},
                        "AC": {"fte": 30.0, "price_1": 1300.0, "cat_curve": 0.08}
                    },
                    "Sales": {
                        "A": {"fte": 20.0, "price_1": 1000.0, "cat_curve": 0.05}
                    }
                }
            }
        }
        
        scenario_data = {
            "baseline_input": {
                "global": {
                    "recruitment": {
                        "Consultant": {
                            "recruitment_1": {"A": 5.0, "AC": 3.0}
                        },
                        "Sales": {
                            "recruitment_1": {"A": 2.0}
                        }
                    }
                },
                "offices": {
                    "Stockholm": {
                        "churn": {
                            "Consultant": {
                                "churn_1": {"A": 0.02, "AC": 0.015}
                            }
                        }
                    }
                }
            },
            "levers": {
                "global": {
                    "recruitment": {"A": 1.2, "AC": 1.1},
                    "progression": {"A": 1.1, "AC": 1.05}
                },
                "offices": {
                    "Stockholm": {
                        "price": {"A": 1.1, "AC": 1.05}
                    }
                }
            },
            "office_scope": ["Stockholm"]
        }
        
        result = self.resolver.resolve_scenario(scenario_data)
        
        # Verify complex combination is handled correctly
        offices_config = result['offices_config']
        assert "Stockholm" in offices_config
        
        stockholm_config = offices_config["Stockholm"]
        
        # Check Consultant A
        consultant_a = stockholm_config["roles"]["Consultant"]["A"]
        assert consultant_a["recruitment_abs_A"] == 5.0
        assert consultant_a["churn_abs_A"] == 0.02
        assert consultant_a["recruitment_multiplier"] == 1.2
        assert consultant_a["price_multiplier"] == 1.1
        assert consultant_a["cat_curve"] == 0.11  # 0.1 * 1.1
        
        # Check Consultant AC
        consultant_ac = stockholm_config["roles"]["Consultant"]["AC"]
        assert consultant_ac["recruitment_abs_AC"] == 3.0
        assert consultant_ac["churn_abs_AC"] == 0.015
        assert consultant_ac["recruitment_multiplier"] == 1.1
        assert consultant_ac["price_multiplier"] == 1.05
        assert consultant_ac["cat_curve"] == 0.084  # 0.08 * 1.05
        
        # Check Sales A (only global baseline, no office-specific overrides)
        sales_a = stockholm_config["roles"]["Sales"]["A"]
        assert sales_a["recruitment_abs_A"] == 2.0
        assert "churn_abs_A" not in sales_a  # No churn baseline for Sales
        assert sales_a["recruitment_multiplier"] == 1.2
        assert sales_a["cat_curve"] == 0.055  # 0.05 * 1.1
    
    def test_resolve_scenario_no_config_service(self):
        """Test resolving scenario when config service returns empty."""
        self.mock_config_service.get_office_config.return_value = {}
        
        scenario_data = {
            "baseline_input": {
                "global": {
                    "recruitment": {
                        "Consultant": {
                            "recruitment_1": {"A": 5.0}
                        }
                    }
                }
            }
        }
        
        result = self.resolver.resolve_scenario(scenario_data)
        
        # Should handle empty config gracefully
        assert result['offices_config'] == {}
        assert result['progression_config'] == {}
        assert result['cat_curves'] == {}
    
    def test_resolve_scenario_missing_role_in_baseline(self):
        """Test resolving scenario when baseline references non-existent role."""
        # Mock config service to return office config
        self.mock_config_service.get_office_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0}
                    }
                }
            }
        }
        
        scenario_data = {
            "baseline_input": {
                "global": {
                    "recruitment": {
                        "NonExistentRole": {
                            "recruitment_1": {"A": 5.0}
                        }
                    }
                }
            }
        }
        
        result = self.resolver.resolve_scenario(scenario_data)
        
        # Should handle missing role gracefully
        assert "Stockholm" in result['offices_config']
        stockholm_config = result['offices_config']["Stockholm"]
        assert "NonExistentRole" not in stockholm_config["roles"]
    
    def test_resolve_scenario_missing_level_in_baseline(self):
        """Test resolving scenario when baseline references non-existent level."""
        # Mock config service to return office config
        self.mock_config_service.get_office_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0}
                    }
                }
            }
        }
        
        scenario_data = {
            "baseline_input": {
                "global": {
                    "recruitment": {
                        "Consultant": {
                            "recruitment_1": {"NonExistentLevel": 5.0}
                        }
                    }
                }
            }
        }
        
        result = self.resolver.resolve_scenario(scenario_data)
        
        # Should handle missing level gracefully
        assert "Stockholm" in result['offices_config']
        stockholm_config = result['offices_config']["Stockholm"]
        consultant_a = stockholm_config["roles"]["Consultant"]["A"]
        assert "recruitment_abs_NonExistentLevel" not in consultant_a 