# src/utils/report_generator.py
from datetime import datetime
from pathlib import Path
import json
from typing import Dict


class ReportGenerator:
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def generate_emergency_report(self, incident_data: Dict, analysis_results: Dict) -> str:
        """
        Generate a detailed report of the emergency response process.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emergency_report_{timestamp}.txt"
        filepath = self.reports_dir / filename

        with open(filepath, 'w') as f:
            f.write("=== EMERGENCY RESPONSE SYSTEM REPORT ===\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Incident Details
            f.write("INCIDENT DETAILS\n")
            f.write("================\n")
            f.write(f"Patient Age: {incident_data['patient_age']}\n")
            f.write(f"Patient Gender: {incident_data['patient_gender']}\n")
            f.write(f"Chief Complaint: {incident_data['chief_complaint']}\n")
            f.write(f"Location: {incident_data['location']['description']}\n")
            f.write("\nVital Signs:\n")
            for key, value in incident_data['vitals'].items():
                f.write(f"- {key}: {value}\n")
            f.write("\n")

            # Emergency Analysis
            f.write("EMERGENCY ANALYSIS\n")
            f.write("=================\n")
            if 'severity_analysis' in analysis_results:
                f.write(f"Severity Level: {analysis_results['severity_analysis'].get('severity_level')}\n")
                f.write("\nMedical Considerations:\n")
                for consideration in analysis_results['severity_analysis'].get('medical_considerations', []):
                    f.write(f"- {consideration}\n")
            f.write("\n")

            # Resource Allocation
            f.write("RESOURCE ALLOCATION\n")
            f.write("==================\n")
            if 'resource_allocation' in analysis_results:
                resources = analysis_results['resource_allocation']
                f.write("\nAssigned Resources:\n")
                for resource_type, details in resources.get('recommended_resources', {}).items():
                    f.write(f"\n{resource_type.upper()}:\n")
                    if isinstance(details, list):
                        for item in details:
                            f.write(f"- {item}\n")
                    else:
                        f.write(f"- {details}\n")
            f.write("\n")

            # Medical Guidance
            f.write("MEDICAL GUIDANCE\n")
            f.write("===============\n")
            if 'medical_guidance' in analysis_results:
                guidance = analysis_results['medical_guidance']

                f.write("\nImmediate Interventions:\n")
                for intervention in guidance.get('immediate_interventions', []):
                    f.write(f"- {intervention}\n")

                f.write("\nTransport Guidelines:\n")
                for guideline in guidance.get('transport_guidelines', []):
                    f.write(f"- {guideline}\n")

                f.write("\nHospital Preparations:\n")
                for prep in guidance.get('hospital_preparations', []):
                    f.write(f"- {prep}\n")
            f.write("\n")

            # Timeline
            f.write("RESPONSE TIMELINE\n")
            f.write("================\n")
            if 'timeline' in analysis_results:
                for entry in analysis_results['timeline']:
                    f.write(f"{entry['timestamp']}: {entry['action']}\n")
            f.write("\n")

        return str(filepath)