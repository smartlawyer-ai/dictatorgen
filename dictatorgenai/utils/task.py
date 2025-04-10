import uuid
from typing import Optional, List, Dict
from dictatorgenai.steps.base_step import TaskStep  # ✅ Import de TaskStep

class TaskStatus:
    """Statut des tâches : normalise les états possibles."""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class Task:
    """
    Représente une tâche avec un identifiant unique, une demande utilisateur,
    un contexte sous forme de liste de `TaskStep`, un statut et des métadonnées.
    """
    def __init__(
        self, 
        request: str,
        steps: Optional[List[TaskStep]] = None,  # ✅ Liste de TaskStep au lieu de dict
        subtasks: Optional[List['Task']] = None,  # Liste des sous-tâches
        metadata: Optional[Dict[str, object]] = None, 
        priority: Optional[int] = 5, 
        status: str = TaskStatus.PENDING,
        task_id: Optional[str] = None,  
    ):
        self.task_id = task_id or str(uuid.uuid4())  # Génération d'un ID unique si non fourni
        self.request = request
        self.steps = steps or []  # ✅ Stocke une liste d'objets TaskStep
        self.subtasks = subtasks or []  # Ajouter un attribut pour les sous-tâches
        self.metadata = metadata or {}
        self.priority = priority
        self.status = status

    def add_step(self, step: TaskStep):
        """
        Ajoute un `TaskStep` au contexte de la tâche.

        Args:
            step (TaskStep): L'étape à ajouter.
        """
        self.steps.append(step)
    
    def add_subtask(self, subtask: 'Task'):
        """Ajoute une sous-tâche à la tâche principale."""
        self.subtasks.append(subtask)

    def add_metadata(self, key: str, value):
        """Ajoute une métadonnée avec validation."""
        if callable(value):  
            raise ValueError("Metadata value cannot be a callable object.")
        self.metadata[key] = value
    
    def remove_metadata(self, key: str):
        """Supprime une métadonnée si elle existe."""
        if key not in self.metadata:
            raise KeyError(f"Metadata key '{key}' not found.")
        del self.metadata[key]

    def __str__(self):
        return f"Task(task_id='{self.task_id}', request='{self.request}', priority={self.priority}, status='{self.status}')"

    def to_dict(self) -> Dict:
        """Convertit l'objet Task en dictionnaire, incluant les sous-tâches."""
        task_dict = {
            "task_id": self.task_id,
            "request": self.request,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": self.metadata,
            "priority": self.priority,
            "status": self.status,
        }
        if self.subtasks:
            task_dict["subtasks"] = [subtask.to_dict() for subtask in self.subtasks]
        return task_dict

    def update_status(self, new_status: str):
        """Met à jour le statut de la tâche avec validation."""
        if new_status not in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, TaskStatus.FAILED):
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status
