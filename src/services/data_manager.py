import json
from typing import Dict, List, Optional
from pathlib import Path
from src.config.settings import DATA_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DataManager:
    def __init__(self):
        self._ambulances = None
        self._hospitals = None
        self._personnel = None
        self.load_all_data()

    def load_all_data(self) -> None:
        """Load all data from JSON files."""
        try:
            self._ambulances = self._load_json_file("ambulances.json")
            self._hospitals = self._load_json_file("hospitals.json")
            self._personnel = self._load_json_file("medical_personnel.json")
            logger.info("Successfully loaded all data")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def _load_json_file(self, filename: str) -> Dict:
        """Load data from a JSON file."""
        file_path = DATA_DIR / filename
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
            return {}

    def get_available_ambulances(self) -> List[Dict]:
        """Return list of available ambulances."""
        return [
            amb for amb in self._ambulances.get('ambulances', [])
            if amb['status'] == 'available'
        ]

    def get_hospital_capacity(self, hospital_id: str) -> Optional[Dict]:
        """Get current capacity for a specific hospital."""
        for hospital in self._hospitals.get('hospitals', []):
            if hospital['hospital_id'] == hospital_id:
                return hospital['emergency_department']
        return None