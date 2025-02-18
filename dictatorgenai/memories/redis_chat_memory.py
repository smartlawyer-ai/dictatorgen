import redis
import json
import uuid
from typing import List, Dict, Optional
from .base_chat_memory import BaseChatMemory

class RedisChatMemory(BaseChatMemory):
    """
    Implémentation de BaseChatMemory utilisant Redis comme backend de stockage, avec UUID pour identifier chaque message.
    """

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, db: int = 0):
        """
        Initialise Redis pour stocker les messages.

        Args:
            redis_host (str): Adresse du serveur Redis.
            redis_port (int): Port du serveur Redis.
            db (int): Numéro de la base de données Redis.
        """
        self.redis_conn = redis.Redis(host=redis_host, port=redis_port, db=db, decode_responses=True)

    def add_message(self, memory_id: str, message: Dict[str, str]) -> str:
        """
        Ajoute un message à Redis avec un UUID unique.

        Args:
            memory_id (str): Identifiant de la discussion.
            message (Dict[str, str]): Message contenant le rôle et le contenu.

        Returns:
            str: L'identifiant unique du message ajouté.
        """
        message_id = str(uuid.uuid4())  # Génération d'un UUID unique
        message["message_id"] = message_id  # Ajout de l'ID unique au message
        serialized_message = json.dumps(message)
        self.redis_conn.rpush(memory_id, serialized_message)  # Ajout dans la liste Redis
        return message_id  # Retourne l'ID unique

    def add_messages(self, memory_id: str, messages: List[Dict[str, str]]) -> List[str]:
        """
        Ajoute plusieurs messages en une seule opération.

        Args:
            memory_id (str): Identifiant de la discussion.
            messages (List[Dict[str, str]]): Liste des messages à ajouter.

        Returns:
            List[str]: Liste des identifiants uniques des messages ajoutés.
        """
        message_ids = []
        serialized_messages = []

        for message in messages:
            message_id = str(uuid.uuid4())
            message["message_id"] = message_id
            message_ids.append(message_id)
            serialized_messages.append(json.dumps(message))

        self.redis_conn.rpush(memory_id, *serialized_messages)  # Ajout en batch
        return message_ids  # Retourne les UUID des messages ajoutés

    def get_messages(self, memory_id: str) -> List[Dict[str, str]]:
        """
        Récupère tous les messages stockés sous `memory_id`.

        Args:
            memory_id (str): Identifiant de la discussion.

        Returns:
            List[Dict[str, str]]: Liste des messages.
        """
        messages = self.redis_conn.lrange(memory_id, 0, -1)
        return [json.loads(msg) for msg in messages] if messages else []

    def delete_memory(self, memory_id: str):
        """
        Supprime tous les messages d'une discussion.

        Args:
            memory_id (str): Identifiant de la discussion.
        """
        self.redis_conn.delete(memory_id)

    def delete_message(self, memory_id: str, message_id: str) -> Optional[Dict[str, str]]:
        """
        Supprime un message spécifique en fonction de son UUID.

        Args:
            memory_id (str): Identifiant de la discussion.
            message_id (str): UUID du message à supprimer.

        Returns:
            Optional[Dict[str, str]]: Le message supprimé, ou `None` s'il n'existe pas.
        """
        messages = self.get_messages(memory_id)
        new_messages = []
        deleted_message = None

        for message in messages:
            if message.get("message_id") == message_id:
                deleted_message = message
            else:
                new_messages.append(json.dumps(message))

        if deleted_message:
            self.redis_conn.delete(memory_id)  # Supprime la clé
            self.redis_conn.rpush(memory_id, *new_messages)  # Réécrit les messages sans celui supprimé

        return deleted_message

    def delete_messages(self, memory_id: str, message_ids: List[str]) -> List[Dict[str, str]]:
        """
        Supprime plusieurs messages en fonction de leurs UUID.

        Args:
            memory_id (str): Identifiant de la discussion.
            message_ids (List[str]): Liste des UUID des messages à supprimer.

        Returns:
            List[Dict[str, str]]: Liste des messages supprimés.
        """
        messages = self.get_messages(memory_id)
        new_messages = []
        deleted_messages = []

        for message in messages:
            if message.get("message_id") in message_ids:
                deleted_messages.append(message)
            else:
                new_messages.append(json.dumps(message))

        if deleted_messages:
            self.redis_conn.delete(memory_id)  # Supprime la clé
            self.redis_conn.rpush(memory_id, *new_messages)  # Réécrit les messages sans ceux supprimés

        return deleted_messages
