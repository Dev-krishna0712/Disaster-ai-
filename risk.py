from datetime import datetime
import json
from app.database import db

class RiskAssessment(db.Model):
    __tablename__ = "risk_assessments"

    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(150), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False, index=True)
    longitude = db.Column(db.Float, nullable=False, index=True)
    disaster_type = db.Column(db.String(50), nullable=False)  # flood, landslide

    # AI outputs
    risk_category = db.Column(db.String(20), nullable=False)  # low, moderate, high, very_high
    risk_score = db.Column(db.Float, nullable=False)          # 0.0 to 100.0
    confidence_score = db.Column(db.Float, nullable=False)    # 0.0 to 1.0 (model certainty)

    # Explainability & features
    features_json = db.Column(db.Text, nullable=False)
    contributing_factors_json = db.Column(db.Text, nullable=False)
    missing_data_warnings_json = db.Column(db.Text, nullable=True)

    # Scientific Provenance
    model_name = db.Column(db.String(100), default="RandomForest-GradientBoosting Ensemble v1.0")
    data_source = db.Column(db.String(200), default="DEMO/SIMULATED - Regional Geo-Climatic Baseline")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "disaster_type": self.disaster_type,
            "risk_category": self.risk_category,
            "risk_score": round(self.risk_score, 1),
            "confidence_score": round(self.confidence_score, 2),
            "features": json.loads(self.features_json) if self.features_json else {},
            "contributing_factors": json.loads(self.contributing_factors_json) if self.contributing_factors_json else [],
            "missing_data_warnings": json.loads(self.missing_data_warnings_json) if self.missing_data_warnings_json else [],
            "model_name": self.model_name,
            "data_source": self.data_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
