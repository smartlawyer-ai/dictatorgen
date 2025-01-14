# dictatorgenai/agents/__init__.py
"""
This package contains the agent definitions for DictatorGenAI.
It includes the BaseAgent, General, and Dictator classes.
"""

from .base_agent import BaseAgent
from .tool import tool
from .dictator import Dictator
from .general import General, TaskExecutionError
from .information_officer import InformationOfficer
from .majordomo import Majordomo

__all__ = [
    "BaseAgent",
    "tool",
    "Dictator",
    "General",
    "Majordomo",
    "TaskExecutionError",
    "InformationOfficer",
]
