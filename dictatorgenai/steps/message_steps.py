from .base_step import TaskStep
from typing import Dict, Optional

@TaskStep.register_step("user_message")
class UserMessageStep(TaskStep):
    def __init__(self, request_id: str, content: str, metadata: Optional[Dict[str, object]] = None):
        super().__init__(request_id, "user_message", metadata)
        self.role = "user"
        self.content = content

    def to_dict(self) -> Dict[str, object]:
        data = super().to_dict()
        data.update({"role": self.role, "content": self.content})
        return data

@TaskStep.register_step("assistant_message")
class AssistantMessageStep(TaskStep):
    def __init__(self, request_id: str, content: str, metadata: Optional[Dict[str, object]] = None):
        super().__init__(request_id, "assistant_message", metadata)
        self.role = "assistant"
        self.content = content

    def to_dict(self) -> Dict[str, object]:
        data = super().to_dict()
        data.update({"role": self.role, "content": self.content})
        return data
