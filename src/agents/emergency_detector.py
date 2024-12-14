# src/agents/emergency_detector.py
from typing import Dict, List
from datetime import datetime
from crewai import Agent
from langchain.tools import Tool
from langchain_community.agent_toolkits.load_tools import load_tools

from src.utils.logger import get_logger
from .base_agent import BaseAgent  # Updated import statement

logger = get_logger(__name__)


class EmergencyDetectorAgent(BaseAgent):
    def _create_agent(self) -> Agent:
        # Load medical research tools
        medical_tools = load_tools(["google-search", "wikipedia"])

        return Agent(
            role='Emergency Detection Specialist',
            goal='Analyze emergency situations and determine severity',
            backstory="""You are an expert in emergency medical situations with 
            years of experience in triage and emergency response. Your role is to 
            quickly and accurately assess medical emergencies.""",
            tools=self.tools + medical_tools,
            verbose=True
        )

    def process(self, incident_data: Dict) -> Dict:
        """
        Analyze emergency situation and determine severity level.
        """
        try:
            # Extract relevant information
            vitals = incident_data.get('vitals', {})
            symptoms = incident_data.get('chief_complaint', '')
            age = incident_data.get('patient_age')

            # Create analysis prompt
            analysis_prompt = f"""
            Analyze the following emergency situation:
            - Patient Age: {age}
            - Symptoms: {symptoms}
            - Vital Signs:
                * Heart Rate: {vitals.get('heart_rate')}
                * Blood Pressure: {vitals.get('blood_pressure')}
                * SpO2: {vitals.get('spo2')}
                * Respiratory Rate: {vitals.get('respiratory_rate')}

            Determine:
            1. Severity level (1-10)
            2. Immediate medical considerations
            3. Required medical resources
            """

            # Get analysis from agent
            response = self.agent.run(analysis_prompt)

            # Parse and structure the response
            # Note: In a real implementation, you'd want more robust parsing
            severity = self._extract_severity(response)
            considerations = self._extract_considerations(response)

            return {
                "severity_level": severity,
                "medical_considerations": considerations,
                "raw_analysis": response
            }

        except Exception as e:
            logger.error(f"Error in emergency detection: {str(e)}")
            raise

    def _extract_severity(self, response: str) -> int:
        """Extract severity level from agent response."""
        try:
            # Implementation would depend on response format
            # This is a simplified version
            if "severity" in response.lower():
                for i in range(1, 11):
                    if str(i) in response:
                        return i
            return 5  # Default moderate severity if unable to determine
        except Exception:
            return 5

    def _extract_considerations(self, response: str) -> List[str]:
        """Extract medical considerations from agent response."""
        # Implementation would depend on response format
        return [line.strip() for line in response.split('\n')
                if line.strip().startswith('-')]