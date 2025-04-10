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
from .colonel_fragmenter import ColonelFragmenter
from .legion_commander import LegionCommander
from .assigned_general  import AssignedGeneral

__all__ = [
    "BaseAgent",
    "tool",
    "Dictator",
    "General",
    "Majordomo",
    "TaskExecutionError",
    "InformationOfficer",
    "ColonelFragmenter",
    "LegionCommander",
    "AssignedGeneral",
]
