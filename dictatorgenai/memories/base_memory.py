# mon_framework/memory/base_memory.py
from abc import ABC, abstractmethod
from typing import List, Optional, Type
from dictatorgenai.utils import Task
from dictatorgenai.steps.base_step import TaskStep
from dictatorgenai.memories.stores import MemoryStore

class BaseMemory(ABC):
    """
    Classe de base pour la gestion de la mémoire d'un régime.
    Elle stocke une seule Task pour toute la discussion et les différentes étapes associées.
    Peut utiliser un MemoryStore pour la persistance.
    """

    def __init__(self, memory_id: str, task: Optional[Task] = None, store: Optional[MemoryStore] = None):
        """
        Initialise la mémoire.

        Args:
            memory_id (str): Identifiant unique de la mémoire.
            task (Task): La tâche principale associée à cette mémoire.
            store (Optional[MemoryStore]): Store optionnel pour la persistance.
        """
        self.memory_id = memory_id
        self.task = task or Task(request="Default Task")
        self.steps: List[TaskStep] = []  # Liste des étapes enregistrées
        self.store = store  # Store pour la persistance si activé

    def add_step(self, step: TaskStep):
        """
        Ajoute une étape à la mémoire et la persiste si nécessaire.

        Args:
            step (TaskStep): L'étape à ajouter.
        """
        self.steps.append(step)
        if self.store:
            self.store.save_step(self.memory_id, step)

    def get_steps(self) -> List[TaskStep]:
        """
        Retourne toutes les étapes enregistrées.

        Returns:
            List[TaskStep]: Liste des étapes enregistrées.
        """
        return self.steps

    def reset(self):
        """
        Réinitialise la mémoire en vidant toutes les étapes.
        """
        self.steps = []
        if self.store:
            self.store.clear_memory(self.memory_id)

    @abstractmethod
    def get_steps_for_request(self, request_id: str) -> List[TaskStep]:
        """
        Récupère toutes les étapes associées à une requête utilisateur spécifique.

        Args:
            request_id (str): Identifiant unique de la requête utilisateur.

        Returns:
            List[TaskStep]: Liste des étapes associées.
        """
        pass
