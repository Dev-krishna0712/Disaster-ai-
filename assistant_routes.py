"""
Disaster AI Citizen Assistant Routes
Fine-tuned LLM conversational endpoints for disaster guidance, life-safety triage,
and live verified shelter/warning context without RAG.
"""

from flask import Blueprint, request, jsonify
from app.assistant.safety_guard import safety_guard
from app.assistant.llm_engine import llm_engine
from app.models.alert import Alert
from app.models.shelter import Shelter

assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")

@assistant_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Message content is required"}), 400

    if len(message) > 1500:
        return jsonify({"error": "Message exceeds maximum character limit of 1500"}), 400

    history = data.get("history", [])
    language = data.get("language", "en")
    user_location = data.get("location")

    # 1. Evaluate Query with Safety Guard
    safety_eval = safety_guard.evaluate_query(message, language=language)

    # 2. Check for Live Data queries (Shelters or Official Alerts) WITHOUT RAG
    # Explicit programmatic database integration
    live_context_items = []
    lower_msg = message.lower()

    if any(k in lower_msg for k in ["shelter", "camp", "relief", "राहत शिविर", "शरण"]):
        shelters = Shelter.query.filter_by(status="open").limit(3).all()
        if shelters:
            shelter_lines = [
                f"- {s.name} ({s.address}): {s.capacity - s.current_occupancy} beds available (Phone: {s.contact_phone or '112'})"
                for s in shelters
            ]
            live_context_items.append("Active Open Relief Camps in Database:\n" + "\n".join(shelter_lines))

    if any(k in lower_msg for k in ["alert", "warning", "forecast", "चेतावनी", "अलर्ट"]):
        active_alerts = Alert.query.filter_by(is_active=True).limit(3).all()
        if active_alerts:
            alert_lines = [
                f"- [{a.severity.upper()}] {a.title_en} for {a.target_region}: {a.action_en or a.message_en}"
                for a in active_alerts
            ]
            live_context_items.append("Current Verified Emergency Bulletins:\n" + "\n".join(alert_lines))

    live_context = "\n\n".join(live_context_items) if live_context_items else None

    # 3. Generate LLM Response
    llm_output = llm_engine.generate(
        message=message,
        history=history,
        context=live_context,
        max_new_tokens=220
    )

    # 4. If immediate peril was flagged, prepend the urgent life-saving directive
    final_reply = llm_output["response"]
    if safety_eval.get("is_immediate_peril") and safety_eval.get("urgent_directive"):
        # Prepend directive if not already present
        if "112" not in final_reply:
            final_reply = f"{safety_eval['urgent_directive']}\n\n{final_reply}"

    return jsonify({
        "reply": final_reply,
        "safety_assessment": {
            "is_immediate_peril": safety_eval["is_immediate_peril"],
            "peril_category": safety_eval["peril_category"],
            "helpline": safety_eval["helpline"],
            "risky_behavior_detected": safety_eval["risky_behavior_detected"]
        },
        "model_metadata": {
            "model_used": llm_output["model_used"],
            "is_fine_tuned": llm_output["is_fine_tuned"],
            "adapter_dir": llm_output["adapter_dir"],
            "latency_seconds": llm_output["latency_seconds"],
            "device": llm_output["device"],
            "status": llm_output["status"]
        },
        "live_context_used": bool(live_context),
        "disclaimer": safety_eval["disclaimer"]
    }), 200

@assistant_bp.route("/health", methods=["GET"])
def health():
    return jsonify(llm_engine.get_health()), 200

@assistant_bp.route("/model-info", methods=["GET"])
def model_info():
    return jsonify(llm_engine.get_info()), 200
