"""
Database Seeding Script for Disaster AI Platform
Populates realistic, physically consistent demonstration data for India.
Explicitly labeled: DEMO / SIMULATED DATA.
"""

from datetime import datetime, timedelta
import json
from app import create_app
from app.database import db
from app.models.user import User
from app.models.incident import Incident
from app.models.risk import RiskAssessment
from app.models.rescue import RescueTeam, RescueAssignment
from app.models.alert import Alert
from app.models.shelter import Shelter, ResourceInventory

app = create_app()

def seed_database():
    with app.app_context():
        print("Initializing Disaster AI database schema...")
        db.drop_all()
        db.create_all()

        print("Seeding demo users...")
        # 1. USERS
        admin_user = User(
            username="admin",
            email="admin@disasterai.gov.in",
            role="admin",
            full_name="Col. Rajesh Sharma (Retd.)",
            phone="+91 98111 00001",
            organization="National Disaster Emergency Operations"
        )
        admin_user.set_password("AdminPass123!")

        citizen_user = User(
            username="citizen",
            email="arun.kumar@gmail.com",
            role="citizen",
            full_name="Arun Kumar",
            phone="+91 94471 23456",
            organization="Local Resident, Wayanad"
        )
        citizen_user.set_password("CitizenPass123!")

        rescue_user = User(
            username="rescue_lead",
            email="inspector.vikram@ndrf.gov.in",
            role="rescue_team",
            full_name="Insp. Vikram Singh",
            phone="+91 98222 33445",
            organization="NDRF 04 Battalion Quick Response"
        )
        rescue_user.set_password("RescuePass123!")

        db.session.add_all([admin_user, citizen_user, rescue_user])
        db.session.commit()

        print("Seeding rescue teams...")
        # 2. RESCUE TEAMS
        team_ndrf_kerala = RescueTeam(
            name="NDRF Team Alpha (Kerala)",
            team_lead="Insp. Vikram Singh",
            contact_phone="+91 98222 33445",
            specialization="flood_rescue",
            status="deployed",
            current_latitude=11.5500,
            current_longitude=76.1000,
            station_name="Wayanad Emergency Operations Base",
            user_id=rescue_user.id
        )

        team_sdrf_uk = RescueTeam(
            name="SDRF Mountain Evac Unit (Uttarakhand)",
            team_lead="Sub-Insp. Priya Rawat",
            contact_phone="+91 98333 44556",
            specialization="landslide_evac",
            status="available",
            current_latitude=30.5500,
            current_longitude=79.5600,
            station_name="Chamoli High-Altitude Station"
        )

        team_ndrf_assam = RescueTeam(
            name="NDRF 01 Battalion Amphibious Unit",
            team_lead="Commander Debajit Saikia",
            contact_phone="+91 98444 55667",
            specialization="amphibious_boat_rescue",
            status="deployed",
            current_latitude=26.5800,
            current_longitude=93.1800,
            station_name="Kaziranga Rapid Water Relief Base"
        )

        team_mumbai_qrf = RescueTeam(
            name="Mumbai Urban Flood Taskforce",
            team_lead="Chief Officer Sanjay Patil",
            contact_phone="+91 98555 66778",
            specialization="urban_water_pumping",
            status="available",
            current_latitude=19.0700,
            current_longitude=72.8800,
            station_name="Kurla Fire & Disaster Station"
        )

        db.session.add_all([team_ndrf_kerala, team_sdrf_uk, team_ndrf_assam, team_mumbai_qrf])
        db.session.commit()

        print("Seeding relief shelters and inventories...")
        # 3. SHELTERS & RESOURCES
        shelter1 = Shelter(
            name="Meppadi St. Joseph Relief Center",
            address="Meppadi Town Center, Wayanad, Kerala 673577",
            latitude=11.5540,
            longitude=76.1280,
            capacity=350,
            current_occupancy=195,
            status="open",
            contact_phone="+91 4936 282210",
            amenities_json=json.dumps(["drinking_water", "first_aid", "emergency_power", "kitchen", "child_friendly_space"])
        )

        shelter2 = Shelter(
            name="Brahmaputra Flood Relief Camp (Bokakhat)",
            address="Govt Higher Secondary School, Bokakhat, Assam 785612",
            latitude=26.6310,
            longitude=93.5920,
            capacity=400,
            current_occupancy=280,
            status="open",
            contact_phone="+91 3776 268240",
            amenities_json=json.dumps(["clean_water_purification", "medical_dispensary", "inflatable_rafts", "baby_food"])
        )

        shelter3 = Shelter(
            name="Joshimath Municipal Transit Center",
            address="Near Bus Stand, Joshimath, Chamoli, Uttarakhand 246443",
            latitude=30.5580,
            longitude=79.5650,
            capacity=220,
            current_occupancy=85,
            status="open",
            contact_phone="+91 1389 222120",
            amenities_json=json.dumps(["thermal_blankets", "doctor_on_call", "oxygen_concentrators", "satellite_phone"])
        )

        shelter4 = Shelter(
            name="Kurla Relief Community Hall",
            address="LBS Marg, Kurla West, Mumbai, Maharashtra 400070",
            latitude=19.0680,
            longitude=72.8790,
            capacity=500,
            current_occupancy=310,
            status="open",
            contact_phone="+91 22 2650 1234",
            amenities_json=json.dumps(["packaged_drinking_water", "dry_rations", "mobile_charging_hub", "emergency_medicines"])
        )

        db.session.add_all([shelter1, shelter2, shelter3, shelter4])
        db.session.commit()

        # Shelter Resources
        r1 = ResourceInventory(shelter_id=shelter1.id, item_name="Packaged Drinking Water", category="water", quantity=1400, unit="liters")
        r2 = ResourceInventory(shelter_id=shelter1.id, item_name="Ready-to-Eat Food Packets", category="food", quantity=850, unit="packets")
        r3 = ResourceInventory(shelter_id=shelter1.id, item_name="First Aid Trauma Kits", category="medical", quantity=45, unit="kits")
        r4 = ResourceInventory(shelter_id=shelter2.id, item_name="Inflatable Rescue Boats", category="equipment", quantity=6, unit="units")
        r5 = ResourceInventory(shelter_id=shelter2.id, item_name="Water Purification Tablets", category="water", quantity=5000, unit="strips")
        r6 = ResourceInventory(shelter_id=shelter3.id, item_name="Thermal Blankets & Sleeping Mats", category="equipment", quantity=300, unit="sets")

        db.session.add_all([r1, r2, r3, r4, r5, r6])
        db.session.commit()

        print("Seeding bilingual alerts...")
        # 4. ALERTS (Bilingual English & Hindi)
        alert1 = Alert(
            title_en="RED ALERT: Severe Landslide Threat in Wayanad Ghats",
            title_hi="रेड अलर्ट: वायनाड घाट में भीषण भूस्खलन का गंभीर खतरा",
            message_en="Extreme rainfall exceeding 200mm in 24 hours has saturated hill slopes. Severe debris flow hazard along Meppadi-Chooralmala corridor.",
            message_hi="24 घंटों में 200 मिमी से अधिक अत्यधिक वर्षा के कारण पहाड़ी ढलानों में भारी जल भराव। मेप्पाडी-चूरलमाला क्षेत्र में गंभीर भूस्खलन और मलबे का खतरा।",
            action_en="Evacuate vulnerable slope dwellings immediately. Move to designated Meppadi relief centers. Avoid ghat roads.",
            action_hi="ढलान वाले घरों से तुरंत सुरक्षित स्थानों पर जाएं। निकटतम मेप्पाडी राहत शिविर में शरण लें। घाट की सड़कों पर यात्रा न करें।",
            severity="critical",
            disaster_type="landslide",
            target_region="Wayanad, Kerala",
            latitude=11.5540,
            longitude=76.1280,
            radius_km=30.0,
            is_official=True,
            is_active=True,
            source_attribution="Disaster AI Operational Center (Simulated)",
            issued_by_user_id=admin_user.id,
            issued_at=datetime.utcnow() - timedelta(hours=3),
            expires_at=datetime.utcnow() + timedelta(hours=45)
        )

        alert2 = Alert(
            title_en="ORANGE ALERT: Brahmaputra River Surges Above Danger Mark",
            title_hi="ऑरेंज अलर्ट: ब्रह्मपुत्र नदी खतरे के निशान से ऊपर बही",
            message_en="Water level in Kaziranga & Bokakhat sector has crossed severe flood stage by 1.1 meters. Low-lying revenue villages inundating.",
            message_hi="काजीरंगा और बोकाखाट क्षेत्र में ब्रह्मपुत्र नदी का जलस्तर खतरे के निशान से 1.1 मीटर ऊपर। निचले गांवों में पानी भरने की आशंका।",
            action_en="Keep emergency kit and livestock ready for higher ground movement. Use NDRF boat evacuation points.",
            action_hi="जरूरी सामान और मवेशियों को ऊंचे स्थानों पर ले जाने के लिए तैयार रखें। एनडीआरएफ की नाव सहायता का उपयोग करें।",
            severity="critical",
            disaster_type="flood",
            target_region="Golaghat & Kaziranga, Assam",
            latitude=26.5800,
            longitude=93.1800,
            radius_km=45.0,
            is_official=True,
            is_active=True,
            source_attribution="State Emergency Operations Center (Simulated)",
            issued_by_user_id=admin_user.id,
            issued_at=datetime.utcnow() - timedelta(hours=5),
            expires_at=datetime.utcnow() + timedelta(hours=36)
        )

        alert3 = Alert(
            title_en="YELLOW ALERT: High Tide & Intense Cloudburst Forecast",
            title_hi="येलो अलर्ट: भारी बारिश और 4.2 मीटर ऊंची समुद्री लहरों की चेतावनी",
            message_en="Mithi River catchment vulnerable to waterlogging as 4.2m Arabian Sea high tide coincides with heavy localized rain spell.",
            message_hi="अरब सागर में 4.2 मीटर ऊंची लहरों और भारी बारिश के चलते मीठी नदी के आसपास जलभराव की संभावना।",
            action_en="Avoid subway underpasses in Kurla and Sion. Stay tuned to municipal flood ward bulletins.",
            action_hi="कुर्ला और सायन के सबवे में जाने से बचें। नगर निगम के बाढ़ नियंत्रण निर्देशों का पालन करें।",
            severity="warning",
            disaster_type="flood",
            target_region="Mumbai Metropolitan Region",
            latitude=19.0760,
            longitude=72.8777,
            radius_km=25.0,
            is_official=True,
            is_active=True,
            source_attribution="Disaster AI Rapid Warning (Simulated)",
            issued_by_user_id=admin_user.id,
            issued_at=datetime.utcnow() - timedelta(hours=1),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )

        db.session.add_all([alert1, alert2, alert3])
        db.session.commit()

        print("Seeding realistic incident reports with AI explainability...")
        # 5. REALISTIC INCIDENTS
        inc1 = Incident(
            title="Chooralmala Riverbank Mudslide — Workers Trapped in Plantation Quarters",
            disaster_type="landslide",
            description="Hill collapsed behind tea plantation settlement. 12 workers and family members trapped inside two submerged single-story quarters. Rapid mud accumulation, immediate earthmoving and rescue required.",
            latitude=11.5365,
            longitude=76.1685,
            address="Chooralmala Tea Division 2, Meppadi Panchayat, Wayanad",
            landmark="Near Chooralmala iron footbridge",
            people_affected=25,
            people_trapped=12,
            people_injured=4,
            needs_medical=True,
            needs_food_water=True,
            needs_evacuation=True,
            image_url=None,
            reported_by_user_id=citizen_user.id,
            reporter_name="Arun Kumar",
            reporter_contact="+91 94471 23456",
            status="assigned",
            verification_status="verified",
            verified_by_user_id=admin_user.id,
            verified_at=datetime.utcnow() - timedelta(minutes=90),
            admin_notes="Verified via local village officer. Dispatched NDRF Team Alpha with hydraulic spreaders.",
            ai_priority="critical",
            ai_priority_score=94.5,
            ai_priority_factors_json=json.dumps([
                {"factor": "Trapped Individuals", "points": 35.0, "weight_desc": "12 people actively trapped under debris", "severity": "CRITICAL"},
                {"factor": "Medical Emergency & Casualties", "points": 25.0, "weight_desc": "4 severe crush injuries reported", "severity": "CRITICAL"},
                {"factor": "Scale of Affected Population", "points": 10.0, "weight_desc": "Cluster settlement of 25 individuals", "severity": "HIGH"},
                {"factor": "Displacement & Essential Sustenance", "points": 15.0, "weight_desc": "Emergency evacuation & medical aid", "severity": "HIGH"},
                {"factor": "Urgent Situational Indicators (NLP)", "points": 9.5, "weight_desc": "Keywords: trapped, mudslide, collapsed, injured", "severity": "CRITICAL"}
            ]),
            ai_keywords_json=json.dumps(["trapped", "mudslide", "collapsed", "injured", "evacuation"]),
            ai_duplicate_suspect=False,
            created_at=datetime.utcnow() - timedelta(hours=2, minutes=15)
        )

        inc2 = Incident(
            title="Brahmaputra Embankment Breach at Bokakhat — 40 Villagers Isolated on Embankment",
            disaster_type="flood",
            description="Earthen bund breached at 4:00 AM. Inundation has reached waist depth across 3 hamlets. 40 people including 8 elderly and 5 children are huddled on the elevated road without clean water or dry shelter.",
            latitude=26.5920,
            longitude=93.2050,
            address="Siljuri Village, Bokakhat Sub-Division, Assam",
            landmark="Near Siljuri Primary Health Subcenter",
            people_affected=65,
            people_trapped=0,
            people_injured=1,
            needs_medical=False,
            needs_food_water=True,
            needs_evacuation=True,
            image_url=None,
            reported_by_user_id=None,
            reporter_name="Pranab Das (Gaon Burha)",
            reporter_contact="+91 94350 99881",
            status="assigned",
            verification_status="verified",
            verified_by_user_id=admin_user.id,
            verified_at=datetime.utcnow() - timedelta(minutes=45),
            admin_notes="Embankment breach verified with water resources department. Assigned boat rescue unit.",
            ai_priority="high",
            ai_priority_score=78.0,
            ai_priority_factors_json=json.dumps([
                {"factor": "Scale of Affected Population", "points": 15.0, "weight_desc": "65+ villagers severely impacted", "severity": "HIGH"},
                {"factor": "Displacement & Essential Sustenance", "points": 15.0, "weight_desc": "Isolated surrounded by flood waters, urgent water/food", "severity": "HIGH"},
                {"factor": "Medical Emergency & Casualties", "points": 8.0, "weight_desc": "Elderly and children stranded in rain", "severity": "MODERATE"},
                {"factor": "Urgent Situational Indicators (NLP)", "points": 7.0, "weight_desc": "Keywords: breach, flood, surrounded, waist deep", "severity": "HIGH"}
            ]),
            ai_keywords_json=json.dumps(["flood", "breach", "submerged", "stranded", "no food"]),
            ai_duplicate_suspect=False,
            created_at=datetime.utcnow() - timedelta(hours=3, minutes=40)
        )

        inc3 = Incident(
            title="Alaknanda Gorge Highway Blocked by Massive Rockfall",
            disaster_type="landslide",
            description="Large boulders collapsed onto NH-7 between Joshimath and Marwari. 15 tourist and transport vehicles halted. No current casualties, but slope continues to shower loose stones.",
            latitude=30.5620,
            longitude=79.5710,
            address="NH-7 Highway Km 482, Chamoli District, Uttarakhand",
            landmark="500m before Marwari Bridge",
            people_affected=35,
            people_trapped=0,
            people_injured=0,
            needs_medical=False,
            needs_food_water=False,
            needs_evacuation=False,
            image_url=None,
            reported_by_user_id=None,
            reporter_name="Sanjay Negi (Taxi Operator)",
            reporter_contact="+91 97561 11223",
            status="pending_verification",
            verification_status="unverified",
            ai_priority="medium",
            ai_priority_score=42.0,
            ai_priority_factors_json=json.dumps([
                {"factor": "Scale of Affected Population", "points": 10.0, "weight_desc": "35 stranded travelers", "severity": "MODERATE"},
                {"factor": "Trapped Individuals", "points": 0.0, "weight_desc": "No trapped or injured persons inside vehicles", "severity": "LOW"},
                {"factor": "Access Hazard", "points": 6.0, "weight_desc": "Route disruption requires BRO heavy clearance", "severity": "MODERATE"}
            ]),
            ai_keywords_json=json.dumps(["landslide", "boulder", "rockfall", "road blocked"]),
            ai_duplicate_suspect=False,
            created_at=datetime.utcnow() - timedelta(minutes=50)
        )

        inc4 = Incident(
            title="Kranti Nagar Slum Water Inundation — Chest Deep Flow",
            disaster_type="flood",
            description="Water from overflowing Mithi river has surged into ground floor dwellings. Power disconnected. 3 elderly residents need assistance exiting ground floor shanties.",
            latitude=19.0720,
            longitude=72.8830,
            address="Kranti Nagar, Near Bail Bazar, Kurla West, Mumbai",
            landmark="Behind Kurla bus depot",
            people_affected=18,
            people_trapped=3,
            people_injured=0,
            needs_medical=False,
            needs_food_water=True,
            needs_evacuation=True,
            image_url=None,
            reported_by_user_id=None,
            reporter_name="Farhan Sheikh",
            reporter_contact="+91 98200 44551",
            status="pending_verification",
            verification_status="unverified",
            ai_priority="high",
            ai_priority_score=72.5,
            ai_priority_factors_json=json.dumps([
                {"factor": "Trapped Individuals", "points": 27.0, "weight_desc": "3 elderly persons trapped by fast-rising ground water", "severity": "CRITICAL"},
                {"factor": "Displacement & Essential Sustenance", "points": 15.0, "weight_desc": "Immediate evacuation needed", "severity": "HIGH"},
                {"factor": "Scale of Affected Population", "points": 10.0, "weight_desc": "18 residents directly affected", "severity": "HIGH"}
            ]),
            ai_keywords_json=json.dumps(["rising water", "chest deep", "trapped", "elderly", "evacuation"]),
            ai_duplicate_suspect=False,
            created_at=datetime.utcnow() - timedelta(minutes=25)
        )

        inc5 = Incident(
            title="Tree Fallen on Electric Line and Minor Waterlogging",
            disaster_type="flood",
            description="Moderate water stagnation on internal society lane. One gulmohar tree fallen across local power cable. No structural collapse or injuries.",
            latitude=19.0850,
            longitude=72.8900,
            address="Ghatkopar West Residential Colony, Mumbai",
            landmark="Near R City Mall back gate",
            people_affected=4,
            people_trapped=0,
            people_injured=0,
            needs_medical=False,
            needs_food_water=False,
            needs_evacuation=False,
            image_url=None,
            reported_by_user_id=None,
            reporter_name="Sneha Patil",
            reporter_contact="+91 98199 88776",
            status="pending_verification",
            verification_status="unverified",
            ai_priority="low",
            ai_priority_score=18.5,
            ai_priority_factors_json=json.dumps([
                {"factor": "Scale of Affected Population", "points": 3.0, "weight_desc": "Minor localized disruption", "severity": "LOW"},
                {"factor": "Life Safety", "points": 0.0, "weight_desc": "Zero trapped or injured individuals", "severity": "LOW"}
            ]),
            ai_keywords_json=json.dumps(["waterlogging", "tree fallen"]),
            ai_duplicate_suspect=False,
            created_at=datetime.utcnow() - timedelta(hours=1, minutes=10)
        )

        db.session.add_all([inc1, inc2, inc3, inc4, inc5])
        db.session.commit()

        # Connect assignments
        assign1 = RescueAssignment(
            incident_id=inc1.id,
            team_id=team_ndrf_kerala.id,
            status="en_route",
            operational_notes="NDRF Team Alpha dispatched from Kalpetta. Heavy rainfall on route; estimated arrival 20 mins.",
            resource_requests="Require 1 additional JCB excavator and 4 folding stretchers at Chooralmala bridge junction.",
            assigned_by_user_id=admin_user.id,
            assigned_at=datetime.utcnow() - timedelta(minutes=80)
        )

        assign2 = RescueAssignment(
            incident_id=inc2.id,
            team_id=team_ndrf_assam.id,
            status="on_site",
            operational_notes="Amphibious unit on site. 2 Gemini boats deployed. Successfully ferried 16 women and children to Bokakhat relief camp.",
            resource_requests="Urgent requirement for 200 chlorine purification packs and dry ration bags.",
            assigned_by_user_id=admin_user.id,
            assigned_at=datetime.utcnow() - timedelta(minutes=40)
        )

        db.session.add_all([assign1, assign2])
        db.session.commit()

        print("Seeding risk assessment records...")
        # 6. RISK ASSESSMENTS
        risk1 = RiskAssessment(
            location_name="Wayanad District, Western Ghats, Kerala",
            latitude=11.6854,
            longitude=76.1320,
            disaster_type="landslide",
            risk_category="very_high",
            risk_score=89.4,
            confidence_score=0.91,
            features_json=json.dumps({
                "recent_rainfall_mm": 210.0,
                "forecast_rainfall_mm": 130.0,
                "soil_moisture_pct": 92.0,
                "slope_deg": 38.0,
                "elevation_m": 1280.0,
                "river_proximity_km": 1.2,
                "historical_disaster_freq": 8.0,
                "drainage_density_score": 1.8
            }),
            contributing_factors_json=json.dumps([
                {"factor": "Critically Steep Terrain Slope", "value": "38.0°", "impact": "CRITICAL", "detail": "Gravitational shear stress dramatically increases debris failure risk."},
                {"factor": "High Monsoon Infiltration", "value": "210.0 mm in 48h", "impact": "CRITICAL", "detail": "Pore-water pressure destabilizes unconsolidated topsoil mantle."},
                {"factor": "Saturated Soil Mantle", "value": "92.0%", "impact": "HIGH", "detail": "Liquefaction and mudflow trigger conditions active."}
            ]),
            missing_data_warnings_json=json.dumps([]),
            model_name="RandomForestClassifier + GradientBoostingRegressor Ensemble",
            data_source="DEMO/SIMULATED - Regional Geo-Climatic Baseline",
            created_at=datetime.utcnow() - timedelta(hours=4)
        )

        risk2 = RiskAssessment(
            location_name="Kaziranga / Brahmaputra Basin, Assam",
            latitude=26.5775,
            longitude=93.1711,
            disaster_type="flood",
            risk_category="very_high",
            risk_score=92.1,
            confidence_score=0.94,
            features_json=json.dumps({
                "recent_rainfall_mm": 185.0,
                "forecast_rainfall_mm": 120.0,
                "soil_moisture_pct": 95.0,
                "slope_deg": 1.8,
                "elevation_m": 65.0,
                "river_proximity_km": 0.4,
                "historical_disaster_freq": 9.0,
                "drainage_density_score": 1.2
            }),
            contributing_factors_json=json.dumps([
                {"factor": "Extreme Recent Rainfall", "value": "185.0 mm in 48h", "impact": "CRITICAL", "detail": "Precipitation volume severely exceeds catchment absorption threshold."},
                {"factor": "Immediate River Proximity", "value": "0.40 km", "impact": "HIGH", "detail": "Within natural overflow buffer during peak stage."},
                {"factor": "High Soil Saturation", "value": "95.0%", "impact": "HIGH", "detail": "Near-complete soil water saturation limits further infiltration."}
            ]),
            missing_data_warnings_json=json.dumps([]),
            model_name="RandomForestClassifier + GradientBoostingRegressor Ensemble",
            data_source="DEMO/SIMULATED - Regional Geo-Climatic Baseline",
            created_at=datetime.utcnow() - timedelta(hours=6)
        )

        db.session.add_all([risk1, risk2])
        db.session.commit()

        print("Database successfully seeded with realistic Indian disaster response scenario!")
        print("Demo User Credentials:")
        print("  Administrator: username='admin', password='AdminPass123!' (Role: admin)")
        print("  Rescue Officer: username='rescue_lead', password='RescuePass123!' (Role: rescue_team)")
        print("  Citizen: username='citizen', password='CitizenPass123!' (Role: citizen)")

if __name__ == "__main__":
    seed_database()
