from .general import General


class Dictator:
    """
    A class that represents a Dictator in the system, encapsulating a General and inheriting its properties and behavior.
    The Dictator uses the capabilities of the General to execute tasks and manage coups d'état.

    Attributes:
        general (General): The General associated with the Dictator.
        government_prompt (str): The overarching directive or instruction guiding the Dictator.
        name (str): The name of the Dictator, inherited from the General.
        capabilities (list): The capabilities of the Dictator, inherited from the General.
        nlp_model (BaseModel): The NLP model used by the Dictator for task analysis, inherited from the General.
        coup_conditions (list): Conditions under which the Dictator can perform a coup, inherited from the General.
        last_failed_task (str): The last task the Dictator failed, inherited from the General.
        failed_attempts (int): The number of failed task attempts, inherited from the General.
    """

    def __init__(self, general: General, government_prompt: str):
        """
        Initializes the Dictator with a General and a government prompt.

        Args:
            general (General): The General that the Dictator is based on.
            government_prompt (str): The prompt or directive guiding the Dictator's actions.
        """
        self.general = general
        self.government_prompt = government_prompt
        self.name = general.name
        self.capabilities = general.capabilities
        self.nlp_model = general.nlp_model
        self.coup_conditions = (
            general.coup_conditions if general.coup_conditions else []
        )
        self.last_failed_task = general.last_failed_task
        self.failed_attempts = general.failed_attempts

    def run(self, task):
        """
        Executes a task using the Dictator's General.

        Args:
            task (str): The task to be executed.

        Returns:
            Any: The result of the task execution.
        """
        return self.general.run(task)

    # def can_execute_task(self, task):
    #     """
    #     Determines whether the Dictator (via the General) has the capabilities to execute the task.

    #     Args:
    #         task (str): The task to evaluate.

    #     Returns:
    #         Dict: A dictionary indicating the ability to execute the task.
    #     """
    #     return self.general.can_execute_task(task)

    def solve_task(self, task):
        """
        Solves the given task using the Dictator's General.

        Args:
            task (str): The task to be solved.

        Returns:
            str: The result of the task solution.
        """
        return self.general.solve_task(task)

    def can_perform_coup(self) -> bool:
        """
        Checks if the Dictator can perform a coup based on coup conditions.

        Returns:
            bool: True if the Dictator can perform a coup, False otherwise.
        """
        return self.general.can_perform_coup()

    def report_failure(self, task=None):
        """
        Reports a failure for a specific task and increments the failure count.

        Args:
            task (str, optional): The task that failed. If None, a general failure is reported.

        Returns:
            None
        """
        return self.general.report_failure(task)