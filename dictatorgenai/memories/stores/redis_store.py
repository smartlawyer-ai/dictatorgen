# mon_framework/memory_store/redis_store.py
import redis
import json
from typing import List
from ...steps.base_step import TaskStep
from .memory_store import MemoryStore

class RedisStore(MemoryStore):
    """
    Implémente MemoryStore avec Redis comme backend.
    """

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, db: int = 0):
        """
        Initialise la connexion Redis.

        Args:
            redis_host (str): Adresse du serveur Redis.
            redis_port (int): Port du serveur Redis.
            db (int): Numéro de la base Redis.
        """
        self.redis_conn = redis.Redis(host=redis_host, port=redis_port, db=db, decode_responses=True)

    def save_step(self, memory_id: str, step: TaskStep):
        """
        Sauvegarde une étape en JSON dans Redis.

        Args:
            memory_id (str): Identifiant unique de la mémoire.
            step (TaskStep): Étape à sauvegarder.
        """
        step_data = json.dumps(step.to_dict())
        self.redis_conn.rpush(memory_id, step_data)

    def load_steps(self, memory_id: str) -> List[TaskStep]:
        """
        Charge toutes les étapes d'une mémoire en JSON et les reconstruit en `TaskStep`.

        Args:
            memory_id (str): Identifiant de la mémoire.

        Returns:
            List[TaskStep]: Liste des étapes rechargées.
        """
        steps_json = self.redis_conn.lrange(memory_id, 0, -1)
        return [TaskStep.from_dict(json.loads(step)) for step in steps_json]

    def clear_memory(self, memory_id: str):
        """
        Supprime toutes les étapes d'une mémoire.

        Args:
            memory_id (str): Identifiant unique de la mémoire.
        """
        self.redis_conn.delete(memory_id)
