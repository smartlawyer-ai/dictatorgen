from typing import AsyncGenerator, List
from dictatorgenai.agents.general import General
from .base_conversation import BaseConversation


class SequentialChat(BaseConversation):
    """
    A sequential chat pattern where the task is passed from one agent to the next,
    with each agent contributing to the task resolution. The conversation proceeds 
    step by step, and the results are streamed as they come in.

    Methods:
        start_conversation(dictator: General, generals: List[General], task: str) -> Generator[str, None, None]:
            Starts a conversation where the dictator initiates the task, and each general 
            sequentially contributes to solving it.
    """

    async def start_conversation(self, dictator: General, generals: List[General], task: str) -> AsyncGenerator[str, None]:
        """
        Initiates the conversation following a sequential pattern. The dictator starts solving the task,
        and then each general contributes one after another.

        Args:
            dictator (General): The dictator leading the conversation and initiating the task resolution.
            generals (List[General]): A list of generals who contribute to solving the task sequentially.
            task (str): The task that needs to be solved.

        Yields:
            str: Chunks of the conversation and task-solving process, as each agent contributes sequentially.

        The conversation follows these steps:
        1. The dictator starts solving the task.
        2. Each general, one after the other, contributes to the task resolution.
        3. Results from the dictator and generals are streamed step by step.
        """

        current_message = task
        
        # Dictator starts the task
        yield f"Dictator {dictator.my_name_is} begins solving the task.\n"
        for chunk in dictator.solve_task(current_message):
            yield f"Dictator {dictator.my_name_is}: {chunk}"
        
        # Each general contributes sequentially to the task
        for general in generals:
            yield f"General {general.my_name_is} continues solving the task.\n"
            for chunk in general.solve_task(current_message):
                yield f"General {general.my_name_is}: {chunk}"
