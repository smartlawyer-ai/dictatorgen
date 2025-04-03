import asyncio
import uuid
import logging
import time
import json
from typing import AsyncGenerator, Dict, List, Optional

from dictatorgenai.models import BaseModel, Message
from dictatorgenai.command_chains import CommandChain, DefaultCommandChain
from dictatorgenai.agents import General, TaskExecutionError
from dictatorgenai.events import BaseEventManager, EventManager, EventType, Event
from dictatorgenai.utils.task import Task
from .base_regime import BaseRegime
from dictatorgenai.memories.regime_memory import RegimeMemory
from dictatorgenai.memories.stores.sqlite_store import SQLiteStore
from dictatorgenai.steps.message_steps import UserMessageStep
from dictatorgenai.steps.action_steps import GeneralSelectionStep, CoupDEtatStep, ActionStep


class RegimeExecutionError(TaskExecutionError):
    """Raised when the entire regime fails to perform the task."""
    pass


class Regime(BaseRegime):
    """
    Gère l'exécution des tâches en délégant aux généraux, en traquant les décisions et les résultats dans `RegimeMemory`.
    """

    def __init__(
        self,
        nlp_model: BaseModel,
        government_prompt: str,
        generals: List[General],
        memory_id: Optional[str] = None,  # ✅ Ajout d'un paramètre memory_id
        command_chain: CommandChain = None,
        event_manager: BaseEventManager = None,
        memory_store: Optional[SQLiteStore] = None,
    ):
        """
        Initialise un régime avec un modèle NLP, des généraux et une mémoire persistante.

        Args:
            nlp_model (BaseModel): Modèle NLP utilisé pour le traitement des tâches.
            government_prompt (str): Objectif principal du régime.
            generals (List[General]): Liste des généraux disponibles.
            memory_id (Optional[str]): Identifiant mémoire pour récupérer une discussion existante.
            command_chain (CommandChain, optional): Chaine de commande pour la gestion des tâches.
            event_manager (BaseEventManager, optional): Gestionnaire d'événements.
            memory_store (Optional[SQLiteStore], optional): Store de mémoire pour la persistance.
        """
        event_manager = event_manager or EventManager()

        super().__init__(
            nlp_model,
            government_prompt,
            generals,
            command_chain or DefaultCommandChain(nlp_model, confidence_threshold=0.6, event_manager=event_manager),
            event_manager
        )

        self.logger = logging.getLogger(self.__class__.__name__)

        # ✅ Si un memory_id est fourni, on le réutilise, sinon on en génère un nouveau
        self.memory_id = memory_id or f"regime_{uuid.uuid4().hex[:8]}"

        # ✅ Initialisation de la mémoire du régime
        self.memory = RegimeMemory(
            memory_id=self.memory_id,
            task=Task(request=government_prompt),
            store=memory_store or SQLiteStore(db_path="regime_store.db")
        )

    async def chat(self, request: str) -> AsyncGenerator[str, None]:
        """
        Gère une discussion utilisateur en traquant chaque étape de raisonnement.

        Args:
            request (str): Requête utilisateur.

        Yields:
            str: Résolution progressive de la tâche.

        Raises:
            RegimeExecutionError: Si tous les généraux échouent.
        """
        start_time = time.time()
        
        task = Task(request=request, steps=self.memory.steps)
        user_step = self.memory.add_user_message(request)
        task.add_step(user_step)
        await self.publish(Event(EventType.TASK_STARTED, f"Starting task", task.task_id, details=task.to_dict()))

        try:
            dictator, generals_to_use, execute_task = await self.command_chain.prepare_task_execution(self.generals, task)
            generals_names = ", ".join([general.my_name_is for general in generals_to_use])
            generals_selection_step = self.memory.select_generals([dictator.my_name_is] + [general.my_name_is for general in generals_to_use])
            task.add_step(GeneralSelectionStep(request_id=len(task.steps) + 1, selected_generals=[dictator.my_name_is] + [general.my_name_is for general in generals_to_use], metadata={"dictator": dictator.my_name_is, "generals": generals_names}))
            await self.publish(Event(EventType.GENERALS_SELECTED, f"Selected generals: {generals_names}", task.task_id, details=task.to_dict()))
            
        except TaskExecutionError as e:
            await self._handle_task_failure(task, e)
            yield e.clarification_request
            return

        if dictator:
            try:
                
                if len(generals_to_use) > 0:
                    self.memory.select_generals([general.my_name_is for general in generals_to_use])
                    await self.perform_coup(dictator, generals_to_use, task=task)
                    # Notify that the dictator is solving the task with help
                    generals_names = ", ".join([general.my_name_is for general in generals_to_use])
                    await self.publish(Event(EventType.TASK_UPDATED, f"General {dictator.my_name_is} is solving the task with help of {generals_names}", task.task_id, details=task.to_dict()))
                    
                else:
                    # Notify that the dictator is solving the task alone
                    self.memory.select_generals([dictator.my_name_is])
                    await self.perform_coup(dictator, task=task)
                    await self.publish(Event(EventType.TASK_UPDATED, f"General {dictator.my_name_is} is solving the task alone", task.task_id, details=task.to_dict()))

                result_generator = execute_task()  # Pas besoin d'attendre ici
                result = ""
                
                async for chunk in result_generator:
                    result += chunk
                    yield chunk

                step = self.memory.add_assistant_message(result)
                task.add_step(step)

                await self.publish(Event(EventType.TASK_COMPLETED, f"Task completed by {dictator.my_name_is}", task.task_id, details=task.to_dict()))
                return
            
            except TaskExecutionError:
                await self.publish(Event(EventType.TASK_FAILED, f"Task failed", task.task_id, details=task.to_dict()))

        await self.publish(Event(EventType.TASK_FAILED, f"Task '{task}' failed in {time.time() - start_time:.2f} seconds.", task.task_id, details=task.to_dict()))
        raise RegimeExecutionError(f"All capable generals failed to execute the task: {task}")


    async def perform_coup(self, general: General, generals_to_use: List[General] = None, task: Optional[Task] = None):
        """
        Gère la transition de pouvoir lorsqu'un général devient dictateur.

        Args:
            general (General): Général prenant le pouvoir.
            generals_to_use (List[General], optional): Généraux assistant.
        """
        if general != self.dictator:
            previous_dictator = self.dictator
            if general in self.generals:
                self.generals.remove(general)
            self.generals.insert(0, general)
            self.dictator = general
            general.perform_coup_detat(True)

            # Ajout des généraux assistants
            if generals_to_use:
                for assisting_general in generals_to_use:
                    assisting_general.perform_coup_detat(False)
                    if assisting_general in self.generals:
                        self.generals.remove(assisting_general)
                    self.generals.insert(1, assisting_general)

            self.logger.debug(f"{general.my_name_is} performed a coup d'état and became the new dictator.")
            await self.publish(Event(EventType.COUP_D_ETAT, f"{general.my_name_is} performed a coup d'état.", task.task_id, details=task.to_dict() if task else None))
            self.memory.coup_detat(new_dictator=general.my_name_is, previous_dictator=previous_dictator.my_name_is if previous_dictator else None)


    async def _handle_task_failure(self, task: Task, error: TaskExecutionError):
        """
        Gère l'échec d'une tâche et enregistre l'erreur en mémoire.

        Args:
            task (Task): Tâche échouée.
            error (TaskExecutionError): Erreur rencontrée.
        """
        await self.publish(Event(EventType.TASK_FAILED, f"Task '{task}' failed: {error.clarification_request}", task.task_id, details=task.to_dict()))
        self.memory.add_action_step("System", "Failure handling", error.clarification_request)

    

