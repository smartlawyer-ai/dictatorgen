from abc import ABC, abstractmethod
from typing import Dict


class TaskExecutionError(Exception):
    pass


class BaseAgent(ABC):
    def __init__(self, my_name_is: str):
        self.my_name_is = my_name_is
        self.failed_attempts = 0
        self.conversation_history = []  # Track the message history

    # Abstract method for evaluating task capabilities
    @abstractmethod
    def can_execute_task(self, task: str) -> Dict:
        pass

    # Abstract method for solving tasks
    @abstractmethod
    def solve_task(self, task: str) -> str:
        pass

    # Abstract method to determine if agent can perform a coup
    @abstractmethod
    def can_perform_coup(self) -> bool:
        pass

    # Common failure reporting mechanism for all agents
    def report_failure(self, task: str = None):
        self.failed_attempts += 1
        if task:
            print(f"{self.my_name_is} - Failed task: {task}")

    # Abstract method for receiving a message from another agent
    @abstractmethod
    def receive_message(self, sender: 'BaseAgent', message: str) -> str:
        """
        Method to receive a message from another agent.
        """
        pass

    # Abstract method for sending a message to another agent
    @abstractmethod
    def send_message(self, recipient: 'BaseAgent', message: str) -> str:
        """
        Method to send a message to another agent.
        """
        pass

    # Abstract method for processing a message and returning a response
    @abstractmethod
    def process_message(self, sender: 'BaseAgent', message: str) -> str:
        """
        Method for processing a received message and generating a response.
        """
        pass
