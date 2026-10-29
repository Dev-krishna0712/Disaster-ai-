from datetime import datetime
import json
from app.database import db

class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    disaster_type = db.Column(db.String(50), nullable=False, index=True)  # flood, landslide, cyclone, etc.
    description = db.Column(db.Text, nullable=False)
    
    # Geospatial
    latitude = db.Column(db.Float, nullable=False, index=True)
    longitude = db.Column(db.Float, nullable=False, index=True)
    address = db.Column(db.String(300), nullable=False)
    landmark = db.Column(db.String(200), nullable=True)

    # Human Impact & Urgency
    people_affected = db.Column(db.Integer, default=1)
    people_trapped = db.Column(db.Integer, default=0)
    people_injured = db.Column(db.Integer, default=0)
    needs_medical = db.Column(db.Boolean, default=False)
    needs_food_water = db.Column(db.Boolean, default=False)
    needs_evacuation = db.Column(db.Boolean, default=False)

    image_url = db.Column(db.String(500), nullable=True)

    # Reporter Info
    reported_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reporter_name = db.Column(db.String(120), nullable=True)
    reporter_contact = db.Column(db.String(50), nullable=True)

    # Workflow & Verification Status
    # Status: pending_verification, verified, assigned, en_route, on_site, resolved, rejected, duplicate
    status = db.Column(db.String(30), default="pending_verification", index=True)
    # Verification: unverified, verified, rejected, duplicate, needs_info
    verification_status = db.Column(db.String(30), default="unverified", index=True)
    verified_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)

    # AI Explainable Scoring & Analysis
    ai_priority = db.Column(db.String(20), default="medium", index=True)  # critical, high, medium, low
    ai_priority_score = db.Column(db.Float, default=50.0)  # 0 to 100
    ai_priority_factors_json = db.Column(db.Text, nullable=True)  # JSON factor breakdown
    ai_keywords_json = db.Column(db.Text, nullable=True)  # JSON list
    ai_duplicate_suspect = db.Column(db.Boolean, default=False)
    ai_duplicate_cluster_id = db.Column(db.Integer, nullable=True)

    # Administrator Override
    admin_override_priority = db.Column(db.String(20), nullable=True)
    admin_override_reason = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignments = db.relationship("RescueAssignment", backref="incident", lazy="dynamic", cascade="all, delete-orphan")
    verifier = db.relationship("User", foreign_keys=[verified_by_user_id])

    @property
    def effective_priority(self) -> str:
        return self.admin_override_priority or self.ai_priority

    def get_priority_factors(self):
        if self.ai_priority_factors_json:
            try:
                return json.loads(self.ai_priority_factors_json)
            except Exception:
                return {}
        return {}

    def get_keywords(self):
        if self.ai_keywords_json:
            try:
                return json.loads(self.ai_keywords_json)
            except Exception:
                return []
        return []

    def to_dict(self, include_sensitive=False):
        data = {
            "id": self.id,
            "title": self.title,
            "disaster_type": self.disaster_type,
            "description": self.description,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "landmark": self.landmark,
            "people_affected": self.people_affected,
            "people_trapped": self.people_trapped,
            "people_injured": self.people_injured,
            "needs_medical": self.needs_medical,
            "needs_food_water": self.needs_food_water,
            "needs_evacuation": self.needs_evacuation,
            "image_url": self.image_url,
            "status": self.status,
            "verification_status": self.verification_status,
            "ai_priority": self.ai_priority,
            "ai_priority_score": self.ai_priority_score,
            "effective_priority": self.effective_priority,
            "ai_priority_factors": self.get_priority_factors(),
            "ai_keywords": self.get_keywords(),
            "ai_duplicate_suspect": self.ai_duplicate_suspect,
            "ai_duplicate_cluster_id": self.ai_duplicate_cluster_id,
            "admin_override_priority": self.admin_override_priority,
            "admin_override_reason": self.admin_override_reason,
            "admin_notes": self.admin_notes,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_sensitive:
            data["reporter_name"] = self.reporter_name
            data["reporter_contact"] = self.reporter_contact
            data["reported_by_user_id"] = self.reported_by_user_id
        return data
