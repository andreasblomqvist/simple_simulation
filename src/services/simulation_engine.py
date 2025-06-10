from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

class SimpleSimulationEngine:
    """A simplified workforce simulation engine."""
    
    def __init__(self):
        self.current_period = 0
        self.start_date = datetime.now()
        
    def run_simulation(self, 
                      initial_headcount: int,
                      growth_rate: float,
                      periods: int,
                      progression_matrix: Optional[Dict] = None) -> Dict:
        """
        Run a simple workforce simulation.
        
        Args:
            initial_headcount: Starting number of employees
            growth_rate: Monthly growth rate (e.g., 0.05 for 5%)
            periods: Number of months to simulate
            progression_matrix: Optional matrix for career progression
            
        Returns:
            Dict containing simulation results
        """
        results = {
            'headcount': [initial_headcount],
            'periods': periods,
            'growth_rate': growth_rate,
            'start_date': self.start_date.isoformat()
        }
        
        current_headcount = initial_headcount
        
        for period in range(1, periods + 1):
            # Apply growth
            growth = int(current_headcount * growth_rate)
            current_headcount += growth
            
            # Store results
            results['headcount'].append(current_headcount)
            
        return results
    
    def calculate_progression(self,
                            employee_level: int,
                            months_in_role: int,
                            progression_matrix: Dict) -> float:
        """
        Calculate probability of progression for an employee.
        
        Args:
            employee_level: Current career level
            months_in_role: Time in current role
            progression_matrix: Matrix defining progression probabilities
            
        Returns:
            Probability of progression (0-1)
        """
        if not progression_matrix:
            return 0.0
            
        base_prob = progression_matrix.get(employee_level, {}).get('base_probability', 0.0)
        time_factor = min(months_in_role / 12, 1.0)  # Cap at 1 year
        
        return base_prob * time_factor 