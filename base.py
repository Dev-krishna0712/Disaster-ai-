"""
Base Data Provider Architecture
Provides standardized contract for weather, hydrological, and geospatial data sources.
Includes provenance tracking, cache management, and graceful degradation.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

class BaseDataProvider(ABC):
    def __init__(self, name: str, source_attribution: str, is_live_api: bool = False):
        self.name = name
        self.source_attribution = source_attribution
        self.is_live_api = is_live_api
        self.last_sync_time: Optional[datetime] = None
        self._cache: Dict[str, Any] = {}

    @abstractmethod
    def fetch_data(self, latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
        """Fetch observations or telemetry for given coordinates."""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "provider_name": self.name,
            "source_attribution": self.source_attribution,
            "is_live_api": self.is_live_api,
            "mode": "LIVE_FEED" if self.is_live_api else "DEMO/SIMULATED_BASELINE",
            "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None
        }
