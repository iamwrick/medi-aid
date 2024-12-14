# src/agents/resource_coordinator.py
from typing import Dict, List
from crewai import Agent
from src.utils.logger import get_logger
from .base_agent import BaseAgent  # Updated import statement

logger = get_logger(__name__)


class ResourceCoordinatorAgent(BaseAgent):
    def _create_agent(self) -> Agent:
        return Agent(
            role='Resource Coordinator',
            goal='Optimize resource allocation for emergency response',
            backstory="""You are an expert in emergency resource management with 
            experience in coordinating complex medical responses. Your role is to 
            ensure optimal allocation of available resources.""",
            tools=self.tools,
            verbose=True
        )

    def process(self, data: Dict) -> Dict:
        """
        Determine optimal resource allocation based on emergency analysis.
        """
        try:
            severity = data.get('severity_level', 5)
            available_resources = data.get('available_resources', {})
            location = data.get('incident_location', {})

            # Create resource allocation prompt
            allocation_prompt = f"""
            Optimize resource allocation for emergency:
            Severity Level: {severity}
            Location: {location}

            Available Resources:
            Ambulances: {len(available_resources.get('ambulances', []))}
            Hospitals: {len(available_resources.get('hospitals', []))}

            Determine:
            1. Number and type of ambulances needed
            2. Best hospital selection criteria
            3. Additional resource requirements
            """

            # Get allocation plan from agent
            response = self.agent.run(allocation_prompt)

            return self._parse_allocation_response(response, available_resources)

        except Exception as e:
            logger.error(f"Error in resource coordination: {str(e)}")
            raise

    def _parse_allocation_response(
            self,
            response: str,
            available_resources: Dict
    ) -> Dict:
        """Parse and structure the resource allocation response."""
        # Implementation would depend on response format
        return {
            "recommended_resources": {
                "ambulances": self._select_ambulances(
                    response,
                    available_resources.get('ambulances', [])
                ),
                "hospital": self._select_hospital(
                    response,
                    available_resources.get('hospitals', [])
                ),
                "additional_resources": self._extract_additional_resources(response)
            },
            "raw_allocation_plan": response
        }

    def _select_ambulances(
            self,
            response: str,
            available_ambulances: List
    ) -> List[Dict]:
        """Select appropriate ambulances based on agent response."""
        # Implementation for ambulance selection
        pass

    def _select_hospital(
            self,
            response: str,
            available_hospitals: List
    ) -> Dict:
        """Select appropriate hospital based on agent response."""
        # Implementation for hospital selection
        pass

    def _extract_additional_resources(self, response: str) -> List[str]:
        """Extract any additional resource requirements."""
        # Implementation for additional resource extraction
        pass