"""
Unit tests for OfficeBuilder service.
"""
import pytest
from unittest.mock import Mock, patch
from src.services.office_builder import OfficeBuilder
from src.services.people_initializer import PeopleInitializer


class TestOfficeBuilder:
    """Test cases for OfficeBuilder service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.office_builder = OfficeBuilder()
    
    def test_build_offices_from_config_empty(self):
        """Test building offices from empty config."""
        offices_config = {}
        progression_config = {}
        
        offices = self.office_builder.build_offices_from_config(offices_config, progression_config)
        
        assert offices == []
    
    def test_build_offices_from_config_single_office(self):
        """Test building a single office from config."""
        offices_config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0},
                        "AC": {"fte": 30.0, "price_1": 1300.0}
                    },
                    "Sales": {
                        "A": {"fte": 20.0, "price_1": 1000.0}
                    }
                }
            }
        }
        
        progression_config = {
            "Consultant": {
                "A": {"AC": 0.1, "C": 0.05},
                "AC": {"C": 0.15, "M": 0.08}
            },
            "Sales": {
                "A": {"AM": 0.12, "M": 0.06}
            }
        }
        
        with patch.object(PeopleInitializer, 'initialize_people_for_office') as mock_init:
            mock_init.return_value = []
            offices = self.office_builder.build_offices_from_config(offices_config, progression_config)
        
        assert len(offices) == 1
        office = offices[0]
        
        assert office.name == "Stockholm"
        assert office.total_fte == 100
        assert office.journey == "Mature Office"
        assert len(office.roles) == 2
        
        # Check Consultant role
        consultant_role = office.roles["Consultant"]
        assert len(consultant_role.levels) == 2
        
        level_a = consultant_role.levels["A"]
        assert level_a.fte == 50.0
        assert level_a.price_1 == 1200.0
        
        level_ac = consultant_role.levels["AC"]
        assert level_ac.fte == 30.0
        assert level_ac.price_1 == 1300.0
        
        # Check Sales role
        sales_role = office.roles["Sales"]
        assert len(sales_role.levels) == 1
        
        sales_a = sales_role.levels["A"]
        assert sales_a.fte == 20.0
        assert sales_a.price_1 == 1000.0
    
    def test_build_offices_from_config_multiple_offices(self):
        """Test building multiple offices from config."""
        offices_config = {
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
            }
        }
        
        progression_config = {
            "Consultant": {
                "A": {"AC": 0.1}
            }
        }
        
        with patch.object(PeopleInitializer, 'initialize_people_for_office') as mock_init:
            mock_init.return_value = []
            offices = self.office_builder.build_offices_from_config(offices_config, progression_config)
        
        assert len(offices) == 2
        
        # Check Stockholm
        stockholm = offices[0]
        assert stockholm.name == "Stockholm"
        assert stockholm.total_fte == 100
        assert stockholm.journey == "Mature Office"
        
        # Check Gothenburg
        gothenburg = offices[1]
        assert gothenburg.name == "Gothenburg"
        assert gothenburg.total_fte == 80
        assert gothenburg.journey == "Emerging Office"
    
    def test_build_offices_with_lever_multipliers(self):
        """Test building offices with lever multipliers applied."""
        offices_config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 50.0,
                            "price_1": 1200.0,
                            "recruitment_multiplier": 1.2,
                            "churn_multiplier": 0.8,
                            "price_multiplier": 1.1,
                            "salary_multiplier": 1.05,
                            "utr_multiplier": 1.1,
                            "cat_curve": 0.11
                        }
                    }
                }
            }
        }
        
        progression_config = {
            "Consultant": {
                "A": {"AC": 0.1}
            }
        }
        
        with patch.object(PeopleInitializer, 'initialize_people_for_office') as mock_init:
            mock_init.return_value = []
            offices = self.office_builder.build_offices_from_config(offices_config, progression_config)
        
        assert len(offices) == 1
        office = offices[0]
        
        consultant_role = office.roles["Consultant"]
        level_a = consultant_role.levels["A"]
        
        # Check that lever multipliers are applied
        assert level_a.recruitment_multiplier == 1.2
        assert level_a.churn_multiplier == 0.8
        assert level_a.price_multiplier == 1.1
        assert level_a.salary_multiplier == 1.05
        assert level_a.utr_multiplier == 1.1
        assert level_a.cat_curve == 0.11
    
    def test_build_offices_with_absolute_values(self):
        """Test building offices with absolute recruitment and churn values."""
        offices_config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 50.0,
                            "price_1": 1200.0,
                            "recruitment_abs_A": 5.0,
                            "churn_abs_A": 0.02
                        }
                    }
                }
            }
        }
        
        progression_config = {
            "Consultant": {
                "A": {"AC": 0.1}
            }
        }
        
        with patch.object(PeopleInitializer, 'initialize_people_for_office') as mock_init:
            mock_init.return_value = []
            offices = self.office_builder.build_offices_from_config(offices_config, progression_config)
        
        assert len(offices) == 1
        office = offices[0]
        
        consultant_role = office.roles["Consultant"]
        level_a = consultant_role.levels["A"]
        
        # Check that absolute values are set
        assert level_a.recruitment_abs_A == 5.0
        assert level_a.churn_abs_A == 0.02
    
    def test_build_offices_with_progression_config(self):
        """Test building offices with progression configuration."""
        offices_config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0},
                        "AC": {"fte": 30.0, "price_1": 1300.0},
                        "C": {"fte": 20.0, "price_1": 1400.0}
                    }
                }
            }
        }
        
        progression_config = {
            "Consultant": {
                "A": {"AC": 0.1, "C": 0.05},
                "AC": {"C": 0.15, "M": 0.08},
                "C": {"M": 0.12, "SM": 0.06}
            }
        }
        
        with patch.object(PeopleInitializer, 'initialize_people_for_office') as mock_init:
            mock_init.return_value = []
            offices = self.office_builder.build_offices_from_config(offices_config, progression_config)
        
        assert len(offices) == 1
        office = offices[0]
        
        consultant_role = office.roles["Consultant"]
        
        # Check that progression config is applied
        level_a = consultant_role.levels["A"]
        assert level_a.progression_to_AC == 0.1
        assert level_a.progression_to_C == 0.05
        
        level_ac = consultant_role.levels["AC"]
        assert level_ac.progression_to_C == 0.15
        assert level_ac.progression_to_M == 0.08
        
        level_c = consultant_role.levels["C"]
        assert level_c.progression_to_M == 0.12
        assert level_c.progression_to_SM == 0.06
    
    def test_build_offices_with_people_initialization(self):
        """Test building offices with people initialization."""
        offices_config = {
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
        
        progression_config = {
            "Consultant": {
                "A": {"AC": 0.1}
            }
        }
        
        # Mock people initialization
        mock_people = [
            Mock(name="Person1", role="Consultant", level="A", months_in_role=6),
            Mock(name="Person2", role="Consultant", level="A", months_in_role=12)
        ]
        
        with patch.object(PeopleInitializer, 'initialize_people_for_office') as mock_init:
            mock_init.return_value = mock_people
            offices = self.office_builder.build_offices_from_config(offices_config, progression_config)
        
        assert len(offices) == 1
        office = offices[0]
        
        # Verify people initialization was called
        mock_init.assert_called_once()
        call_args = mock_init.call_args
        assert call_args[0][0] == office  # First argument should be the office
        assert call_args[0][1] == progression_config  # Second argument should be progression config
    
    def test_build_offices_missing_required_fields(self):
        """Test building offices with missing required fields."""
        offices_config = {
            "Stockholm": {
                # Missing name, total_fte, journey
                "roles": {
                    "Consultant": {
                        "A": {"fte": 50.0, "price_1": 1200.0}
                    }
                }
            }
        }
        
        progression_config = {}
        
        with patch.object(PeopleInitializer, 'initialize_people_for_office') as mock_init:
            mock_init.return_value = []
            offices = self.office_builder.build_offices_from_config(offices_config, progression_config)
        
        # Should handle missing fields gracefully
        assert len(offices) == 1
        office = offices[0]
        
        # Default values should be used
        assert office.name == "Stockholm"  # Uses key as name
        assert office.total_fte == 0  # Default value
        assert office.journey == ""  # Default value
    
    def test_build_offices_empty_roles(self):
        """Test building offices with empty roles."""
        offices_config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {}
            }
        }
        
        progression_config = {}
        
        with patch.object(PeopleInitializer, 'initialize_people_for_office') as mock_init:
            mock_init.return_value = []
            offices = self.office_builder.build_offices_from_config(offices_config, progression_config)
        
        assert len(offices) == 1
        office = offices[0]
        
        # Should have no roles
        assert len(office.roles) == 0
    
    def test_build_offices_empty_levels(self):
        """Test building offices with empty levels in a role."""
        offices_config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {}
                }
            }
        }
        
        progression_config = {
            "Consultant": {}
        }
        
        with patch.object(PeopleInitializer, 'initialize_people_for_office') as mock_init:
            mock_init.return_value = []
            offices = self.office_builder.build_offices_from_config(offices_config, progression_config)
        
        assert len(offices) == 1
        office = offices[0]
        
        consultant_role = office.roles["Consultant"]
        # Should have no levels
        assert len(consultant_role.levels) == 0
    
    def test_build_offices_complex_structure(self):
        """Test building offices with complex structure."""
        offices_config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 200,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 80.0,
                            "price_1": 1200.0,
                            "price_2": 1250.0,
                            "recruitment_multiplier": 1.2,
                            "churn_multiplier": 0.8,
                            "recruitment_abs_A": 8.0,
                            "churn_abs_A": 0.025
                        },
                        "AC": {
                            "fte": 60.0,
                            "price_1": 1300.0,
                            "price_2": 1350.0,
                            "recruitment_multiplier": 1.1,
                            "churn_multiplier": 0.9,
                            "recruitment_abs_AC": 6.0,
                            "churn_abs_AC": 0.02
                        }
                    },
                    "Sales": {
                        "A": {
                            "fte": 40.0,
                            "price_1": 1000.0,
                            "recruitment_multiplier": 1.15,
                            "churn_multiplier": 0.85
                        },
                        "AM": {
                            "fte": 20.0,
                            "price_1": 1100.0,
                            "recruitment_multiplier": 1.05,
                            "churn_multiplier": 0.95
                        }
                    }
                }
            }
        }
        
        progression_config = {
            "Consultant": {
                "A": {"AC": 0.1, "C": 0.05},
                "AC": {"C": 0.15, "M": 0.08}
            },
            "Sales": {
                "A": {"AM": 0.12, "M": 0.06},
                "AM": {"M": 0.18, "SM": 0.09}
            }
        }
        
        with patch.object(PeopleInitializer, 'initialize_people_for_office') as mock_init:
            mock_init.return_value = []
            offices = self.office_builder.build_offices_from_config(offices_config, progression_config)
        
        assert len(offices) == 1
        office = offices[0]
        
        assert office.name == "Stockholm"
        assert office.total_fte == 200
        assert office.journey == "Mature Office"
        assert len(office.roles) == 2
        
        # Check Consultant role
        consultant_role = office.roles["Consultant"]
        assert len(consultant_role.levels) == 2
        
        consultant_a = consultant_role.levels["A"]
        assert consultant_a.fte == 80.0
        assert consultant_a.price_1 == 1200.0
        assert consultant_a.price_2 == 1250.0
        assert consultant_a.recruitment_multiplier == 1.2
        assert consultant_a.churn_multiplier == 0.8
        assert consultant_a.recruitment_abs_A == 8.0
        assert consultant_a.churn_abs_A == 0.025
        assert consultant_a.progression_to_AC == 0.1
        assert consultant_a.progression_to_C == 0.05
        
        consultant_ac = consultant_role.levels["AC"]
        assert consultant_ac.fte == 60.0
        assert consultant_ac.price_1 == 1300.0
        assert consultant_ac.price_2 == 1350.0
        assert consultant_ac.recruitment_multiplier == 1.1
        assert consultant_ac.churn_multiplier == 0.9
        assert consultant_ac.recruitment_abs_AC == 6.0
        assert consultant_ac.churn_abs_AC == 0.02
        assert consultant_ac.progression_to_C == 0.15
        assert consultant_ac.progression_to_M == 0.08
        
        # Check Sales role
        sales_role = office.roles["Sales"]
        assert len(sales_role.levels) == 2
        
        sales_a = sales_role.levels["A"]
        assert sales_a.fte == 40.0
        assert sales_a.price_1 == 1000.0
        assert sales_a.recruitment_multiplier == 1.15
        assert sales_a.churn_multiplier == 0.85
        assert sales_a.progression_to_AM == 0.12
        assert sales_a.progression_to_M == 0.06
        
        sales_am = sales_role.levels["AM"]
        assert sales_am.fte == 20.0
        assert sales_am.price_1 == 1100.0
        assert sales_am.recruitment_multiplier == 1.05
        assert sales_am.churn_multiplier == 0.95
        assert sales_am.progression_to_M == 0.18
        assert sales_am.progression_to_SM == 0.09 