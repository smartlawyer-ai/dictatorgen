import logging
from .base_event_manager import BaseEventManager


class EventManager(BaseEventManager):
    """
    EventManager extends the BaseEventManager class and adds logging functionality.
    This class is responsible for managing event subscriptions and publishing events
    to all subscribers, with additional logging for event management.

    Attributes:
        logger (logging.Logger): Logger instance for logging event management activity.
    
    Methods:
        start():
            Starts the EventManager. In this basic implementation, it logs that the EventManager has started.
    """

    def __init__(self):
        """
        Initializes the EventManager by calling the BaseEventManager constructor and setting up logging.
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        """
        Starts the EventManager. In this implementation, there is no specific action required to start,
        but the method logs a debug message indicating that the EventManager has been started.
        """
        self.logger.debug("EventManager started")
