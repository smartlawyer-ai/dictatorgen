from typing import List, Dict, Optional
from .base_step import TaskStep

@TaskStep.register_step("general_selection")
class GeneralSelectionStep(TaskStep):
    def __init__(self, request_id: str, selected_generals: Optional[List[str]] = None, metadata: Optional[Dict[str, object]] = None):
        super().__init__(request_id, "general_selection", metadata)
        self.selected_generals = selected_generals if selected_generals is not None else []

    def to_dict(self) -> Dict[str, object]:
        data = super().to_dict()
        data.update({"selected_generals": self.selected_generals})
        return data

@TaskStep.register_step("coup_d_etat")
class CoupDEtatStep(TaskStep):
    def __init__(self, request_id: str, new_dictator: str, previous_dictator: Optional[str] = None, metadata: Optional[Dict[str, object]] = None):
        super().__init__(request_id, "coup_d_etat", metadata)
        self.new_dictator = new_dictator
        self.previous_dictator = previous_dictator

    def to_dict(self) -> Dict[str, object]:
        data = super().to_dict()
        data.update({"new_dictator": self.new_dictator, "previous_dictator": self.previous_dictator})
        return data

@TaskStep.register_step("general_evaluation")
class GeneralEvaluationStep(TaskStep):
    def __init__(self, request_id: str, general: str, evaluation: str, metadata: Optional[Dict[str, object]] = None):
        super().__init__(request_id, "general_evaluation", metadata)
        self.general = general
        self.evaluation = evaluation

    def to_dict(self) -> Dict[str, object]:
        data = super().to_dict()
        data.update({"general": self.general, "evaluation": self.evaluation})
        return data

@TaskStep.register_step("planning_step")
class PlanningStep(TaskStep):
    def __init__(self, request_id: str, plan: str, metadata: Optional[Dict[str, object]] = None):
        super().__init__(request_id, "planning_step", metadata)
        self.plan = plan

    def to_dict(self) -> Dict[str, object]:
        data = super().to_dict()
        data.update({"plan": self.plan})
        return data

@TaskStep.register_step("action")
class ActionStep(TaskStep):
    def __init__(self, request_id: str, action: str, result: Optional[str] = None, metadata: Optional[Dict[str, object]] = None):
        super().__init__(request_id, "action", metadata)
        self.action = action
        self.result = result

    def to_dict(self) -> Dict[str, object]:
        data = super().to_dict()
        data.update({"action": self.action, "result": self.result})
        return data

@TaskStep.register_step("tool_execution")
class ToolExecutionStep(TaskStep):
    def __init__(
        self,
        request_id: str,
        tool_name: str,
        arguments: Dict[str, object],
        output: Optional[object] = None,
        metadata: Optional[Dict[str, object]] = None
    ):
        super().__init__(request_id, "tool_execution", metadata)
        self.tool_name = tool_name
        self.arguments = arguments
        self.output = output

    def to_dict(self) -> Dict[str, object]:
        data = super().to_dict()
        data.update({
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "output": self.output
        })
        return data

