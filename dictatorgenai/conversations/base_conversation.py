from abc import ABC, abstractmethod
from typing import Generator, List
from dictatorgenai.agents.general import General
from dictatorgenai.utils.task import Task

class BaseConversation(ABC):
    """
    Abstract base class for managing conversations between a dictator and generals.
    This class serves as a blueprint for different conversation patterns, where derived
    classes must implement the logic to handle conversations.

    Methods:
        start_conversation(dictator: General, generals: List[General], task: str) -> Generator[str, None, None]:
            Starts a conversation between the dictator and the generals to solve a task.
            This method should be implemented by subclasses to define a specific conversation pattern.
    """

    def __init__(self):
        """
        Initializes the BaseConversation class. The constructor can be extended in subclasses if needed.
        """
        pass

    @abstractmethod
    async def start_conversation(self, dictator: General, generals: List[General], task: Task) -> Generator[str, None, None]:
        """
        Starts the conversation between the dictator and the generals.
        
        Args:
            dictator (General): The dictator leading the conversation.
            generals (List[General]): A list of generals contributing to the conversation.
            task (str): The task to be solved during the conversation.

        Returns:
            Generator[str, None, None]: A generator that streams the results of the task-solving conversation.
        
        This method must be implemented by subclasses to define their own conversation pattern.
        """
        pass
