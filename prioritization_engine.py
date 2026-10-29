"""
Explainable Rescue Prioritization Engine
Calculates transparent objective urgency scores for disaster response teams.
Ensures zero demographic discrimination, prioritizes pure human safety & urgency.
"""

from typing import Dict, Any, List
from datetime import datetime

class PrioritizationEngine:
    def __init__(self):
        pass

    def calculate_priority(
        self,
        incident_data: Dict[str, Any],
        keywords: List[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates an explainable priority score (0-100) and priority category.
        Provides a transparent breakdown of scoring components.
        """
        keywords = keywords or []
        factors = []
        score = 0.0

        people_affected = int(incident_data.get("people_affected") or 1)
        people_trapped = int(incident_data.get("people_trapped") or 0)
        people_injured = int(incident_data.get("people_injured") or 0)
        needs_medical = bool(incident_data.get("needs_medical", False))
        needs_food_water = bool(incident_data.get("needs_food_water", False))
        needs_evacuation = bool(incident_data.get("needs_evacuation", False))

        # 1. IMMEDIATE LIFE THREAT: Trapped Individuals (Max 35 pts)
        if people_trapped > 0:
            trapped_pts = min(35.0, 15.0 + (people_trapped * 4.0))
            score += trapped_pts
            factors.append({
                "factor": "Trapped Individuals",
                "points": round(trapped_pts, 1),
                "weight_desc": f"{people_trapped} people actively trapped or stranded without safe exit",
                "severity": "CRITICAL"
            })

        # 2. SEVERE INJURY & MEDICAL EMERGENCY (Max 25 pts)
        injury_pts = 0.0
        if people_injured > 0:
            injury_pts += min(15.0, 8.0 + (people_injured * 2.5))
        if needs_medical:
            injury_pts += 10.0

        if injury_pts > 0:
            injury_pts = min(25.0, injury_pts)
            score += injury_pts
            factors.append({
                "factor": "Medical Emergency & Casualties",
                "points": round(injury_pts, 1),
                "weight_desc": f"{people_injured} injured / critical medical assistance requested",
                "severity": "CRITICAL" if injury_pts >= 18 else "HIGH"
            })

        # 3. POPULATION SCALE AFFECTED (Max 15 pts)
        if people_affected > 50:
            scale_pts = 15.0
            scale_desc = f"Large community impact: {people_affected}+ individuals affected"
        elif people_affected > 15:
            scale_pts = 10.0
            scale_desc = f"Cluster group: {people_affected} individuals affected"
        elif people_affected > 4:
            scale_pts = 6.0
            scale_desc = f"Family group: {people_affected} individuals affected"
        else:
            scale_pts = 3.0
            scale_desc = f"Local individual/household incident ({people_affected} person)"
        
        score += scale_pts
        factors.append({
            "factor": "Scale of Affected Population",
            "points": round(scale_pts, 1),
            "weight_desc": scale_desc,
            "severity": "HIGH" if scale_pts >= 10 else "MODERATE"
        })

        # 4. EVACUATION & ISOLATION THREAT (Max 15 pts)
        evac_pts = 0.0
        if needs_evacuation:
            evac_pts += 8.0
        if needs_food_water:
            evac_pts += 7.0

        if evac_pts > 0:
            score += evac_pts
            factors.append({
                "factor": "Displacement & Essential Sustenance",
                "points": round(evac_pts, 1),
                "weight_desc": "Active evacuation and critical food/potable water relief needed",
                "severity": "HIGH" if evac_pts > 10 else "MODERATE"
            })

        # 5. NLP KEYWORD ESCALATION BOOST (Max 10 pts)
        urgent_nlp_hits = [
            k for k in keywords if k in [
                "rising water", "flash flood", "submerged", "chest deep", "mudslide",
                "collapsed", "oxygen", "infant", "pregnant", "dialysis"
            ]
        ]
        if urgent_nlp_hits:
            nlp_pts = min(10.0, len(urgent_nlp_hits) * 3.5)
            score += nlp_pts
            factors.append({
                "factor": "Urgent Situational Indicators (NLP)",
                "points": round(nlp_pts, 1),
                "weight_desc": f"Critical terms detected in report text: {', '.join(urgent_nlp_hits)}",
                "severity": "CRITICAL"
            })

        # Final Score Clamping
        final_score = round(min(100.0, max(5.0, score)), 1)

        # Priority Categorization
        if final_score >= 70.0:
            category = "critical"
        elif final_score >= 45.0:
            category = "high"
        elif final_score >= 25.0:
            category = "medium"
        else:
            category = "low"

        return {
            "priority_category": category,
            "priority_score": final_score,
            "scoring_factors": factors,
            "methodology": "Multi-Criteria Life-Threat Priority Matrix (Objective Human-Safety Index)",
            "ethical_compliance": "Zero demographic bias: Prioritization strictly governed by verified peril and vulnerability metrics."
        }

prioritization_engine = PrioritizationEngine()
