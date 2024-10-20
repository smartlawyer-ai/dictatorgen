from abc import ABC, abstractmethod
from typing import Dict


class TaskExecutionError(Exception):
    """
    Custom exception raised when a task execution fails.
    """
    pass


class BaseAgent(ABC):
    """
    Abstract base class for defining an agent in the system.

    Attributes:
        my_name_is (str): The name of the agent.
        failed_attempts (int): Counter to track the number of failed tasks.
        conversation_history (list): A list that tracks the message history of the agent.
    """

    def __init__(self, my_name_is: str):
        """
        Initializes the BaseAgent with the given name.

        Args:
            my_name_is (str): The name of the agent.
        """
        self.my_name_is = my_name_is
        self.failed_attempts = 0
        self.conversation_history = []  # Track the message history

    @abstractmethod
    def can_execute_task(self, task: str) -> Dict:
        """
        Abstract method to evaluate if the agent has the capabilities to execute a task.

        Args:
            task (str): The task to be evaluated.

        Returns:
            Dict: A dictionary indicating the agent's capability to perform the task.
        """
        pass

    @abstractmethod
    def solve_task(self, task: str) -> str:
        """
        Abstract method to solve a given task.

        Args:
            task (str): The task to be solved.

        Returns:
            str: The result of the task execution.
        """
        pass

    @abstractmethod
    def can_perform_coup(self) -> bool:
        """
        Abstract method to determine if the agent is capable of performing a coup.

        Returns:
            bool: True if the agent can perform a coup, False otherwise.
        """
        pass

    def report_failure(self, task: str = None):
        """
        Increments the agent's failure count and prints a failure message.

        Args:
            task (str, optional): The task that failed. If None, a generic failure message is printed.
        """
        self.failed_attempts += 1
        if task:
            print(f"{self.my_name_is} - Failed task: {task}")

    @abstractmethod
    def receive_message(self, sender: 'BaseAgent', message: str) -> str:
        """
        Abstract method to handle receiving a message from another agent.

        Args:
            sender (BaseAgent): The agent that sends the message.
            message (str): The message content.

        Returns:
            str: The response to the received message.
        """
        pass

    @abstractmethod
    def send_message(self, recipient: 'BaseAgent', message: str) -> str:
        """
        Abstract method to send a message to another agent.

        Args:
            recipient (BaseAgent): The agent that will receive the message.
            message (str): The message content to be sent.

        Returns:
            str: The response from the recipient agent after processing the message.
        """
        pass

    @abstractmethod
    def process_message(self, sender: 'BaseAgent', message: str) -> str:
        """
        Abstract method to process a received message and generate a response.

        Args:
            sender (BaseAgent): The agent that sent the message.
            message (str): The content of the message.

        Returns:
            str: The response generated after processing the message.
        """
        pass
