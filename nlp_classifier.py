"""
NLP Classifier & Duplicate Detection for Emergency Reports
Extracts keywords, detects disaster type, clusters duplicate reports within spatial/text thresholds.
"""

import re
import math
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# High-priority disaster keywords and categories
KEYWORD_DICTIONARY = {
    "trapped": ["trapped", "stuck", "stranded", "isolated", "surrounded", "cut off", "roof", "rooftop"],
    "injury_medical": ["injured", "bleeding", "unconscious", "heart", "oxygen", "medicine", "pregnant", "casualty", "hurt", "fracture", "elderly", "infant", "baby", "dialysis"],
    "structural_damage": ["collapsed", "caved in", "crushed", "submerged", "underwater", "bridge washed away", "road blocked", "debris"],
    "rising_water": ["rising water", "water level rising", "flash flood", "chest deep", "neck deep", "swept away", "breach", "dam overflow"],
    "landslide_flow": ["mudslide", "rockfall", "debris flow", "landslide", "hill collapse", "boulders falling"],
    "supplies_critical": ["no food", "drinking water", "starving", "no electricity", "blackout", "rations finished"]
}

DISASTER_KEYWORDS = {
    "flood": ["flood", "flooding", "water", "submerged", "drowning", "river", "inundated", "monsoon", "overflow"],
    "landslide": ["landslide", "mudslide", "rockslide", "hillside", "slope failure", "mud", "boulder", "debris", "mountain"],
    "cyclone": ["cyclone", "storm", "hurricane", "gust", "winds", "gale", "tree fallen"],
    "earthquake": ["earthquake", "tremor", "quake", "aftershock", "building collapsed", "rubble"]
}

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two GPS coordinates in kilometers."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class NLPReportProcessor:
    def __init__(self):
        pass

    def extract_keywords(self, text: str) -> List[str]:
        """Extracts critical emergency keywords present in report title and description."""
        found_keywords = set()
        clean_text = text.lower()

        for category, kws in KEYWORD_DICTIONARY.items():
            for kw in kws:
                if re.search(r'\b' + re.escape(kw) + r'\b', clean_text):
                    found_keywords.add(kw)

        return sorted(list(found_keywords))

    def classify_disaster_type(self, title: str, description: str, stated_type: str = "flood") -> str:
        """Confirms or refines disaster type from textual content."""
        if stated_type and stated_type.lower() in DISASTER_KEYWORDS:
            return stated_type.lower()

        text = (title + " " + description).lower()
        scores = {}
        for dtype, terms in DISASTER_KEYWORDS.items():
            count = sum(1 for t in terms if re.search(r'\b' + re.escape(t) + r'\b', text))
            scores[dtype] = count

        best_type = max(scores, key=scores.get)
        return best_type if scores[best_type] > 0 else "flood"

    def check_duplicate(
        self,
        new_title: str,
        new_description: str,
        new_lat: float,
        new_lon: float,
        existing_incidents: List[Dict[str, Any]],
        spatial_radius_km: float = 3.0,
        text_similarity_threshold: float = 0.55
    ) -> Tuple[bool, int or None, float]:
        """
        Checks whether the new report is likely a duplicate of a recent incident
        occurring within the spatial radius with high semantic/keyword overlap.
        """
        if not existing_incidents:
            return False, None, 0.0

        candidates = []
        for inc in existing_incidents:
            dist = haversine_distance_km(new_lat, new_lon, inc["latitude"], inc["longitude"])
            if dist <= spatial_radius_km:
                candidates.append((inc, dist))

        if not candidates:
            return False, None, 0.0

        # Run TF-IDF cosine similarity on descriptions of nearby candidates
        new_text = f"{new_title} {new_description}".strip()
        corpus = [new_text] + [f"{c[0]['title']} {c[0]['description']}".strip() for c in candidates]

        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(corpus)
            sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

            best_idx = int(sim_scores.argmax())
            best_score = float(sim_scores[best_idx])

            if best_score >= text_similarity_threshold:
                matched_incident = candidates[best_idx][0]
                return True, matched_incident["id"], round(best_score, 2)
        except Exception:
            # Fallback to direct word set overlap
            new_words = set(new_text.lower().split())
            for inc, dist in candidates:
                cand_words = set(f"{inc['title']} {inc['description']}".lower().split())
                overlap = len(new_words.intersection(cand_words)) / max(1, len(new_words.union(cand_words)))
                if overlap > 0.4:
                    return True, inc["id"], round(overlap, 2)

        return False, None, 0.0

nlp_processor = NLPReportProcessor()
