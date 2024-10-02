import logging
from typing import List, Dict, Generator, Optional
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
        self.conversation_history: List[Dict] = [] 
        self.failed_attempts = 0
        self.logger = logging.getLogger(self.my_name_is)

    def build_capabilities_prompt(self, task: str) -> List[Message]:
        capabilities_str = ", ".join(self.my_capabilities_are)
        messages = [
            {
                "role": "system",
                "content": (
                    f"My name is {self.my_name_is}. I am {self.iam}. "
                    f"My capabilities are: {capabilities_str}. "
                    f"My goal is to determine if my capabilities and/or roles can solve a given task. "
                    f"Format the response as JSON with the keys 'result', 'confidence', and 'details'. "
                    f"The 'result' key should have the value 'entirely', 'partially', or 'no'. "
                    f"The 'confidence' key should represent your confidence level in executing the task, "
                    f"as a float between 0 and 1. "
                    f"Give a blank array for 'details' if the result is 'no'. "
                    f"If the result is 'partially', the 'details' key should be an array of objects, "
                    f"each with a 'capability' key and an explanation. Provide a brief explanation for each capability."
                ),
            },
            {
                "role": "user",
                "content": f"With your capabilities, can you solve the following task: {task}?",
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
    
    # Making the agent communicate with others
    def send_message(self, recipient: 'General', message: str) -> str:
        # Store the outgoing message in the conversation history
        self.conversation_history.append({
            "role": "sender",
            "recipient": recipient.my_name_is,
            "message": message
        })
        self.logger.info(f"{self.my_name_is} sends message to {recipient.my_name_is}: {message}")
        return recipient.receive_message(self, message)

    def receive_message(self, sender: 'General', message: str) -> str:
        # Store the incoming message in the conversation history
        self.conversation_history.append({
            "role": "receiver",
            "sender": sender.my_name_is,
            "message": message
        })
        self.logger.info(f"{self.my_name_is} received message from {sender.my_name_is}: {message}")
        # Process the message and formulate a reply
        reply = self.process_message(sender, message)
        return reply

    def process_message(self, sender: 'General', message: str) -> str:
        # The agent processes the message and generates a response
        return f"{self.my_name_is} acknowledges the message from {sender.my_name_is}."

    def solve_task(self, task: str) -> Generator[str, None, None]:
        my_capabilities_str = ", ".join(self.my_capabilities_are)
        messages = [
            {
                "role": "system",
                "content": (
                    f"My name is {self.my_name_is}. I am {self.iam}. "
                    f"My capabilities include: {my_capabilities_str}. "
                    f"I am tasked with solving the following task."
                ),
            },
            {"role": "user", "content": f"The task to resolve is: '{task}'"},
        ]
        return self.nlp_model.stream_chat_completion(messages)

    def can_perform_coup(self) -> bool:
        prompt = self.build_prompt("Can you perform a coup?")
        return self.nlp_model.can_perform_coup(prompt)

    def report_failure(self, task: str = None):
        self.failed_attempts += 1
        if task:
            self.logger.warning(f"Failed task: {task}")
