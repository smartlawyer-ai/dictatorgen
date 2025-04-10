from abc import ABC
import time
import inspect  # ✅ Ajout de l'import manquant
from typing import Optional, Dict, Type

# Registre global des types de step
TASK_STEP_REGISTRY: Dict[str, Type["TaskStep"]] = {}

class TaskStep(ABC):
    """
    Classe de base pour toutes les étapes d'exécution d'une tâche.
    """
    def __init__(self, request_id: str, step_type: str, metadata: Optional[Dict[str, object]] = None):
        self.request_id = request_id
        self.step_type = step_type  # ✅ Chaque sous-classe doit enregistrer son propre type
        self.timestamp = time.time()
        self.metadata = metadata if metadata is not None else {}

    def to_dict(self) -> Dict[str, object]:
        """
        Convertit l'objet en dictionnaire pour JSON serialization.

        Returns:
            Dict[str, object]: Représentation de l'objet sous forme de dictionnaire.
        """
        return {
            "step_type": self.step_type,  # ✅ On enregistre `step_type` et non le nom de classe
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "TaskStep":
        """
        Recrée une instance de TaskStep ou d'une de ses sous-classes à partir d'un dictionnaire.
        """
        print("DEBUG data before pop:", data)  # ✅ Ajoute ce log pour voir la structure de `data`
        step_type = data.pop("step_type", None)
        print("DEBUG step_type:", step_type)  # ✅ Vérifie si step_type est bien récupéré

        if not step_type:
            raise ValueError("Le dictionnaire ne contient pas de type d'étape.")

        # Trouver la classe correspondante dans le registre
        step_class = TASK_STEP_REGISTRY.get(step_type)
        if not step_class:
            raise ValueError(f"Aucune classe trouvée pour le type d'étape: {step_type}")

        # 🔹 Récupérer les arguments acceptés par le constructeur de la classe
        step_params = inspect.signature(step_class).parameters
        filtered_data = {key: value for key, value in data.items() if key in step_params}

        # 🔹 Instancier la classe avec uniquement les arguments valides
        return step_class(**filtered_data)

    @classmethod
    def register_step(cls, step_type: str):
        """
        Décorateur pour enregistrer une sous-classe de TaskStep dans le registre.
        """
        def decorator(subclass: Type["TaskStep"]):
            TASK_STEP_REGISTRY[step_type] = subclass
            return subclass
        return decorator
