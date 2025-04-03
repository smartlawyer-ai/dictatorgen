from typing import List, Dict, Optional, TypedDict
from .general import General  # ou le bon chemin
from dictatorgenai.utils.task import Task

class CapabilityUsed(TypedDict):
    capability: str
    explanation: str
    subtasks: List[str]
    sources: List[str]

class AssignedGeneral(General):
    """
    Décorateur de General qui ajoute des métadonnées sur une tâche assignée spécifique.
    Utilisé pour contextualiser un général sélectionné pour une sous-tâche donnée.
    """

    def __init__(
        self,
        base_general: General,
        assigned_subtasks: Optional[List[Dict]] = None,
        capabilities_used: Optional[List[CapabilityUsed]] = None,
        confidence: Optional[float] = None,
    ):
        # Copier les attributs initiaux du general de base
        super().__init__(
            my_name_is=base_general.my_name_is,
            iam=base_general.iam,
            my_capabilities_are=base_general.my_capabilities_are,
            nlp_model=base_general.nlp_model,
        )

        # Ajouts spécifiques
        self._base_general = base_general
        self.assigned_subtasks = assigned_subtasks or []
        self.capabilities_used = capabilities_used or []
        self.confidence = confidence or 0.0

    async def solve_task(self, task: Task, **kwargs):
        """
        Redéfinit solve_task pour injecter de la logique métier ou des validations
        selon les sous-tâches assignées.
        """
        task.add_metadata("assigned_general", self.my_name_is)
        task.add_metadata("assigned_subtasks", self.assigned_subtasks)
        task.add_metadata("confidence", self.confidence)
        task.add_metadata("capabilities_used", self.capabilities_used)

        # Appelle la version de base (peut être overloadée ici si besoin)
        async for chunk in self._base_general.solve_task(task, **kwargs):
            yield chunk

    def __getattr__(self, item):
        """
        Délègue les appels d'attributs non définis à l'objet décoré.
        """
        return getattr(self._base_general, item)
