"""
Disaster Operations Analytics & Metrics Routes
Calculates live aggregation statistics from real database records.
Provides data for Recharts analytical dashboards.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from sqlalchemy import func

from app.database import db
from app.models.incident import Incident
from app.models.rescue import RescueAssignment, RescueTeam
from app.models.risk import RiskAssessment
from app.models.shelter import Shelter
from app.utils.auth_guard import token_required, role_required

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

@analytics_bp.route("/overview", methods=["GET"])
@token_required
@role_required(["admin", "rescue_team"])
def get_overview(current_user):
    # Total counts
    total_reports = Incident.query.count()
    unverified_reports = Incident.query.filter_by(verification_status="unverified").count()
    verified_incidents = Incident.query.filter_by(verification_status="verified").count()
    
    # Critical cases (effective priority)
    critical_cases = Incident.query.filter(
        (Incident.admin_override_priority == "critical") |
        ((Incident.admin_override_priority == None) & (Incident.ai_priority == "critical"))
    ).count()

    active_rescues = RescueAssignment.query.filter(RescueAssignment.status.in_(["assigned", "en_route", "on_site"])).count()
    resolved_incidents = Incident.query.filter_by(status="resolved").count()

    # Hazard type breakdown
    hazard_counts = db.session.query(
        Incident.disaster_type, func.count(Incident.id)
    ).group_by(Incident.disaster_type).all()
    by_hazard = [{"name": h[0].capitalize(), "count": h[1]} for h in hazard_counts]

    # Priority breakdown
    priority_counts = db.session.query(
        Incident.ai_priority, func.count(Incident.id)
    ).group_by(Incident.ai_priority).all()
    by_priority = [{"priority": p[0], "count": p[1]} for p in priority_counts]

    # Status breakdown
    status_counts = db.session.query(
        Incident.status, func.count(Incident.id)
    ).group_by(Incident.status).all()
    by_status = [{"status": s[0], "count": s[1]} for s in status_counts]

    # Timeline trend: Group incidents by day for the last 7 days
    now = datetime.utcnow()
    past_week = now - timedelta(days=7)
    recent_incidents = Incident.query.filter(Incident.created_at >= past_week).all()
    
    timeline_map = defaultdict(lambda: {"date": "", "total": 0, "critical": 0, "verified": 0})
    for day_offset in range(7, -1, -1):
        d = (now - timedelta(days=day_offset)).strftime("%b %d")
        timeline_map[d]["date"] = d

    for inc in recent_incidents:
        d = inc.created_at.strftime("%b %d")
        if d in timeline_map:
            timeline_map[d]["total"] += 1
            if inc.effective_priority == "critical":
                timeline_map[d]["critical"] += 1
            if inc.verification_status == "verified":
                timeline_map[d]["verified"] += 1

    trend_timeline = list(timeline_map.values())

    # Shelter capacity summary
    shelters = Shelter.query.all()
    total_shelter_capacity = sum(s.capacity for s in shelters)
    total_shelter_occupancy = sum(s.current_occupancy for s in shelters)

    # Average time to verification (minutes)
    verified_with_time = Incident.query.filter(
        Incident.verified_at != None, Incident.created_at != None
    ).all()
    if verified_with_time:
        diffs = [(inc.verified_at - inc.created_at).total_seconds() / 60.0 for inc in verified_with_time]
        avg_verification_time_min = round(sum(diffs) / len(diffs), 1)
    else:
        avg_verification_time_min = None

    return jsonify({
        "metrics": {
            "total_reports": total_reports,
            "unverified_reports": unverified_reports,
            "verified_incidents": verified_incidents,
            "critical_cases": critical_cases,
            "active_rescues": active_rescues,
            "resolved_incidents": resolved_incidents,
            "total_shelter_capacity": total_shelter_capacity,
            "total_shelter_occupancy": total_shelter_occupancy,
            "avg_verification_time_min": avg_verification_time_min
        },
        "by_hazard": by_hazard,
        "by_priority": by_priority,
        "by_status": by_status,
        "trend_timeline": trend_timeline
    }), 200
