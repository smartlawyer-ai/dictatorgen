from datetime import datetime
from typing import Optional, Dict, Set
from enum import Enum


class EventType(Enum):
    """Enumeration of all possible event types in the system."""

    # 🎯 Task Events
    TASK_STARTED = "task_started"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"

    # 🎯 System Events
    SYSTEM_ALERT = "system_alert"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SYSTEM_ERROR = "system_error"

    # 🎯 User Interaction Events
    USER_MESSAGE = "user_message"
    USER_FEEDBACK = "user_feedback"

    # 🎯 General Management
    GENERALS_SELECTED = "generals_selected"
    GENERAL_REMOVED = "general_removed"
    COUP_D_ETAT = "coup_d_etat"

    # 🎯 Custom Events (modifiable by developers)
    _custom_events: Set[str] = set()

    @classmethod
    def list(cls):
        """
        Returns a list of all predefined and custom event types.
        """
        # Corrected: Use cls to iterate over the enum members
        return [e.value for e in cls.__members__.values()]

    @classmethod
    def add_custom_event(cls, event_name: str):
        """
        Allows developers to add a custom event type dynamically.

        Args:
            event_name (str): The name of the custom event.
        
        Raises:
            ValueError: If the event already exists or the name is invalid.
        """
        if event_name in cls.list():
            raise ValueError(f"Event '{event_name}' already exists.")
        cls._custom_events.add(event_name)

    @classmethod
    def is_valid(cls, event_name: str) -> bool:
        """
        Checks if the given event name is a valid event type.

        Args:
            event_name (str): The event type to check.
        
        Returns:
            bool: True if the event type is valid, False otherwise.
        """
        return event_name in cls.list()
    
    def __str__(self):
        """
        Retourne la valeur de l'énumération directement lors de l'appel à str(EventType.TASK_STARTED).
        """
        return self.value


class Event:
    """
    A flexible class representing an event with predefined and custom event types.
    """

    def __init__(self, event_type: str, message: str, task_id: Optional[str] = None, details: Optional[Dict] = None):
        """
        Initializes a new event.

        Args:
            event_type (str): The type of the event (can be predefined or custom).
            message (str): A descriptive message related to the event.
            task_id (Optional[str]): The unique identifier of the task (default: None).
            details (Optional[Dict]): Optional additional details for the event (default: None).
        """
        if isinstance(event_type, EventType):
            event_type = event_type.value

        if not EventType.is_valid(event_type):
            raise ValueError(f"Invalid event_type '{event_type}'. Must be one of: {EventType.list()}")


        self.event_type = event_type
        self.timestamp = self._get_timestamp()
        self.task_id = task_id
        self.message = message
        self.details = details or {}

    def _get_timestamp(self) -> str:
        """Returns the current timestamp in ISO 8601 format with UTC."""
        return datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict:
        """Returns the event as a dictionary."""
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "task_id": self.task_id,
            "message": self.message,
            "details": self.details
        }
