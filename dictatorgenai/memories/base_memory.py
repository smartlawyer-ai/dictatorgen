from abc import ABC, abstractmethod
from typing import Any, List

class Memory(ABC):
    """
    Classe abstraite pour le stockage en mémoire.
    Chaque instance est associée à un memory_id unique.
    """

    def __init__(self, memory_id: str):
        self.memory_id = memory_id

    @abstractmethod
    def add_message(self, message: Any):
        """
        Ajoute un message à la mémoire associée.
        """
        pass

    @abstractmethod
    def get_messages(self) -> List[Any]:
        """
        Récupère tous les messages de la mémoire associée.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Ferme les ressources utilisées par la mémoire.
        """
        pass
