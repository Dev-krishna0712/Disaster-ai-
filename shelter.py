from datetime import datetime
import json
from app.database import db

class Shelter(db.Model):
    __tablename__ = "shelters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_occupancy = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="open")  # open, full, closed
    contact_phone = db.Column(db.String(30), nullable=True)
    amenities_json = db.Column(db.Text, default='["drinking_water", "first_aid", "emergency_power"]')

    resources = db.relationship("ResourceInventory", backref="shelter", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def occupancy_rate(self) -> float:
        if self.capacity <= 0:
            return 100.0
        return round((self.current_occupancy / self.capacity) * 100, 1)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "capacity": self.capacity,
            "current_occupancy": self.current_occupancy,
            "occupancy_rate": self.occupancy_rate,
            "status": self.status,
            "contact_phone": self.contact_phone,
            "amenities": json.loads(self.amenities_json) if self.amenities_json else [],
            "resources": [r.to_dict() for r in self.resources],
        }

class ResourceInventory(db.Model):
    __tablename__ = "resource_inventory"

    id = db.Column(db.Integer, primary_key=True)
    shelter_id = db.Column(db.Integer, db.ForeignKey("shelters.id"), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # food, water, medical, boats, blankets, equipment
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(30), nullable=False)  # liters, packets, kits, units
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "shelter_id": self.shelter_id,
            "item_name": self.item_name,
            "category": self.category,
            "quantity": self.quantity,
            "unit": self.unit,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }
