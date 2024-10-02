from typing import Generator, List

from dictatorgenai.core.general import General
from .BaseConversation import BaseConversation

class GroupChat(BaseConversation):
    def start_conversation(self, dictator: General, generals: List[General], task: str) -> Generator[str, None, None]:
        """
        A group chat pattern where the dictator leads the conversation and generals
        contribute to solving the task, yielding results as they come in.
        """
        # Dictator initiates the task-solving conversation
        yield f"Dictator {dictator.my_name_is} begins solving the task.\n"
        
        # Stream the dictator's task resolution result
        for chunk in dictator.solve_task(task):
           yield chunk
        
        # Each general contributes to the task and yields their responses
        for general in generals:
            yield f"General {general.my_name_is} begins solving the task.\n"
            for chunk in general.solve_task(task):
                yield chunk

