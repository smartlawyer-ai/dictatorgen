from datetime import datetime
from typing import Optional, Dict

class Event:
    """
    A simple class representing an event without specific methods for different event types.

    Attributes:
        event_type (str): The type of the event (e.g., 'task_started', 'task_update', etc.).
        timestamp (str): The timestamp when the event was created, in ISO 8601 format (UTC).
        task_id (str): The unique identifier of the task associated with the event.
        agent (str): The name of the agent responsible for the event.
        message (str): A descriptive message related to the event.
        details (dict): Optional additional details about the event.

    Methods:
        _get_timestamp() -> str:
            Generates the current timestamp in ISO 8601 format with UTC.
        
        to_dict() -> dict:
            Returns the event as a dictionary for easy use.
    """

    def __init__(self, event_type: str, task_id: str, agent: str, message: str, details: Optional[Dict] = None):
        """
        Initializes a new task event.

        Args:
            event_type (str): The type of the event (e.g., 'task_started', 'task_update', etc.).
            task_id (str): The unique identifier of the task.
            agent (str): The name of the agent responsible for the event.
            message (str): A descriptive message related to the event.
            details (Optional[Dict]): Optional additional details for the event (default is None).
        """
        self.event_type = event_type
        self.timestamp = self._get_timestamp()
        self.task_id = task_id
        self.agent = agent
        self.message = message
        self.details = details or {}

    def _get_timestamp(self) -> str:
        """
        Returns the current timestamp in ISO 8601 format with UTC.

        Returns:
            str: The timestamp in ISO 8601 format.
        """
        return datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict:
        """
        Returns the event as a dictionary for easy usage.

        Returns:
            dict: The event represented as a dictionary.
        """
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "task_id": self.task_id,
            "agent": self.agent,
            "message": self.message,
            "details": self.details
        }
