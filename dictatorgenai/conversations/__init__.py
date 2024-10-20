# dictatorgenai/conversations/__init__.py

from .base_conversation import BaseConversation
from .group_chat import GroupChat
from .nested_chat import NestedChat
from .sequential_chat import SequentialChat
from .two_agent_chat import TwoAgentChat

__all__ = [
    "base_conversation",
    "group_chat",
    "nested_chat",
    "sequential_chat",
    "two_agent_chat"
]
