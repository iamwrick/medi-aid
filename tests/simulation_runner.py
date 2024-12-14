# tests/simulation_runner.py
import sys
import json
import random
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import concurrent.futures
import asyncio
import traceback

from src.services.maps_service import MapsService
from src.utils.audit_logger import AuditLogger
from uuid import uuid4

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


class EmergencySimulator:
    def __init__(self):
        self.simulation_id = str(uuid4())[:8]
        self.base_url = "http://localhost:8000"
        self.reports_dir = project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.debug_mode = True  # Enable debugging
        # Initialize Maps Service
        self.maps_service = MapsService()

        # Initialize audit logger
        self.audit_logger = AuditLogger(self.simulation_id)

        # Simulation configurations
        self.num_scenarios = 5
        self.delay_between_scenarios = 2

    def check_api_health(self):
        """Check if the API is running and healthy"""
        try:
            response = requests.get(f"{self.base_url}/")
            print("\nAPI Health Check Response:")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

            if response.status_code == 200:
                print("✓ API is running and healthy")
                return True
            else:
                print(f"✗ API returned status code {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("✗ Could not connect to API - please ensure it's running")
            return False
        except Exception as e:
            print(f"✗ Error checking API health: {str(e)}")
            return False

    def generate_random_incident(self) -> Dict:
        """Generate random incident data with enhanced location handling"""
        chief_complaints = [
            "chest pain with left arm radiation",
            "severe shortness of breath",
            "sudden onset severe headache",
            "loss of consciousness"
        ]

        # Predefined locations with proper formatting
        locations = [
            {"lat": 40.7829, "lng": -73.9654, "name": "Central Park"},
            {"lat": 40.7484, "lng": -73.9857, "name": "Times Square"},
            {"lat": 40.7527, "lng": -73.9772, "name": "Grand Central"},
            {"lat": 40.7589, "lng": -73.9851, "name": "Rockefeller Center"}
        ]

        # Select random location
        location = random.choice(locations)

        try:
            # Get location details
            location_coords = (location['lat'], location['lng'])
            location_details = self.maps_service.get_location_details(location_coords)

            if location_details:
                self.audit_logger.log_step(
                    "Location Details Retrieved",
                    location_details
                )

            # Find nearest hospital
            nearest_hospital = self.maps_service.get_nearest_hospital(location_coords)

            if nearest_hospital:
                self.audit_logger.log_step(
                    "Nearest Hospital Found",
                    nearest_hospital
                )

                hospital_info = {
                    "name": nearest_hospital.get('name', 'Unknown'),
                    "address": nearest_hospital.get('vicinity', 'Unknown'),
                    "rating": nearest_hospital.get('rating', 'N/A')
                }
            else:
                hospital_info = None
                self.audit_logger.log_error(
                    "Hospital Search",
                    Exception("No hospitals found nearby")
                )

            # Create incident data
            incident = {
                "patient_age": random.randint(25, 85),
                "patient_gender": random.choice(["male", "female"]),
                "chief_complaint": random.choice(chief_complaints),
                "location": {
                    "lat": location['lat'],
                    "lng": location['lng'],
                    "description": location_details.get('formatted_address', location['name']) if location_details else
                    location['name'],
                    "nearest_hospital": hospital_info
                },
                "vitals": {
                    "heart_rate": random.randint(60, 130),
                    "blood_pressure_systolic": random.randint(100, 180),
                    "blood_pressure_diastolic": random.randint(60, 100),
                    "spo2": random.randint(88, 100),
                    "respiratory_rate": random.randint(12, 24)
                }
            }

            if self.debug_mode:
                print("\nGenerated incident data:")
                print(json.dumps(incident, indent=2))

            return incident

        except Exception as e:
            self.audit_logger.log_error(
                "Incident Generation",
                e,
                {"location": location}
            )
            # Return basic incident data without enhanced location details
            return {
                "patient_age": random.randint(25, 85),
                "patient_gender": random.choice(["male", "female"]),
                "chief_complaint": random.choice(chief_complaints),
                "location": {
                    "lat": location['lat'],
                    "lng": location['lng'],
                    "description": location['name'],
                    "nearest_hospital": None
                },
                "vitals": {
                    "heart_rate": random.randint(60, 130),
                    "blood_pressure_systolic": random.randint(100, 180),
                    "blood_pressure_diastolic": random.randint(60, 100),
                    "spo2": random.randint(88, 100),
                    "respiratory_rate": random.randint(12, 24)
                }
            }

    async def process_incident(self, incident_data: Dict, scenario_num: int):
        """Process a single incident with detailed logging"""
        try:
            self.audit_logger.log_step(
                f"Starting Scenario {scenario_num}",
                {
                    "incident_data": incident_data,
                    "timestamp": datetime.now().isoformat()
                }
            )

            # Make the request
            self.audit_logger.log_step("Sending Request", {
                "url": f"{self.base_url}/incidents/",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "payload": incident_data
            })

            response = requests.post(
                f"{self.base_url}/incidents/",
                json=incident_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            self.audit_logger.log_step("Received Response", {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text
            })

            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                self.audit_logger.log_error(
                    "Response Parsing",
                    e,
                    {"raw_response": response.text}
                )
                response_data = None

            if response.status_code == 200 and response_data:
                self.audit_logger.log_step(
                    f"Scenario {scenario_num} Successful",
                    response_data
                )
                return {
                    "status": "success",
                    "data": response_data,
                    "response_code": response.status_code
                }
            else:
                self.audit_logger.log_error(
                    f"Scenario {scenario_num} Failed",
                    Exception(f"Status code: {response.status_code}"),
                    {"response": response.text}
                )
                return {
                    "status": "failed",
                    "error": f"Failed with status {response.status_code}: {response.text}",
                    "response_code": response.status_code
                }

        except Exception as e:
            self.audit_logger.log_error(
                f"Scenario {scenario_num} Exception",
                e,
                {"incident_data": incident_data}
            )
            return {"status": "failed", "error": str(e)}

    async def run_simulation(self):
        """Run the complete simulation with audit logging"""
        self.audit_logger.log_step("Starting Simulation", {
            "simulation_id": self.simulation_id,
            "num_scenarios": self.num_scenarios,
            "timestamp": datetime.now().isoformat()
        })

        if not self.check_api_health():
            self.audit_logger.log_error(
                "API Health Check",
                Exception("API not healthy")
            )
            return

        results = []
        for i in range(self.num_scenarios):
            try:
                incident_data = self.generate_random_incident()
                result = await self.process_incident(incident_data, i + 1)
                results.append({
                    "scenario_num": i + 1,
                    "incident_data": incident_data,
                    "result": result
                })
                await asyncio.sleep(self.delay_between_scenarios)
            except Exception as e:
                self.audit_logger.log_error(
                    f"Scenario {i + 1}",
                    e
                )

        # Generate reports
        self.generate_simulation_summary(results)
        audit_report = self.audit_logger.generate_audit_report()

        print(f"\nSimulation completed!")
        print(f"Audit report generated: {audit_report}")

    def generate_simulation_summary(self, results: List[Dict]):
        """Generate a comprehensive summary with error details"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_path = self.reports_dir / f"simulation_summary_{timestamp}.txt"

        successful_scenarios = len([r for r in results if r['result'].get('status') == 'success'])

        with open(summary_path, 'w') as f:
            # Write header
            f.write("=== Emergency Response System Simulation Summary ===\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Scenarios: {self.num_scenarios}\n")
            f.write(f"Successful Scenarios: {successful_scenarios}\n")
            f.write(f"Failed Scenarios: {self.num_scenarios - successful_scenarios}\n")
            f.write("\nDetailed Results:\n")

            # Write detailed results for each scenario
            for result in results:
                f.write(f"\n{'=' * 50}\n")
                f.write(f"Scenario {result['scenario_num']}:\n")
                f.write("\nIncident Data:\n")
                f.write(json.dumps(result['incident_data'], indent=2) + "\n")

                # Write result details
                scenario_result = result['result']
                f.write(f"\nStatus: {scenario_result.get('status', 'unknown')}\n")

                if scenario_result.get('status') == 'success':
                    f.write("\nResponse Data:\n")
                    f.write(json.dumps(scenario_result.get('data', {}), indent=2) + "\n")
                    if 'report_path' in scenario_result.get('data', {}):
                        f.write(f"\nReport Generated: {scenario_result['data']['report_path']}\n")
                else:
                    f.write("\nError Details:\n")
                    f.write(f"Response Code: {scenario_result.get('response_code', 'N/A')}\n")
                    f.write(f"Error Message: {scenario_result.get('error', 'Unknown error')}\n")

                f.write("\nTimestamp: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")

            # Write summary footer
            f.write(f"\n{'=' * 50}\n")
            f.write("\nSimulation Summary:\n")
            f.write(f"Success Rate: {(successful_scenarios / self.num_scenarios) * 100:.2f}%\n")
            f.write(f"Total Runtime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            if successful_scenarios < self.num_scenarios:
                f.write("\nTroubleshooting Tips:\n")
                f.write("1. Verify that the API server is running and accessible\n")
                f.write("2. Check API logs for detailed error messages\n")
                f.write("3. Verify that all required services are operational\n")
                f.write("4. Check network connectivity and firewall settings\n")

        print(f"\nSimulation completed!")
        print(f"Summary report generated: {summary_path}")

        # If in debug mode, print the summary to console as well
        if self.debug_mode:
            with open(summary_path, 'r') as f:
                print("\nSummary Report Contents:")
                print(f.read())

        return summary_path


async def run():
    """Async wrapper for running the simulation"""
    try:
        # Check if the API is accessible
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code != 200:
                print(f"\n⚠️  Warning: API returned status code {response.status_code}")
                print("Response:", response.text)
                if input("Continue anyway? (y/n): ").lower() != 'y':
                    return
        except requests.exceptions.ConnectionError:
            print("\n⚠️  Error: Could not connect to API at http://localhost:8000")
            print("Please ensure the API server is running first!")
            print("\nTo start the API server, run:")
            print("python src/main.py")
            return
        except Exception as e:
            print(f"\n⚠️  Error checking API: {str(e)}")
            if input("Continue anyway? (y/n): ").lower() != 'y':
                return

        # Create and run simulator
        simulator = EmergencySimulator()
        await simulator.run_simulation()

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    except Exception as e:
        print(f"\nFatal error in simulation:")
        traceback.print_exc()


def main():
    """Main entry point"""
    try:
        # Check if running on Windows
        if sys.platform.startswith('win'):
            # Set up proper async event loop for Windows
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Run the async simulation
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()