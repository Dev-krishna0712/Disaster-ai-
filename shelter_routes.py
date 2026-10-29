"""
Shelter & Emergency Relief Logistics Routes
Tracks relief shelters, bed capacity, occupancy, and critical supplies.
"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models.shelter import Shelter, ResourceInventory
from app.utils.auth_guard import token_required, role_required

shelter_bp = Blueprint("shelters", __name__, url_prefix="/api/shelters")

@shelter_bp.route("", methods=["GET"])
def get_shelters():
    shelters = Shelter.query.all()
    return jsonify({
        "total": len(shelters),
        "shelters": [s.to_dict() for s in shelters]
    }), 200

@shelter_bp.route("/<int:shelter_id>/occupancy", methods=["PATCH"])
@token_required
@role_required(["admin", "rescue_team"])
def update_occupancy(current_user, shelter_id):
    shelter = Shelter.query.get_or_404(shelter_id)
    data = request.get_json() or {}

    new_occupancy = data.get("current_occupancy")
    if new_occupancy is not None:
        try:
            val = int(new_occupancy)
            shelter.current_occupancy = max(0, val)
            if shelter.current_occupancy >= shelter.capacity:
                shelter.status = "full"
            else:
                shelter.status = "open"
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid occupancy count"}), 400

    if "status" in data and data["status"] in ["open", "full", "closed"]:
        shelter.status = data["status"]

    db.session.commit()
    return jsonify({
        "message": "Shelter occupancy updated",
        "shelter": shelter.to_dict()
    }), 200
