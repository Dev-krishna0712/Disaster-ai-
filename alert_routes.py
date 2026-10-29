"""
Bilingual Emergency Alerts & Public Notifications
Distributes critical life-safety warnings in Hindi and English.
Allows authorized emergency administrators to broadcast verified warnings.
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.database import db
from app.models.alert import Alert
from app.schemas.validators import AlertCreateSchema
from app.utils.auth_guard import token_required, role_required

alert_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")

@alert_bp.route("", methods=["GET"])
def get_alerts():
    # Fetch active alerts
    now = datetime.utcnow()
    alerts = Alert.query.filter_by(is_active=True).order_by(Alert.issued_at.desc()).all()
    return jsonify({
        "total": len(alerts),
        "alerts": [a.to_dict() for a in alerts]
    }), 200

@alert_bp.route("", methods=["POST"])
@token_required
@role_required(["admin"])
def create_alert(current_user):
    data = request.get_json() or {}
    try:
        validated = AlertCreateSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    alert = Alert(
        title_en=validated.title_en,
        title_hi=validated.title_hi,
        message_en=validated.message_en,
        message_hi=validated.message_hi,
        action_en=validated.action_en,
        action_hi=validated.action_hi,
        severity=validated.severity,
        disaster_type=validated.disaster_type,
        target_region=validated.target_region,
        latitude=validated.latitude,
        longitude=validated.longitude,
        radius_km=validated.radius_km,
        is_official=True,
        is_active=True,
        source_attribution=f"Disaster Management Authority ({current_user.full_name})",
        issued_by_user_id=current_user.id,
        issued_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=48)
    )

    db.session.add(alert)
    db.session.commit()

    return jsonify({
        "message": "Emergency alert broadcasted successfully",
        "alert": alert.to_dict()
    }), 201

@alert_bp.route("/<int:alert_id>", methods=["DELETE"])
@token_required
@role_required(["admin"])
def deactivate_alert(current_user, alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.is_active = False
    db.session.commit()
    return jsonify({"message": "Alert deactivated successfully"}), 200
