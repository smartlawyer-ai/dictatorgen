from .base_event_manager import BaseEventManager


class EventManager(BaseEventManager):
    def __init__(self):
        super().__init__()

    def start(self):
        """Démarre l'EventManager. Dans cette version, il n'y a rien à démarrer explicitement."""
        print("EventManager started")
