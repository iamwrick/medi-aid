# src/models/incident.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

@dataclass
class Location:
    latitude: float
    longitude: float
    description: Optional[str] = None

@dataclass
class VitalSigns:
    heart_rate: int
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    spo2: int
    respiratory_rate: int

@dataclass
class Incident:
    id: UUID
    timestamp: datetime
    location: Location
    patient_age: int
    patient_gender: str
    chief_complaint: str
    vitals: VitalSigns
    severity_level: Optional[int] = None

    @classmethod
    def create(cls, **kwargs):
        kwargs['id'] = kwargs.get('id', uuid4())
        kwargs['timestamp'] = kwargs.get('timestamp', datetime.now())
        return cls(**kwargs)