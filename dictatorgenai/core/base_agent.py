from abc import ABC, abstractmethod
from typing import Dict


class TaskExecutionError(Exception):
    pass


class BaseAgent(ABC):
    def __init__(self, my_name_is: str):
        self.my_name_is = my_name_is
        self.failed_attempts = 0

    @abstractmethod
    def can_execute_task(self, task: str) -> Dict:
        pass

    @abstractmethod
    def solve_task(self, task: str) -> str:
        pass

    @abstractmethod
    def can_perform_coup(self) -> bool:
        pass

    def report_failure(self, task: str = None):
        self.failed_attempts += 1
        if task:
            self.logger.warning(f"Failed task: {task}")
