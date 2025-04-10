import logging
from typing import List, Dict, Any
import json
from .base_agent import BaseAgent


class InformationOfficer(BaseAgent):
    """
    The InformationOfficer is responsible for analyzing the context and filtering relevant information
    for the task at hand. It supports the regime by ensuring that only pertinent data is passed to
    generals or the dictator.
    """

    def __init__(self, my_name_is: str, my_capabilities_are: List[Dict[str, str]], tools=None):
        super().__init__(my_name_is, my_capabilities_are, tools)
        self.logger = logging.getLogger(self.__class__.__name__)

    def build_context_filter_prompt(self, task: str, context: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Constructs a prompt to filter relevant context for a task.

        Args:
            task (str): The task to solve.
            context (List[Dict[str, str]]): The discussion context to analyze.

        Returns:
            List[Dict[str, str]]: A structured prompt for the NLP model.
        """
        context_snippets = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context])

        prompt = [
            {
                "role": "system",
                "content": (
                    f"My name is {self.my_name_is}. I am an Information Officer specialized in filtering relevant "
                    f"context for tasks. My goal is to identify the most pertinent information from the discussion "
                    f"history that helps in solving a given task."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Task: {task}\n"
                    f"Here is the discussion history:\n{context_snippets}\n"
                    "Please extract only the most relevant pieces of information that directly pertain to the task. "
                    "Format the response as a JSON object with keys 'task' and 'relevant_context', where 'relevant_context' "
                    "is an array of the relevant messages."
                ),
            },
        ]
        return prompt

    async def solve_task(self, task: str, context: List[Dict[str, str]]) -> str:
        """
        Extracts the relevant context for the given task from the discussion history.

        Args:
            task (str): The task to solve.
            context (List[Dict[str, str]]): The discussion context to analyze.

        Returns:
            str: The extracted relevant context as a JSON string.
        """
        self.logger.info(f"{self.my_name_is} is filtering context for task: {task}")

        # Build the NLP model prompt
        prompt = self.build_context_filter_prompt(task, context)

        # Call NLP model for context filtering
        try:
            response = await self.nlp_model.chat_completion(prompt)
            message = response.message
            relevant_context = json.loads(getattr(message, "content", ""))
            self.logger.debug(f"Relevant context extracted: {relevant_context}")
            return json.dumps(relevant_context)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response from NLP model: {e}")
            raise ValueError("Could not decode the NLP model's response for context filtering.")
        except Exception as e:
            self.logger.error(f"Error during context filtering: {e}")
            raise ValueError("An error occurred while filtering the context.")

    async def process_message(self, sender: 'BaseAgent', message: str) -> str:
        """
        Processes a received message and responds with filtered context.

        Args:
            sender (BaseAgent): The agent that sent the message.
            message (str): The content of the message.

        Returns:
            str: A response summarizing the task-relevant context.
        """
        self.logger.info(f"{self.my_name_is} received a message from {sender.my_name_is}: {message}")

        # Example message parsing (could be enhanced with NLP)
        parsed_task = {"task": message, "context": self.conversation_history}
        relevant_context = await self.solve_task(parsed_task["task"], parsed_task["context"])
        response = f"Relevant context for task '{parsed_task['task']}': {relevant_context}"
        
        return response

    # async def can_execute_task(self, task: str, context: List[Dict[str, str]]) -> Dict:
    #     """
    #     Determines if the Information Officer can process the context and extract relevant information
    #     for the given task.

    #     Args:
    #         task (str): The task to evaluate.
    #         context (List[Dict[str, str]]): The discussion context to analyze.

    #     Returns:
    #         Dict: An evaluation indicating capability to process the task.
    #     """
    #     return {
    #         "result": "entirely",
    #         "confidence": 1.0,
    #         "details": [{"capability": "context_filtering", "description": "Can analyze and extract task-relevant context"}],
    #     }

    async def can_perform_coup(self) -> bool:
        """
        Determines if the Information Officer can perform a coup (not applicable).

        Returns:
            bool: Always False, as Information Officers do not perform coups.
        """
        return False
