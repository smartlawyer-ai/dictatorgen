import json
import logging
import asyncio
from typing import Dict, AsyncGenerator, List, Tuple
from dictatorgenai.models import BaseModel, Message
from .command_chain import CommandChain
from ..agents.general import General, TaskExecutionError
from dictatorgenai.conversations import BaseConversation

class DefaultCommandChain(CommandChain):
    """
    Default implementation of the CommandChain for managing task execution among generals.
    It uses an NLP model to determine if the generals' combined capabilities can solve a given task.

    Attributes:
        nlp_model (BaseModel): The NLP model used for task decomposition and decision making.
        logger (logging.Logger): Logger for recording debug and error messages.
    """

    def __init__(self, nlp_model: BaseModel, confidence_threshold: float = 1.0):
        super().__init__(None)
        self.nlp_model = nlp_model
        self.logger = logging.getLogger(self.__class__.__name__)
        self.confidence_threshold = confidence_threshold
    
    def build_capabilities_cover_task_prompt(self, task: str, capabilities: List[str]) -> List[Message]:
        capabilities_str = ", ".join(capabilities)
        messages = [
            {
                "role": "system",
                "content": (
                    f"Your goal is to determine if the given capabilities from agents are able to solve the given task. "
                    f"Format the response as JSON with a result that equals 'true' or 'false' and a confidence by capability.\n"
                    f"If sum of confidence is equal or greater than {self.confidence_threshold} reply with result true.\n"
                    f"Here is an example of the expected JSON result:\n"
                    "----------------------\n"
                    '{\n'
                    '  "result": "true",\n'
                    '  "confidence_capabilities": {\n'
                    '    "write_contract": "0.7",\n'
                    '    "reply_with_lawcase": "0.3",\n'
                    '    "speak_french": "0.9"\n'
                    '  }\n'
                    '}\n'
                    "----------------------"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Here are the capabilities:\n"
                    f"-------------------------\n"
                    f"{capabilities_str}\n"
                    f"-------------------------\n"
                    f"Can you solve the following task: {task}?"
                ),
            },
        ]
        return messages

    async def capabilities_cover_task(self, combined_capabilities: set, task: str) -> Dict:
        prompt = self.build_capabilities_cover_task_prompt(task, list(combined_capabilities))
        print('prompt', prompt)
        try:
            response = await self.nlp_model.chat_completion(
                prompt, tools= [], response_format={"type": "json_object"}
            )
            message = response.message
            evaluation = json.loads(getattr(message, "content", None))
            self.logger.debug(
                f"Evaluating generals can cover tasks together: {task} - Result: {evaluation}"
            )
            return evaluation
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {response}")
            raise TaskExecutionError(
                f"Failed to decode JSON response: {response}"
            ) from e
        except Exception as e:
            self.logger.error(f"Default CommandChain : An error occurred while evaluating the task: {str(e)}")
            raise TaskExecutionError(
                f"Default CommandChain : An error occurred while evaluating the task: {str(e)}"
            ) from e

    async def _select_dictator_and_generals(self, generals: List[General], task: str) -> Tuple[General, List[General]]:
        selected_generals = []
        combined_capabilities = set()
        general_capabilities = []

        async def evaluate_general(general: General):
            """Helper function to evaluate a general asynchronously."""
            print('evaluate', general.my_name_is)
            capability_level = await general.can_execute_task(task)
            result = capability_level.get("result")
            confidence = capability_level.get("confidence", 0)
            details = capability_level.get("details", [])
            return general, result, confidence, details

        # Run evaluations in parallel for all generals
        evaluations = await asyncio.gather(*(evaluate_general(g) for g in generals))

        # Process evaluations
        for general, result, confidence, details in evaluations:
            if result == "entirely":
                # If any general can solve the task entirely, select them as Dictator
                return general, []

            elif result == "partially":
                # Collect generals who are partially capable
                selected_generals.append(general)
                general_capabilities.append({
                    "general": general,
                    "confidence": confidence,
                    "capabilities": {detail.get("capability") for detail in details}
                })
                # Update combined capabilities
                combined_capabilities.update({detail.get("capability") for detail in details})

        # Check combined capabilities after evaluating all generals
        if len(selected_generals) > 1:
            # Construire confidence_capabilities directement
            confidence_capabilities = {
                cap: max(
                    float(info["confidence"])  # Utiliser la confiance individuelle
                    for info in general_capabilities
                    if cap in info["capabilities"]
                )
                for cap in combined_capabilities
            }

            # Calculer combined_confidence
            combined_confidence = sum(confidence_capabilities.values()) / len(confidence_capabilities)
            print('confidence', combined_confidence)

            if combined_confidence >= self.confidence_threshold:
                # Calculer les contributions
                general_contributions = []
                for general_info in general_capabilities:
                    capabilities = general_info["capabilities"]
                    contribution_score = sum([
                        float(confidence_capabilities.get(cap, 0))  # Utilise confidence_capabilities
                        for cap in capabilities
                    ]) / len(combined_capabilities)
                    general_contributions.append({
                        "general": general_info["general"],
                        "contribution_score": contribution_score,
                        "confidence": general_info["confidence"]
                    })

                # Sélectionner le meilleur général comme Dictateur
                best_general = max(general_contributions, key=lambda x: x["contribution_score"])
                dictator = best_general["general"]
                other_generals = [g["general"] for g in general_contributions if g["general"] != dictator]

                return dictator, other_generals

        # Si aucun groupe de généraux ne peut résoudre la tâche
        raise TaskExecutionError("No group of generals is capable of executing the task.")



    async def solve_task(
        self,
        dictator: General,
        generals: List[General],
        task: str
    ) -> AsyncGenerator[str, None]:
        """
        Executes the task-solving process, either by the dictator alone or with the help of generals.

        Args:
            dictator (General): The selected dictator.
            generals (List[General]): A list of generals assisting the dictator.
            task (str): The task to solve.

        Yields:
            str: Chunks of the task-solving process, if successful.
        """
        if not generals:
            self.logger.debug(f"{dictator.my_name_is} is solving the task alone.\n")
            print('teub')
            async for chunk in dictator.solve_task(task):
                yield chunk
            print('teub2')
        else:
            general_names = ", ".join([general.my_name_is for general in generals])
            self.logger.debug(f"Dictator {dictator.my_name_is} will solve the task with the following generals: {general_names}.\n")
            async for chunk in self.conversation.start_conversation(dictator, generals, task):
                yield chunk
