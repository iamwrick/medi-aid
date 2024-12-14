# src/main.py
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import Dict
from datetime import datetime
import json
import os
from pathlib import Path

from src.models.incident import Incident, Location, VitalSigns
from src.utils.logger import get_logger

# Initialize logging
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Emergency Response System",
    description="AI-powered emergency response coordination system",
    version="1.0.0"
)

# Ensure reports directory exists
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/incidents/")
async def create_incident(incident_data: Dict):
    """Handle new emergency incidents"""
    try:
        logger.info("Received new incident")
        logger.debug(f"Incident data: {json.dumps(incident_data, indent=2)}")

        # Validate required fields
        required_fields = ['patient_age', 'patient_gender', 'chief_complaint', 'location', 'vitals']
        for field in required_fields:
            if field not in incident_data:
                logger.error(f"Missing required field: {field}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        # Create incident objects
        try:
            location = Location(
                latitude=incident_data['location']['lat'],
                longitude=incident_data['location']['lng'],
                description=incident_data['location'].get('description', '')
            )

            vitals = VitalSigns(
                heart_rate=incident_data['vitals']['heart_rate'],
                blood_pressure_systolic=incident_data['vitals']['blood_pressure_systolic'],
                blood_pressure_diastolic=incident_data['vitals']['blood_pressure_diastolic'],
                spo2=incident_data['vitals']['spo2'],
                respiratory_rate=incident_data['vitals']['respiratory_rate']
            )

            incident = Incident.create(
                location=location,
                patient_age=incident_data['patient_age'],
                patient_gender=incident_data['patient_gender'],
                chief_complaint=incident_data['chief_complaint'],
                vitals=vitals
            )

        except Exception as e:
            logger.error(f"Error creating incident objects: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data format: {str(e)}"
            )

        # Generate mock response for testing
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = REPORTS_DIR / f"incident_report_{timestamp}.txt"

        # Create a simple report
        with open(report_path, 'w') as f:
            f.write(f"=== Emergency Incident Report ===\n")
            f.write(f"Time: {datetime.now().isoformat()}\n")
            f.write(f"\nPatient Information:\n")
            f.write(f"Age: {incident_data['patient_age']}\n")
            f.write(f"Gender: {incident_data['patient_gender']}\n")
            f.write(f"Chief Complaint: {incident_data['chief_complaint']}\n")
            f.write(f"\nVital Signs:\n")
            for key, value in incident_data['vitals'].items():
                f.write(f"{key}: {value}\n")

        return {
            "status": "success",
            "incident_id": f"INC-{timestamp}",
            "report_path": str(report_path),
            "summary": {
                "severity_level": calculate_severity(incident_data),
                "response_time": "immediate",
                "assigned_resources": ["ambulance-1", "trauma-team-A"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


def calculate_severity(incident_data: Dict) -> int:
    """Calculate incident severity (mock implementation)"""
    severity = 3  # Default moderate severity

    vitals = incident_data['vitals']

    # Check vital signs for severity indicators
    if (vitals['heart_rate'] > 120 or vitals['heart_rate'] < 50 or
            vitals['blood_pressure_systolic'] > 180 or
            vitals['blood_pressure_systolic'] < 90 or
            vitals['spo2'] < 90):
        severity = 4

    # Check chief complaint for critical conditions
    critical_conditions = [
        "chest pain",
        "difficulty breathing",
        "unconscious",
        "severe bleeding"
    ]

    if any(condition in incident_data['chief_complaint'].lower()
           for condition in critical_conditions):
        severity = 5

    return severity


def start():
    """Start the FastAPI application"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )


if __name__ == "__main__":
    start()