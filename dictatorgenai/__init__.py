# dictatorgenai/__init__.py

from .core.base_agent import BaseAgent
from .core.dictator import Dictator
from .core.general import General, TaskExecutionError
from .core.regime import Regime, RegimeExecutionError
from .core.coup_condition import (
    CoupCondition,
    FailedAttemptsCondition,
    SpecificTaskFailureCondition,
)
from .core.command_chain import CommandChain
from .core.default_command_chain import DefaultCommandChain

from .models.nlp_model import NLPModel, Message
from .models.sbert_model import SBERTModel
from .models.qabert_model import QABERTModel
from .models.distilbert_model import DistilBERTModel
from .models.gpt3_model import GPT3Model

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
    "NLPModel",
    "SBERTModel",
    "QABERTModel",
    "DistilBERTModel",
    "GPT3Model",
    "Message",
]
