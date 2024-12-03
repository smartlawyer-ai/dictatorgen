import asyncio
from typing import Callable, List, Dict, Any, Union
from .event import Event

class BaseEventManager:
    """
    Base class for managing events and allowing subscribers to listen for specific event types.
    This class provides a simple mechanism for subscribing to events and publishing structured events
    to all registered listeners.

    Attributes:
        subscribers (Dict[str, List[Callable[[Any], Union[None, Any]]]]): 
            A dictionary mapping event types to a list of listener functions subscribed to those events.
        events (Dict[str, asyncio.Event]):
            A dictionary of asyncio.Event objects for each event type, used to wait for events to be published.
    """

    def __init__(self):
        """
        Initializes the BaseEventManager by creating an empty dictionary of subscribers and events.
        """
        self.subscribers: Dict[str, List[Callable[[Any], Union[None, Any]]]] = {}
        self.events: Dict[str, asyncio.Event] = {}

    def subscribe(self, event_type: str, listener: Callable[[Any], Union[None, Any]]):
        """
        Subscribe a listener to a specific event type. Whenever this event type is published,
        the listener will be notified.

        Args:
            event_type (str): The type of event to subscribe to (e.g., 'task_started').
            listener (Callable[[Any], Union[None, Any]]): The listener function that will be called when the event is published.
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
            self.events[event_type] = asyncio.Event()  # Create an asyncio.Event for this type of event
        self.subscribers[event_type].append(listener)

    def unsubscribe(self, event_type: str, listener: Callable[[Any], Union[None, Any]]):
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(listener)
            if not self.subscribers[event_type]:
                del self.subscribers[event_type]
                del self.events[event_type]


    async def publish(self, event_type: str, event: Event):
        """
        Publish a structured event (an instance of the Event class) to all listeners
        subscribed to the specified event type. If the listener is asynchronous, it is awaited.

        Args:
            event_type (str): The type of event being published (e.g., 'task_started', 'task_update', etc.).
            event (Event): The event object containing the details of the event being published.
        """
        # Convert the event object to a dictionary
        event_data = event.to_dict()
        
        # Notify all listeners subscribed to this event type
        if event_type in self.subscribers:
            tasks = []
            tasks = [self._safe_call(listener, event_data) for listener in self.subscribers[event_type]]  # Call sync listeners directly
            self.events[event_type].set()  
            await asyncio.gather(*tasks)   
            self.events[event_type].clear() 
    
    async def _safe_call(self, listener, event_data):
        try:
            await listener(event_data) if asyncio.iscoroutinefunction(listener) else listener(event_data)
        except Exception as e:
            # Log or handle the exception as needed
            print(f"Exception in listener: {e}")

    async def wait_for_event(self, event_type: str):
        """
        Wait until the specified event type is published.

        Args:
            event_type (str): The type of event to wait for.
        """
        if event_type in self.events:
            await self.events[event_type].wait()  # Wait for the event to be set
