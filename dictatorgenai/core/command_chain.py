from typing import List, Callable, Generator, Tuple
from abc import ABC, abstractmethod
from .general import General

class CommandChain(ABC):
    def prepare_task_execution(self, generals: List[General], task: str):
        # Sélection du dictateur et des généraux
        dictator, generals_to_use = self._select_dictator_and_generals(generals, task)

        def execute_task():
            return self.solve_task(dictator, generals_to_use, task)

        return dictator, generals_to_use, execute_task

    def solve_task(self, dictator: General, generals: List[General], task: str):
        # Implémentation de la résolution de la tâche
        assisting_generals = [g for g in generals if g != dictator]
        if assisting_generals:
            yield f"{dictator.my_name_is} résout la tâche avec l'aide de {', '.join([g.my_name_is for g in assisting_generals])}.\n"
        else:
            yield f"{dictator.my_name_is} résout la tâche seul.\n"
        # Appel au modèle d'IA
        # ...
        yield "Tâche complétée avec succès.\n"

    @abstractmethod
    def _select_dictator_and_generals(self, generals: List[General], task: str) -> Tuple[General, List[General]]:
        """
        Logique de sélection du dictateur et des généraux.
        Retourne un tuple contenant le dictateur et la liste des généraux à utiliser.
        """
        pass
