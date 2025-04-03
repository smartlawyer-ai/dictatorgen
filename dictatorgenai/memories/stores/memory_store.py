# mon_framework/memory_store/base_store.py
from abc import ABC, abstractmethod
from typing import List
from ...steps.base_step import TaskStep

class MemoryStore(ABC):
    """
    Interface pour les différents systèmes de stockage des mémoires.
    """

    @abstractmethod
    def save_step(self, memory_id: str, step: TaskStep):
        """
        Sauvegarde une étape spécifique dans la mémoire persistante.
        
        Args:
            memory_id (str): Identifiant de la mémoire.
            step (TaskStep): Étape à sauvegarder.
        """
        pass

    @abstractmethod
    def load_steps(self, memory_id: str) -> List[TaskStep]:
        """
        Charge toutes les étapes associées à une mémoire donnée.

        Args:
            memory_id (str): Identifiant de la mémoire.

        Returns:
            List[TaskStep]: Liste des étapes stockées.
        """
        pass

    @abstractmethod
    def clear_memory(self, memory_id: str):
        """
        Supprime toutes les étapes associées à une mémoire.

        Args:
            memory_id (str): Identifiant de la mémoire.
        """
        pass
