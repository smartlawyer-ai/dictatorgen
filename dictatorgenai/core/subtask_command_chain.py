import json
import logging
from typing import Dict, Generator, List, Tuple, Optional

from dictatorgenai.models import NLPModel, Message
from .command_chain import CommandChain
from .general import General, TaskExecutionError

class DefaultCommandChain(CommandChain):
    def __init__(self, nlp_model: NLPModel):
        """
        Initializes the DefaultCommandChain with the given NLP model.

        Args:
            nlp_model (NLPModel): An instance of the NLPModel to be used for task decomposition and solution.
        """
        self.nlp_model = nlp_model
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)  # Set desired logging level
        
    def _decompose_task(self, task: str) -> List[str]:
        # Use the NLP model to decompose the task
        prompt = self._build_decompose_task_prompt(task=task)
        decomposed_task = self.nlp_model.chat_completion(
            prompt, response_format={"type": "json_object"}
        )
       
        self.logger.debug(
            f"Command Chain Evaluating task: {task} with prompt: {prompt} - Result: {decomposed_task}"
        )
        
        subtasks = self._parse_subtasks(decomposed_task)
        return subtasks
    
    def _build_decompose_task_prompt(self, task: str) -> List[Message]:
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are an assistant specialized in breaking down complex tasks into manageable subtasks. "
                    f"Decompose the following task into a detailed list of subtasks necessary to accomplish it. "
                    f"Format the response as a JSON object with a key 'subtasks' containing an array of objects. "
                    f"Each object should have 'description' (a string) and 'confidence' (a float between 0 and 1) keys."
                ),
            },
            {
                "role": "user",
                "content": f"Please decompose the following task into a list of subtasks with confidence levels: '{task}'.",
            },
        ]
        return messages


    def _parse_subtasks(self, response: str) -> List[Dict[str, any]]:
        """
        Parse la réponse JSON du modèle NLP pour extraire les sous-tâches.

        Args:
            response (str): La chaîne JSON de réponse du modèle NLP.

        Returns:
            List[Dict[str, any]]: Liste des sous-tâches avec leurs descriptions et niveaux de confiance.

        Raises:
            TaskExecutionError: Si la réponse JSON est malformée ou les clés attendues sont manquantes.
        """
        try:
            parsed_response = json.loads(response)
            subtasks = parsed_response.get("subtasks", [])
            if not isinstance(subtasks, list):
                raise TaskExecutionError("La clé 'subtasks' doit contenir une liste.")
            for subtask in subtasks:
                if not isinstance(subtask, dict) or "description" not in subtask or "confidence" not in subtask:
                    raise TaskExecutionError("Chaque sous-tâche doit être un dictionnaire avec 'description' et 'confidence'.")
            self.logger.debug(f"Sous-tâches après parsing JSON: {subtasks}")
            return subtasks
        except json.JSONDecodeError as e:
            self.logger.error(f"Échec du décodage JSON de la réponse: {response}")
            raise TaskExecutionError(f"Échec du décodage JSON de la réponse: {response}") from e
        except Exception as e:
            self.logger.error(f"Une erreur est survenue lors du parsing des sous-tâches: {str(e)}")
            raise TaskExecutionError(f"Une erreur est survenue lors du parsing des sous-tâches: {str(e)}") from e


    
    def _assign_generals_to_subtasks(self, generals: List[General], subtasks: List[Dict[str, any]]) -> Dict[str, General]:
        """
        Assigne les généraux aux sous-tâches basées sur leurs capacités et leur confiance.

        Args:
            generals (List[General]): Liste des généraux disponibles.
            subtasks (List[Dict[str, any]]): Liste des sous-tâches avec leurs descriptions et niveaux de confiance.

        Returns:
            Dict[str, General]: Mapping des descriptions de sous-tâches aux généraux assignés.

        Raises:
            TaskExecutionError: Si aucun général n'est capable d'effectuer une sous-tâche.
        """
        subtask_assignments = {}
        for subtask in subtasks:
            description = subtask.get('description')
            if not description:
                self.logger.error(f"Sous-tâche sans description trouvée: {subtask}")
                raise TaskExecutionError("Chaque sous-tâche doit avoir une description.")
            
            best_general = self._find_best_general_for_subtask(generals, description)
            if best_general:
                subtask_assignments[description] = best_general
                self.logger.debug(f"Assigné la sous-tâche '{description}' au général '{best_general.my_name_is}'.")
            else:
                # Aucun général n'est capable de réaliser la sous-tâche
                self.logger.error(f"Aucun général n'est capable de réaliser la sous-tâche: '{description}'.")
                #raise TaskExecutionError(f"Aucun général n'est capable de réaliser la sous-tâche: '{description}'.")
        
        self.logger.debug(f"Assignations des sous-tâches: {subtask_assignments}")
        return subtask_assignments

    def _find_best_general_for_subtask(self, generals: List[General], subtask_description: str) -> Optional[General]:
        """
        Trouve le meilleur général pour une sous-tâche spécifique basée sur la capacité et la confiance.

        Args:
            generals (List[General]): Liste des généraux disponibles.
            subtask_description (str): Description de la sous-tâche à assigner.

        Returns:
            Optional[General]: Le général le plus approprié ou None si aucun général n'est capable.
        """
        capable_generals = []
        for general in generals:
            capability_level = general.can_execute_task(subtask_description)
            result = capability_level.get("result")
            confidence = capability_level.get("confidence", 0)
            if result in ["entirely", "partially"]:
                capable_generals.append((general, confidence))
                self.logger.debug(
                    f"Le général '{general.my_name_is}' peut exécuter '{subtask_description}' avec le résultat '{result}' et une confiance de {confidence}."
                )
        if capable_generals:
            # Trier les généraux par niveau de confiance décroissant
            capable_generals.sort(key=lambda x: x[1], reverse=True)
            selected_general = capable_generals[0][0]
            self.logger.info(
                f"Général sélectionné '{selected_general.my_name_is}' pour la sous-tâche '{subtask_description}' avec la confiance la plus élevée de {capable_generals[0][1]}."
            )
            return selected_general
        else:
            self.logger.warning(f"Aucun général capable de réaliser la sous-tâche '{subtask_description}'.")
            return None



    def _select_dictator_and_generals(
        self, 
        generals: List[General], 
        task: str
    ) -> Tuple[General, List[General], List[str], Dict[str, General]]:
        # Decompose the task
        subtasks = self._decompose_task(task)
        
        # Assign generals to subtasks
        subtask_assignments = self._assign_generals_to_subtasks(generals, subtasks)
        
        # Select the dictator
        dictator = self._select_dictator(generals, task, subtask_assignments)
        
        # Involved generals
        generals_involved = list(set(subtask_assignments.values()))
        
        return dictator, generals_involved, subtasks, subtask_assignments

    def _select_dictator(
        self, 
        generals: List[General], 
        task: str, 
        subtask_assignments: Dict[str, General]
    ) -> General:
        # Option 1: Choose a general who can integrate subtasks
        #for general in generals:
            #if general.can_integrate_subtasks(task):
                #return general
        # Option 2: By default, choose the general assigned to the main subtask
        main_subtask = list(subtask_assignments.keys())[0]
        return subtask_assignments[main_subtask]

    def solve_task(
        self,
        dictator: General,
        generals: List[General],
        task: str,
        subtasks: List[str],
        subtask_assignments: Dict[str, General]
    ) -> Generator[str, None, None]:
        yield f"{dictator.my_name_is} supervises the resolution of the task.\n"
        yield f"Identified subtasks: {', '.join(subtasks)}.\n"
        
        subtask_results = {}
        for subtask in subtasks:
            general = subtask_assignments[subtask]
            yield f"{general.my_name_is} is working on the subtask: '{subtask}'.\n"
            result = ''.join(general.solve_task(subtask))
            subtask_results[subtask] = result
        
        yield f"{dictator.my_name_is} integrates the results of the subtasks.\n"
        final_result = ''.join(dictator.integrate_subtask_results(subtask_results, task))
        yield final_result
