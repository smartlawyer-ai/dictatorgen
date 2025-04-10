# mon_framework/memory/regime_memory.py
from typing import List, Optional, Union
from .base_memory import BaseMemory
from ..steps.base_step import TaskStep
from ..steps.message_steps import UserMessageStep, AssistantMessageStep
from ..steps.action_steps import GeneralSelectionStep, CoupDEtatStep, ActionStep
from .stores.memory_store import MemoryStore
from ..utils.task import Task

class RegimeMemory(BaseMemory):
    """
    Gestion de la mémoire du régime, incluant les étapes de sélection des généraux, des coups d'état et des actions.
    """

    def __init__(self, memory_id: str, task: Task, store: MemoryStore):
        """
        Initialise la mémoire du régime.

        Args:
            memory_id (str): Identifiant unique de la mémoire.
            task (Task): Objet représentant la tâche principale de la discussion.
            store (MemoryStore): Instance de stockage (RedisStore ou SQLiteStore).
        """
        super().__init__(memory_id)
        self.task = task
        self.steps: List[TaskStep] = []  # Liste des étapes stockées
        self.store = store  # Store de persistance (Redis ou SQLite)
        self.current_request_id: Optional[str] = None  # Permet de suivre la requête en cours

        # Charger les étapes existantes depuis le store
        self.load_from_store()

    def load_from_store(self):
        """
        Charge les étapes de la mémoire depuis le store de persistance.
        """
        self.steps = self.store.load_steps(self.memory_id)

    def save_step(self, step: TaskStep):
        """
        Ajoute une étape en mémoire et la persiste dans le store.

        Args:
            step (TaskStep): Étape à ajouter.
        """
        self.steps.append(step)
        self.store.save_step(self.memory_id, step)

    def add_user_message(self, content: str) -> UserMessageStep:
        """
        Ajoute un message utilisateur sous forme de `UserMessageStep`.

        Args:
            content (str): Contenu du message utilisateur.
        """
        self.current_request_id = f"req_{len(self.steps) + 1}"  # Génération d'un ID de requête
        step = UserMessageStep(request_id=self.current_request_id, content=content)
        self.save_step(step)
        return step

    def add_assistant_message(self, content: str) -> AssistantMessageStep:
        """
        Ajoute un message assistant sous forme de `AssistantMessageStep`.

        Args:
            content (str): Contenu du message assistant.
        """
        if not self.current_request_id:
            raise ValueError("Aucune requête utilisateur en cours. Ajoutez d'abord un message utilisateur.")
        
        step = AssistantMessageStep(request_id=self.current_request_id, content=content)
        self.save_step(step)
        return step

    def select_generals(self, selected_generals: List[str]) -> GeneralSelectionStep:
        """
        Ajoute une étape de sélection des généraux.

        Args:
            selected_generals (List[str]): Liste des généraux sélectionnés.
        """
        if not self.current_request_id:
            raise ValueError("Aucune requête utilisateur en cours. Ajoutez d'abord un message utilisateur.")
        
        step = GeneralSelectionStep(request_id=self.current_request_id, selected_generals=selected_generals)
        self.save_step(step)
        return step

    def coup_detat(self, new_dictator: str, previous_dictator: Optional[str] = None):
        """
        Ajoute une étape de coup d'état.

        Args:
            new_dictator (str): Nom du nouveau dictateur.
            previous_dictator (Optional[str]): Ancien dictateur s'il y en avait un.
        """
        if not self.current_request_id:
            raise ValueError("Aucune requête utilisateur en cours. Ajoutez d'abord un message utilisateur.")
        
        step = CoupDEtatStep(request_id=self.current_request_id, new_dictator=new_dictator, previous_dictator=previous_dictator)
        self.save_step(step)

    def add_action_step(self, general: str, action: str, result: Optional[str] = None):
        """
        Ajoute une étape d'action exécutée par un général.

        Args:
            general (str): Nom du général effectuant l'action.
            action (str): Description de l'action réalisée.
            result (Optional[str]): Résultat de l'action si disponible.
        """
        if not self.current_request_id:
            raise ValueError("Aucune requête utilisateur en cours. Ajoutez d'abord un message utilisateur.")
        
        step = ActionStep(request_id=self.current_request_id, general=general, action=action, result=result)
        self.save_step(step)

    def get_steps_for_request(self, request_id: str) -> List[TaskStep]:
        """
        Récupère toutes les étapes associées à une requête spécifique.

        Args:
            request_id (str): Identifiant de la requête utilisateur.

        Returns:
            List[TaskStep]: Liste des étapes associées à la requête.
        """
        return [step for step in self.steps if step.request_id == request_id]

    def clear_memory(self):
        """
        Efface toute la mémoire et réinitialise la discussion.
        """
        self.steps = []
        self.store.clear_memory(self.memory_id)
