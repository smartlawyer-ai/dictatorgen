from abc import ABC, abstractmethod
from typing import TypedDict, List, Dict, Generator, Any


class Message(TypedDict):
    role: str
    content: str


class Tool(TypedDict):
    name: str
    description: str
    parameters: Dict[str, Any]  # Schéma JSON pour les paramètres de l'outil


class BaseModel(ABC):
    @abstractmethod
    async def chat_completion(
        self, messages: List[Message], tools: List[Tool] = None
    ) -> str:
        """
        Gère une complétion de chat avec support optionnel des tools.
        
        Args:
            messages (List[Message]): Historique des messages pour le modèle.
            tools (List[Tool], optional): Liste des outils disponibles avec leurs schémas JSON.
        
        Returns:
            str: La réponse du modèle.
        """
        pass

    @abstractmethod
    async def stream_chat_completion(
        self, messages: List[Message], tools: List[Tool] = None, **kwargs: Any
    ) -> Generator[str, None, None]:
        """
        Gère une complétion de chat en streaming avec support des tools.
        
        Args:
            messages (List[Message]): Historique des messages pour le modèle.
            tools (List[Tool], optional): Liste des outils disponibles avec leurs schémas JSON.
        
        Yields:
            str: Un morceau de la réponse générée par le modèle.
        """
        pass
