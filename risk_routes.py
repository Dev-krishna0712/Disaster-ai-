"""
AI Disaster Risk Engine Routes
Endpoints for predictive hazard modeling, explainable feature analysis,
historical assessment querying, and monitored regional risk zones.
"""

import json
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.database import db
from app.models.risk import RiskAssessment
from app.schemas.validators import RiskPredictSchema
from app.ml.hazard_risk_model import hazard_engine
from app.data_providers.imd_weather import imd_provider
from app.data_providers.terrain_elevation import terrain_provider

risk_bp = Blueprint("risk", __name__, url_prefix="/api/risk")

# Pre-defined monitored risk zones in India for interactive map and decision support
MONITORED_INDIAN_RISK_ZONES = [
    {
        "id": "zone-wayanad",
        "name": "Wayanad District, Western Ghats, Kerala",
        "latitude": 11.6854,
        "longitude": 76.1320,
        "disaster_type": "landslide",
        "terrain": "Steep Escarpment & Plantation Slopes",
        "recent_rainfall_mm": 210.0,
        "forecast_rainfall_mm": 130.0,
        "soil_moisture_pct": 92.0,
        "slope_deg": 38.0,
        "elevation_m": 1280.0,
        "river_proximity_km": 1.2,
        "historical_disaster_freq": 8.0,
        "drainage_density_score": 1.8,
        "risk_category": "very_high",
        "risk_score": 89.4,
        "description": "High saturation with gravitational slope instability warning."
    },
    {
        "id": "zone-joshimath",
        "name": "Joshimath / Chamoli, Uttarakhand",
        "latitude": 30.5574,
        "longitude": 79.5668,
        "disaster_type": "landslide",
        "terrain": "Himalayan Fault & Subsidence Zone",
        "recent_rainfall_mm": 115.0,
        "forecast_rainfall_mm": 85.0,
        "soil_moisture_pct": 84.0,
        "slope_deg": 42.0,
        "elevation_m": 1890.0,
        "river_proximity_km": 0.8,
        "historical_disaster_freq": 7.0,
        "drainage_density_score": 1.5,
        "risk_category": "very_high",
        "risk_score": 87.2,
        "description": "Structural slope stress along Alaknanda gorge corridor."
    },
    {
        "id": "zone-brahmaputra",
        "name": "Kaziranga / Brahmaputra Basin, Assam",
        "latitude": 26.5775,
        "longitude": 93.1711,
        "disaster_type": "flood",
        "terrain": "Major Riverine Alluvial Floodplain",
        "recent_rainfall_mm": 185.0,
        "forecast_rainfall_mm": 120.0,
        "soil_moisture_pct": 95.0,
        "slope_deg": 1.8,
        "elevation_m": 65.0,
        "river_proximity_km": 0.4,
        "historical_disaster_freq": 9.0,
        "drainage_density_score": 1.2,
        "risk_category": "very_high",
        "risk_score": 92.1,
        "description": "River stage exceeding high-flood-level; severe catchment inundation."
    },
    {
        "id": "zone-mumbai",
        "name": "Mithi River Catchment, Mumbai Suburban",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "disaster_type": "flood",
        "terrain": "Coastal Lowland Urban Basin",
        "recent_rainfall_mm": 140.0,
        "forecast_rainfall_mm": 90.0,
        "soil_moisture_pct": 88.0,
        "slope_deg": 2.5,
        "elevation_m": 8.0,
        "river_proximity_km": 0.3,
        "historical_disaster_freq": 8.5,
        "drainage_density_score": 1.6,
        "risk_category": "high",
        "risk_score": 78.5,
        "description": "High tide coinciding with heavy cloudburst runoff."
    },
    {
        "id": "zone-kuttanad",
        "name": "Kuttanad Below-Sea-Level Delta, Alappuzha, Kerala",
        "latitude": 9.3833,
        "longitude": 76.4500,
        "disaster_type": "flood",
        "terrain": "Sub-sea-level Delta Basin",
        "recent_rainfall_mm": 95.0,
        "forecast_rainfall_mm": 60.0,
        "soil_moisture_pct": 91.0,
        "slope_deg": 0.8,
        "elevation_m": -1.5,
        "river_proximity_km": 0.2,
        "historical_disaster_freq": 7.5,
        "drainage_density_score": 2.0,
        "risk_category": "high",
        "risk_score": 73.0,
        "description": "Prolonged backwater stagnation and estuarine ingress."
    },
    {
        "id": "zone-mandi",
        "name": "Beas River Basin, Mandi, Himachal Pradesh",
        "latitude": 31.7087,
        "longitude": 76.9320,
        "disaster_type": "landslide",
        "terrain": "Mid-Himalayan River Canyon",
        "recent_rainfall_mm": 90.0,
        "forecast_rainfall_mm": 70.0,
        "soil_moisture_pct": 79.0,
        "slope_deg": 31.0,
        "elevation_m": 760.0,
        "river_proximity_km": 0.6,
        "historical_disaster_freq": 6.0,
        "drainage_density_score": 2.2,
        "risk_category": "high",
        "risk_score": 69.8,
        "description": "National Highway corridor slope slippage hazard."
    }
]

@risk_bp.route("/predict", methods=["POST"])
def predict():
    data = request.get_json() or {}
    try:
        validated = RiskPredictSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    # If environmental metrics were omitted, fetch from regional terrain & weather providers
    input_dict = validated.model_dump()
    
    if input_dict.get("recent_rainfall_mm") is None:
        weather_info = imd_provider.fetch_data(validated.latitude, validated.longitude)
        input_dict["recent_rainfall_mm"] = weather_info["rainfall_last_24h_mm"]
        input_dict["forecast_rainfall_mm"] = weather_info["rainfall_forecast_24h_mm"]
        input_dict["soil_moisture_pct"] = weather_info["relative_humidity_pct"]

    if input_dict.get("elevation_m") is None:
        terrain_info = terrain_provider.fetch_data(validated.latitude, validated.longitude)
        input_dict["elevation_m"] = terrain_info["elevation_m"]
        input_dict["slope_deg"] = terrain_info["slope_deg"]

    # Run Scikit-Learn Hazard Engine
    prediction = hazard_engine.predict_risk(input_dict, disaster_type=validated.disaster_type)

    # Persist in Database history
    assessment = RiskAssessment(
        location_name=validated.location_name or f"Coords ({validated.latitude:.3f}, {validated.longitude:.3f})",
        latitude=validated.latitude,
        longitude=validated.longitude,
        disaster_type=prediction["disaster_type"],
        risk_category=prediction["risk_category"],
        risk_score=prediction["risk_score"],
        confidence_score=prediction["confidence_score"],
        features_json=json.dumps(prediction["input_features"]),
        contributing_factors_json=json.dumps(prediction["contributing_factors"]),
        missing_data_warnings_json=json.dumps(prediction["missing_data_warnings"]),
        model_name=prediction["model_metadata"]["algorithm"],
        data_source=prediction["model_metadata"]["data_provenance"]
    )
    db.session.add(assessment)
    db.session.commit()

    return jsonify({
        "assessment_id": assessment.id,
        "prediction": prediction,
        "stored_record": assessment.to_dict()
    }), 200

@risk_bp.route("/history", methods=["GET"])
def get_risk_history():
    limit = int(request.args.get("limit", 25))
    disaster_type = request.args.get("disaster_type")

    query = RiskAssessment.query
    if disaster_type:
        query = query.filter_by(disaster_type=disaster_type)

    records = query.order_by(RiskAssessment.created_at.desc()).limit(limit).all()
    return jsonify({
        "count": len(records),
        "history": [r.to_dict() for r in records]
    }), 200

@risk_bp.route("/areas", methods=["GET"])
def get_monitored_areas():
    return jsonify({
        "status": "success",
        "data_mode": "DEMO/SIMULATED - Regional Geo-Climatic Baseline",
        "total_zones": len(MONITORED_INDIAN_RISK_ZONES),
        "zones": MONITORED_INDIAN_RISK_ZONES
    }), 200
