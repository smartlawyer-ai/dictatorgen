from typing import List, Dict

from .base_chat_memory import BaseChatMemory

class ChatDiscussion(BaseChatMemory):
    """
    Classe spécialisée pour la gestion des discussions de chat avec une mémoire configurable.
    """

    def __init__(self, memory_id: str, memory: BaseChatMemory):
        super().__init__(memory_id)
        self.memory = memory

    def add_message(self, message: Dict[str, str]):
        """
        Ajoute un message avec un rôle et un contenu à la discussion.
        """
        self.memory.add_message(self.memory_id, message)

    def get_messages(self) -> List[Dict[str, str]]:
        """
        Récupère tous les messages de la discussion.
        """
        return self.memory.get_messages(self.memory_id)
    
    def delete_memory(self, memory_id: str):
        """
        Supprime tous les messages associés à `memory_id`.
        """
        self.memory.delete_memory(self.memory_id)

    def close(self):
        """
        Supprime tous les messages associés à cette discussion.
        """
        self.memory.delete_memory(self.memory_id)
