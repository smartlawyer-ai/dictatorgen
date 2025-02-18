# dictatorgenai/memories/__init__.py
"""
This package contains the agent definitions for DictatorGenAI.
It includes the BaseAgent, General, and Dictator classes.
"""

from .base_chat_memory import BaseChatMemory
from .chat_discussion import ChatDiscussion
from .sql_ite_chat_memory import SQLiteChatMemory
from .redis_chat_memory import RedisChatMemory


__all__ = [
    "BaseChatMemory",
    "ChatDiscussion",
    "SQLiteChatMemory",
    "RedisChatMemory",
]
