# src/agents/medical_advisor.py
from typing import Dict, List
from datetime import datetime
from crewai import Agent
from langchain.tools import Tool
from src.utils.logger import get_logger
from .base_agent import BaseAgent  # Updated import statement

logger = get_logger(__name__)


class MedicalAdvisorAgent(BaseAgent):
    def _create_agent(self) -> Agent:
        return Agent(
            role='Medical Advisor',
            goal='Provide medical guidance and protocol recommendations',
            backstory="""You are a senior emergency medicine physician with 
            expertise in rapid response protocols and emergency care guidelines. 
            Your role is to provide critical medical guidance.""",
            tools=self.tools,
            verbose=True
        )

    def process(self, data: Dict) -> Dict:
        """
        Provide medical guidance based on emergency analysis and resource allocation.
        """
        try:
            severity = data.get('severity_level', 5)
            medical_considerations = data.get('medical_considerations', [])
            allocated_resources = data.get('allocated_resources', {})
            patient_data = data.get('patient_data', {})

            # Create medical guidance prompt
            guidance_prompt = f"""
            Provide medical guidance for emergency:
            Severity Level: {severity}
            Medical Considerations: {medical_considerations}

            Patient Information:
            - Age: {patient_data.get('age')}
            - Gender: {patient_data.get('gender')}
            - Chief Complaint: {patient_data.get('chief_complaint')}
            - Vital Signs: {patient_data.get('vitals')}

            Allocated Resources:
            - Ambulance Type: {allocated_resources.get('ambulance_type')}
            - Hospital: {allocated_resources.get('hospital')}

            Provide:
            1. Immediate medical interventions
            2. Transportation considerations
            3. Preparation instructions for receiving hospital
            4. Additional medical protocols to be followed
            """

            # Get medical guidance from agent
            response = self.agent.run(guidance_prompt)

            return self._parse_medical_guidance(response)

        except Exception as e:
            logger.error(f"Error in medical advisory: {str(e)}")
            raise

    def _parse_medical_guidance(self, response: str) -> Dict:
        """
        Parse and structure the medical guidance response.
        """
        try:
            return {
                "immediate_interventions": self._extract_interventions(response),
                "transport_guidelines": self._extract_transport_guidelines(response),
                "hospital_preparations": self._extract_hospital_preparations(response),
                "medical_protocols": self._extract_protocols(response),
                "raw_guidance": response
            }
        except Exception as e:
            logger.error(f"Error parsing medical guidance: {str(e)}")
            raise

    def _extract_interventions(self, response: str) -> List[str]:
        """
        Extract immediate intervention steps from the response.
        """
        interventions = []
        in_section = False

        for line in response.split('\n'):
            line = line.strip()
            if 'immediate' in line.lower() and 'intervention' in line.lower():
                in_section = True
                continue
            elif in_section and line and line[0].isdigit():
                interventions.append(line.split('. ', 1)[1] if '. ' in line else line)
            elif in_section and not line:
                in_section = False

        return interventions

    def _extract_transport_guidelines(self, response: str) -> Dict:
        """
        Extract transportation guidelines from the response.
        """
        guidelines = {
            "positioning": None,
            "monitoring": [],
            "precautions": []
        }

        transport_section = self._extract_section(response, "transportation")
        if transport_section:
            # Extract positioning information
            position_match = [line for line in transport_section.split('\n')
                              if 'position' in line.lower()]
            if position_match:
                guidelines["positioning"] = position_match[0].split(': ', 1)[1] if ': ' in position_match[0] else \
                position_match[0]

            # Extract monitoring requirements
            guidelines["monitoring"] = [line.strip() for line in transport_section.split('\n')
                                        if 'monitor' in line.lower()]

            # Extract precautions
            guidelines["precautions"] = [line.strip() for line in transport_section.split('\n')
                                         if any(word in line.lower() for word in ['caution', 'warning', 'avoid'])]

        return guidelines

    def _extract_hospital_preparations(self, response: str) -> Dict:
        """
        Extract hospital preparation instructions from the response.
        """
        preparations = {
            "immediate_needs": [],
            "specialist_requirements": [],
            "equipment_preparation": []
        }

        prep_section = self._extract_section(response, "preparation")
        if prep_section:
            for line in prep_section.split('\n'):
                line = line.strip()
                if line:
                    if 'specialist' in line.lower() or 'consult' in line.lower():
                        preparations["specialist_requirements"].append(line)
                    elif 'equipment' in line.lower() or 'prepare' in line.lower():
                        preparations["equipment_preparation"].append(line)
                    else:
                        preparations["immediate_needs"].append(line)

        return preparations

    def _extract_protocols(self, response: str) -> List[Dict]:
        """
        Extract specific medical protocols from the response.
        """
        protocols = []
        protocol_section = self._extract_section(response, "protocol")

        if protocol_section:
            current_protocol = None
            current_steps = []

            for line in protocol_section.split('\n'):
                line = line.strip()
                if line:
                    if line.endswith(':'):
                        if current_protocol:
                            protocols.append({
                                "name": current_protocol,
                                "steps": current_steps
                            })
                        current_protocol = line[:-1]
                        current_steps = []
                    elif current_protocol and line:
                        current_steps.append(line)

            if current_protocol:
                protocols.append({
                    "name": current_protocol,
                    "steps": current_steps
                })

        return protocols

    def _extract_section(self, response: str, section_keyword: str) -> str:
        """
        Helper method to extract a specific section from the response.
        """
        lines = response.split('\n')
        section_content = []
        in_section = False

        for line in lines:
            if section_keyword in line.lower():
                in_section = True
                continue
            elif in_section and line.strip() and not any(keyword in line.lower()
                                                         for keyword in
                                                         ['immediate', 'transport', 'preparation', 'protocol']):
                section_content.append(line)
            elif in_section and not line.strip():
                in_section = False

        return '\n'.join(section_content)

    def get_emergency_protocols(self, condition: str) -> List[Dict]:
        """
        Retrieve standard emergency protocols for specific conditions.
        """
        try:
            protocol_prompt = f"""
            Provide standard emergency medical protocols for: {condition}
            Include:
            1. Initial assessment steps
            2. Critical interventions
            3. Monitoring requirements
            4. Contraindications
            5. Special considerations
            """

            response = self.agent.run(protocol_prompt)
            return self._parse_protocols(response)

        except Exception as e:
            logger.error(f"Error retrieving protocols for {condition}: {str(e)}")
            raise

    def validate_intervention(self, intervention: str, patient_data: Dict) -> Dict:
        """
        Validate proposed medical intervention against patient data and contraindications.

        Args:
            intervention (str): Proposed medical intervention
            patient_data (Dict): Patient information including history and current status

        Returns:
            Dict: Validation results including safety assessment and recommendations
        """
        try:
            # Create validation prompt
            validation_prompt = f"""
            Validate the following medical intervention:
            Intervention: {intervention}

            Patient Information:
            - Age: {patient_data.get('age')}
            - Gender: {patient_data.get('gender')}
            - Medical History: {patient_data.get('medical_history', [])}
            - Current Medications: {patient_data.get('medications', [])}
            - Allergies: {patient_data.get('allergies', [])}
            - Current Vitals: {patient_data.get('vitals', {})}

            Assess:
            1. Safety considerations
            2. Potential contraindications
            3. Drug interactions (if applicable)
            4. Alternative recommendations (if needed)
            """

            # Get validation analysis from agent
            response = self.agent.run(validation_prompt)

            return self._parse_validation_response(response)

        except Exception as e:
            logger.error(f"Error validating intervention: {str(e)}")
            raise

    def _parse_validation_response(self, response: str) -> Dict:
        """
        Parse and structure the intervention validation response.

        Args:
            response (str): Raw response from the agent

        Returns:
            Dict: Structured validation results
        """
        validation_results = {
            "is_safe": True,  # Default to True, will be set to False if concerns found
            "safety_concerns": [],
            "contraindications": [],
            "drug_interactions": [],
            "alternatives": [],
            "recommendations": []
        }

        try:
            # Process response by sections
            sections = response.lower().split('\n\n')

            for section in sections:
                if 'safety' in section:
                    concerns = self._extract_bullet_points(section)
                    if concerns:
                        validation_results["safety_concerns"] = concerns
                        validation_results["is_safe"] = False

                elif 'contraindicat' in section:
                    validation_results["contraindications"] = self._extract_bullet_points(section)

                elif 'interaction' in section:
                    validation_results["drug_interactions"] = self._extract_bullet_points(section)

                elif 'alternative' in section:
                    validation_results["alternatives"] = self._extract_bullet_points(section)

                elif 'recommend' in section:
                    validation_results["recommendations"] = self._extract_bullet_points(section)

            return validation_results

        except Exception as e:
            logger.error(f"Error parsing validation response: {str(e)}")
            raise

    def _extract_bullet_points(self, text: str) -> List[str]:
        """
        Extract bulleted or numbered points from text.

        Args:
            text (str): Text containing bullet points

        Returns:
            List[str]: Extracted points
        """
        points = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            # Match different types of bullet points or numbering
            if line.startswith(('-', '*', '•')) or (line[0].isdigit() and '. ' in line):
                # Remove bullet point or number and clean up
                point = line.lstrip('-*•0123456789. ').strip()
                if point:
                    points.append(point)

        return points

    def get_treatment_updates(self, patient_id: str, intervention_history: List[Dict]) -> Dict:
        """
        Generate treatment updates and recommendations based on intervention history.

        Args:
            patient_id (str): Patient identifier
            intervention_history (List[Dict]): History of interventions and responses

        Returns:
            Dict: Treatment updates and recommendations
        """
        try:
            # Create treatment update prompt
            update_prompt = f"""
            Review treatment history and provide updates for patient {patient_id}:

            Intervention History:
            {self._format_intervention_history(intervention_history)}

            Provide:
            1. Treatment effectiveness assessment
            2. Patient response evaluation
            3. Recommended adjustments
            4. Next steps
            """

            # Get treatment update from agent
            response = self.agent.run(update_prompt)

            return {
                "timestamp": datetime.now().isoformat(),
                "patient_id": patient_id,
                "assessment": self._extract_section(response, "assessment"),
                "response_evaluation": self._extract_section(response, "response"),
                "adjustments": self._extract_section(response, "adjustment"),
                "next_steps": self._extract_section(response, "next steps"),
                "raw_update": response
            }

        except Exception as e:
            logger.error(f"Error generating treatment updates: {str(e)}")
            raise

    def _format_intervention_history(self, intervention_history: List[Dict]) -> str:
        """
        Format intervention history for the prompt.

        Args:
            intervention_history (List[Dict]): History of interventions

        Returns:
            str: Formatted intervention history
        """
        formatted_history = []

        for intervention in intervention_history:
            formatted_history.append(
                f"""
                Time: {intervention.get('timestamp')}
                Intervention: {intervention.get('intervention')}
                Response: {intervention.get('response')}
                Vitals: {intervention.get('vitals')}
                Notes: {intervention.get('notes')}
                """
            )

        return "\n".join(formatted_history)