from typing import AsyncGenerator, Generator, List
import logging

from dictatorgenai.agents.general import General
from .base_conversation import BaseConversation

# Configuration du logger
logger = logging.getLogger(__name__)

class GroupChat(BaseConversation):
    async def start_conversation(
        self, dictator: General, generals: List[General], task: str
    ) -> AsyncGenerator[str, None]:
        """
        The dictator sends an imperative message to all the generals,
        collects their responses, and then uses their input to resolve the task.
        """
        
        # Step 1: Dictator initiates the task with an imperative message
        imperative_message = f"Dictator {dictator.my_name_is} commands: Solve the task '{task}'."
        logger.debug(f"Imperative message sent by Dictator {dictator.my_name_is}: {imperative_message}")
        
        # Step 2: Dictator sends the command to all generals and collects their responses
        responses = []
        for general in generals:
            logger.debug(f"Sending command to General {general.my_name_is}...\n")
            response = await dictator.send_message(general, imperative_message)
            logger.debug(f"General {general.my_name_is}'s response: {response}\n")
            responses.append(response)

        # Step 3: Dictator processes the responses
        logger.debug(f"Dictator {dictator.my_name_is} is analyzing the generals' responses...\n")
        combined_response = self.compile_responses(responses)
        logger.debug(f"Combined responses from generals: {combined_response}\n")

        # Step 4: Dictator uses its own solve_task method to finalize the task resolution
        logger.debug(f"Dictator {dictator.my_name_is} is now resolving the task based on the responses...\n")
        async for chunk in dictator.solve_task(task):
            yield chunk

    def compile_responses(self, responses: List[str]) -> str:
        """
        Combine the responses from the generals into a final decision.
        For now, just concatenates the responses.
        """
        return " | ".join(responses)


