import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Type

from dictatorgenai.utils.task import Task 

class TaskExecutionError(Exception):
    """Custom exception raised when a task execution fails."""
    pass

class BaseAgent(ABC):
    """
    Abstract base class for defining an agent in the system.

    Attributes:
        my_name_is (str): The name of the agent.
        failed_attempts (int): Counter to track the number of failed tasks.
        conversation_history (List[Dict]): A list that tracks the message history of the agent.
        tools (Dict[str, Callable]): Dictionary of registered tools for the agent.
    """

    def __init__(self, my_name_is: str, my_capabilities_are: List[Dict[str, str]], tools = None):
        """
        Initializes the BaseAgent with the given name.

        Args:
            my_name_is (str): The name of the agent.
        """
        self.my_name_is = my_name_is
        self.my_capabilities_are = my_capabilities_are
        self.failed_attempts = 0
        self.conversation_history: List[Dict] = []  # Track the message history
        self.logger = logging.getLogger(self.my_name_is)
        self.tools: Dict[str, Callable] = {}
        self._register_internal_tools()
        if tools:
            self._register_external_tools(tools)

    def _register_internal_tools(self):
        """Register tools defined within the class (decorated with @tool)."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and getattr(attr, "is_tool", False):
                self.tools[attr_name] = attr

    def _register_external_tools(self, tools: List[Callable]):
        """Register external tools passed as arguments to the constructor."""
        for tool_func in tools:
            if getattr(tool_func, "is_tool", False):
                self.tools[tool_func.__name__] = tool_func
            else:
                raise ValueError(f"{tool_func.__name__} is not decorated with @tool.")

    def generate_tool_schemas(self) -> list:
        """
        Generate tool schemas for API compatibility with OpenAI's expected structure.

        Returns:
            list: A list of tool schemas structured for OpenAI.
        """
        schemas = []
        for tool_name, tool_func in self.tools.items():
            parameters = getattr(tool_func, "tool_parameters", {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            })
            schema = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": getattr(tool_func, "tool_description", "No description available."),
                    "parameters": parameters,
                },
            }
            schemas.append(schema)
        return schemas




    async def call_tool(self, tool_name: str, *args, **kwargs):
        """
        Call a registered tool by name.

        Args:
            tool_name (str): The name of the tool.
            *args: Positional arguments for the tool.
            **kwargs: Keyword arguments for the tool.

        Returns:
            Any: The result of the tool execution.
        """
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found.")
        
        if callable(getattr(tool, '__await__', None)):
            return await tool(*args, **kwargs)
        else:
            return tool(*args, **kwargs)

    @abstractmethod
    async def solve_task(self, task: Task) -> str:
        """
        Abstract method to solve a given task.

        Args:
            task (str): The task to be solved.

        Returns:
            str: The result of the task execution.
        """
        pass

    @abstractmethod
    async def can_perform_coup(self) -> bool:
        """
        Abstract method to determine if the agent is capable of performing a coup.

        Returns:
            bool: True if the agent can perform a coup, False otherwise.
        """
        pass

    def report_failure(self, task: str = None):
        """
        Increments the agent's failure count and logs a failure message.

        Args:
            task (str, optional): The task that failed. If None, a generic failure message is logged.
        """
        self.failed_attempts += 1
        if task:
            self.logger.warning(f"{self.my_name_is} - Failed task: {task}")

    async def receive_message(self, sender: 'BaseAgent', message: str, task: Task) -> str:
        """
        Handles receiving a message from another agent.

        Args:
            sender (BaseAgent): The agent that sends the message.
            message (str): The message content.

        Returns:
            str: The response to the received message.
        """
        self.conversation_history.append({"role": "receiver", "sender": sender.my_name_is, "message": message})
        self.logger.info(f"{self.my_name_is} received message from {sender.my_name_is}: {message}")
        return await self.process_message(sender, message)

    async def send_message(self, recipient: 'BaseAgent', message: str, task: Task) -> str:
        """
        Sends a message to another agent.

        Args:
            recipient (BaseAgent): The agent that will receive the message.
            message (str): The message content to be sent.

        Returns:
            str: The response from the recipient agent after processing the message.
        """
        self.conversation_history.append({"role": "sender", "recipient": recipient.my_name_is, "message": message})
        self.logger.info(f"{self.my_name_is} sends message to {recipient.my_name_is}: {message}")
        return await recipient.receive_message(self, message)

    @abstractmethod
    async def process_message(self, sender: 'BaseAgent', message: str, task: Task) -> str:
        """
        Processes a received message and generates a response.

        Args:
            sender (BaseAgent): The agent that sent the message.
            message (str): The content of the message.

        Returns:
            str: The response generated after processing the message.
        """
        pass
