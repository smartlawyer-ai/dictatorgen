# dictatorgenai/agents/__init__.py
"""
This package contains the agent definitions for DictatorGenAI.
It includes the BaseAgent, General, and Dictator classes.
"""

from .base_agent import BaseAgent
from .dictator import Dictator
from .general import General, TaskExecutionError

__all__ = [
    "BaseAgent",
    "Dictator",
    "General",
    "TaskExecutionError",
]
