from typing import List, Dict, Optional
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

from .base_chat_memory import BaseChatMemory

class MongoChatDiscussion(BaseChatMemory):
    """
    Implémentation de BaseChatMemory utilisant MongoDB comme backend de stockage.
    """

    def __init__(self, memory_id: str, mongo_client: MongoClient, db_name: str = "chat_memory", collection_name: str = "discussions"):
        """
        Initialise une discussion de chat stockée dans MongoDB.

        Args:
            memory_id (str): L'identifiant unique de la discussion.
            mongo_client (MongoClient): Client MongoDB.
            db_name (str, optional): Nom de la base de données. Par défaut "chat_memory".
            collection_name (str, optional): Nom de la collection. Par défaut "discussions".
        """
        super().__init__(memory_id)
        self.db = mongo_client[db_name]
        self.collection = self.db[collection_name]

    def add_message(self, memory_id: str, message: Dict[str, str]) -> str:
        """
        Ajoute un message à la discussion.

        Args:
            memory_id (str): L'identifiant de la discussion.
            message (Dict[str, str]): Message sous forme {"role": "user", "content": "message"}.

        Returns:
            str: L'identifiant du message ajouté.
        """
        message["memory_id"] = memory_id
        message["timestamp"] = datetime.datetime.utcnow()
        result = self.collection.insert_one(message)
        return str(result.inserted_id)

    def add_messages(self, memory_id: str, messages: List[Dict[str, str]]) -> List[str]:
        """
        Ajoute plusieurs messages en une seule opération.

        Args:
            memory_id (str): L'identifiant de la discussion.
            messages (List[Dict[str, str]]): Liste des messages.

        Returns:
            List[str]: Liste des identifiants des messages ajoutés.
        """
        for message in messages:
            message["memory_id"] = memory_id
            message["timestamp"] = datetime.datetime.utcnow()
        
        result = self.collection.insert_many(messages)
        return [str(msg_id) for msg_id in result.inserted_ids]

    def get_messages(self, memory_id: str) -> List[Dict[str, str]]:
        """
        Récupère tous les messages associés à une discussion.

        Args:
            memory_id (str): L'identifiant de la discussion.

        Returns:
            List[Dict[str, str]]: Liste des messages triés par date.
        """
        messages = list(self.collection.find({"memory_id": memory_id}).sort("timestamp", 1))
        for message in messages:
            message["_id"] = str(message["_id"])  # Convert BSON ObjectId en string
        return messages

    def delete_memory(self, memory_id: str):
        """
        Supprime tous les messages d'une discussion.

        Args:
            memory_id (str): L'identifiant de la discussion.
        """
        self.collection.delete_many({"memory_id": memory_id})

    def delete_message(self, memory_id: str, message_id: str) -> Optional[Dict[str, str]]:
        """
        Supprime un message spécifique d'une discussion.

        Args:
            memory_id (str): L'identifiant de la discussion.
            message_id (str): L'identifiant du message à supprimer.

        Returns:
            Optional[Dict[str, str]]: Le message supprimé s'il existe, sinon None.
        """
        message = self.collection.find_one_and_delete({"_id": ObjectId(message_id), "memory_id": memory_id})
        if message:
            message["_id"] = str(message["_id"])
        return message

    def delete_messages(self, memory_id: str, message_ids: List[str]) -> List[Dict[str, str]]:
        """
        Supprime plusieurs messages d'une discussion.

        Args:
            memory_id (str): L'identifiant de la discussion.
            message_ids (List[str]): Liste des identifiants des messages à supprimer.

        Returns:
            List[Dict[str, str]]: Liste des messages supprimés.
        """
        object_ids = [ObjectId(msg_id) for msg_id in message_ids]
        deleted_messages = list(self.collection.find({"_id": {"$in": object_ids}, "memory_id": memory_id}))
        
        self.collection.delete_many({"_id": {"$in": object_ids}, "memory_id": memory_id})
        
        for message in deleted_messages:
            message["_id"] = str(message["_id"])
        
        return deleted_messages
