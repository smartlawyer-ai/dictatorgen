from typing import Callable, List, Dict, Any


class BaseEventManager:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: str, listener: Callable[[Any], None]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(listener)

    def publish(self, event_type: str, data: Any):
        if event_type in self.subscribers:
            for listener in self.subscribers[event_type]:
                listener(data)

    def start(self):
        """Méthode pour démarrer l'EventManager, à surcharger dans les sous-classes si nécessaire"""
        pass
