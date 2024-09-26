import logging
import time
from typing import List, Callable, Any, Generator
from dictatorgenai.models import NLPModel, Message
from .command_chain import CommandChain
from .default_command_chain import DefaultCommandChain
from .general import General, TaskExecutionError
from .base_event_manager import BaseEventManager
from .event_manager import EventManager


class RegimeExecutionError(TaskExecutionError):
    """Raised when the entire regime cannot perform the task"""
    pass


class Regime:
    def __init__(
        self,
        nlp_model: NLPModel,
        government_prompt: str,
        generals: List[General],
        command_chain: CommandChain = None,
        event_manager: BaseEventManager = None,
    ):
        self.nlp_model = nlp_model
        self.government_prompt = government_prompt
        self.generals = generals
        self.dictator = None
        self.command_chain = command_chain if command_chain else DefaultCommandChain()
        self.event_manager = event_manager if event_manager else EventManager()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.memory: List[Message] = []

    def subscribe(self, event_type: str, listener: Callable[[Any], None]):
        self.event_manager.subscribe(event_type, listener)

    def publish(self, event_type: str, message: str):
        self.event_manager.publish(event_type, message)

    def add_to_memory(self, message: Message):
        self.memory.append(message)

    def run(self, task: str) -> Generator[str, None, None]:
        start_time = time.time()
        try:
            # Utiliser 'prepare_task_execution' pour obtenir le dictateur, les généraux et la fonction 'execute_task'
            dictator, generals_to_use, execute_task = self.command_chain.prepare_task_execution(
                self.generals, task
            )
        except TaskExecutionError as e:
            self.publish("task_failed", str(e))
            end_time = time.time()
            self.publish(
                "task_failed",
                f"Task '{task}' failed to start due to: {e}",
            )
            raise RegimeExecutionError(
                f"All generals are incapable of executing the task: {task}"
            ) from e

        self.publish("task_started", f"Starting task: {task}")
        self.add_to_memory({"role": "user", "content": task})

        if dictator and generals_to_use:
            try:
                self.perform_coup(general=dictator)
                self.publish(
                    "task_update",
                    f"General {dictator.my_name_is} is attempting to solve the task: {task}",
                )
                # Exécuter la tâche en utilisant 'execute_task'
                result_generator = execute_task()
                result = ""
                for chunk in result_generator:
                    result += chunk
                    yield chunk
                self.add_to_memory({"role": "assistant", "content": result})
                self.publish(
                    "task_completed",
                    f"General {dictator.my_name_is} solved the task: {result}",
                )
                end_time = time.time()
                return
            except TaskExecutionError:
                self.publish(
                    "task_failed",
                    f"General {dictator.my_name_is} failed to complete the task.",
                )

        end_time = time.time()
        self.publish(
            "task_failed",
            f"Task '{task}' failed to complete in {end_time - start_time:.2f} seconds.",
        )

        raise RegimeExecutionError(
            f"All capable generals failed to execute the task: {task}"
        )

    def perform_coup(self, general):
        if general != self.dictator:
            self.generals.remove(general)
            self.generals.insert(0, general)
            self.dictator = general
            self.logger.info(
                f"{general.my_name_is} is performing a coup d'état and becoming the new dictator."
            )
            return general
