"""
Unit tests for ConfigService
"""

import pytest
import sys
import os

# Add backend src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'src'))

from services.config_service import ConfigService


class TestConfigService:
    """Unit tests for ConfigService"""

    @pytest.fixture
    def config_service(self):
        """Create a ConfigService instance"""
        return ConfigService()

    def test_config_service_initialization(self, config_service):
        """Test that ConfigService initializes correctly"""
        assert config_service is not None
        assert hasattr(config_service, 'config_file_path')
        assert hasattr(config_service, '_cached_config')
        assert hasattr(config_service, '_file_mtime')

    def test_get_configuration(self, config_service):
        """Test configuration loading"""
        config = config_service.get_configuration()
        
        assert config is not None
        assert isinstance(config, dict)
        assert len(config) > 0
        
        # Check that offices have required fields
        office_name = list(config.keys())[0]
        office = config[office_name]
        assert 'name' in office
        assert 'total_fte' in office
        assert 'roles' in office

    def test_get_office_names(self, config_service):
        """Test getting office names list"""
        office_names = config_service.get_office_names()
        
        assert isinstance(office_names, list)
        assert len(office_names) > 0
        
        # Check office name structure
        office_name = office_names[0]
        assert isinstance(office_name, str)
        assert len(office_name) > 0

    def test_update_configuration_flat_format(self, config_service):
        """Test configuration update with flat format"""
        # Get initial config
        initial_config = config_service.get_configuration()
        
        # Find Stockholm office for testing
        stockholm = initial_config.get('Stockholm')
        assert stockholm is not None
        
        original_value = stockholm['roles']['Consultant']['A']['recruitment_1']
        new_value = 0.07  # 7%
        
        # Update using flat format
        updates = {"Stockholm.Consultant.A.recruitment_1": new_value}
        result = config_service.update_configuration(updates)
        
        assert result >= 0  # Should return number of updates
        
        # Verify the update
        updated_config = config_service.get_configuration()
        updated_stockholm = updated_config.get('Stockholm')
        assert updated_stockholm['roles']['Consultant']['A']['recruitment_1'] == new_value
        
        # Restore original value
        config_service.update_configuration({"Stockholm.Consultant.A.recruitment_1": original_value})

    def test_update_configuration_nested_format(self, config_service):
        """Test configuration update with nested format"""
        initial_config = config_service.get_configuration()
        
        stockholm = initial_config.get('Stockholm')
        original_value = stockholm['roles']['Consultant']['A']['churn_1']
        new_value = 0.02  # 2%
        
        # Update using nested format
        updates = {
            "Stockholm": {
                "roles": {
                    "Consultant": {
                        "A": {
                            "churn_1": new_value
                        }
                    }
                }
            }
        }
        
        result = config_service.update_configuration(updates)
        
        assert result >= 0  # Should return number of updates
        
        # Verify the update
        updated_config = config_service.get_configuration()
        updated_stockholm = updated_config.get('Stockholm')
        assert updated_stockholm['roles']['Consultant']['A']['churn_1'] == new_value
        
        # Restore original value
        config_service.update_configuration({"Stockholm.Consultant.A.churn_1": original_value})

    def test_update_configuration_invalid_path(self, config_service):
        """Test configuration update with invalid path"""
        initial_config = config_service.get_configuration()
        
        updates = {"NonExistent.Office.Role.Level.field": 0.05}
        result = config_service.update_configuration(updates)
        
        # Should not crash, but may not update anything
        assert result >= 0
        
        # Config should remain unchanged
        final_config = config_service.get_configuration()
        assert len(final_config) == len(initial_config)

    def test_configuration_persistence(self, config_service):
        """Test that configuration changes are persisted"""
        initial_config = config_service.get_configuration()
        
        # Make a change
        original_value = 0.03
        new_value = 0.04
        updates = {"Stockholm.Consultant.A.progression_1": new_value}
        
        config_service.update_configuration(updates)
        
        # Create new service instance and verify persistence
        new_service = ConfigService()
        new_config = new_service.get_configuration()
        
        stockholm = new_config.get('Stockholm')
        assert stockholm['roles']['Consultant']['A']['progression_1'] == new_value
        
        # Restore original value
        config_service.update_configuration({"Stockholm.Consultant.A.progression_1": original_value})

    def test_get_office_config(self, config_service):
        """Test getting configuration for a specific office"""
        config = config_service.get_configuration()
        office_name = list(config.keys())[0]
        
        office_config = config_service.get_office_config(office_name)
        
        assert office_config is not None
        assert office_config['name'] == office_name
        assert 'total_fte' in office_config
        assert 'roles' in office_config

    def test_clear_cache(self, config_service):
        """Test cache clearing functionality"""
        # Load config to populate cache
        config_service.get_configuration()
        
        # Clear cache
        config_service.clear_cache()
        
        # Cache should be cleared
        assert config_service._cached_config is None
        assert config_service._file_mtime is None
