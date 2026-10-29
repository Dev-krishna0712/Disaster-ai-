"""
Pydantic Request Schemas & Input Validators
Ensures safe typing, prevents malicious payloads, and provides helpful validation errors.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator

class UserRegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(default="citizen")
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    organization: Optional[str] = None

    @field_validator("role")
    def validate_role(cls, v):
        allowed = {"citizen", "admin", "rescue_team"}
        if v not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return v

class UserLoginSchema(BaseModel):
    username: str
    password: str

class IncidentCreateSchema(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    disaster_type: str = Field(default="flood")
    description: str = Field(..., min_length=10, max_length=2000)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address: str = Field(..., min_length=3, max_length=300)
    landmark: Optional[str] = None
    people_affected: int = Field(default=1, ge=1, le=100000)
    people_trapped: int = Field(default=0, ge=0, le=10000)
    people_injured: int = Field(default=0, ge=0, le=10000)
    needs_medical: bool = False
    needs_food_water: bool = False
    needs_evacuation: bool = False
    image_url: Optional[str] = None
    reporter_name: Optional[str] = None
    reporter_contact: Optional[str] = None

class IncidentVerifySchema(BaseModel):
    verification_status: str  # verified, rejected, duplicate, needs_info
    admin_notes: Optional[str] = None
    admin_override_priority: Optional[str] = None  # critical, high, medium, low
    admin_override_reason: Optional[str] = None

    @field_validator("verification_status")
    def validate_verification(cls, v):
        allowed = {"verified", "rejected", "duplicate", "needs_info"}
        if v not in allowed:
            raise ValueError(f"Verification status must be one of {allowed}")
        return v

class IncidentStatusUpdateSchema(BaseModel):
    status: str  # pending_verification, verified, assigned, en_route, on_site, resolved, rejected, duplicate

    @field_validator("status")
    def validate_status(cls, v):
        allowed = {"pending_verification", "verified", "assigned", "en_route", "on_site", "resolved", "rejected", "duplicate"}
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v

class RiskPredictSchema(BaseModel):
    location_name: Optional[str] = "Selected Coordinates"
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    disaster_type: str = Field(default="flood")
    recent_rainfall_mm: Optional[float] = None
    forecast_rainfall_mm: Optional[float] = None
    soil_moisture_pct: Optional[float] = None
    slope_deg: Optional[float] = None
    elevation_m: Optional[float] = None
    river_proximity_km: Optional[float] = None
    historical_disaster_freq: Optional[float] = None
    drainage_density_score: Optional[float] = None

class AlertCreateSchema(BaseModel):
    title_en: str = Field(..., min_length=5, max_length=200)
    title_hi: str = Field(..., min_length=5, max_length=250)
    message_en: str = Field(..., min_length=10)
    message_hi: str = Field(..., min_length=10)
    action_en: Optional[str] = None
    action_hi: Optional[str] = None
    severity: str = Field(default="warning")  # info, warning, critical
    disaster_type: str = Field(default="general")
    target_region: str = Field(..., min_length=3, max_length=150)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: float = Field(default=25.0, ge=1.0, le=500.0)

class RescueAssignSchema(BaseModel):
    incident_id: int
    team_id: int
    operational_notes: Optional[str] = None
