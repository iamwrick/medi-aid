# src/agents/base_agent.py
from abc import ABC, abstractmethod
from crewai import Agent
from langchain.tools import Tool
from typing import List, Optional

class BaseAgent(ABC):
    def __init__(self, tools: Optional[List[Tool]] = None):
        self.tools = tools or []
        self.agent = self._create_agent()

    @abstractmethod
    def _create_agent(self) -> Agent:
        """Create and return a CrewAI agent."""
        pass

    @abstractmethod
    def process(self, data: dict) -> dict:
        """Process the input data and return results."""
        pass