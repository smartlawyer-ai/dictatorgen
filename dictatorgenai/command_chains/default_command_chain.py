import json
import logging
from typing import Dict, Generator, List, Tuple
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

    def __init__(self, nlp_model: BaseModel):
        """
        Initializes the DefaultCommandChain with the given NLP model.

        Args:
            nlp_model (BaseModel): An instance of the BaseModel to be used for task decomposition and solution.
        """
        super().__init__(None)
        self.nlp_model = nlp_model
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def build_capabilities_cover_task_prompt(self, task: str, capabilities: List[str]) -> List[Message]:
        """
        Builds a prompt for the NLP model to determine if the combined capabilities can solve the task.

        Args:
            task (str): The task to solve.
            capabilities (List[str]): A list of capabilities from the generals.

        Returns:
            List[Message]: A list of messages to prompt the NLP model for the task evaluation.
        """
        capabilities_str = ", ".join(capabilities)
        messages = [
            {
                "role": "system",
                "content": (
                    "Your goal is to determine if the given capabilities from agents are able to solve the given task. "
                    "Format the response as JSON with a result that equals 'true' or 'false' and a confidence by capability.\n"
                    "If sum of confidence is equal or greater than 1 reply with result true.\n"
                    "Here is an example of the expected JSON result:\n"
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
    
    def capabilities_cover_task(self, combined_capabilities: set, task: str) -> Dict:
        """
        Checks if the combined capabilities of generals can cover the task requirements by prompting the NLP model.

        Args:
            combined_capabilities (set): A set of capabilities from the generals.
            task (str): The task to solve.

        Returns:
            Dict: The result from the NLP model containing a boolean result and confidence levels.

        Raises:
            TaskExecutionError: If the NLP model fails to return a valid JSON response.
        """
        prompt = self.build_capabilities_cover_task_prompt(task, list(combined_capabilities))
    
        try:
            evaluation_str = self.nlp_model.chat_completion(
                prompt, response_format={"type": "json_object"}
            )
            evaluation = json.loads(evaluation_str)
            self.logger.debug(
                f"Evaluating generals can cover tasks together: {task} - Result: {evaluation}"
            )
            return evaluation
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {evaluation_str}")
            raise TaskExecutionError(
                f"Failed to decode JSON response: {evaluation_str}"
            ) from e
        except Exception as e:
            self.logger.error(f"An error occurred while evaluating the task: {str(e)}")
            raise TaskExecutionError(
                f"An error occurred while evaluating the task: {str(e)}"
            ) from e

    def _select_dictator_and_generals(self, generals: List[General], task: str) -> Tuple[General, List[General]]:
        """
        Selects the dictator and the generals that will contribute to solving the task.

        Args:
            generals (List[General]): A list of available generals.
            task (str): The task to solve.

        Returns:
            Tuple[General, List[General]]: A tuple containing the selected dictator and the list of generals assisting.

        Raises:
            TaskExecutionError: If no combination of generals can solve the task.
        """
        selected_generals = []
        combined_capabilities = set()
        general_capabilities = []
        
        for general in generals:
            capability_level = general.can_execute_task(task)
            result = capability_level.get("result")
            confidence = capability_level.get("confidence", 0)
            details = capability_level.get("details", [])
            
            if result == "entirely":
                # General capable of solving the task entirely
                dictator = general
                return dictator, []
            
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
                # We need minimum two generals to check capabilities task solvability
                if len(selected_generals) > 1:
                    # Check if the combined capabilities cover the task requirements
                    capabilities_check = self.capabilities_cover_task(combined_capabilities, task)
                    # Extract the result and confidence levels
                    if capabilities_check["result"] == "true":
                        # Calculate the contribution of each general to the overall task solution
                        general_contributions = []
                        for general in general_capabilities:
                            capabilities = general["capabilities"]
                            confidence = general["confidence"]
                            contribution_score = sum([float(capabilities_check["confidence_capabilities"].get(cap, 0)) for cap in capabilities])
                            general_contributions.append({
                                "general": general["general"],
                                "contribution_score": contribution_score,
                                "confidence": confidence
                            })

                        # Select the general with the highest contribution as the Dictator
                        best_general = max(general_contributions, key=lambda x: x["contribution_score"])
                        dictator = best_general["general"]
                        other_generals = [g["general"] for g in general_contributions if g["general"] != dictator]

                        # Return the Dictator and other generals
                        return dictator, other_generals

        # If no group of generals can solve the task
        raise TaskExecutionError("No group of generals is capable of executing the task.")


    def solve_task(
        self,
        dictator: General,
        generals: List[General],
        task: str
    ) -> Generator[str, None, None]:
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
            # The Dictator solves the task alone
            self.logger.debug(
                f"{dictator.my_name_is} is solving the task alone.\n"
            )
            yield from dictator.solve_task(task)
        else:
            # Prepare a list of general names
            general_names = ", ".join([general.my_name_is for general in generals])
            
            # Announce that the Dictator will solve the task with the generals
            self.logger.debug(
                f"Dictator {dictator.my_name_is} will solve the task with the following generals: {general_names}.\n"
            )
            
            # Collective task-solving process
            yield from self.conversation.start_conversation(dictator, generals, task)
