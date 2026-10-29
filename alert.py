from datetime import datetime, timedelta
from app.database import db

class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.String(200), nullable=False)
    title_hi = db.Column(db.String(250), nullable=False)
    message_en = db.Column(db.Text, nullable=False)
    message_hi = db.Column(db.Text, nullable=False)
    
    # Actionable guidance
    action_en = db.Column(db.Text, nullable=True)
    action_hi = db.Column(db.Text, nullable=True)

    severity = db.Column(db.String(20), default="warning", index=True)  # info, warning, critical
    disaster_type = db.Column(db.String(50), default="general")
    target_region = db.Column(db.String(150), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    radius_km = db.Column(db.Float, default=25.0)

    is_official = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    source_attribution = db.Column(db.String(150), default="Disaster Management Authority (Simulated)")

    issued_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title_en": self.title_en,
            "title_hi": self.title_hi,
            "message_en": self.message_en,
            "message_hi": self.message_hi,
            "action_en": self.action_en,
            "action_hi": self.action_hi,
            "severity": self.severity,
            "disaster_type": self.disaster_type,
            "target_region": self.target_region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius_km": self.radius_km,
            "is_official": self.is_official,
            "is_active": self.is_active,
            "source_attribution": self.source_attribution,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
