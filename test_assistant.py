import unittest
from app import create_app
from app.config import Config
from app.database import db
from app.assistant.safety_guard import EmergencySafetyGuard

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class AssistantTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.guard = EmergencySafetyGuard()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_immediate_peril_detection(self):
        # Flood peril
        res = self.guard.evaluate_query("Floodwater is entering my house and rising rapidly!")
        self.assertTrue(res["is_immediate_peril"])
        self.assertEqual(res["peril_category"], "flood_submerged")
        self.assertIsNotNone(res["urgent_directive"])
        self.assertIn("112", res["urgent_directive"])

        # Hindi flood peril
        res_hi = self.guard.evaluate_query("मेरे घर में पानी घुस रहा है, क्या करूं?", language="hi")
        self.assertTrue(res_hi["is_immediate_peril"])
        self.assertIn("112", res_hi["urgent_directive"])

        # Severe medical peril
        res_med = self.guard.evaluate_query("Someone is bleeding severely after a wall collapsed.")
        self.assertTrue(res_med["is_immediate_peril"])
        self.assertEqual(res_med["peril_category"], "severe_medical")

        # Non-peril general preparedness
        res_prep = self.guard.evaluate_query("How can I prepare an emergency kit for my family?")
        self.assertFalse(res_prep["is_immediate_peril"])
        self.assertIsNone(res_prep["urgent_directive"])

    def test_assistant_health_and_info_endpoints(self):
        # Health
        resp_health = self.client.get("/api/assistant/health")
        self.assertEqual(resp_health.status_code, 200)
        data_health = resp_health.get_json()
        self.assertEqual(data_health["status"], "healthy")
        self.assertIn("base_model", data_health)

        # Model Info
        resp_info = self.client.get("/api/assistant/model-info")
        self.assertEqual(resp_info.status_code, 200)
        data_info = resp_info.get_json()
        self.assertIn("official_sources", data_info)
        self.assertTrue(data_info["rag_free_architecture"])

    def test_assistant_chat_endpoint_validation(self):
        # Empty query
        resp_empty = self.client.post("/api/assistant/chat", json={"message": ""})
        self.assertEqual(resp_empty.status_code, 400)

        # Valid chat query
        resp_chat = self.client.post("/api/assistant/chat", json={
            "message": "Water is entering my ground floor room. What should I do?",
            "language": "en"
        })
        self.assertEqual(resp_chat.status_code, 200)
        data_chat = resp_chat.get_json()
        self.assertIn("reply", data_chat)
        self.assertIn("safety_assessment", data_chat)
        self.assertTrue(data_chat["safety_assessment"]["is_immediate_peril"])
        self.assertIn("112", data_chat["reply"])

if __name__ == "__main__":
    unittest.main()
