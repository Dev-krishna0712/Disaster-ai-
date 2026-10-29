"""
Geospatial Terrain & Elevation Provider
Provides elevation and slope gradients based on digital elevation modeling.
"""

from typing import Dict, Any
from app.data_providers.base import BaseDataProvider

class TerrainDataProvider(BaseDataProvider):
    def __init__(self):
        super().__init__(
            name="SRTM / CartoDEM Terrain Model",
            source_attribution="Digital Elevation Model (DEMO/Simulated Baseline)",
            is_live_api=False
        )

    def fetch_data(self, latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
        # Approximate elevation & slope gradient based on Indian physiography
        # Himalayan north
        if latitude > 29.0 and 75.0 <= longitude <= 88.0:
            elevation = 1850.0 + ((latitude - 29.0) * 450.0)
            slope = 34.5
            terrain_type = "High-relief Mountainous Terrain"
        # Western Ghats
        elif 8.0 <= latitude <= 16.0 and 74.0 <= longitude <= 77.0:
            elevation = 920.0
            slope = 26.0
            terrain_type = "Escarpment & Ghat Ridge"
        # Coastal lowlands
        elif (longitude < 73.5 and 8.0 <= latitude <= 21.0) or (longitude > 80.0 and 8.0 <= latitude <= 22.0 and latitude < 18.0):
            elevation = 14.0
            slope = 3.2
            terrain_type = "Coastal Alluvial Lowland"
        # Indo-Gangetic & Brahmaputra plains
        elif 24.0 <= latitude <= 27.5 and 80.0 <= longitude <= 95.0:
            elevation = 65.0
            slope = 2.1
            terrain_type = "Riverine Floodplain"
        else:
            elevation = 350.0
            slope = 8.5
            terrain_type = "Deccan Plateau"

        return {
            "latitude": latitude,
            "longitude": longitude,
            "elevation_m": round(elevation, 1),
            "slope_deg": round(slope, 1),
            "terrain_type": terrain_type,
            "metadata": self.get_metadata()
        }

terrain_provider = TerrainDataProvider()
