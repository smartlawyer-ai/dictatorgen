import logging
from typing import List, Dict, Generator
from .base_agent import BaseAgent
from dictatorgenai.models import NLPModel, Message
import json


class TaskExecutionError(Exception):
    pass


class General(BaseAgent):
    def __init__(
        self,
        my_name_is: str,
        iam: str,
        my_capabilities_are: List[str],
        nlp_model: NLPModel,
        coup_conditions=None,
    ):
        super().__init__(my_name_is)
        self.my_name_is = my_name_is
        self.iam = iam
        self.my_capabilities_are = my_capabilities_are
        self.nlp_model = nlp_model
        self.coup_conditions = coup_conditions if coup_conditions else []
        self.failed_attempts = 0
        self.logger = logging.getLogger(self.my_name_is)

    def build_capabilities_prompt(self, task: str) -> List[Message]:
        capabilities_str = ", ".join(self.my_capabilities_are)
        messages = [
            {
                "role": "system",
                "content": f"My name is {self.my_name_is}. I am {self.iam}."
                f"My capabilities are '{capabilities_str}'."
                f"My goal is to determine if capabilites and/or roles can solve a given task."
                f"Format the response as JSON with the keys 'result' and 'details'. "
                f"The 'result' key should have the value 'entirely' or 'partially' or 'no'."
                f"Give a blank array if result is 'no'. If result is 'partially', the 'details' key should be an array of objects, each with a 'capability' key and an explanation. Give a short explanation.",
            },
            {
                "role": "user",
                "content": f"With your capabilities can you solve the following task: {task}?",
            },
        ]
        return messages

    def can_execute_task(self, task: str) -> Dict:
        prompt = self.build_capabilities_prompt(task)
        try:
            evaluation_str = self.nlp_model.chat_completion(
                prompt, response_format={"type": "json_object"}
            )
            evaluation = json.loads(evaluation_str)
            self.logger.debug(
                f"Evaluating task: {task} with prompt: {prompt} - Result: {evaluation}"
            )
            return evaluation
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {evaluation_str}")
            raise TaskExecutionError(
                f"Failed to decode JSON response: {evaluation_str}"
            ) from e
        except Exception as e:
            self.logger.error(f"An error occurred while evaluating the task: {str(e)}")
            raise TaskExecutionError(
                f"An error occurred while evaluating the task: {str(e)}"
            ) from e

    def solve_task(self, task: str) -> Generator[str, None, None]:
        my_capabilities_str = ", ".join(self.my_capabilities_are)
        messages = [
            {
                "role": "system",
                "content": f"My name is {self.my_name_is}. I am {self.iam}. My capabilities include '{my_capabilities_str}'. I solve the given task.",
            },
            {"role": "user", "content": f"The task to resolve is '{task}'"},
        ]
        return self.nlp_model.stream_chat_completion(messages)

    def can_perform_coup(self) -> bool:
        prompt = self.build_prompt("Can you perform a coup?")
        return self.nlp_model.can_perform_coup(prompt)

    def report_failure(self, task: str = None):
        self.failed_attempts += 1
        if task:
            self.logger.warning(f"Failed task: {task}")
