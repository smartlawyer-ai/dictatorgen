from abc import ABC, abstractmethod
from typing import Generator, List
from dictatorgenai.core.general import General


class BaseConversation(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def start_conversation(self, dictator: General, generals: List[General], task: str) -> Generator[str, None, None]:
        """
        Start the conversation between the dictator and generals.
        Each derived class will define its own conversation pattern.
        The conversation will return a generator to stream the task results.
        """
        pass
