from abc import ABC, abstractmethod
from typing import List, Dict, Optional

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
    def add_message(self, memory_id: str, message: Dict[str, str]) -> str:
        pass

    @abstractmethod
    def add_messages(self, memory_id: str, messages: List[Dict[str, str]]) -> List[str]:
        pass

    @abstractmethod
    def get_messages(self, memory_id: str) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str):
        pass

    @abstractmethod
    def delete_message(self, memory_id: str, message_id: str) -> Optional[Dict[str, str]]:
        pass

    @abstractmethod
    def delete_messages(self, memory_id: str, message_ids: List[str]) -> List[Dict[str, str]]:
        pass