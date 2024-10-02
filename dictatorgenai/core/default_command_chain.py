import json
import logging
from typing import Generator, List, Tuple

from dictatorgenai.models import NLPModel
from .command_chain import CommandChain
from .general import General, TaskExecutionError
from dictatorgenai.conversations import BaseConversation

class DefaultCommandChain(CommandChain):
    def __init__(self, nlp_model: NLPModel):
        """
        Initializes the DefaultCommandChain with the given NLP model.

        Args:
            nlp_model (NLPModel): An instance of the NLPModel to be used for task decomposition and solution.
        """
        super().__init__(None)
        self.nlp_model = nlp_model
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)  # Set desired logging level

    def _select_dictator_and_generals(self, generals: List[General], task: str) -> Tuple[General, List[General]]:
        selected_generals = []
        dictator = None

        for general in generals:
            capability_level = general.can_execute_task(task)
            if capability_level.get("result") == "entirely":
                dictator = general
                break  # On a trouvé un dictateur capable, on peut sortir de la boucle
            elif capability_level.get("result") == "partially":
                selected_generals.append(general)

        if not dictator:
            if selected_generals:
                # Utiliser le premier général des selected_generals comme dictateur
                dictator = selected_generals[0]
                selected_generals = selected_generals[1:]  # Retirer ce général de la liste des généraux
            else:
                # Aucun général ne peut exécuter la tâche, lever une erreur
                raise TaskExecutionError("Aucun général n'est capable d'exécuter la tâche.")

        return dictator, selected_generals


    def solve_task(
        self,
        dictator: General,
        generals: List[General],
        task: str
    ) -> Generator[str, None, None]:
        if len(generals) == 1 and generals[0] == dictator:
            # Le dictateur résout la tâche seul
            yield f"{dictator.my_name_is} résout la tâche seul.\n"
            yield from dictator.solve_task(task)
        else:
            # Processus de résolution collective de la tâche
            yield f"Dictator {dictator.my_name_is} integrates the responses from the generals.\n"
            yield from self.conversation.start_conversation(dictator, generals, task)
            
            # The dictator integrates the results from the generals
            #yield f"Task '{task}' completed with the following results: {conversation_result}"