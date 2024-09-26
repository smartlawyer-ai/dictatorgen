# dictatorgenai/core/__init__.py

from .base_agent import BaseAgent
from .dictator import Dictator
from .general import General, TaskExecutionError
from .regime import Regime, RegimeExecutionError
from .coup_condition import (
    CoupCondition,
    FailedAttemptsCondition,
    SpecificTaskFailureCondition,
)
from .command_chain import CommandChain
from .default_command_chain import DefaultCommandChain
from .event_manager import EventManager

__all__ = [
    "BaseAgent",
    "Dictator",
    "General",
    "TaskExecutionError",
    "Regime",
    "RegimeExecutionError",
    "CoupCondition",
    "FailedAttemptsCondition",
    "SpecificTaskFailureCondition",
    "CommandChain",
    "DefaultCommandChain",
    "EventManager",
]
