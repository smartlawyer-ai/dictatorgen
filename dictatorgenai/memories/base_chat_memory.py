from abc import ABC, abstractmethod
from typing import List, Dict

class BaseChatMemory(ABC):
    """
    Interface abstraite pour gérer les mémoires de chat avec différents systèmes de stockage.
    """

    def __init__(self, memory_id: str):
        """
        Initialise la mémoire avec un identifiant unique pour chaque discussion.

        Args:
            memory_id (str): L'identifiant unique pour cette mémoire de chat.
        """
        self.memory_id = memory_id

    @abstractmethod
    def add_message(self, memory_id: str, message: Dict[str, str]):
        """
        Ajoute un message à une discussion identifiée par `memory_id`.
        """
        pass

    @abstractmethod
    def get_messages(self, memory_id: str) -> List[Dict[str, str]]:
        """
        Récupère tous les messages pour une discussion identifiée par `memory_id`.
        """
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str):
        """
        Supprime tous les messages associés à `memory_id`.
        """
        pass
