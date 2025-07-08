"""
Progression Models for Simulation Engine

This module contains dataclasses for progression rules and CAT curves
to replace Dict[str, Any] parameters in the simulation engine.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class Month(Enum):
    """Enumeration for months of the year"""
    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEP = 9
    OCT = 10
    NOV = 11
    DEC = 12


@dataclass
class LevelProgressionConfig:
    """Configuration for a specific level's progression rules"""
    level_name: str
    progression_months: List[int]  # List of month numbers (1-12) when progression occurs
    time_on_level: int = 6  # Minimum months required on level before progression
    progression_rate: float = 0.0  # Base progression rate (percentage)
    journey: str = "Journey 1"  # Career journey stage


@dataclass
class ProgressionConfig:
    """Complete progression configuration for all levels"""
    levels: Dict[str, LevelProgressionConfig]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProgressionConfig':
        """Create ProgressionConfig from dictionary data"""
        levels = {}
        for level_name, level_data in data.items():
            levels[level_name] = LevelProgressionConfig(
                level_name=level_name,
                progression_months=level_data.get('progression_months', []),
                time_on_level=level_data.get('time_on_level', 6),
                progression_rate=level_data.get('progression_rate', 0.0),
                journey=level_data.get('journey', 'Journey 1')
            )
        return cls(levels=levels)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for backward compatibility"""
        return {
            level_name: {
                'progression_months': config.progression_months,
                'time_on_level': config.time_on_level,
                'progression_rate': config.progression_rate,
                'journey': config.journey
            }
            for level_name, config in self.levels.items()
        }
    
    def get_level_config(self, level_name: str) -> Optional[LevelProgressionConfig]:
        """Get configuration for a specific level"""
        return self.levels.get(level_name)
    
    def is_progression_month(self, level_name: str, month: int) -> bool:
        """Check if a given month is a progression month for a level"""
        level_config = self.get_level_config(level_name)
        if level_config:
            return month in level_config.progression_months
        return False
    
    def get_minimum_tenure(self, level_name: str) -> int:
        """Get minimum tenure required for progression from a level"""
        level_config = self.get_level_config(level_name)
        return level_config.time_on_level if level_config else 6


@dataclass
class CATCurve:
    """CAT curve data for a specific level"""
    level_name: str
    cat_probabilities: Dict[str, float]  # CAT0, CAT6, CAT12, etc. -> probability
    
    @classmethod
    def from_dict(cls, level_name: str, data: Dict[str, float]) -> 'CATCurve':
        """Create CATCurve from dictionary data"""
        return cls(level_name=level_name, cat_probabilities=data)
    
    def get_probability(self, cat_category: str) -> float:
        """Get progression probability for a CAT category"""
        return self.cat_probabilities.get(cat_category, 0.0)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format for backward compatibility"""
        return self.cat_probabilities


@dataclass
class CATCurves:
    """Complete CAT curves configuration for all levels"""
    curves: Dict[str, CATCurve]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, float]]) -> 'CATCurves':
        """Create CATCurves from dictionary data"""
        curves = {}
        for level_name, cat_data in data.items():
            curves[level_name] = CATCurve.from_dict(level_name, cat_data)
        return cls(curves=curves)
    
    def to_dict(self) -> Dict[str, Dict[str, float]]:
        """Convert to dictionary format for backward compatibility"""
        return {
            level_name: curve.to_dict()
            for level_name, curve in self.curves.items()
        }
    
    def get_curve(self, level_name: str) -> Optional[CATCurve]:
        """Get CAT curve for a specific level"""
        return self.curves.get(level_name)
    
    def get_probability(self, level_name: str, cat_category: str) -> float:
        """Get progression probability for a level and CAT category"""
        curve = self.get_curve(level_name)
        if curve:
            return curve.get_probability(cat_category)
        return 0.0 