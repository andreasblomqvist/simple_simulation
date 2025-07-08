"""
Integration tests for absolute and percentage-based recruitment/churn support.
"""
import pytest
import json
import tempfile
import os
from src.services.simulation_engine import SimulationEngine
from src.services.config_service import ConfigService


class TestAbsolutePercentageIntegration:
    """Integration tests for absolute and percentage-based recruitment/churn support."""
    
    def test_simulation_with_mixed_absolute_percentage_config(self):
        """Test end-to-end simulation with mixed absolute and percentage values."""
        # Create a temporary config file
        config_data = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 50,
                            # Month 1: Absolute recruitment, percentage churn
                            "recruitment_1": 0.1,      # 10% fallback
                            "recruitment_abs_1": 5,    # 5 absolute (overrides)
                            "churn_1": 0.05,           # 5% fallback
                            "churn_abs_1": None,       # Use percentage
                            
                            # Month 2: Percentage recruitment, absolute churn
                            "recruitment_2": 0.1,      # 10% fallback
                            "recruitment_abs_2": None, # Use percentage
                            "churn_2": 0.05,           # 5% fallback
                            "churn_abs_2": 2,          # 2 absolute (overrides)
                            
                            # Other months: Default values
                            "recruitment_3": 0.1, "recruitment_4": 0.1, "recruitment_5": 0.1, "recruitment_6": 0.1,
                            "recruitment_7": 0.1, "recruitment_8": 0.1, "recruitment_9": 0.1, "recruitment_10": 0.1,
                            "recruitment_11": 0.1, "recruitment_12": 0.1,
                            "churn_3": 0.05, "churn_4": 0.05, "churn_5": 0.05, "churn_6": 0.05,
                            "churn_7": 0.05, "churn_8": 0.05, "churn_9": 0.05, "churn_10": 0.05,
                            "churn_11": 0.05, "churn_12": 0.05,
                            "price_1": 1000, "price_2": 1000, "price_3": 1000, "price_4": 1000,
                            "price_5": 1000, "price_6": 1000, "price_7": 1000, "price_8": 1000,
                            "price_9": 1000, "price_10": 1000, "price_11": 1000, "price_12": 1000,
                            "salary_1": 50000, "salary_2": 50000, "salary_3": 50000, "salary_4": 50000,
                            "salary_5": 50000, "salary_6": 50000, "salary_7": 50000, "salary_8": 50000,
                            "salary_9": 50000, "salary_10": 50000, "salary_11": 50000, "salary_12": 50000,
                            "utr_1": 0.85, "utr_2": 0.85, "utr_3": 0.85, "utr_4": 0.85,
                            "utr_5": 0.85, "utr_6": 0.85, "utr_7": 0.85, "utr_8": 0.85,
                            "utr_9": 0.85, "utr_10": 0.85, "utr_11": 0.85, "utr_12": 0.85
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file_path = f.name
        
        try:
            # Create config service with temporary file
            config_service = ConfigService(config_file_path)
            
            # Create simulation engine
            engine = SimulationEngine(config_service)
            
            # Run a short simulation (2 months)
            results = engine.run_simulation(
                start_year=2025, start_month=1,
                end_year=2025, end_month=2
            )
            
            # Verify results contain the expected data
            assert results is not None
            assert "offices" not in results
            
            # Check that the simulation ran without errors
            stockholm_data = results["years"]["2025"]["offices"]["Stockholm"]
            assert "levels" in stockholm_data
            
            # Verify that the monthly metrics contain method information
            consultant_a_months = stockholm_data["levels"]["Consultant"]["A"]
            assert isinstance(consultant_a_months, list)
            assert "churned" in consultant_a_months[0]
            assert "price" in consultant_a_months[0]
            assert "salary" in consultant_a_months[0]
            assert "utr" in consultant_a_months[0]
            
            # Check that recruitment and churn methods are tracked
            jan_metrics = consultant_a_months[0]
            feb_metrics = consultant_a_months[1]
            
            # Verify Consultant.A level exists and has method tracking
            if "Consultant" in jan_metrics and "A" in jan_metrics["Consultant"]:
                level_metrics = jan_metrics["Consultant"]["A"]
                assert "recruitment_method" in level_metrics
                assert "churn_method" in level_metrics
                assert "recruitment_details" in level_metrics
                assert "churn_details" in level_metrics
                
                # Verify the methods used are correct
                assert level_metrics["recruitment_method"] == "absolute"  # recruitment_abs_1 = 5
                assert level_metrics["churn_method"] == "percentage"      # churn_abs_1 = None
            
            if "Consultant" in feb_metrics and "A" in feb_metrics["Consultant"]:
                level_metrics = feb_metrics["Consultant"]["A"]
                assert "recruitment_method" in level_metrics
                assert "churn_method" in level_metrics
                
                # Verify the methods used are correct
                assert level_metrics["recruitment_method"] == "percentage"  # recruitment_abs_2 = None
                assert level_metrics["churn_method"] == "absolute"          # churn_abs_2 = 2
        
        finally:
            # Clean up temporary file
            if os.path.exists(config_file_path):
                os.unlink(config_file_path)
    
    def test_simulation_backward_compatibility(self):
        """Test that existing percentage-only configurations continue to work."""
        # Create a config with only percentage values (backward compatible)
        config_data = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 50,
                            "recruitment_1": 0.1,      # 10% recruitment
                            "recruitment_2": 0.1,      # 10% recruitment
                            "churn_1": 0.05,           # 5% churn
                            "churn_2": 0.05,           # 5% churn
                            # Other months: Default values
                            "recruitment_3": 0.1, "recruitment_4": 0.1, "recruitment_5": 0.1, "recruitment_6": 0.1,
                            "recruitment_7": 0.1, "recruitment_8": 0.1, "recruitment_9": 0.1, "recruitment_10": 0.1,
                            "recruitment_11": 0.1, "recruitment_12": 0.1,
                            "churn_3": 0.05, "churn_4": 0.05, "churn_5": 0.05, "churn_6": 0.05,
                            "churn_7": 0.05, "churn_8": 0.05, "churn_9": 0.05, "churn_10": 0.05,
                            "churn_11": 0.05, "churn_12": 0.05,
                            "price_1": 1000, "price_2": 1000, "price_3": 1000, "price_4": 1000,
                            "price_5": 1000, "price_6": 1000, "price_7": 1000, "price_8": 1000,
                            "price_9": 1000, "price_10": 1000, "price_11": 1000, "price_12": 1000,
                            "salary_1": 50000, "salary_2": 50000, "salary_3": 50000, "salary_4": 50000,
                            "salary_5": 50000, "salary_6": 50000, "salary_7": 50000, "salary_8": 50000,
                            "salary_9": 50000, "salary_10": 50000, "salary_11": 50000, "salary_12": 50000,
                            "utr_1": 0.85, "utr_2": 0.85, "utr_3": 0.85, "utr_4": 0.85,
                            "utr_5": 0.85, "utr_6": 0.85, "utr_7": 0.85, "utr_8": 0.85,
                            "utr_9": 0.85, "utr_10": 0.85, "utr_11": 0.85, "utr_12": 0.85
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file_path = f.name
        
        try:
            # Create config service with temporary file
            config_service = ConfigService(config_file_path)
            
            # Create simulation engine
            engine = SimulationEngine(config_service)
            
            # Run a short simulation (2 months)
            results = engine.run_simulation(
                start_year=2025, start_month=1,
                end_year=2025, end_month=2
            )
            
            # Verify results contain the expected data
            assert results is not None
            assert "offices" not in results
            
            # Check that the simulation ran without errors
            stockholm_data = results["years"]["2025"]["offices"]["Stockholm"]
            assert "levels" in stockholm_data
            
            # Verify that all methods used are "percentage"
            consultant_a_months = stockholm_data["levels"]["Consultant"]["A"]
            assert isinstance(consultant_a_months, list)
            for month_data in consultant_a_months:
                if "Consultant" in month_data and "A" in month_data["Consultant"]:
                    level_metrics = month_data["Consultant"]["A"]
                    assert "recruitment_method" in level_metrics
                    assert "churn_method" in level_metrics
                    assert level_metrics["recruitment_method"] == "percentage"
                    assert level_metrics["churn_method"] == "percentage"
        
        finally:
            # Clean up temporary file
            if os.path.exists(config_file_path):
                os.unlink(config_file_path)


if __name__ == "__main__":
    pytest.main([__file__]) 