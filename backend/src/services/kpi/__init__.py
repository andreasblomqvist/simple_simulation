"""
KPI Service Package

This package contains the refactored KPI calculation logic split into logical modules.
"""

from .kpi_service import KPIService
from .kpi_models import (
    EconomicParameters,
    FinancialKPIs,
    GrowthKPIs,
    JourneyKPIs,
    YearlyKPIs,
    AllKPIs
)

__all__ = [
    'KPIService',
    'EconomicParameters',
    'FinancialKPIs', 
    'GrowthKPIs',
    'JourneyKPIs',
    'YearlyKPIs',
    'AllKPIs'
] 