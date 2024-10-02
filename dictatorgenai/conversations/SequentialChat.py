from typing import Generator, List
from dictatorgenai.core.general import General
from .BaseConversation import BaseConversation


class SequentialChat(BaseConversation):
    def start_conversation(self, dictator: General, generals: List[General], task: str) -> Generator[str, None, None]:
        """
        A sequential chat pattern where the task is passed sequentially through agents,
        with each agent contributing to the task resolution, yielding results as they come in.
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


