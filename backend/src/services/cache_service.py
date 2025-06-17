from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
from fastapi import HTTPException

class CacheEntry:
    """Represents a single cache entry with expiration"""
    def __init__(self, data: Any, ttl_seconds: int):
        self.data = data
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl_seconds)

class CacheService:
    """Service for caching year-level simulation data"""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = 3600  # 1 hour default TTL
    
    def get(self, key: str) -> Optional[Any]:
        """Get data from cache if it exists and hasn't expired"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if entry.is_expired():
            del self._cache[key]
            return None
        
        return entry.data
    
    def set(self, key: str, data: Any, ttl_seconds: Optional[int] = None) -> None:
        """Store data in cache with optional TTL"""
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        self._cache[key] = CacheEntry(data, ttl)
    
    def delete(self, key: str) -> None:
        """Remove data from cache"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
    
    def get_or_set(self, key: str, getter_func: callable, ttl_seconds: Optional[int] = None) -> Any:
        """Get data from cache or compute and store it if not present"""
        cached_data = self.get(key)
        if cached_data is not None:
            return cached_data
        
        data = getter_func()
        self.set(key, data, ttl_seconds)
        return data

class SimulationCacheService:
    """Specialized cache service for simulation data"""
    
    def __init__(self):
        self._cache = CacheService()
    
    def _get_year_key(self, year: int) -> str:
        """Generate cache key for year data"""
        return f"year_{year}"
    
    def _get_comparison_key(self, year1: int, year2: int) -> str:
        """Generate cache key for year comparison"""
        return f"compare_{min(year1, year2)}_{max(year1, year2)}"
    
    def get_year_data(self, year: int, include_monthly: bool = False) -> Optional[Dict[str, Any]]:
        """Get cached year data"""
        key = f"{self._get_year_key(year)}_{include_monthly}"
        return self._cache.get(key)
    
    def set_year_data(self, year: int, data: Dict[str, Any], include_monthly: bool = False) -> None:
        """Cache year data"""
        key = f"{self._get_year_key(year)}_{include_monthly}"
        self._cache.set(key, data)
    
    def get_comparison(self, year1: int, year2: int, include_monthly: bool = False) -> Optional[Dict[str, Any]]:
        """Get cached year comparison data"""
        key = f"{self._get_comparison_key(year1, year2)}_{include_monthly}"
        return self._cache.get(key)
    
    def set_comparison(self, year1: int, year2: int, data: Dict[str, Any], include_monthly: bool = False) -> None:
        """Cache year comparison data"""
        key = f"{self._get_comparison_key(year1, year2)}_{include_monthly}"
        self._cache.set(key, data)
    
    def invalidate_year(self, year: int) -> None:
        """Invalidate all cached data for a specific year"""
        # Invalidate year data
        self._cache.delete(f"{self._get_year_key(year)}_True")
        self._cache.delete(f"{self._get_year_key(year)}_False")
        
        # Invalidate all comparisons involving this year
        for key in list(self._cache._cache.keys()):
            if key.startswith("compare_") and str(year) in key:
                self._cache.delete(key)
    
    def invalidate_all(self) -> None:
        """Invalidate all cached simulation data"""
        self._cache.clear()

# Global cache service instance
simulation_cache = SimulationCacheService() 