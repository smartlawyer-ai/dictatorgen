from .general import General


class Dictator:
    def __init__(self, general: General, government_prompt: str):
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
        return self.general.run(task)

    def can_execute_task(self, task):
        return self.general.can_execute_task(task)

    def solve_task(self, task):
        return self.general.solve_task(task)

    def can_perform_coup(self) -> bool:
        return self.general.can_perform_coup()

    def report_failure(self, task=None):
        return self.general.report_failure(task)
