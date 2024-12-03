import logging
from typing import AsyncGenerator, List
from dictatorgenai.agents.general import General
from .base_conversation import BaseConversation

logger = logging.getLogger(__name__)

class NestedChat(BaseConversation):
    """
    A nested chat conversation pattern where the dictator communicates with each general individually, 
    collects their input, and aggregates their responses to solve the task.

    Methods:
        start_conversation(dictator: General, generals: List[General], task: str) -> Generator[str, None, None]:
            Initiates the conversation where the dictator sequentially asks each general for input and 
            integrates their responses to resolve the task.
    """

    async def start_conversation(self, dictator: General, generals: List[General], task: str) -> AsyncGenerator[str, None]:
        """
        Starts the conversation using a nested communication pattern.
        The dictator asks each general for input, processes their responses, and integrates the information
        to solve the task.

        Args:
            dictator (General): The dictator leading the conversation and solving the task.
            generals (List[General]): A list of generals who provide input during the conversation.
            task (str): The task that needs to be solved.

        Yields:
            str: Chunks of the conversation process as the dictator requests input and generates the solution.

        The conversation follows these steps:
        1. The dictator communicates with each general individually.
        2. Generals respond to the task, and their input is streamed.
        3. The dictator integrates the responses to finalize the task solution.
        """

        # Dictator initiates the task and communicates with each general
        logger.debug(
            "Dictator {dictator.my_name_is} starts the conversation with generals.\n"
        )
        
        # Each general provides input, and the dictator aggregates the responses
        for general in generals:
            logger.debug(
                "Dictator {dictator.my_name_is} requests input from General {general.my_name_is}.\n"
            )
            for chunk in dictator.send_message(general, task):
                yield f"General {general.my_name_is}: {chunk}\n"
        
        # Dictator integrates the responses and yields final output
        logger.debug(
            f"Dictator {dictator.my_name_is} integrates the responses.\n"
            )
        for chunk in dictator.solve_task(task):
            yield f"Final result: {chunk}"
