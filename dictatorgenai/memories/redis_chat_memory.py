import redis
from typing import List, Dict

from dictatorgenai.memories.base_chat_memory import BaseChatMemory

class RedisChatMemory(BaseChatMemory):
    """
    Implémentation de la mémoire de chat utilisant Redis comme stockage.
    """

    def __init__(self, memory_id: str, redis_host: str = 'localhost', redis_port: int = 6379, redis_db: int = 0):
        """
        Initialise la mémoire avec un identifiant unique pour chaque discussion et se connecte à Redis.

        Args:
            memory_id (str): L'identifiant unique pour cette mémoire de chat.
            redis_host (str): L'hôte Redis.
            redis_port (int): Le port Redis.
            redis_db (int): La base de données Redis à utiliser.
        """
        super().__init__(memory_id)
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

    def add_message(self, memory_id: str, message: Dict[str, str]):
        """
        Ajoute un message à une discussion identifiée par `memory_id`.
        """
        self.redis_client.rpush(memory_id, str(message))

    def add_messages(self, memory_id: str, messages: List[Dict[str, str]]):
        """
        Ajoute plusieurs messages à une discussion identifiée par `memory_id`.
        """
        for message in messages:
            self.redis_client.rpush(memory_id, str(message))

    def get_messages(self, memory_id: str) -> List[Dict[str, str]]:
        """
        Récupère tous les messages pour une discussion identifiée par `memory_id`.
        """
        messages = self.redis_client.lrange(memory_id, 0, -1)
        return [eval(message) for message in messages]

    def delete_memory(self, memory_id: str):
        """
        Supprime tous les messages associés à `memory_id`.
        """
        self.redis_client.delete(memory_id)
