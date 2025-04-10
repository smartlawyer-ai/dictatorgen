from typing import List, Dict, Optional

from .base_chat_memory import BaseChatMemory

class ChatDiscussion(BaseChatMemory):
    """
    Classe spécialisée pour la gestion des discussions de chat avec une mémoire configurable.
    """

    def __init__(self, memory_id: str, memory: BaseChatMemory):
        """
        Initialise une discussion avec une mémoire.

        Args:
            memory_id (str): L'identifiant unique de la discussion.
            memory (BaseChatMemory): Instance de la mémoire sous-jacente.
        """
        super().__init__(memory_id)
        self.memory = memory

    def add_message(self, message: Dict[str, str]) -> str:
        """
        Ajoute un message à la discussion.

        Args:
            message (Dict[str, str]): Message sous la forme {"role": "user", "content": "message"}.

        Returns:
            str: L'identifiant du message ajouté.
        """
        return self.memory.add_message(self.memory_id, message)

    def add_messages(self, messages: List[Dict[str, str]]) -> List[str]:
        """
        Ajoute plusieurs messages à la discussion.

        Args:
            messages (List[Dict[str, str]]): Liste de messages à ajouter.

        Returns:
            List[str]: Liste des identifiants des messages ajoutés.
        """
        return self.memory.add_messages(self.memory_id, messages)

    def get_messages(self) -> List[Dict[str, str]]:
        """
        Récupère tous les messages de la discussion.

        Returns:
            List[Dict[str, str]]: Liste des messages sous forme de dictionnaires.
        """
        return self.memory.get_messages(self.memory_id)
    
    def delete_memory(self):
        """
        Supprime tous les messages associés à cette discussion.
        """
        self.memory.delete_memory(self.memory_id)

    def delete_message(self, message_id: str) -> Optional[Dict[str, str]]:
        """
        Supprime un message spécifique de la discussion.

        Args:
            message_id (str): L'identifiant du message à supprimer.

        Returns:
            Optional[Dict[str, str]]: Le message supprimé s'il existe, sinon None.
        """
        return self.memory.delete_message(self.memory_id, message_id)

    def delete_messages(self, message_ids: List[str]) -> List[Dict[str, str]]:
        """
        Supprime plusieurs messages d'une discussion en fonction de leurs identifiants.

        Args:
            message_ids (List[str]): Liste des identifiants des messages à supprimer.

        Returns:
            List[Dict[str, str]]: Liste des messages supprimés.
        """
        return self.memory.delete_messages(self.memory_id, message_ids)

    def get_last_message(self) -> Optional[Dict[str, str]]:
        """
        Récupère le dernier message de la discussion.

        Returns:
            Optional[Dict[str, str]]: Le dernier message s'il existe, sinon None.
        """
        messages = self.memory.get_messages(self.memory_id)
        return messages[-1] if messages else None

    def delete_last_message(self) -> Optional[Dict[str, str]]:
        """
        Supprime le dernier message de la discussion.

        Returns:
            Optional[Dict[str, str]]: Le dernier message supprimé s'il existe, sinon None.
        """
        messages = self.memory.get_messages(self.memory_id)
        if messages:
            last_message_id = messages[-1].get("id")
            return self.memory.delete_message(self.memory_id, last_message_id) if last_message_id else None
        return None

    def get_messages_by_role(self, role: str) -> List[Dict[str, str]]:
        """
        Récupère tous les messages d'un certain rôle (ex: 'user', 'assistant').

        Args:
            role (str): Le rôle des messages à récupérer.

        Returns:
            List[Dict[str, str]]: Liste des messages filtrés.
        """
        messages = self.memory.get_messages(self.memory_id)
        return [msg for msg in messages if msg.get("role") == role]
