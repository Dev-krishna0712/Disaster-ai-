"""
Hazard Risk Engine
Uses Scikit-learn (Random Forest Classifier + Gradient Boosting Regressor)
Trained on simulated geo-climatic domain baseline physics data.
Provides explainable factor contributions, uncertainty estimates, and missing data imputation.

NOTE: As per project guidelines, this baseline model is labeled:
DEMO/SIMULATED - Regional Geo-Climatic Baseline.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

class HazardRiskEngine:
    def __init__(self):
        self.flood_model = None
        self.landslide_model = None
        self.flood_regressor = None
        self.landslide_regressor = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            "recent_rainfall_mm",
            "forecast_rainfall_mm",
            "soil_moisture_pct",
            "slope_deg",
            "elevation_m",
            "river_proximity_km",
            "historical_disaster_freq",
            "drainage_density_score"
        ]
        self._initialize_baseline_models()

    def _generate_synthetic_training_data(self, n_samples: int = 1200) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Generates hydro-geological physics-consistent synthetic training data
        representing Indian monsoon and mountainous conditions.
        Explicitly marked as SIMULATED / BASELINE DATA.
        """
        np.random.seed(42)

        # Environmental features
        recent_rain = np.random.uniform(0, 450, n_samples)       # mm in last 48h
        forecast_rain = np.random.uniform(0, 250, n_samples)     # mm next 24h
        soil_moisture = np.random.uniform(10, 98, n_samples)     # % saturation
        slope = np.random.uniform(0, 65, n_samples)              # degrees
        elevation = np.random.uniform(5, 3500, n_samples)        # meters MSL
        river_dist = np.random.uniform(0.1, 40, n_samples)       # km
        hist_freq = np.random.uniform(0, 10, n_samples)          # past incidents
        drainage = np.random.uniform(0.5, 5.0, n_samples)        # drainage capacity

        df = pd.DataFrame({
            "recent_rainfall_mm": recent_rain,
            "forecast_rainfall_mm": forecast_rain,
            "soil_moisture_pct": soil_moisture,
            "slope_deg": slope,
            "elevation_m": elevation,
            "river_proximity_km": river_dist,
            "historical_disaster_freq": hist_freq,
            "drainage_density_score": drainage
        })

        # FLOOD RISK FORMULA (Hydrological physics proxy)
        # Heavy rain + saturated soil + near river + low elevation + poor drainage
        flood_raw = (
            (recent_rain / 450.0) * 32.0 +
            (forecast_rain / 250.0) * 22.0 +
            (soil_moisture / 100.0) * 18.0 +
            np.clip(1.0 - (river_dist / 15.0), 0, 1) * 18.0 +
            np.clip(1.0 - (elevation / 600.0), 0, 1) * 10.0 +
            (hist_freq / 10.0) * 8.0 -
            (drainage / 5.0) * 8.0
        )
        flood_score = np.clip(flood_raw * 1.15, 0, 100)
        flood_cats = np.where(flood_score > 75, "very_high",
                     np.where(flood_score > 50, "high",
                     np.where(flood_score > 25, "moderate", "low")))

        # LANDSLIDE RISK FORMULA (Geotechnical slope stability proxy)
        # Steep slope + high recent rainfall + saturated pore pressure + higher elevation
        landslide_raw = (
            np.clip(slope / 50.0, 0, 1.3) * 38.0 +
            (recent_rain / 400.0) * 26.0 +
            (soil_moisture / 100.0) * 18.0 +
            (hist_freq / 10.0) * 10.0 +
            np.clip(elevation / 2500.0, 0, 1.0) * 8.0
        )
        landslide_score = np.clip(landslide_raw, 0, 100)
        landslide_cats = np.where(landslide_score > 75, "very_high",
                         np.where(landslide_score > 50, "high",
                         np.where(landslide_score > 25, "moderate", "low")))

        return df, flood_cats, flood_score, landslide_cats, landslide_score

    def _initialize_baseline_models(self):
        """Trains Scikit-Learn Random Forest and Gradient Boosting estimators."""
        X, y_flood_cat, y_flood_score, y_land_cat, y_land_score = self._generate_synthetic_training_data()
        X_scaled = self.scaler.fit_transform(X)

        # Flood models
        self.flood_model = RandomForestClassifier(n_estimators=60, max_depth=8, random_state=42)
        self.flood_model.fit(X_scaled, y_flood_cat)

        self.flood_regressor = GradientBoostingRegressor(n_estimators=70, max_depth=4, random_state=42)
        self.flood_regressor.fit(X_scaled, y_flood_score)

        # Landslide models
        self.landslide_model = RandomForestClassifier(n_estimators=60, max_depth=8, random_state=42)
        self.landslide_model.fit(X_scaled, y_land_cat)

        self.landslide_regressor = GradientBoostingRegressor(n_estimators=70, max_depth=4, random_state=42)
        self.landslide_regressor.fit(X_scaled, y_land_score)

        self.is_trained = True

    def predict_risk(self, inputs: Dict[str, Any], disaster_type: str = "flood") -> Dict[str, Any]:
        """
        Validates input features, handles missing values with explainable warnings,
        computes Scikit-learn predictions, and outputs factor explanations.
        """
        disaster_type = disaster_type.lower()
        if disaster_type not in ["flood", "landslide"]:
            disaster_type = "flood"

        warnings = []
        imputed_features = {}

        # Default fallback values representing typical Indian geographical baseline
        defaults = {
            "recent_rainfall_mm": 25.0,
            "forecast_rainfall_mm": 15.0,
            "soil_moisture_pct": 45.0,
            "slope_deg": 8.0 if disaster_type == "flood" else 22.0,
            "elevation_m": 150.0 if disaster_type == "flood" else 1200.0,
            "river_proximity_km": 5.0,
            "historical_disaster_freq": 2.0,
            "drainage_density_score": 2.5
        }

        feature_vector = []
        for feat in self.feature_names:
            val = inputs.get(feat)
            if val is None or str(val).strip() == "":
                fallback = defaults[feat]
                warnings.append(f"Missing '{feat}' — defaulted to regional baseline {fallback}")
                imputed_features[feat] = fallback
                feature_vector.append(fallback)
            else:
                try:
                    num_val = float(val)
                    # Enforce realistic bounds
                    if feat == "slope_deg":
                        num_val = max(0.0, min(89.0, num_val))
                    elif feat in ["soil_moisture_pct"]:
                        num_val = max(0.0, min(100.0, num_val))
                    elif feat in ["recent_rainfall_mm", "forecast_rainfall_mm"]:
                        num_val = max(0.0, min(1000.0, num_val))
                    elif feat == "river_proximity_km":
                        num_val = max(0.05, min(200.0, num_val))

                    imputed_features[feat] = num_val
                    feature_vector.append(num_val)
                except (ValueError, TypeError):
                    fallback = defaults[feat]
                    warnings.append(f"Invalid '{feat}' ({val}) — defaulted to {fallback}")
                    imputed_features[feat] = fallback
                    feature_vector.append(fallback)

        X_input = pd.DataFrame([feature_vector], columns=self.feature_names)
        X_scaled = self.scaler.transform(X_input)

        if disaster_type == "landslide":
            cat_preds = self.landslide_model.predict(X_scaled)[0]
            cat_probs = self.landslide_model.predict_proba(X_scaled)[0]
            score_pred = float(self.landslide_regressor.predict(X_scaled)[0])
            importances = self.landslide_model.feature_importances_
        else:
            cat_preds = self.flood_model.predict(X_scaled)[0]
            cat_probs = self.flood_model.predict_proba(X_scaled)[0]
            score_pred = float(self.flood_regressor.predict(X_scaled)[0])
            importances = self.flood_model.feature_importances_

        score_pred = round(max(0.0, min(100.0, score_pred)), 1)
        confidence = round(float(np.max(cat_probs)), 2)

        # Enforce consistency between regressor score and risk category
        if score_pred >= 75.0:
            category = "very_high"
        elif score_pred >= 50.0:
            category = "high"
        elif score_pred >= 25.0:
            category = "moderate"
        else:
            category = "low"

        # Generate Explainability breakdown
        contributing_factors = self._generate_explanations(
            imputed_features, disaster_type, importances
        )

        return {
            "disaster_type": disaster_type,
            "risk_category": category,
            "risk_score": score_pred,
            "confidence_score": confidence,
            "input_features": imputed_features,
            "contributing_factors": contributing_factors,
            "missing_data_warnings": warnings,
            "model_metadata": {
                "algorithm": "RandomForestClassifier + GradientBoostingRegressor Ensemble",
                "framework": "Scikit-learn",
                "training_status": "Pre-trained on simulated hydro-geological domain physics",
                "is_demo": True,
                "data_provenance": "DEMO/SIMULATED - Regional Geo-Climatic Baseline (Decision Support System)"
            }
        }

    def _generate_explanations(
        self, features: Dict[str, float], disaster_type: str, importances: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Produces transparent factor-by-factor contributions for human operators."""
        factors = []
        recent_rain = features["recent_rainfall_mm"]
        forecast_rain = features["forecast_rainfall_mm"]
        soil = features["soil_moisture_pct"]
        slope = features["slope_deg"]
        river_dist = features["river_proximity_km"]
        elevation = features["elevation_m"]

        if disaster_type == "flood":
            if recent_rain > 100:
                factors.append({
                    "factor": "Extreme Recent Rainfall",
                    "value": f"{recent_rain:.1f} mm in 48h",
                    "impact": "CRITICAL",
                    "detail": "Precipitation volume severely exceeds catchment absorption threshold."
                })
            elif recent_rain > 50:
                factors.append({
                    "factor": "Elevated Recent Rainfall",
                    "value": f"{recent_rain:.1f} mm in 48h",
                    "impact": "HIGH",
                    "detail": "Runoff generation is actively accumulating."
                })

            if river_dist < 2.0:
                factors.append({
                    "factor": "Immediate River Proximity",
                    "value": f"{river_dist:.2f} km",
                    "impact": "HIGH",
                    "detail": "Within natural overflow buffer during peak stage."
                })

            if soil > 80:
                factors.append({
                    "factor": "High Soil Saturation",
                    "value": f"{soil:.1f}%",
                    "impact": "HIGH",
                    "detail": "Near-complete soil water saturation limits further infiltration."
                })

            if forecast_rain > 40:
                factors.append({
                    "factor": "Upcoming Heavy Rainfall Forecast",
                    "value": f"{forecast_rain:.1f} mm in 24h",
                    "impact": "MODERATE",
                    "detail": "Imminent additional rainfall will compound peak discharge."
                })
        else: # Landslide
            if slope > 30:
                factors.append({
                    "factor": "Critically Steep Terrain Slope",
                    "value": f"{slope:.1f}°",
                    "impact": "CRITICAL",
                    "detail": "Gravitational shear stress dramatically increases debris failure risk."
                })
            elif slope > 20:
                factors.append({
                    "factor": "Steep Hillside Incline",
                    "value": f"{slope:.1f}°",
                    "impact": "HIGH",
                    "detail": "Moderate to high slope angle prone to slippage."
                })

            if recent_rain > 80:
                factors.append({
                    "factor": "High Monsoon Infiltration",
                    "value": f"{recent_rain:.1f} mm",
                    "impact": "CRITICAL",
                    "detail": "Pore-water pressure destabilizes unconsolidated topsoil."
                })

            if soil > 75:
                factors.append({
                    "factor": "Saturated Soil Mantle",
                    "value": f"{soil:.1f}%",
                    "impact": "HIGH",
                    "detail": "Liquefaction and mudflow trigger conditions present."
                })

        if not factors:
            factors.append({
                "factor": "Stable Environmental Readings",
                "value": "Parameters within safe thresholds",
                "impact": "LOW",
                "detail": "Rainfall and terrain conditions indicate low immediate hazard potential."
            })

        return factors

hazard_engine = HazardRiskEngine()
