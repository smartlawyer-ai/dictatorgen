from typing import AsyncGenerator, List, Callable, Generator, Tuple, Dict
from abc import ABC, abstractmethod

from dictatorgenai.conversations import BaseConversation, GroupChat
from ..agents.general import General

class CommandChain(ABC):
    """
    Abstract base class for defining the command chain in the system. 
    A CommandChain manages the selection of a dictator and the generals, and orchestrates the execution of tasks.

    Attributes:
        conversation (BaseConversation): The conversation pattern used by the command chain. Defaults to GroupChat if not provided.
    """

    def __init__(self, conversation: BaseConversation = None):
        """
        Initializes the CommandChain with an optional conversation type. Defaults to GroupChat.

        Args:
            conversation (BaseConversation, optional): The conversation pattern to be used by the command chain.
        """
        # Default to GroupChat if no conversation type is provided
        self.conversation = conversation if conversation else GroupChat()
        
    async def prepare_task_execution(self, generals: List[General], task: str):
        """
        Prepares the execution of a task by selecting a dictator and the generals, 
        and returning a function to execute the task.

        Args:
            generals (List[General]): A list of generals available for the task.
            task (str): The task to be executed.

        Returns:
            Tuple[General, List[General], Callable]: A tuple containing the dictator, the selected generals, 
            and a callable function to execute the task.
        """
        # Selection of the dictator, generals, subtasks, and assignments
        dictator, generals_to_use = await self._select_dictator_and_generals(generals, task)

        async def execute_task() -> AsyncGenerator[str, None]:
            async for chunk in self.solve_task(dictator, generals_to_use, task):
                yield chunk

        return dictator, generals_to_use, execute_task

    @abstractmethod
    async def _select_dictator_and_generals(
        self, 
        generals: List[General], 
        task: str
    ) -> Tuple[General, List[General], List[str], Dict[str, General]]:
        """
        Logic for selecting the dictator and generals.
        Returns a tuple containing the dictator, the list of generals to be used, 
        the list of subtasks, and the subtask assignments.

        Args:
            generals (List[General]): A list of available generals.
            task (str): The task to be solved.

        Returns:
            Tuple[General, List[General], List[str], Dict[str, General]]: A tuple consisting of the selected dictator, 
            the list of generals, the list of subtasks, and a dictionary of subtask assignments.
        """
        pass

    @abstractmethod
    async def solve_task(
        self, 
        dictator: General, 
        generals: List[General], 
        task: str,
    ) -> AsyncGenerator[str, None]:
        """
        Abstract method for implementing task resolution. This method must be implemented by derived classes.

        Args:
            dictator (General): The dictator responsible for overseeing the task.
            generals (List[General]): A list of generals assisting in solving the task.
            task (str): The task to be solved.

        Returns:
            Generator[str, None, None]: A generator yielding chunks of the task resolution process.
        """
        pass
