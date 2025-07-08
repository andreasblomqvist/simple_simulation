"""
Data transformation service for scenario operations.
Handles conversion between different data formats and model objects.

This service has a single responsibility: transform data between different formats
while maintaining data integrity and providing validation.
"""
import logging
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel

from .logger_service import LoggerService
from .error_handler import ValidationError
from .simulation.progression_models import ProgressionConfig, CATCurves
from .kpi.kpi_models import EconomicParameters

logger = LoggerService("scenario_transformer")

class ScenarioTransformer:
    """
    Transforms data between different formats for scenario operations.
    Focused on data conversion, validation, and serialization.
    """
    
    def __init__(self):
        self.logger = logger
    
    def transform_scenario_to_economic_params(self, scenario_def: BaseModel, correlation_id: Optional[str] = None) -> EconomicParameters:
        """
        Transform scenario definition to EconomicParameters.
        
        Args:
            scenario_def: Scenario definition containing economic parameters
            correlation_id: Optional correlation ID for logging
            
        Returns:
            EconomicParameters object with validated and defaulted values
        """
        self.logger.info("Transforming scenario to economic parameters", correlation_id=correlation_id)
        
        try:
            # Extract economic parameters from scenario definition
            economic_params = getattr(scenario_def, 'economic_params', None) or {}
            
            # Define valid keys and their default values
            valid_keys = {
                'unplanned_absence',
                'other_expense', 
                'employment_cost_rate',
                'working_hours_per_month',
                'utilization',
                'price_increase',
                'salary_increase'
            }
            
            # Filter and validate parameters
            filtered_params = {k: v for k, v in economic_params.items() if k in valid_keys}
            
            # Create EconomicParameters with defaults
            economic_params_obj = EconomicParameters(
                unplanned_absence=filtered_params.get('unplanned_absence', 0.05),
                other_expense=filtered_params.get('other_expense', 19000000.0),
                employment_cost_rate=filtered_params.get('employment_cost_rate', 0.40),
                working_hours_per_month=filtered_params.get('working_hours_per_month', 166.4),
                utilization=filtered_params.get('utilization', 0.85),
                price_increase=filtered_params.get('price_increase', 0.03),
                salary_increase=filtered_params.get('salary_increase', 0.02)
            )
            
            self.logger.info("Economic parameters transformation completed", correlation_id=correlation_id, extra={
                "params_count": len(filtered_params),
                "defaults_used": len(valid_keys) - len(filtered_params)
            })
            
            return economic_params_obj
            
        except Exception as e:
            self.logger.error(f"Failed to transform economic parameters: {e}", correlation_id=correlation_id)
            raise ValidationError(f"Economic parameters transformation failed: {e}")
    
    def transform_dict_to_progression_config(self, progression_data: Dict[str, Any], correlation_id: Optional[str] = None) -> ProgressionConfig:
        """
        Transform dictionary data to ProgressionConfig model.
        
        Args:
            progression_data: Dictionary containing progression configuration
            correlation_id: Optional correlation ID for logging
            
        Returns:
            ProgressionConfig object
        """
        self.logger.info("Transforming dict to ProgressionConfig", correlation_id=correlation_id)
        
        try:
            # Handle None or empty data
            if progression_data is None:
                self.logger.warning("Progression data is None, using empty dict", correlation_id=correlation_id)
                progression_data = {}
            
            progression_config = ProgressionConfig.from_dict(progression_data)
            
            self.logger.info("ProgressionConfig transformation completed", correlation_id=correlation_id, extra={
                "levels_count": len(progression_data)
            })
            
            return progression_config
            
        except Exception as e:
            self.logger.error(f"Failed to transform ProgressionConfig: {e}", correlation_id=correlation_id)
            raise ValidationError(f"ProgressionConfig transformation failed: {e}")
    
    def transform_dict_to_cat_curves(self, cat_curves_data: Dict[str, Any], correlation_id: Optional[str] = None) -> CATCurves:
        """
        Transform dictionary data to CATCurves model.
        
        Args:
            cat_curves_data: Dictionary containing CAT curves data
            correlation_id: Optional correlation ID for logging
            
        Returns:
            CATCurves object
        """
        self.logger.info("Transforming dict to CATCurves", correlation_id=correlation_id)
        
        try:
            # Handle None or empty data
            if cat_curves_data is None:
                self.logger.warning("CAT curves data is None, using empty dict", correlation_id=correlation_id)
                cat_curves_data = {}
            
            cat_curves = CATCurves.from_dict(cat_curves_data)
            
            self.logger.info("CATCurves transformation completed", correlation_id=correlation_id, extra={
                "levels_count": len(cat_curves_data)
            })
            
            return cat_curves
            
        except Exception as e:
            self.logger.error(f"Failed to transform CATCurves: {e}", correlation_id=correlation_id)
            raise ValidationError(f"CATCurves transformation failed: {e}")
    
    def transform_results_to_serializable(self, results: Any, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Transform simulation results to serializable format.
        
        Args:
            results: Simulation results (can be model objects, dicts, etc.)
            correlation_id: Optional correlation ID for logging
            
        Returns:
            Serializable dictionary representation of results
        """
        self.logger.info("Transforming results to serializable format", correlation_id=correlation_id)
        
        try:
            # Convert to dictionary format
            serializable_results = self._to_dict(results)
            
            # Clean for serialization
            final_results = self._clean_for_serialization(serializable_results)
            
            self.logger.info("Results transformation completed", correlation_id=correlation_id, extra={
                "results_type": type(results).__name__
            })
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"Failed to transform results: {e}", correlation_id=correlation_id)
            raise ValidationError(f"Results transformation failed: {e}")
    
    def _to_dict(self, data: Any) -> Any:
        """
        Recursively convert data to dictionary format.
        
        Args:
            data: Data to convert
            
        Returns:
            Dictionary representation of data
        """
        # If the object has a model_dump method, call it and recurse
        if hasattr(data, 'model_dump') and callable(data.model_dump):
            return self._to_dict(data.model_dump())
        elif isinstance(data, dict):
            return {k: self._to_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._to_dict(item) for item in data]
        else:
            return data
    
    def _clean_for_serialization(self, data: Any) -> Any:
        """
        Clean data for JSON serialization.
        
        Args:
            data: Data to clean
            
        Returns:
            Cleaned data suitable for JSON serialization
        """
        if isinstance(data, dict):
            return {k: self._clean_for_serialization(v) for k, v in data.items() if k is not None}
        elif isinstance(data, list):
            return [self._clean_for_serialization(item) for item in data]
        elif isinstance(data, (int, float, str, bool, type(None))):
            return data
        else:
            return str(data)
    
    def transform_scenario_data_for_engine(self, resolved_data: Dict[str, Any], correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Transform resolved scenario data for simulation engine consumption.
        
        Args:
            resolved_data: Resolved scenario data
            correlation_id: Optional correlation ID for logging
            
        Returns:
            Engine-ready data with proper model objects
        """
        self.logger.info("Transforming scenario data for engine", correlation_id=correlation_id)
        
        try:
            # Transform progression config
            progression_config = self.transform_dict_to_progression_config(
                resolved_data['progression_config'], 
                correlation_id
            )
            
            # Transform CAT curves
            cat_curves = self.transform_dict_to_cat_curves(
                resolved_data['cat_curves'], 
                correlation_id
            )
            
            engine_data = {
                'offices': resolved_data['offices'],
                'progression_config': progression_config,
                'cat_curves': cat_curves
            }
            
            self.logger.info("Engine data transformation completed", correlation_id=correlation_id, extra={
                "offices_count": len(resolved_data['offices']),
                "has_progression_config": progression_config is not None,
                "has_cat_curves": cat_curves is not None
            })
            
            return engine_data
            
        except Exception as e:
            self.logger.error(f"Failed to transform engine data: {e}", correlation_id=correlation_id)
            raise ValidationError(f"Engine data transformation failed: {e}") 