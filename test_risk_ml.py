import unittest
from app.ml.hazard_risk_model import HazardRiskEngine

class TestHazardRiskModel(unittest.TestCase):
    def setUp(self):
        self.engine = HazardRiskEngine()

    def test_flood_risk_extreme_rainfall(self):
        inputs = {
            "recent_rainfall_mm": 240.0,
            "forecast_rainfall_mm": 150.0,
            "soil_moisture_pct": 95.0,
            "slope_deg": 1.5,
            "elevation_m": 45.0,
            "river_proximity_km": 0.3,
            "historical_disaster_freq": 8.0,
            "drainage_density_score": 1.2
        }
        res = self.engine.predict_risk(inputs, disaster_type="flood")
        self.assertEqual(res["disaster_type"], "flood")
        self.assertIn(res["risk_category"], ["high", "very_high"])
        self.assertGreaterEqual(res["risk_score"], 60.0)
        self.assertGreaterEqual(res["confidence_score"], 0.60)
        self.assertGreater(len(res["contributing_factors"]), 0)
        self.assertIn("DEMO/SIMULATED", res["model_metadata"]["data_provenance"])

    def test_landslide_risk_steep_slope(self):
        inputs = {
            "recent_rainfall_mm": 180.0,
            "forecast_rainfall_mm": 90.0,
            "soil_moisture_pct": 89.0,
            "slope_deg": 42.0,  # Critically steep
            "elevation_m": 1650.0,
            "river_proximity_km": 2.5,
            "historical_disaster_freq": 6.0,
            "drainage_density_score": 2.0
        }
        res = self.engine.predict_risk(inputs, disaster_type="landslide")
        self.assertEqual(res["disaster_type"], "landslide")
        self.assertIn(res["risk_category"], ["high", "very_high"])
        self.assertGreaterEqual(res["risk_score"], 65.0)

    def test_missing_data_imputation_and_warnings(self):
        # Empty input dict should trigger graceful regional default imputation and missing warnings
        res = self.engine.predict_risk({}, disaster_type="flood")
        self.assertGreater(len(res["missing_data_warnings"]), 0)
        self.assertIn("recent_rainfall_mm", res["input_features"])
        self.assertIsNotNone(res["risk_score"])

if __name__ == "__main__":
    unittest.main()
