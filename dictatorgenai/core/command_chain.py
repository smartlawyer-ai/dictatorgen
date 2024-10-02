from typing import List, Callable, Generator, Tuple, Dict
from abc import ABC, abstractmethod

from dictatorgenai.conversations import BaseConversation, GroupChat
from .general import General

class CommandChain(ABC):
    def __init__(self, conversation: BaseConversation = None):
        # Default to GroupChat if no conversation type is provided
        self.conversation = conversation if conversation else GroupChat()
        
    def prepare_task_execution(self, generals: List[General], task: str):
        # Sélection du dictateur, des généraux, des sous-tâches et des assignations
        dictator, generals_to_use = self._select_dictator_and_generals(generals, task)

        def execute_task():
            return self.solve_task(dictator, generals_to_use, task)

        return dictator, generals_to_use, execute_task

    @abstractmethod
    def _select_dictator_and_generals(
        self, 
        generals: List[General], 
        task: str
    ) -> Tuple[General, List[General], List[str], Dict[str, General]]:
        """
        Logique de sélection du dictateur et des généraux.
        Retourne un tuple contenant le dictateur, la liste des généraux à utiliser,
        la liste des sous-tâches et les assignations des sous-tâches.
        """
        pass

    @abstractmethod
    def solve_task(
        self, 
        dictator: General, 
        generals: List[General], 
        task: str,
    ) -> Generator[str, None, None]:
        """
        Implémentation de la résolution de la tâche.
        Doit être implémentée par les classes dérivées.
        """
        pass
