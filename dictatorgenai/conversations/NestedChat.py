from typing import Generator, List
from dictatorgenai.core.general import General
from .BaseConversation import BaseConversation

class NestedChat(BaseConversation):
    def start_conversation(self, dictator: General, generals: List[General], task: str) -> Generator[str, None, None]:
        """
        A nested chat pattern where the dictator communicates with each general and aggregates their input,
        yielding results as they come in.
        """
        # Dictator initiates the task and communicates with each general
        yield f"Dictator {dictator.my_name_is} starts the conversation with generals.\n"
        
        # Each general provides input, and the dictator aggregates the responses
        for general in generals:
            yield f"Dictator {dictator.my_name_is} requests input from General {general.my_name_is}.\n"
            for chunk in dictator.send_message(general, task):
                yield f"General {general.my_name_is}: {chunk}\n"
        
        # Dictator integrates the responses and yields final output
        yield f"Dictator {dictator.my_name_is} integrates the responses.\n"
        for chunk in dictator.solve_task(task):
            yield f"Final result: {chunk}"


