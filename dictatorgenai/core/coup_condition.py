class CoupCondition:
    def can_perform_coup(self, general):
        raise NotImplementedError("Subclasses should implement this method")


class FailedAttemptsCondition(CoupCondition):
    def __init__(self, threshold):
        self.threshold = threshold

    def can_perform_coup(self, general):
        return general.failed_attempts >= self.threshold


class SpecificTaskFailureCondition(CoupCondition):
    def __init__(self, failing_task):
        self.failing_task = failing_task

    def can_perform_coup(self, general):
        return general.last_failed_task == self.failing_task
