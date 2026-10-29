"""
Disaster AI Assistant Safety & Emergency Peril Guard
Independent safety layer running alongside the LLM.
Detects immediate life-threatening peril, enforces rapid survival directives,
promotes Emergency Helpline 112, and prevents dangerous hallucinated advice.
"""

import re
from typing import Dict, Any, List

# Emergency peril patterns indicating immediate threat to human life
PERIL_KEYWORDS = {
    "flood_submerged": [
        "water entering", "water is entering", "floodwater entering", "rising water",
        "chest deep", "neck deep", "rooftop", "stranded", "trapped in water", "submerged",
        "paani bhar", "paani ghar", "pani bhar", "pani ghar",
        "पानी भर", "पानी घुस", "डूब", "जलभराव"
    ],
    "earthquake_shaking": [
        "earthquake", "shaking", "tremor", "building shaking", "crack in wall",
        "crack in building", "trapped under debris", "rubble", "aftershock",
        "भूकंप", "झटके", "मलबा", "मलबे"
    ],
    "building_fire": [
        "fire", "smoke", "flames", "clothes on fire", "trapped in fire", "burning",
        "आग", "धुआं", "जल रहा"
    ],
    "landslide_active": [
        "landslide", "mudslide", "rockfall", "hill collapse", "debris flow",
        "भूस्खलन", "चट्टान"
    ],
    "severe_medical": [
        "bleeding", "severe bleeding", "unconscious", "heart attack", "not breathing",
        "choking", "fracture", "खून बह", "बेहोश"
    ]
}

RISKY_ACTION_PATTERNS = [
    r"jump\s+into", r"swim\s+across", r"walk\s+through\s+fast\s+water",
    r"touch\s+wire", r"use\s+elevator", r"throw\s+water\s+on\s+electrical",
    r"return\s+to\s+burning"
]

class EmergencySafetyGuard:
    def __init__(self):
        pass

    def evaluate_query(self, user_query: str, language: str = "en") -> Dict[str, Any]:
        """
        Evaluates citizen message for immediate danger and emergency category.
        Enforces verified life-safety rules.
        """
        query_lower = user_query.lower()
        detected_peril = False
        peril_category = None

        # 1. Match Peril Keywords
        for category, terms in PERIL_KEYWORDS.items():
            for term in terms:
                if term in query_lower:
                    detected_peril = True
                    peril_category = category
                    break
            if detected_peril:
                break

        # Also support flexible regex like 'water.*entering' or 'पानी.*भर'
        if not detected_peril:
            if re.search(r"water.*entering", query_lower) or re.search(r"पानी.*घुस", user_query) or re.search(r"पानी.*भर", user_query):
                detected_peril = True
                peril_category = "flood_submerged"
            elif re.search(r"building.*crack", query_lower) or re.search(r"wall.*crack", query_lower):
                detected_peril = True
                peril_category = "earthquake_shaking"

        # Check for risky action queries
        risky_behavior_warned = False
        for r_pat in RISKY_ACTION_PATTERNS:
            if re.search(r_pat, query_lower):
                risky_behavior_warned = True
                break

        # Emergency Helpline recommendation
        helpline = {
            "number": "112",
            "name": "National Emergency Helpline (All-in-One)",
            "ndrf": "1078",
            "ambulance": "108",
            "fire": "101"
        }

        # Safety Guidance Header to prioritize immediate action
        urgent_directive = None
        if detected_peril:
            if peril_category == "flood_submerged":
                urgent_directive = (
                    "🚨 IMMEDIATE LIFE SAFETY DIRECTIVE:\n"
                    "1. Turn off the main electricity switch and gas cylinder valve immediately.\n"
                    "2. Move all family members to upper floor or rooftop immediately.\n"
                    "3. Do NOT step into water touching electrical points.\n"
                    "4. Call 112 / 1078 with your exact location."
                    if language != "hi" else
                    "🚨 तत्काल जीवन रक्षा निर्देश:\n"
                    "1. तुरंत बिजली का मेन स्विच और गैस रेगुलेटर बंद करें।\n"
                    "2. सभी को तुरंत ऊपरी मंजिल या पक्की छत पर ले जाएं।\n"
                    "3. पानी में डूबे बिजली के तारों या उपकरणों को न छुएं।\n"
                    "4. तुरंत आपातकालीन नंबर 112 या एनडीआरएफ 1078 पर अपनी लोकेशन बताएं।"
                )
            elif peril_category == "building_fire":
                urgent_directive = (
                    "🚨 IMMEDIATE FIRE SAFETY DIRECTIVE:\n"
                    "1. Call 112 / 101 immediately.\n"
                    "2. Crawl low under smoke on hands and knees; cleaner air is near the floor.\n"
                    "3. Never use elevators. Feel door handle before opening.\n"
                    "4. If clothes catch fire: STOP, DROP, and ROLL."
                    if language != "hi" else
                    "🚨 तत्काल अग्नि सुरक्षा निर्देश:\n"
                    "1. तुरंत 112 या 101 पर फायर ब्रिगेड को सूचित करें।\n"
                    "2. धुएं से बचने के लिए फर्श के करीब झुककर रेंगें।\n"
                    "3. लिफ्ट का उपयोग कभी न करें।\n"
                    "4. कपड़ों में आग लगने पर: रुकें, जमीन पर लेटें और रोल करें (Stop, Drop, Roll)।"
                )
            elif peril_category == "severe_medical":
                urgent_directive = (
                    "🚨 IMMEDIATE MEDICAL EMERGENCY:\n"
                    "1. Call 112 / 108 immediately for an ambulance.\n"
                    "2. Apply direct, firm, continuous pressure with a clean cloth onto the bleeding wound.\n"
                    "3. Keep the patient lying down and calm. Do not give food/drink if unconscious."
                    if language != "hi" else
                    "🚨 तत्काल आपातकालीन चिकित्सा निर्देश:\n"
                    "1. तुरंत 112 या 108 पर एम्बुलेंस बुलाएं।\n"
                    "2. घाव पर साफ कपड़े से लगातार और मजबूत दबाव बनाए रखें।\n"
                    "3. घायल को शांत लेटा कर रखें। बेहोश व्यक्ति को कुछ न पिलाएं।"
                )
            elif peril_category == "earthquake_shaking":
                urgent_directive = (
                    "🚨 IMMEDIATE EARTHQUAKE SAFETY DIRECTIVE:\n"
                    "1. DROP, COVER, and HOLD ON under sturdy furniture away from glass and outer walls.\n"
                    "2. If outside a building, move to clear open ground away from overhead cables.\n"
                    "3. If deep cracks appear on walls or pillars, evacuate calmly via stairs after shaking stops and dial 112."
                )

        return {
            "is_immediate_peril": bool(detected_peril),
            "peril_category": peril_category,
            "urgent_directive": urgent_directive,
            "risky_behavior_detected": risky_behavior_warned,
            "helpline": helpline,
            "disclaimer": "Disaster AI is a decision-support assistant. Always follow verified local emergency authority instructions."
        }

safety_guard = EmergencySafetyGuard()
