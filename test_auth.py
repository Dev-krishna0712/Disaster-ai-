import unittest
from app import create_app
from app.config import Config
from app.database import db
from app.models.user import User

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_registration_and_login(self):
        # Register new citizen
        reg_response = self.client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "SecretPassword123!",
            "role": "citizen",
            "full_name": "Test User",
            "phone": "+91 99999 88888"
        })
        self.assertEqual(reg_response.status_code, 201)
        data = reg_response.get_json()
        self.assertIn("token", data)
        self.assertEqual(data["user"]["username"], "testuser")
        self.assertEqual(data["user"]["role"], "citizen")

        # Login with correct password
        login_response = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "SecretPassword123!"
        })
        self.assertEqual(login_response.status_code, 200)
        login_data = login_response.get_json()
        self.assertIn("token", login_data)

        # Login with incorrect password
        bad_login = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "WrongPassword!"
        })
        self.assertEqual(bad_login.status_code, 401)

    def test_role_based_access_control(self):
        # Register citizen
        reg_citizen = self.client.post("/api/auth/register", json={
            "username": "citizen1",
            "email": "c1@example.com",
            "password": "Password123!",
            "role": "citizen",
            "full_name": "Citizen One"
        })
        citizen_token = reg_citizen.get_json()["token"]

        # Register admin
        reg_admin = self.client.post("/api/auth/register", json={
            "username": "admin1",
            "email": "a1@example.com",
            "password": "Password123!",
            "role": "admin",
            "full_name": "Admin One"
        })
        admin_token = reg_admin.get_json()["token"]

        # Citizen attempts to broadcast official alert (Admin-only)
        alert_payload = {
            "title_en": "Flood Warning",
            "title_hi": "बाढ़ चेतावनी",
            "message_en": "Evacuate low lying areas",
            "message_hi": "निचले इलाकों को खाली करें",
            "target_region": "River Basin"
        }
        citizen_alert_resp = self.client.post(
            "/api/alerts",
            json=alert_payload,
            headers={"Authorization": f"Bearer {citizen_token}"}
        )
        self.assertEqual(citizen_alert_resp.status_code, 403)

        # Admin broadcasts official alert
        admin_alert_resp = self.client.post(
            "/api/alerts",
            json=alert_payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(admin_alert_resp.status_code, 201)

if __name__ == "__main__":
    unittest.main()
