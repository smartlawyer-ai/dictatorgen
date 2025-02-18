import logging
from typing import AsyncGenerator, Dict, Any
from dictatorgenai.config.settings import DictatorSettings
from dictatorgenai.models.base_model import BaseModel
from dictatorgenai.utils.task import Task
from dictatorgenai.agents.base_agent import BaseAgent

class Majordomo(BaseAgent):
    """
    The Majordomo handles user interaction for clarification or feedback,
    acting as the intermediary for the Human-in-the-Loop mechanism.
    """

    def __init__(self, nlp_model: BaseModel = None, my_name_is: str = "Majordomo", my_capabilities_are=None, tools=None):
        """
        Initializes the Majordomo with its name and capabilities.
        """
        self.nlp_model = nlp_model or DictatorSettings.get_nlp_model()
        if my_capabilities_are is None:
            my_capabilities_are = [{"capability": "clarify_request", "description": "Request clarification from the user"}]
        super().__init__(my_name_is, my_capabilities_are, tools)
        self.logger = logging.getLogger(self.__class__.__name__)

    # async def can_execute_task(self, task: Task) -> Dict:
    #     """
    #     Determines if the Majordomo can execute the task.

    #     The Majordomo is always capable of managing tasks that involve user interaction.

    #     Args:
    #         task (Task): The task to evaluate.

    #     Returns:
    #         Dict: Result indicating the Majordomo can assist.
    #     """
    #     return {
    #         "result": "entirely",
    #         "confidence": 1.0,
    #         "details": [{"capability": "clarify_request", "explanation": "Capable of requesting user input"}]
    #     }

    async def solve_task(self, task: Task) -> AsyncGenerator[str, None]:
        """
        Handles solving a task by generating a clarification request message for the user
        and sending it as an assistant's input.

        Args:
            task (Task): The task requiring user interaction.

        Returns:
            str: The user-provided clarification or feedback.
        """
        # Generate a clarification message based on the task's request and context
        reply_language = f"Reply in {DictatorSettings.get_language()} language."

        # Construire le contexte à partir de la discussion
        context_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in task.context
        ]

        # Ajouter le message reçu et les informations de base
        clarification_message = [
            {
                "role": "system",
                "content": (
                    f"I am {self.my_name_is}, serving as the Majordomo for this system. "
                    f"My role is to facilitate the resolution of your task by ensuring we have all the necessary information. "
                    f"Currently, we have no enough information to solve the task, I have to generate a clarification message to better understand and address your request.\n\n"
                    f"Context is the current discussion history."
                    f"{reply_language}"
                ),
            }
        ]

        # Combiner contexte, message initial, et tâche
        all_messages = clarification_message + context_messages + [
            {"role": "user", "content": task.request}
        ]

        async for chunk in self.nlp_model.stream_chat_completion(all_messages):
            yield chunk  # Diffuse chaque fragment de la réponse au fur et à mesure


    async def process_message(self, sender: 'BaseAgent', message: str, task: Task) -> str:
        """
        Processes a message and responds accordingly.

        Args:
            sender (BaseAgent): The agent that sent the message.
            message (str): The received message.
            task (Task): The task being addressed.

        Returns:
            str: The response generated after processing the message.
        """
        self.logger.info(f"Processing message from {sender.my_name_is}: {message}")
        user_feedback = await self.solve_task(task)
        return user_feedback

    async def can_perform_coup(self) -> bool:
        """
        The Majordomo does not perform coups.

        Returns:
            bool: Always False.
        """
        return False

    async def simulate_user_input(self, message: str) -> str:
        """
        Simulates user interaction for demo purposes. Replace this with actual user input handling.

        Args:
            message (str): The message to display to the user.

        Returns:
            str: Simulated user input.
        """
        print(message)  # Replace this with actual user interface
        return "Simulated user clarification response"  # Replace with actual user input
