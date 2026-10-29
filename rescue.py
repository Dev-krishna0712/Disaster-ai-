from datetime import datetime
from app.database import db

class RescueTeam(db.Model):
    __tablename__ = "rescue_teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    team_lead = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(30), nullable=False)
    specialization = db.Column(db.String(80), nullable=False)  # flood_rescue, landslide_evac, medical_first_response, amphibious
    status = db.Column(db.String(30), default="available")    # available, deployed, standby, off_duty
    current_latitude = db.Column(db.Float, nullable=False)
    current_longitude = db.Column(db.Float, nullable=False)
    station_name = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Associated user account if any

    assignments = db.relationship("RescueAssignment", backref="team", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "team_lead": self.team_lead,
            "contact_phone": self.contact_phone,
            "specialization": self.specialization,
            "status": self.status,
            "current_latitude": self.current_latitude,
            "current_longitude": self.current_longitude,
            "station_name": self.station_name,
            "user_id": self.user_id,
        }

class RescueAssignment(db.Model):
    __tablename__ = "rescue_assignments"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("rescue_teams.id"), nullable=False, index=True)
    status = db.Column(db.String(30), default="assigned")  # assigned, en_route, on_site, resolved
    operational_notes = db.Column(db.Text, nullable=True)
    resource_requests = db.Column(db.Text, nullable=True)
    assigned_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "team_id": self.team_id,
            "team_name": self.team.name if self.team else None,
            "team_lead": self.team.team_lead if self.team else None,
            "status": self.status,
            "operational_notes": self.operational_notes,
            "resource_requests": self.resource_requests,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "incident": self.incident.to_dict() if self.incident else None,
        }
