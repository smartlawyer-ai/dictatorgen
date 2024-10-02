from typing import Generator, List
from .BaseConversation import BaseConversation
from dictatorgenai.core.general import General


class TwoAgentChat(BaseConversation):
    def start_conversation(self, dictator: General, generals: List[General], task: str) -> Generator[str, None, None]:
        """
        A two-agent chat pattern where the dictator collaborates with one general to solve the task,
        yielding results as they come in.
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

