"""
Scenario Storage Service - Handles storage and retrieval of scenario data.

This service has a single responsibility: manage the persistence of scenario
definitions and results to/from the file system.
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from .scenario_models import ScenarioDefinition

logger = logging.getLogger(__name__)

class ScenarioStorageService:
    """
    Handles storage and retrieval of scenario definitions and results.
    Focused solely on file I/O operations and data persistence.
    """
    
    def __init__(self, storage_dir: str = 'data/scenarios'):
        """
        Initialize the storage service.
        
        Args:
            storage_dir: Directory to store scenario files
        """
        self.storage_dir = storage_dir
        self.definitions_dir = os.path.join(storage_dir, 'definitions')
        self.results_dir = os.path.join(storage_dir, 'results')
        
        # Create directories if they don't exist
        os.makedirs(self.definitions_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
    
    def create_scenario(self, scenario_def: ScenarioDefinition) -> str:
        """
        Create and save a new scenario definition.
        
        Args:
            scenario_def: The scenario definition to save
            
        Returns:
            The generated scenario ID
        """
        # Generate unique ID if not provided
        if not scenario_def.id:
            scenario_def.id = str(uuid.uuid4())
        
        # Set creation timestamp if not provided
        if not scenario_def.created_at:
            scenario_def.created_at = datetime.now().isoformat()
        
        # Set updated timestamp
        scenario_def.updated_at = datetime.now().isoformat()
        
        # Save to file
        file_path = os.path.join(self.definitions_dir, f"{scenario_def.id}.json")
        try:
            with open(file_path, 'w') as f:
                json.dump(scenario_def.model_dump(), f, indent=2, default=str)
            
            logger.info(f"Created scenario: {scenario_def.id} - {scenario_def.name}")
            return scenario_def.id
            
        except Exception as e:
            logger.error(f"Error creating scenario {scenario_def.id}: {e}")
            raise
    
    def get_scenario(self, scenario_id: str) -> Optional[ScenarioDefinition]:
        """
        Retrieve a scenario definition by ID.
        
        Args:
            scenario_id: The scenario ID to retrieve
            
        Returns:
            ScenarioDefinition if found, None otherwise
        """
        # Try new location first (definitions subdirectory)
        file_path = os.path.join(self.definitions_dir, f"{scenario_id}.json")
        
        # If not found, try legacy location (root directory)
        if not os.path.exists(file_path):
            file_path = os.path.join(self.storage_dir, f"{scenario_id}.json")
        
        if not os.path.exists(file_path):
            logger.warning(f"Scenario not found: {scenario_id}")
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert string timestamps back to datetime if needed
            if 'created_at' in data and isinstance(data['created_at'], str):
                data['created_at'] = data['created_at']
            if 'updated_at' in data and isinstance(data['updated_at'], str):
                data['updated_at'] = data['updated_at']
            
            return ScenarioDefinition(**data)
            
        except Exception as e:
            logger.error(f"Error reading scenario {scenario_id}: {e}")
            return None
    
    def update_scenario(self, scenario_id: str, scenario_def: ScenarioDefinition) -> bool:
        """
        Update an existing scenario definition.
        
        Args:
            scenario_id: The scenario ID to update
            scenario_def: The updated scenario definition
            
        Returns:
            True if successful, False if scenario not found
        """
        logger.info(f"[DEBUG] StorageService.update_scenario called with ID: {scenario_id}")
        logger.info(f"[DEBUG] Scenario definition name: {scenario_def.name}")
        
        # Check if scenario exists
        existing_scenario = self.get_scenario(scenario_id)
        if not existing_scenario:
            logger.warning(f"[DEBUG] Cannot update non-existent scenario: {scenario_id}")
            return False
        
        logger.info(f"[DEBUG] Found existing scenario: {existing_scenario.name}")
        
        # Set the ID and update timestamp
        scenario_def.id = scenario_id
        scenario_def.updated_at = datetime.now().isoformat()
        
        # Save updated scenario
        file_path = os.path.join(self.definitions_dir, f"{scenario_id}.json")
        logger.info(f"[DEBUG] Saving to file: {file_path}")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(scenario_def.model_dump(), f, indent=2, default=str)
            
            logger.info(f"[DEBUG] Successfully updated scenario: {scenario_id} - {scenario_def.name}")
            return True
            
        except Exception as e:
            logger.error(f"[DEBUG] Error updating scenario {scenario_id}: {e}")
            return False
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """
        Delete a scenario definition and its results.
        
        Args:
            scenario_id: The scenario ID to delete
            
        Returns:
            True if successful, False if scenario not found
        """
        definition_path = os.path.join(self.definitions_dir, f"{scenario_id}.json")
        results_path = os.path.join(self.results_dir, f"{scenario_id}_results.json")
        
        success = True
        
        # Delete definition file
        if os.path.exists(definition_path):
            try:
                os.remove(definition_path)
                logger.info(f"Deleted scenario definition: {scenario_id}")
            except Exception as e:
                logger.error(f"Error deleting scenario definition {scenario_id}: {e}")
                success = False
        
        # Delete results file
        if os.path.exists(results_path):
            try:
                os.remove(results_path)
                logger.info(f"Deleted scenario results: {scenario_id}")
            except Exception as e:
                logger.error(f"Error deleting scenario results {scenario_id}: {e}")
                success = False
        
        if not success:
            logger.warning(f"Partial deletion for scenario: {scenario_id}")
        
        return success
    
    def list_scenarios(self) -> List[Dict[str, Any]]:
        """
        List all saved scenario definitions.
        
        Returns:
            List of scenario metadata dictionaries
        """
        scenarios = []
        
        try:
            # Check new location (definitions subdirectory)
            if os.path.exists(self.definitions_dir):
                for filename in os.listdir(self.definitions_dir):
                    if filename.endswith('.json'):
                        scenario_id = filename[:-5]  # Remove .json extension
                        scenario = self.get_scenario(scenario_id)
                        
                        if scenario:
                            # Return metadata only
                            scenarios.append({
                                'id': scenario.id,
                                'name': scenario.name,
                                'description': scenario.description,
                                'created_at': scenario.created_at,
                                'updated_at': scenario.updated_at,
                                'time_range': scenario.time_range,
                                'office_scope': scenario.office_scope
                            })
            
            # Check legacy location (root directory)
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json') and not filename.endswith('_results.json'):
                    scenario_id = filename[:-5]  # Remove .json extension
                    # Skip if we already have this scenario from the definitions directory
                    if not any(s['id'] == scenario_id for s in scenarios):
                        scenario = self.get_scenario(scenario_id)
                        
                        if scenario:
                            # Return metadata only
                            scenarios.append({
                                'id': scenario.id,
                                'name': scenario.name,
                                'description': scenario.description,
                                'created_at': scenario.created_at,
                                'updated_at': scenario.updated_at,
                                'time_range': scenario.time_range,
                                'office_scope': scenario.office_scope
                            })
            
            # Sort by updated_at (most recent first)
            scenarios.sort(key=lambda x: x['updated_at'] or '', reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing scenarios: {e}")
        
        return scenarios
    
    def save_scenario_results(self, scenario_id: str, results: Dict[str, Any]) -> bool:
        """
        Save scenario execution results.
        
        Args:
            scenario_id: The scenario ID
            results: The results data to save
            
        Returns:
            True if successful, False otherwise
        """
        file_path = os.path.join(self.results_dir, f"{scenario_id}_results.json")
        
        try:
            # Add metadata
            results_with_metadata = {
                'scenario_id': scenario_id,
                'saved_at': datetime.now().isoformat(),
                'results': results
            }
            
            with open(file_path, 'w') as f:
                json.dump(results_with_metadata, f, indent=2, default=str)
            
            logger.info(f"Saved results for scenario: {scenario_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving results for scenario {scenario_id}: {e}")
            return False
    
    def get_scenario_results(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve scenario execution results.
        
        Args:
            scenario_id: The scenario ID
            
        Returns:
            Results data if found, None otherwise
        """
        file_path = os.path.join(self.results_dir, f"{scenario_id}_results.json")
        
        if not os.path.exists(file_path):
            logger.warning(f"Results not found for scenario: {scenario_id}")
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return data.get('results', {})
            
        except Exception as e:
            logger.error(f"Error reading results for scenario {scenario_id}: {e}")
            return None
    
    def scenario_exists(self, scenario_id: str) -> bool:
        """
        Check if a scenario definition exists.
        
        Args:
            scenario_id: The scenario ID to check
            
        Returns:
            True if scenario exists, False otherwise
        """
        # Check new location first
        file_path = os.path.join(self.definitions_dir, f"{scenario_id}.json")
        if os.path.exists(file_path):
            return True
        
        # Check legacy location
        file_path = os.path.join(self.storage_dir, f"{scenario_id}.json")
        return os.path.exists(file_path)
    
    def results_exist(self, scenario_id: str) -> bool:
        """
        Check if scenario results exist.
        
        Args:
            scenario_id: The scenario ID to check
            
        Returns:
            True if results exist, False otherwise
        """
        file_path = os.path.join(self.results_dir, f"{scenario_id}_results.json")
        return os.path.exists(file_path)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            definition_files = [f for f in os.listdir(self.definitions_dir) if f.endswith('.json')]
            results_files = [f for f in os.listdir(self.results_dir) if f.endswith('.json')]
            
            total_size = 0
            for file_path in [os.path.join(self.definitions_dir, f) for f in definition_files]:
                total_size += os.path.getsize(file_path)
            for file_path in [os.path.join(self.results_dir, f) for f in results_files]:
                total_size += os.path.getsize(file_path)
            
            return {
                'total_scenarios': len(definition_files),
                'total_results': len(results_files),
                'total_size_bytes': total_size,
                'storage_directory': self.storage_dir
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {
                'total_scenarios': 0,
                'total_results': 0,
                'total_size_bytes': 0,
                'storage_directory': self.storage_dir,
                'error': str(e)
            } 