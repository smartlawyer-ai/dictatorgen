import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Any, Generator
from dictatorgenai.models import BaseModel, Message
from dictatorgenai.command_chains import CommandChain
from dictatorgenai.agents import General, TaskExecutionError
from dictatorgenai.events import BaseEventManager, Event

class RegimeExecutionError(TaskExecutionError):
    """
    Exception raised when the entire regime fails to perform the task.
    """
    pass

class BaseRegime(ABC):
    """
    Abstract base class that defines the general structure of a regime.
    Subclasses must implement specific methods for task execution and power transitions.
    """

    def __init__(
        self,
        nlp_model: BaseModel,
        government_prompt: str,
        generals: List[General],
        command_chain: CommandChain,
        event_manager: BaseEventManager,
    ):
        """
        Initializes the BaseRegime.

        Args:
            nlp_model (BaseModel): The NLP model for task execution and decision-making.
            government_prompt (str): The prompt that defines the regime's objectives or instructions.
            generals (List[General]): A list of generals (agents) under the regime's control.
            command_chain (CommandChain): The command chain used to assign tasks and responsibilities.
            event_manager (BaseEventManager): The event manager to handle event notifications.
        """
        self.nlp_model = nlp_model
        self.government_prompt = government_prompt
        self.generals = generals
        self.dictator = None
        self.command_chain = command_chain
        self.event_manager = event_manager
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def perform_coup(self, general: General):
        """
        Abstract method to handle the power transition when a coup is performed by a general.

        Args:
            general (General): The general executing the coup to take control.
        """
        pass

    def get_generals(self) -> List[General]:
        """
        Returns the list of available generals.

        Returns:
            List[General]: The list of generals in the regime.
        """
        return self.generals

    def subscribe(self, event_type: str, listener: Callable[[Any], None]):
        """
        Allows listeners to subscribe to specific event types.

        Args:
            event_type (str): The type of event to subscribe to (e.g., 'task_started').
            listener (Callable[[Any], None]): The listener function to invoke when the event is published.
        """
        self.event_manager.subscribe(event_type, listener)
    
    async def wait_for_event(self, event_type: str):
        await self.event_manager.wait_for_event(event_type)

    async def publish(self, event_type: str, task_id: str, agent: str, message: str, details: Dict = None):
        """
        Publishes a structured event using the Event class.

        Args:
            event_type (str): The type of event (e.g., 'task_started').
            task_id (str): The unique identifier of the task.
            agent (str): The name of the agent (general) associated with the event.
            message (str): A descriptive message related to the event.
            details (Dict, optional): Additional details for the event (default is None).
        """
        event = Event(
            event_type=event_type,
            task_id=task_id,
            agent=agent,
            message=message,
            details=details or {}
        )
        await self.event_manager.publish(event_type, event)

    @abstractmethod
    async def chat(self, message: str, discussion_id: str = None) -> Generator[str, None, None]:
        """
        Manages task execution and discussion interaction through a unified method.

        Args:
            message (str): The message or task to process.
            discussion_id (str, optional): The ID of a discussion for persistent conversations (default is None).

        Returns:
            Generator[str, None, None]: A generator yielding responses from the task or discussion.
        """
        pass
