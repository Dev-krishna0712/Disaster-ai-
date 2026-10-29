"""
Rescue Operations & Field Team Dispatch
Tracks rescue teams, dispatches units to verified incidents,
and records field progression: Assigned -> En Route -> On Site -> Resolved.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.database import db
from app.models.rescue import RescueTeam, RescueAssignment
from app.models.incident import Incident
from app.schemas.validators import RescueAssignSchema
from app.utils.auth_guard import token_required, role_required

rescue_bp = Blueprint("rescue", __name__, url_prefix="/api/rescue")

@rescue_bp.route("/teams", methods=["GET"])
def get_teams():
    teams = RescueTeam.query.all()
    return jsonify({
        "total": len(teams),
        "teams": [t.to_dict() for t in teams]
    }), 200

@rescue_bp.route("/teams", methods=["POST"])
@token_required
@role_required(["admin"])
def create_team(current_user):
    data = request.get_json() or {}
    team = RescueTeam(
        name=data.get("name", "NDRF Quick Response Unit"),
        team_lead=data.get("team_lead", "Officer"),
        contact_phone=data.get("contact_phone", "+91 98000 00000"),
        specialization=data.get("specialization", "flood_rescue"),
        status=data.get("status", "available"),
        current_latitude=float(data.get("current_latitude", 11.6854)),
        current_longitude=float(data.get("current_longitude", 76.1320)),
        station_name=data.get("station_name", "Regional Disaster Hub")
    )
    db.session.add(team)
    db.session.commit()
    return jsonify({"message": "Rescue team registered", "team": team.to_dict()}), 201

@rescue_bp.route("/assign", methods=["POST"])
@token_required
@role_required(["admin"])
def assign_team(current_user):
    data = request.get_json() or {}
    try:
        validated = RescueAssignSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    incident = Incident.query.get_or_404(validated.incident_id)
    team = RescueTeam.query.get_or_404(validated.team_id)

    # Create assignment
    assignment = RescueAssignment(
        incident_id=incident.id,
        team_id=team.id,
        status="assigned",
        operational_notes=validated.operational_notes,
        assigned_by_user_id=current_user.id
    )

    # Update incident status to 'assigned'
    incident.status = "assigned"
    team.status = "deployed"

    db.session.add(assignment)
    db.session.commit()

    return jsonify({
        "message": f"Team '{team.name}' assigned to incident #{incident.id}",
        "assignment": assignment.to_dict()
    }), 201

@rescue_bp.route("/assignments", methods=["GET"])
@token_required
def list_assignments(current_user):
    """Lists rescue assignments. Team members see their unit's assignments; admins see all."""
    if current_user.role == "admin":
        assignments = RescueAssignment.query.order_by(RescueAssignment.assigned_at.desc()).all()
    else:
        # Check if user is linked to a team or filter by phone / username
        team = RescueTeam.query.filter_by(user_id=current_user.id).first()
        if team:
            assignments = RescueAssignment.query.filter_by(team_id=team.id).order_by(RescueAssignment.assigned_at.desc()).all()
        else:
            assignments = RescueAssignment.query.order_by(RescueAssignment.assigned_at.desc()).all()

    return jsonify({
        "total": len(assignments),
        "assignments": [a.to_dict() for a in assignments]
    }), 200

@rescue_bp.route("/assignments/<int:assignment_id>/status", methods=["PATCH"])
@token_required
@role_required(["rescue_team", "admin"])
def update_assignment_status(current_user, assignment_id):
    assignment = RescueAssignment.query.get_or_404(assignment_id)
    data = request.get_json() or {}

    new_status = data.get("status")  # assigned, en_route, on_site, resolved
    allowed = ["assigned", "en_route", "on_site", "resolved"]
    if new_status not in allowed:
        return jsonify({"error": f"Status must be one of {allowed}"}), 400

    assignment.status = new_status
    if "operational_notes" in data:
        assignment.operational_notes = data["operational_notes"]
    if "resource_requests" in data:
        assignment.resource_requests = data["resource_requests"]

    # Sync incident status
    if assignment.incident:
        assignment.incident.status = new_status
        if new_status == "resolved":
            assignment.resolved_at = datetime.utcnow()
            if assignment.team:
                assignment.team.status = "available"

    db.session.commit()

    return jsonify({
        "message": f"Rescue task status updated to '{new_status}'",
        "assignment": assignment.to_dict()
    }), 200
