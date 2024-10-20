# dictatorgenai/__init__.py

from .agents.base_agent import BaseAgent
from .agents.dictator import Dictator
from .agents.general import General, TaskExecutionError
from .regimes.regime import Regime, RegimeExecutionError
from .command_chains.command_chain import CommandChain
from .command_chains.default_command_chain import DefaultCommandChain
from .conversations.base_conversation import BaseConversation
from .conversations.group_chat import GroupChat
from .conversations.nested_chat import NestedChat
from .conversations.sequential_chat import SequentialChat
from .conversations.two_agent_chat import TwoAgentChat
from .events import BaseEventManager, EventManager, Event
from .models.base_model import BaseModel, Message
from .models.openai_model import OpenaiModel


__all__ = [
    "BaseAgent",
    "Dictator",
    "General",
    "TaskExecutionError",
    "Regime",
    "RegimeExecutionError",
    "FailedAttemptsCondition",
    "SpecificTaskFailureCondition",
    "CommandChain",
    "DefaultCommandChain",
    "BaseModel",
    "OpenaiModel",
    "Message",
    "BaseConversation",
    "GroupChat",
    "NestedChat",
    "SequentialChat",
    "TwoAgentChat",
    "BaseEventManager",
    "EventManager",
    "Event",
]
