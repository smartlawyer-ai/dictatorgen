from openai import OpenAI
from .nlp_model import Message, NLPModel
from typing import Any, Generator, List


class GPT3Model(NLPModel):
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def chat_completion(self, messages, **kwargs: Any):
        completion_args = {
            "model": "gpt-4o",
            "messages": messages,
        }
        if "response_format" in kwargs:
            completion_args["response_format"] = kwargs.pop("response_format")

        # Sinon, obtenir la réponse complète
        completion = self.client.chat.completions.create(**completion_args)
        return completion.choices[0].message.content.strip()

    def stream_chat_completion(
        self, messages: List[Message], **kwargs: Any
    ) -> Generator[str, None, None]:
        completion_args = {"model": "gpt-4o", "messages": messages, "stream": True}
        # Si le streaming est activé, gérer les réponses en streaming
        completion_args["stream"] = True

        stream = self.client.chat.completions.create(**completion_args)
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
