import unittest
from app.ml.prioritization_engine import PrioritizationEngine
from app.ml.nlp_classifier import NLPReportProcessor

class TestPrioritizationAndNLP(unittest.TestCase):
    def setUp(self):
        self.priority_engine = PrioritizationEngine()
        self.nlp = NLPReportProcessor()

    def test_critical_life_threat_prioritization(self):
        incident_data = {
            "people_affected": 20,
            "people_trapped": 8,
            "people_injured": 3,
            "needs_medical": True,
            "needs_food_water": True,
            "needs_evacuation": True
        }
        keywords = ["trapped", "mudslide", "injured", "rising water"]
        result = self.priority_engine.calculate_priority(incident_data, keywords)

        self.assertEqual(result["priority_category"], "critical")
        self.assertGreaterEqual(result["priority_score"], 70.0)
        self.assertGreaterEqual(len(result["scoring_factors"]), 4)

    def test_low_urgency_prioritization(self):
        incident_data = {
            "people_affected": 2,
            "people_trapped": 0,
            "people_injured": 0,
            "needs_medical": False,
            "needs_food_water": False,
            "needs_evacuation": False
        }
        result = self.priority_engine.calculate_priority(incident_data, [])
        self.assertIn(result["priority_category"], ["low", "medium"])
        self.assertLess(result["priority_score"], 45.0)

    def test_keyword_extraction(self):
        text = "Flash flood caused chest deep water! 4 elderly people trapped without oxygen or drinking water."
        keywords = self.nlp.extract_keywords(text)
        self.assertIn("trapped", keywords)
        self.assertIn("elderly", keywords)
        self.assertIn("oxygen", keywords)

    def test_duplicate_detection_nearby_overlap(self):
        existing = [
            {
                "id": 101,
                "title": "Chooralmala Riverbank Mudslide",
                "description": "Hill collapsed near tea estate quarters with people trapped",
                "latitude": 11.5365,
                "longitude": 76.1685
            }
        ]
        # Same incident reported 400m away with similar words
        is_dup, match_id, sim = self.nlp.check_duplicate(
            new_title="Mudslide near Chooralmala tea estate",
            new_description="Tea estate quarters hill collapse people are trapped",
            new_lat=11.5380,
            new_lon=76.1690,
            existing_incidents=existing
        )
        self.assertTrue(is_dup)
        self.assertEqual(match_id, 101)

if __name__ == "__main__":
    unittest.main()
