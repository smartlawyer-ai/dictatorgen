import json
import logging
import asyncio
from typing import Dict, AsyncGenerator, List, Tuple
from dictatorgenai.agents.majordomo import Majordomo
from dictatorgenai.agents.legion_commander import LegionCommander
from dictatorgenai.agents.colonel_fragmenter import ColonelFragmenter
from dictatorgenai.agents.assigned_general import AssignedGeneral
from dictatorgenai.models import BaseModel, Message
from dictatorgenai.utils.task import Task
from .command_chain import CommandChain
from ..agents.general import General, TaskExecutionError
from dictatorgenai.config import DictatorSettings
from dictatorgenai.steps.action_steps import ActionStep, PlanningStep, GeneralEvaluationStep
from dictatorgenai.events import BaseEventManager, EventManager, Event, EventType

class DefaultCommandChain(CommandChain):
    """
    Default implementation of the CommandChain for managing task execution among generals.
    It uses an NLP model to determine if the generals' combined capabilities can solve a given task.

    Attributes:
        nlp_model (BaseModel): The NLP model used for task decomposition and decision making.
        logger (logging.Logger): Logger for recording debug and error messages.
    """

    def __init__(self, nlp_model: BaseModel, confidence_threshold: float = 1.0, event_manager: BaseEventManager = None):
        super().__init__(None)
        self.nlp_model = nlp_model
        self.logger = logging.getLogger(self.__class__.__name__)
        self.confidence_threshold = confidence_threshold
        self.event_manager = event_manager or EventManager()
    
    def build_capabilities_cover_task_prompt(self, task: Task, capabilities: List[str]) -> List[Message]:
        capabilities_str = ", ".join(capabilities)
        messages = [
            {
                "role": "system",
                "content": (
                    f"Your goal is to determine if the given capabilities from agents are able to solve the given task. "
                    f"Format the response as JSON with a result that equals 'true' or 'false' and a confidence by capability.\n"
                    f"If sum of confidence is equal or greater than {self.confidence_threshold} reply with result true.\n"
                    f"Here is an example of the expected JSON result:\n"
                    "----------------------\n"
                    '{\n'
                    '  "result": "true",\n'
                    '  "confidence_capabilities": {\n'
                    '    "write_contract": "0.7",\n'
                    '    "reply_with_lawcase": "0.3",\n'
                    '    "speak_french": "0.9"\n'
                    '  }\n'
                    '}\n'
                    "----------------------"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Here are the capabilities:\n"
                    f"-------------------------\n"
                    f"{capabilities_str}\n"
                    f"-------------------------\n"
                    f"Can you solve the following task: {task.request}?"
                ),
            },
        ]
        return messages

    async def capabilities_cover_task(self, combined_capabilities: set, task: Task) -> Dict:
        prompt = self.build_capabilities_cover_task_prompt(task, list(combined_capabilities))
        try:
            response = await self.nlp_model.chat_completion(
                prompt, tools= [], response_format={"type": "json_object"}
            )
            message = response.message
            evaluation = json.loads(getattr(message, "content", None))
            self.logger.debug(
                f"Evaluating generals can cover tasks together: {task.request} - Result: {evaluation}"
            )
            return evaluation
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {response}")
            raise TaskExecutionError(
                f"Failed to decode JSON response: {response}"
            ) from e
        except Exception as e:
            self.logger.error(f"Default CommandChain : An error occurred while evaluating the task: {str(e)}")
            raise TaskExecutionError(
                f"Default CommandChain : An error occurred while evaluating the task: {str(e)}"
            ) from e
        
    async def _select_dictator_and_generals(self, generals: List[General], task: Task) -> Tuple[AssignedGeneral, List[AssignedGeneral], Task]:
        """
        Sélectionne le dictateur et les généraux pour résoudre la tâche en la découpant en sous-tâches.
        """
        selected_generals = []
        combined_capabilities = set()
        general_capabilities = []

        # 1. Décomposer la tâche en sous-tâches avec le ColonelFragmenter
        colonel_fragmenter = ColonelFragmenter(my_name_is="ColonelFragmenter", iam="Fragmentation Specialist", my_capabilities_are=[], nlp_model=self.nlp_model)
        
        try:
            subtasks = await colonel_fragmenter.solve_task(task, generals=generals)
            # for subtask in subtasks:
            #     task.add_subtask(Task(request=json.dumps(subtask), metadata=subtask))

            task.add_step(PlanningStep(request_id=len(task.steps) + 1, plan=json.dumps(subtasks), metadata=subtasks))
            await self.event_manager.publish(Event(EventType.TASK_UPDATED, f"Task has been decomposed into subtasks.", task.task_id, details=task.to_dict()))
            
        except TaskExecutionError as e:
            raise TaskExecutionError(f"Task could not be fragmented: {e}")

        await self.event_manager.publish(Event(EventType.TASK_UPDATED, f"Task has been decomposed into subtasks.", task.task_id, details=task.to_dict()))

        # 2. Sélectionner les généraux avec le LegionCommander
        legion_commander = LegionCommander(my_name_is="LegionCommander", iam="Legion Commander", my_capabilities_are=[], nlp_model=self.nlp_model)
        
        try:
            # Nous passons les généraux et les sous-tâches à solve_task de LegionCommander via kwargs
            selected_generals = await legion_commander.solve_task(task, generals=generals, subtasks=subtasks)

        except TaskExecutionError as e:
            raise TaskExecutionError(f"Task could not be solved by generals: {e}")

        # 3. Finaliser le dictateur et les généraux sélectionnés
        if selected_generals:
            
            # Sélectionner le dictateur parmi les généraux en fonction de leur contribution
            # Le dictateur sera ici le premier général dans la liste triée (ce que tu as déjà fait dans _rank_generals_by_capabilities)
            dictator = selected_generals[0]
            # Retourner le dictateur et les généraux sélectionnés
            return dictator, selected_generals, task

        else:
            raise TaskExecutionError(message="No general is capable of solving this task.")

    def _select_dictator_from_generals(self, generals: List[General]) -> General:
        """
        Sélectionne le dictateur parmi les généraux en fonction de leur contribution.
        """
        best_general = max(generals, key=lambda g: g.confidence)  # Exemple basique pour choisir un dictateur
        return best_general

    #async def _select_dictator_and_generals(self, generals: List[General], task: Task) -> Tuple[General, List[General], Task]:
    #     selected_generals = []
    #     combined_capabilities = set()
    #     general_capabilities = []
    #     majordomo = Majordomo()

    #     subtasks_response = await self.nlp_model.chat_completion([
    #         Message(role="system", content=self.build_task_decomposition_prompt(task)),
    #         Message(role="user", content=task.request)
    #     ], tools=[], response_format={"type": "json_object"})

    #     subtasks = json.loads(getattr(subtasks_response.message, "content", "{}"))
    #     task.add_step(PlanningStep(request_id=len(task.steps) + 1, plan=getattr(subtasks_response.message, "content", "{}"), metadata=subtasks))
        
    #     await self.event_manager.publish(Event(EventType.TASK_UPDATED, f"Task has been decomposed into subtasks.", task.task_id, details=task.to_dict()))

    #     def build_capabilities_prompt_for_general(general: General, subtasks: Dict) -> List[Message]:
    #         """
    #         Construit un prompt pour évaluer si les capacités du général sont suffisantes pour résoudre certaines sous-tâches.

    #         Args:
    #             general (General): Le général pour lequel on évalue les capacités.
    #             subtasks (Dict): Résultat de la décomposition de la tâche en sous-tâches (format JSON).

    #         Returns:
    #             List[Message]: Un prompt structuré pour l'évaluation des capacités.
    #         """

    #         # 🔹 Formatage propre des sous-tâches pour affichage dans le prompt
    #         subtasks_str = json.dumps(subtasks, ensure_ascii=False, indent=2)

    #         reply_language = f"Provide details in {DictatorSettings.get_language()} language."

    #         # 🔹 Création du message système décrivant les capacités du général
    #         system_message = {
    #             "role": "system",
    #             "content": (
    #                 f"My name is {general.my_name_is}. I am {general.iam}. "
    #                 "I have the following capabilities:\n" +
    #                 "\n".join([f"- {cap['capability']}: {cap.get('description', 'No description provided')}" 
    #                         for cap in general.my_capabilities_are]) +
    #                 "\n\nAnalyze the following subtasks and determine whether I can solve them based on my skills.\n"
    #                 "Reply in JSON format with 'result', 'confidence', and 'details'.\n"
    #                 "'result' should be 'entirely', 'partially', or 'no'.\n"
    #                 "'confidence' is a float between 0 and 1.\n"
    #                 "If 'result' is 'partially' or 'entirely', provide an array of objects in 'details', "
    #                 "each with 'capability' and 'explanation'.\n"
    #                 f"{reply_language}"
    #             )
    #         }

    #         # 🔹 Création du message utilisateur contenant les sous-tâches à résoudre
    #         user_message = {
    #             "role": "user",
    #             "content": f"Here are the tasks that need to be solved:\n```json\n{subtasks_str}\n```\n\nCan I solve them?"
    #         }

    #         return [system_message, user_message]

    #     async def evaluate_general(general: General, subtasks: Dict):
    #         """Helper function to evaluate a general asynchronously."""
    #         print('evaluate', general.my_name_is)

    #         # Construire le prompt à l'aide de la méthode de la CommandChain
    #         prompt = build_capabilities_prompt_for_general(general, subtasks)
            
    #         try:
    #             # Obtenir la réponse du modèle
    #             response = await self.nlp_model.chat_completion(
    #                 prompt, tools=[], response_format={"type": "json_object"}
    #             )
    #             message = response.message
                
    #             # Analyser la réponse du modèle
    #             evaluation = json.loads(getattr(message, "content", "{}"))
                
    #             # Extraire les détails de l'évaluation
    #             result = evaluation.get("result")
    #             confidence = evaluation.get("confidence", 0)
    #             details = evaluation.get("details", [])
    #             task.add_step(GeneralEvaluationStep(request_id=len(task.steps) + 1, general=general.my_name_is, evaluation=getattr(message, "content", "{}"), metadata={"general": general.my_name_is, "evaluation": evaluation}))
                
    #             await self.event_manager.publish(Event(EventType.TASK_UPDATED, f"Task has been evaluated by {general.my_name_is}.", task.task_id, details=task.to_dict()))
                
    #             # Retourner le résultat de l'évaluation
    #             return general, result, confidence, details
                
    #         except json.JSONDecodeError as e:
    #             self.logger.error(f"Failed to decode JSON response: {response}")
    #             raise TaskExecutionError(f"Failed to decode JSON response: {response}") from e
    #         except Exception as e:
    #             self.logger.error(f"An error occurred while evaluating the task: {str(e)}")
    #             raise TaskExecutionError(f"An error occurred while evaluating the task: {str(e)}") from e


    #     # Run evaluations in parallel for all generals
    #     evaluations = await asyncio.gather(*(evaluate_general(g, subtasks=subtasks) for g in generals))
        
    #     # Process evaluations
    #     for general, result, confidence, details in evaluations:
    #         if result == "entirely" or result == "partially":
    #             # Collect generals who are partially capable
    #             #print(general.my_name_is, result, confidence, details, "\n")
    #             selected_generals.append(general)
    #             general_capabilities.append({
    #                 "general": general,
    #                 "confidence": confidence,
    #                 "capabilities": {detail.get("capability") for detail in details},
    #                 "details": details
    #             })
    #             # Update combined capabilities
    #             combined_capabilities.update({detail.get("capability") for detail in details})

    #     # Check combined capabilities after evaluating all generals
    #     if len(selected_generals) > 0:
    #         # Construire confidence_capabilities directement
    #         confidence_capabilities = {
    #             cap: max(
    #                 float(info["confidence"])  # Utiliser la confiance individuelle
    #                 for info in general_capabilities
    #                 if cap in info["capabilities"]
    #             )
    #             for cap in combined_capabilities
    #         }

    #         # Calculer combined_confidence
    #         combined_confidence = sum(confidence_capabilities.values()) / len(confidence_capabilities)

    #         if combined_confidence >= self.confidence_threshold:
    #                 # Calculer les contributions
    #             general_contributions = []
    #             for general_info in general_capabilities:
    #                 capabilities = general_info["capabilities"]
    #                 contribution_score = sum([
    #                     float(confidence_capabilities.get(cap, 0))  # Utilise confidence_capabilities
    #                     for cap in capabilities
    #                 ]) / len(combined_capabilities)
    #                 general_contributions.append({
    #                     "general": general_info["general"],
    #                     "contribution_score": contribution_score,
    #                     "details": general_info["details"],
    #                     "confidence": general_info["confidence"]
    #                 })

    #             # Sélectionner le meilleur général comme Dictateur
    #             best_general = max(general_contributions, key=lambda x: x["contribution_score"])
    #             dictator = best_general["general"]
    #             other_generals = [g["general"] for g in general_contributions if g["general"] != dictator]
    #             task.add_metadata('selected_dictator', dictator.my_name_is)
    #             task.add_metadata('general_contributions', [general["general"].my_name_is for general in general_contributions])
    #             self.logger.info(general_capabilities)
    #             return dictator, other_generals, task

    #     clarification_request= ""
    #     async for chunk in majordomo.solve_task(task):
    #         clarification_request += chunk
        
    #     # Si aucun groupe de généraux ne peut résoudre la tâche
    #     raise TaskExecutionError(message="No group of generals is capable of executing the task.", clarification_request=clarification_request)
    
    async def solve_task(
        self,
        dictator: AssignedGeneral,
        generals: List[AssignedGeneral],
        task: Task
    ) -> AsyncGenerator[str, None]:
        """
        Executes the task-solving process, either by the dictator alone or with the help of generals.

        Args:
            dictator (General): The selected dictator.
            generals (List[General]): A list of generals assisting the dictator.
            task (str): The task to solve.

        Yields:
            str: Chunks of the task-solving process, if successful.
        """
        if not generals:
            self.logger.debug(f"{dictator.my_name_is} is solving the task alone.\n")
            
            async for chunk in dictator.solve_task(task):
                yield chunk
            
        else:
            general_names = ", ".join([assignedGeneral.my_name_is for assignedGeneral in generals])
            self.logger.debug(f"Dictator {dictator.my_name_is} will solve the task with the following generals: {general_names}.\n")
            async for chunk in self.conversation.start_conversation(dictator, generals, task):
                yield chunk

    def build_task_decomposition_prompt(self, task: Task) -> str:
        """
        Construit le prompt pour analyser une requête juridique et la décomposer en sous-problèmes distincts.
        
        :param conversation_history: Historique des derniers échanges entre l'utilisateur et l'assistant juridique.
        :param user_request: La requête juridique de l'utilisateur.
        :return: Un prompt structuré pour une IA d'analyse juridique.
        """
        conversation_history = [
            {"role": step.role, "content": step.content}
            for step in task.steps
            if step.step_type in ("user_message", "assistant_message")  # ✅ Filtrage des messages utiles
        ]

        # 🔹 Conversion en JSON formaté
        formatted_history = json.dumps(conversation_history, ensure_ascii=False, indent=2)

        prompt_template = f"""
    # Contexte
    Tu es un assistant juridique expert dans la planification et la structuration des dossiers juridiques.  
    Ton rôle est d’analyser la demande utilisateur qui est une **requête juridique** et son contexte afin de la décomposer en **sous-problèmes juridiques distincts**.

    # Historique de la conversation
    Voici les échanges récents entre l’utilisateur et l’assistant juridique :  
    {formatted_history}

    # Objectif
    Décompose la demande utilisateur en plusieurs sous-tâches juridiques et attribue chaque sous-tâche à un **expert juridique spécialisé**.  
    Si certaines parties nécessitent une expertise particulière, précise **le domaine du droit applicable**.

    # Format attendu (JSON)
    Retourne une réponse sous le format suivant :
    {{
    "main_legal_issue": "Résumé global de la problématique juridique",
    "subtasks": [
        {{
        "id": 1,
        "description": "Première sous-tâche juridique à résoudre",
        "required_expert": "Nom du spécialiste en droit concerné",
        "applicable_law": "Code ou loi applicable"
        }},
        {{
        "id": 2,
        "description": "Deuxième sous-tâche juridique",
        "required_expert": "Nom du spécialiste en droit concerné",
        "applicable_law": "Code ou loi applicable"
        }}
    ]
    }}
        """
        return prompt_template.strip()
