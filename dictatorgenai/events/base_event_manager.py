from typing import Callable, List, Dict, Any
from .event import Event

class BaseEventManager:
    """
    Base class for managing events and allowing subscribers to listen for specific event types.
    This class provides a simple mechanism for subscribing to events and publishing structured events
    to all registered listeners.

    Attributes:
        subscribers (Dict[str, List[Callable[[Any], None]]]): 
            A dictionary mapping event types to a list of listener functions subscribed to those events.
    
    Methods:
        subscribe(event_type: str, listener: Callable[[Any], None]):
            Allows a listener to subscribe to a specific type of event.
        publish(event_type: str, event: Event):
            Publishes a structured event to all listeners subscribed to the specified event type.
        start():
            Can be overridden by subclasses to define a startup procedure for the event manager.
    """

    def __init__(self):
        """
        Initializes the BaseEventManager by creating an empty dictionary of subscribers.
        """
        self.subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: str, listener: Callable[[Any], None]):
        """
        Subscribe a listener to a specific event type. Whenever this event type is published,
        the listener will be notified.

        Args:
            event_type (str): The type of event to subscribe to (e.g., 'task_started').
            listener (Callable[[Any], None]): The listener function that will be called when the event is published.
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(listener)

    def publish(self, event_type: str, event: Event):
        """
        Publish a structured event (an instance of the Event class) to all listeners
        subscribed to the specified event type.

        Args:
            event_type (str): The type of event being published (e.g., 'task_started', 'task_update', etc.).
            event (Event): The event object containing the details of the event being published.
        """
        # Convert the event object to a dictionary
        event_data = event.to_dict()

        # Notify all listeners subscribed to this event type
        if event_type in self.subscribers:
            for listener in self.subscribers[event_type]:
                listener(event_data)  # Publish the event data as a Python dictionary

    def start(self):
        """
        A placeholder method for starting the event manager.
        This can be overridden by subclasses to provide additional functionality when the event manager starts.
        """
        pass
