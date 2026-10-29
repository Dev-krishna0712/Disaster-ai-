import unittest
from app import create_app
from app.config import Config
from app.database import db
from app.models.user import User
from app.models.incident import Incident

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class IncidentAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

            # Create test admin
            admin = User(username="admin", email="admin@test.com", role="admin", full_name="Admin Test")
            admin.set_password("AdminPass123!")

            # Create test citizen
            citizen = User(username="citizen", email="citizen@test.com", role="citizen", full_name="Citizen Test")
            citizen.set_password("CitizenPass123!")

            db.session.add_all([admin, citizen])
            db.session.commit()

            # Store tokens
            resp_a = self.client.post("/api/auth/login", json={"username": "admin", "password": "AdminPass123!"})
            self.admin_token = resp_a.get_json()["token"]

            resp_c = self.client.post("/api/auth/login", json={"username": "citizen", "password": "CitizenPass123!"})
            self.citizen_token = resp_c.get_json()["token"]

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_incident_submission_and_ai_prioritization(self):
        report_payload = {
            "title": "Severe flash flood in river colony",
            "disaster_type": "flood",
            "description": "Chest deep water entered ground floor. 5 people trapped on roof, including pregnant woman and child. Urgent rescue boat needed.",
            "latitude": 26.5800,
            "longitude": 93.1800,
            "address": "Ward 4, River Colony, Kaziranga",
            "landmark": "Near temple",
            "people_affected": 15,
            "people_trapped": 5,
            "people_injured": 1,
            "needs_medical": True,
            "needs_food_water": True,
            "needs_evacuation": True,
            "reporter_name": "Citizen Test",
            "reporter_contact": "+91 99999 11111"
        }

        resp = self.client.post(
            "/api/incidents",
            json=report_payload,
            headers={"Authorization": f"Bearer {self.citizen_token}"}
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        incident = data["incident"]
        self.assertEqual(incident["status"], "pending_verification")
        self.assertEqual(incident["verification_status"], "unverified")
        self.assertIn("ai_analysis", data)
        self.assertIn("priority", data["ai_analysis"])
        self.assertGreaterEqual(incident["ai_priority_score"], 60.0)

        # Admin verifies incident
        incident_id = incident["id"]
        verify_resp = self.client.post(
            f"/api/incidents/{incident_id}/verify",
            json={
                "verification_status": "verified",
                "admin_notes": "Ground staff confirmed roof trapping. High urgency."
            },
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(verify_resp.status_code, 200)
        verified_data = verify_resp.get_json()
        self.assertEqual(verified_data["incident"]["verification_status"], "verified")
        self.assertEqual(verified_data["incident"]["status"], "verified")

if __name__ == "__main__":
    unittest.main()
