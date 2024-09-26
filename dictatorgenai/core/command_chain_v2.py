from typing import List
from .general import General
from abc import abstractmethod

class CommandChain:
    def prepare_task_execution(self, generals: List[General], task: str):
        # Sélection du dictateur et des généraux
        dictator = self._select_dictator(generals, task)
        generals_to_use = self._select_generals(generals, task)

        def execute_task():
            return self.solve_task(dictator, generals_to_use, task)

        return dictator, generals_to_use, execute_task

    def solve_task(self, dictator: General, generals: List[General], task: str):
        # Implémentation de la résolution de la tâche
        yield f"{dictator.my_name_is} résout la tâche avec l'aide de {', '.join([g.my_name_is for g in generals])}.\n"
        # Appel au modèle d'IA
        # ...
        yield "Tâche complétée avec succès.\n"

    @abstractmethod
    def _select_dictator(self, generals: List[General], task: str) -> General:
        # Logique de sélection du dictateur
        pass
    
    @abstractmethod
    def _select_generals(self, generals: List[General], task: str) -> List[General]:
        # Logique de sélection des généraux
        pass