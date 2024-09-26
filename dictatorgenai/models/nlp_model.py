from abc import ABC, abstractmethod
from typing import TypedDict, List, Generator, Any


class Message(TypedDict):
    role: str
    content: str


class NLPModel(ABC):
    @abstractmethod
    def chat_completion(self, messages: List[Message]) -> str:
        pass

    @abstractmethod
    def stream_chat_completion(
        self, messages: List[Message], **kwargs: Any
    ) -> Generator[str, None, None]:
        pass
