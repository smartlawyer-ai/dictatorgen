from typing import AsyncGenerator, Generator, List
from .base_conversation import BaseConversation
from dictatorgenai.agents.general import General


class TwoAgentChat(BaseConversation):
    """
    A two-agent chat pattern where the dictator collaborates with a single general to solve a task.
    The conversation involves just two agents (the dictator and one general), and the task resolution
    proceeds through their back-and-forth communication.

    Methods:
        start_conversation(dictator: General, generals: List[General], task: str) -> Generator[str, None, None]:
            Starts a conversation where the dictator and one general collaborate to solve the task,
            and results are streamed as they are generated.
    """

    async def start_conversation(self, dictator: General, generals: List[General], task: str) -> AsyncGenerator[str, None]:
        """
        Starts a two-agent conversation where the dictator collaborates with exactly one general 
        to solve the task.

        Args:
            dictator (General): The dictator leading the conversation and initiating the task resolution.
            generals (List[General]): A list containing exactly one general who collaborates with the dictator.
            task (str): The task that needs to be solved.

        Yields:
            str: Chunks of the conversation and task-solving process as the dictator and the general
            communicate and work together.

        Raises:
            ValueError: If the list of generals does not contain exactly one general.

        The conversation follows these steps:
        1. The dictator starts solving the task and shares their progress.
        2. The single general responds to the dictator's actions and continues contributing to the task.
        3. Results from both the dictator and the general are streamed in sequence.
        """
        if len(generals) != 1:
            raise ValueError("TwoAgentChat requires exactly one general.")
        
        general = generals[0]
        
        # Dictator initiates the task
        yield f"Dictator {dictator.my_name_is} begins solving the task with General {general.my_name_is}.\n"
        for chunk in dictator.solve_task(task):
            yield f"Dictator {dictator.my_name_is}: {chunk}"
        
        # General responds to the dictator and contributes
        yield f"General {general.my_name_is} responds and continues the task.\n"
        for chunk in general.send_message(dictator, ''.join(chunk)):
            yield f"General {general.my_name_is}: {chunk}"
