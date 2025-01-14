import uuid
from typing import Optional, List, Dict


class TaskStatus:
    """
    Statut des tâches. Permet de normaliser les états possibles d'une tâche.
    """
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"


class Task:
    """
    Représente une tâche avec les détails de la demande de l'utilisateur, 
    un contexte associé, un statut, et un identifiant unique.
    """
    def __init__(
        self, 
        request: str,
        context: Optional[List[Dict[str, str]]] = None, 
        metadata: Optional[Dict[str, object]] = None, 
        priority: Optional[int] = 5, 
        status: str = TaskStatus.PENDING,
        task_id: Optional[str] = None,  # Ajout de task_id
    ):
        self.task_id = task_id or str(uuid.uuid4())  # Génération d'un ID unique si non fourni
        self.request = request
        self.context = context or []
        self.metadata = metadata or {}
        self.priority = priority
        self.status = status

    def add_metadata(self, key: str, value):
        """
        Ajoute une métadonnée avec validation.
        :param key: La clé de la métadonnée.
        :param value: La valeur de la métadonnée.
        """
        # Exemple : restreindre certains types interdits
        if callable(value):  # Interdire les fonctions pour éviter des complications
            raise ValueError("Metadata value cannot be a callable object.")
        self.metadata[key] = value
    
    def remove_metadata(self, key: str):
        """
        Supprime une métadonnée si elle existe.

        :param key: La clé de la métadonnée à supprimer.
        :raises KeyError: Si la clé n'existe pas dans les métadonnées.
        """
        if key not in self.metadata:
            raise KeyError(f"Metadata key '{key}' not found.")
        del self.metadata[key]


    def __str__(self):
        return (
            f"Task(task_id='{self.task_id}', request='{self.request}', "
            f"priority={self.priority}, status='{self.status}')"
        )

    def to_dict(self) -> Dict:
        """
        Convertit l'objet Task en dictionnaire.
        """
        return {
            "task_id": self.task_id,
            "request": self.request,
            "context": self.context,
            "metadata": self.metadata,
            "priority": self.priority,
            "status": self.status,
        }

    def update_status(self, new_status: str):
        """
        Met à jour le statut de la tâche.
        """
        if new_status not in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, TaskStatus.FAILED):
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status
