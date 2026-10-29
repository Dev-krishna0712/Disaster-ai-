"""
Incident Management Routes
Submission, NLP keyword extraction, duplicate clustering, AI prioritization,
human-in-the-loop verification, and status lifecycle tracking.
"""

import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from pydantic import ValidationError

from app.database import db
from app.models.incident import Incident
from app.models.user import User
from app.schemas.validators import IncidentCreateSchema, IncidentVerifySchema, IncidentStatusUpdateSchema
from app.utils.auth_guard import token_required, optional_token, role_required
from app.ml.nlp_classifier import nlp_processor
from app.ml.prioritization_engine import prioritization_engine

incident_bp = Blueprint("incidents", __name__, url_prefix="/api/incidents")

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

@incident_bp.route("", methods=["POST"])
@optional_token
def create_incident(current_user):
    data = request.get_json() or {}
    try:
        validated = IncidentCreateSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    # 1. NLP Keyword Extraction
    full_text = f"{validated.title} {validated.description}"
    extracted_keywords = nlp_processor.extract_keywords(full_text)

    # 2. Disaster Type refinement
    disaster_type = nlp_processor.classify_disaster_type(
        validated.title, validated.description, validated.disaster_type
    )

    # 3. Duplicate Report Detection against active recent incidents
    recent_incidents = [
        {"id": inc.id, "title": inc.title, "description": inc.description, "latitude": inc.latitude, "longitude": inc.longitude}
        for inc in Incident.query.filter(Incident.status.notin_(["resolved", "rejected"])).all()
    ]
    is_dup, cluster_id, sim_score = nlp_processor.check_duplicate(
        validated.title, validated.description, validated.latitude, validated.longitude, recent_incidents
    )

    # 4. Explainable AI Prioritization
    priority_output = prioritization_engine.calculate_priority(
        incident_data=validated.model_dump(),
        keywords=extracted_keywords
    )

    # 5. Create Database Record
    incident = Incident(
        title=validated.title,
        disaster_type=disaster_type,
        description=validated.description,
        latitude=validated.latitude,
        longitude=validated.longitude,
        address=validated.address,
        landmark=validated.landmark,
        people_affected=validated.people_affected,
        people_trapped=validated.people_trapped,
        people_injured=validated.people_injured,
        needs_medical=validated.needs_medical,
        needs_food_water=validated.needs_food_water,
        needs_evacuation=validated.needs_evacuation,
        image_url=validated.image_url,
        reported_by_user_id=current_user.id if current_user else None,
        reporter_name=validated.reporter_name or (current_user.full_name if current_user else "Anonymous Citizen"),
        reporter_contact=validated.reporter_contact or (current_user.phone if current_user else "Not provided"),
        status="pending_verification",
        verification_status="duplicate" if is_dup else "unverified",
        ai_priority=priority_output["priority_category"],
        ai_priority_score=priority_output["priority_score"],
        ai_priority_factors_json=json.dumps(priority_output["scoring_factors"]),
        ai_keywords_json=json.dumps(extracted_keywords),
        ai_duplicate_suspect=is_dup,
        ai_duplicate_cluster_id=cluster_id
    )

    db.session.add(incident)
    db.session.commit()

    return jsonify({
        "message": "Incident report submitted successfully",
        "incident": incident.to_dict(include_sensitive=True),
        "ai_analysis": {
            "priority": priority_output["priority_category"],
            "priority_score": priority_output["priority_score"],
            "scoring_factors": priority_output["scoring_factors"],
            "keywords_detected": extracted_keywords,
            "duplicate_suspected": is_dup,
            "duplicate_match_incident_id": cluster_id,
            "similarity_score": sim_score if is_dup else 0.0
        }
    }), 201

@incident_bp.route("", methods=["GET"])
@optional_token
def list_incidents(current_user):
    # Query parameters
    disaster_type = request.args.get("disaster_type")
    status = request.args.get("status")
    verification_status = request.args.get("verification_status")
    priority = request.args.get("priority")
    my_reports = request.args.get("my_reports", "false").lower() == "true"
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    query = Incident.query

    if my_reports and current_user:
        query = query.filter_by(reported_by_user_id=current_user.id)
    if disaster_type:
        query = query.filter_by(disaster_type=disaster_type)
    if status:
        query = query.filter_by(status=status)
    if verification_status:
        query = query.filter_by(verification_status=verification_status)
    if priority:
        query = query.filter(
            (Incident.admin_override_priority == priority) |
            ((Incident.admin_override_priority == None) & (Incident.ai_priority == priority))
        )

    # Order by priority score descending, then created_at desc
    query = query.order_by(Incident.ai_priority_score.desc(), Incident.created_at.desc())

    total = query.count()
    incidents = query.offset((page - 1) * per_page).limit(per_page).all()

    # RBAC: Only admin or rescue_team (or original reporter) sees sensitive contact info
    can_view_sensitive = current_user and current_user.role in ["admin", "rescue_team"]

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "incidents": [
            inc.to_dict(include_sensitive=can_view_sensitive or (current_user and inc.reported_by_user_id == current_user.id))
            for inc in incidents
        ]
    }), 200

@incident_bp.route("/<int:incident_id>", methods=["GET"])
@optional_token
def get_incident(current_user, incident_id):
    incident = Incident.query.get_or_404(incident_id)
    can_view_sensitive = current_user and (
        current_user.role in ["admin", "rescue_team"] or
        incident.reported_by_user_id == current_user.id
    )
    return jsonify({
        "incident": incident.to_dict(include_sensitive=can_view_sensitive)
    }), 200

@incident_bp.route("/<int:incident_id>/verify", methods=["POST"])
@token_required
@role_required(["admin"])
def verify_incident(current_user, incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json() or {}

    try:
        validated = IncidentVerifySchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    incident.verification_status = validated.verification_status
    incident.admin_notes = validated.admin_notes
    incident.verified_by_user_id = current_user.id
    incident.verified_at = datetime.utcnow()

    # Update lifecycle status if verified or rejected
    if validated.verification_status == "verified" and incident.status == "pending_verification":
        incident.status = "verified"
    elif validated.verification_status == "rejected":
        incident.status = "rejected"
    elif validated.verification_status == "duplicate":
        incident.status = "duplicate"

    # Human-in-the-loop priority override
    if validated.admin_override_priority:
        incident.admin_override_priority = validated.admin_override_priority
        incident.admin_override_reason = validated.admin_override_reason

    db.session.commit()

    return jsonify({
        "message": f"Incident verification updated to '{incident.verification_status}'",
        "incident": incident.to_dict(include_sensitive=True)
    }), 200

@incident_bp.route("/<int:incident_id>/status", methods=["PATCH"])
@token_required
@role_required(["admin", "rescue_team"])
def update_incident_status(current_user, incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json() or {}

    try:
        validated = IncidentStatusUpdateSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    incident.status = validated.status
    db.session.commit()

    return jsonify({
        "message": f"Incident status updated to '{incident.status}'",
        "incident": incident.to_dict(include_sensitive=True)
    }), 200

@incident_bp.route("/upload-image", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        filename = secure_filename(f"{int(datetime.utcnow().timestamp())}_{file.filename}")
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        
        file_url = f"/api/incidents/uploads/{filename}"
        return jsonify({"message": "Image uploaded successfully", "image_url": file_url}), 201

    return jsonify({"error": "File extension not allowed. Use png, jpg, jpeg, webp."}), 400

@incident_bp.route("/uploads/<filename>", methods=["GET"])
def get_uploaded_image(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
