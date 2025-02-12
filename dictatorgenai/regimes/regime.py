import asyncio
import uuid
import logging
import time
from typing import AsyncGenerator, Dict, List, Callable, Any, Generator
from dictatorgenai.memories.chat_discussion import ChatDiscussion
from dictatorgenai.memories.sql_ite_chat_memory import SQLiteChatMemory
from dictatorgenai.models import BaseModel, Message
from dictatorgenai.command_chains import CommandChain, DefaultCommandChain
from dictatorgenai.agents import General, TaskExecutionError
from dictatorgenai.events import BaseEventManager, EventManager, Event
from dictatorgenai.utils.task import Task
from .base_regime import BaseRegime

class RegimeExecutionError(TaskExecutionError):
    """
    Raised when the entire regime fails to perform the task.
    """
    pass


class Regime(BaseRegime):
    """
    A concrete implementation of the BaseRegime class. It handles the execution of tasks
    by delegating them to generals (agents), managing event notifications, and handling
    the transition of power (coup d'état) if necessary.

    Attributes:
        nlp_model (BaseModel): The NLP model used for processing tasks.
        government_prompt (str): The regime's central objective or task.
        generals (List[General]): A list of generals (agents) available to the regime.
        dictator (General): The general currently leading the task.
        command_chain (CommandChain): The command chain responsible for delegating tasks.
        event_manager (BaseEventManager): Handles event notifications and subscriptions.
        memory (ChatDiscussion): Memory for storing past messages and events.
    """

    def __init__(
        self,
        nlp_model: BaseModel,
        government_prompt: str,
        generals: List[General],
        command_chain: CommandChain = None,
        event_manager: BaseEventManager = None,
        memory: ChatDiscussion = None, 
    ):
        """
        Initializes the Regime with the given NLP model, list of generals, and optional command chain
        and event manager.

        Args:
            nlp_model (BaseModel): The NLP model used for task execution and communication.
            government_prompt (str): The central prompt or objective for the regime.
            generals (List[General]): A list of generals (agents) under the regime's control.
            command_chain (CommandChain, optional): The command chain used to delegate tasks. Defaults to DefaultCommandChain.
            event_manager (BaseEventManager, optional): The event manager for handling event notifications. Defaults to EventManager.
            memory (ChatDiscussion, optional): The chat discussion memory backend. Defaults to SQLiteMemory.
        """
        super().__init__(nlp_model, government_prompt, generals, command_chain or DefaultCommandChain(nlp_model, confidence_threshold=0.6), event_manager or EventManager())
        self.logger = logging.getLogger(self.__class__.__name__)
        memory_id = f"regime_{uuid.uuid4().hex[:8]}"
        self.memory = memory or ChatDiscussion(memory_id=memory_id, memory=SQLiteChatMemory(db_path="regime_memory.db"))

    async def chat(self, request: str) -> AsyncGenerator[str, None]:
        """
        Orchestrates the execution of the task, handling event notifications and managing
        the generals assigned to complete the task.

        Args:
            task (str): The task to execute.

        Yields:
            str: Chunks of the task solution as the generals work to resolve it.

        Raises:
            RegimeExecutionError: If all generals fail to complete the task.
        """
       
        start_time = time.time()
        print(self.memory.get_messages())
        task = Task(request=request, context=self.memory.get_messages())
        await self.publish("task_started", task.task_id, "System", f"Starting task: {task}")

        
        try:
            # Use 'prepare_task_execution' to get the dictator, assisting generals, and the execution function
            dictator, generals_to_use, execute_task = await self.command_chain.prepare_task_execution(
                self.generals, 
                task,
            )
        except TaskExecutionError as e:
            end_time = time.time()
            await self.publish(
                "task_failed",
                task.task_id,
                "System",
                f"Task '{task}' failed to start due to: {e.clarification_request}",
            )
            self.memory.add_message({"role": "user", "content": task.request})
            self.memory.add_message({"role": "assistant", "content": e.clarification_request})
            yield e.clarification_request
            return
        if dictator:
            try:
                # Perform a coup if necessary
                await self.perform_coup(general=dictator, generals_to_use=generals_to_use)

                if len(generals_to_use) > 0:
                    # Notify that the dictator is solving the task with help
                    generals_names = ", ".join([general.my_name_is for general in generals_to_use])
                    await self.publish(
                        "task_update",
                        task.task_id,
                        dictator.my_name_is,
                        f"General {dictator.my_name_is} is attempting to solve the task with the help of: {generals_names}",
                        details={"task": task.task_id, "generals_assisting": generals_names}
                    )
                else:
                    # Notify that the dictator is solving the task alone
                    await self.publish(
                        "task_update",
                        task.task_id,
                        dictator.my_name_is,
                        f"General {dictator.my_name_is} is attempting to solve the task alone.",
                        details={"task": task.task_id}
                    )

                # Execute the task and stream results
                result_generator = execute_task()  # Pas besoin d'attendre ici
                result = ""
                
                async for chunk in result_generator:
                    result += chunk
                    yield chunk

                self.memory.add_message({"role": "user", "content": task.request})
                self.memory.add_message({"role": "assistant", "content": result})
                
                await self.publish(
                    "task_completed",
                    task.task_id,
                    dictator.my_name_is,
                    f"General {dictator.my_name_is} solved the task",
                    details={"result": result}
                )
                end_time = time.time()
                return
            except TaskExecutionError:
                await self.publish(
                    "task_failed",
                    task.task_id,
                    dictator.my_name_is,
                    f"General {dictator.my_name_is} failed to complete the task.",
                )

        end_time = time.time()
        await self.publish(
            "task_failed",
            task.task_id,
            "System",
            f"Task '{task}' failed to complete in {end_time - start_time:.2f} seconds.",
        )

        raise RegimeExecutionError(
            f"All capable generals failed to execute the task: {task}"
        )

    async def perform_coup(self, general: General, generals_to_use: List[General] = None):
        """
        Handles the power transition (coup d'état) when a general takes over as dictator.
        Also rearranges the list of generals, placing the dictator and assisting generals at the top.

        Args:
            general (General): The general executing the coup.
            generals_to_use (List[General], optional): List of generals assisting the dictator.
        """
        if general != self.dictator:
            previous_dictator = self.dictator  # Save the previous dictator for event details

            # Remove the general and place them at the top of the generals list
            if general in self.generals:
                self.generals.remove(general)
            self.generals.insert(0, general)  # Dictator is placed at the top
            self.dictator = general
            general.perform_coup_detat(True)

            # Handle assisting generals
            if generals_to_use:
                for assisting_general in generals_to_use:
                    assisting_general.perform_coup_detat(False)
                    if assisting_general in self.generals:
                        self.generals.remove(assisting_general)  # Remove from current position
                    self.generals.insert(1, assisting_general)  # Place after the dictator
            # Log the coup d'état
            self.logger.debug(f"{general.my_name_is} is performing a coup d'état and becoming the new dictator.")

            # Publish a 'coup_d_etat' event
            await self.publish(
                event_type="coup_d_etat",
                task_id="system",  # Use 'system' because it's not part of an active task
                agent=general.my_name_is,  # Name of the general performing the coup
                message=f"{general.my_name_is} has performed a coup d'état and is now the dictator.",
                details={"previous_dictator": previous_dictator.my_name_is if previous_dictator else "None",
                         "assisting_generals": [gen.my_name_is for gen in generals_to_use] if generals_to_use else []}
            )
