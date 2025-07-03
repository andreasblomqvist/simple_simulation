"""
Scenario Storage Service - Handles persistence and management of scenario definitions.

This service provides:
- Scenario definition persistence (create, read, update, delete)
- Results storage and retrieval
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from .scenario_models import (
    ScenarioDefinition,
    ScenarioRequest, 
    ScenarioResponse
)

logger = logging.getLogger(__name__)

class ScenarioStorageService:
    """
    Service for managing scenario definitions and results storage.
    Handles persistence and retrieval of scenarios and their results.
    """
    
    def __init__(self, storage_dir: str = None):
        # Hardcode to data/scenarios since environment variable is not being picked up
        if storage_dir is None:
            storage_dir = "data/scenarios"  # Hardcoded path instead of os.environ.get("SCENARIO_STORAGE_DIR", "data/scenarios")
        self.storage_dir = storage_dir
        self._ensure_storage_directory()
        # Log the absolute path for debugging
        abs_path = os.path.abspath(self.storage_dir)
        logger.info(f"[SCENARIO STORAGE] Using scenario storage directory: {abs_path}")
        print(f"[SCENARIO STORAGE] Using scenario storage directory: {abs_path}")
        print(f"[SCENARIO STORAGE] Directory exists: {os.path.exists(abs_path)}")
        if os.path.exists(self.storage_dir):
            files = os.listdir(self.storage_dir)
            print(f"[SCENARIO STORAGE] Files in directory: {files}")
    
    def _ensure_storage_directory(self):
        """Ensure the scenario storage directory exists."""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            logger.info(f"Created scenario storage directory: {self.storage_dir}")
    
    def create_scenario(self, scenario_def: ScenarioDefinition) -> str:
        """Create and save a new scenario definition."""
        scenario_id = str(uuid.uuid4())
        scenario_def.created_at = datetime.now()
        scenario_def.updated_at = datetime.now()
        
        scenario_data = {
            "id": scenario_id,
            "definition": scenario_def.model_dump(),
            "created_at": scenario_def.created_at.isoformat(),
            "updated_at": scenario_def.updated_at.isoformat()
        }
        
        file_path = os.path.join(self.storage_dir, f"{scenario_id}.json")
        with open(file_path, 'w') as f:
            json.dump(scenario_data, f, indent=2, default=str)
        
        logger.info(f"Created scenario: {scenario_id} - {scenario_def.name}")
        return scenario_id
    
    def get_scenario(self, scenario_id: str) -> Optional[ScenarioDefinition]:
        """Retrieve a scenario definition by ID."""
        file_path = os.path.join(self.storage_dir, f"{scenario_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                scenario_data = json.load(f)
            
            return ScenarioDefinition(**scenario_data["definition"])
        except Exception as e:
            logger.error(f"Error loading scenario {scenario_id}: {e}")
            return None
    
    def list_scenarios(self) -> List[Any]:
        """List all saved scenarios as full ScenarioDefinition objects with IDs."""
        scenarios = []
        print(f"[SCENARIO STORAGE] list_scenarios called, storage_dir: {self.storage_dir}")
        print(f"[SCENARIO STORAGE] Directory exists: {os.path.exists(self.storage_dir)}")
        if not os.path.exists(self.storage_dir):
            print(f"[SCENARIO STORAGE] Directory does not exist: {self.storage_dir}")
            return scenarios
        files = os.listdir(self.storage_dir)
        print(f"[SCENARIO STORAGE] All files in directory: {files}")
        for filename in files:
            # Only include scenario definition files, not results files
            if filename.endswith('.json') and not filename.endswith('_results.json'):
                print(f"[SCENARIO STORAGE] Processing file: {filename}")
                file_path = os.path.join(self.storage_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        scenario_data = json.load(f)
                    scenario_def = ScenarioDefinition(**scenario_data["definition"])
                    
                    # Extract scenario ID from filename (remove .json extension)
                    scenario_id = filename.replace('.json', '')
                    
                    # Create a dict with both the scenario definition and the ID
                    scenario_with_id = {
                        "id": scenario_id,
                        **scenario_def.model_dump()
                    }
                    scenarios.append(scenario_with_id)
                    print(f"[SCENARIO STORAGE] Successfully loaded scenario: {scenario_def.name}")
                except Exception as e:
                    logger.error(f"Error loading scenario from {filename}: {e}")
                    print(f"[SCENARIO STORAGE] Error loading scenario from {filename}: {e}")
                    print(f"[SCENARIO STORAGE] Data that failed: {scenario_data.get('definition', scenario_data)}")
        print(f"[SCENARIO STORAGE] Total scenarios found: {len(scenarios)}")
        scenarios.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return scenarios
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario definition and its results."""
        try:
            # Delete scenario definition file
            scenario_file = os.path.join(self.storage_dir, f"{scenario_id}.json")
            if os.path.exists(scenario_file):
                os.remove(scenario_file)
                logger.info(f"Deleted scenario definition: {scenario_id}")
            
            # Delete results file if it exists
            results_file = os.path.join(self.storage_dir, f"{scenario_id}_results.json")
            if os.path.exists(results_file):
                os.remove(results_file)
                logger.info(f"Deleted scenario results: {scenario_id}")
            
            return True
        except Exception as e:
            logger.error(f"Error deleting scenario {scenario_id}: {e}")
            return False
    
    def update_scenario(self, scenario_id: str, scenario_def: ScenarioDefinition) -> bool:
        """Update an existing scenario definition."""
        try:
            file_path = os.path.join(self.storage_dir, f"{scenario_id}.json")
            
            if not os.path.exists(file_path):
                return False
            
            # Update timestamps
            scenario_def.updated_at = datetime.now()
            
            # Load existing data to preserve created_at
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
            
            scenario_data = {
                "id": scenario_id,
                "definition": scenario_def.model_dump(),
                "created_at": existing_data.get("created_at"),
                "updated_at": scenario_def.updated_at.isoformat()
            }
            
            with open(file_path, 'w') as f:
                json.dump(scenario_data, f, indent=2, default=str)
            
            logger.info(f"Updated scenario: {scenario_id} - {scenario_def.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating scenario {scenario_id}: {e}")
            return False
    
    def save_scenario_results(self, scenario_id: str, results: Dict[str, Any]):
        """Save simulation results to storage."""
        self._save_scenario_results(scenario_id, results)
    
    def get_scenario_results(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get saved simulation results for a scenario."""
        try:
            results_file = os.path.join(self.storage_dir, f"{scenario_id}_results.json")
            if not os.path.exists(results_file):
                return None
            
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            return results
            
        except Exception as e:
            logger.error(f"Error loading scenario results for {scenario_id}: {e}")
            return None
    
    def _save_scenario_results(self, scenario_id: str, results: Dict[str, Any]):
        """Save simulation results to storage."""
        try:
            results_file = os.path.join(self.storage_dir, f"{scenario_id}_results.json")
            
            # Convert results to serializable format
            def clean_for_serialization(data):
                if isinstance(data, dict):
                    return {k: clean_for_serialization(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [clean_for_serialization(item) for item in data]
                elif hasattr(data, 'model_dump'):
                    return data.model_dump()
                elif hasattr(data, '__dict__'):
                    return {k: clean_for_serialization(v) for k, v in data.__dict__.items()}
                else:
                    return data
            
            clean_results = clean_for_serialization(results)
            
            with open(results_file, 'w') as f:
                json.dump(clean_results, f, indent=2, default=str)
            
            logger.info(f"Saved scenario results: {scenario_id}")
            
        except Exception as e:
            logger.error(f"Error saving scenario results for {scenario_id}: {e}")
            raise 