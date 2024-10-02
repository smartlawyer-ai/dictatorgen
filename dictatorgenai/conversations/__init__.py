# dictatorgenai/conversations/__init__.py

from .BaseConversation import BaseConversation
from .GroupChat import GroupChat
from .NestedChat import NestedChat
from .SequentialChat import SequentialChat
from .TwoAgentChat import TwoAgentChat

__all__ = [
    "BaseConversation",
    "GroupChat",
    "NestedChat",
    "SequentialChat",
    "TwoAgentChat"
]
