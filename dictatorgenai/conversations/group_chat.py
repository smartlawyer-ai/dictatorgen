from typing import Any, AsyncGenerator, Dict, Generator, List
import logging

from dictatorgenai.agents.general import General
from dictatorgenai.utils.task import Task
from .base_conversation import BaseConversation
# Configuration du logger
logger = logging.getLogger(__name__)

class GroupChat(BaseConversation):
    async def start_conversation(
        self, dictator: General, generals: List[General], task: Task
    ) -> AsyncGenerator[str, None]:
        """
        The dictator sends an imperative message to all the generals,
        validates their responses, and then uses the input to resolve the task.
        """
        try:
            
            responses = []
            for general in generals:
                try:
                    # Obtenir les capacités pertinentes du général pour la tâche
                    general_relevant_capabilities = self.get_general_relevant_capabilities(general, task)
                    
                    # Vérifier si le général n'a aucune capacité pertinente pour la tâche
                    if not general_relevant_capabilities:
                        logger.debug(f"General {general.my_name_is} has no relevant capabilities for this task.")
                        continue
                    
                    # Générer une liste de capacités sous forme de texte
                    selected_capabilities = [
                        f"{cap['capability']} (Explanation : {cap['explanation']} Confidence: {cap['confidence']})" 
                        for cap in general_relevant_capabilities
                    ]
                    selected_capabilities_str = "\n- ".join(selected_capabilities)

                    # Construire le message impératif
                    imperative_message = (
                        f"I am {dictator.my_name_is}, and I have selected you, {general.my_name_is}, to assist with the task: '{task.request}'.\n"
                        f"You have been chosen based on the following capabilities:\n"
                        f"- {selected_capabilities_str}.\n\n"
                        f"Focus strictly on these capabilities and their details, and provide your input accordingly. "
                        f"Ignore any aspect of the task that falls outside your expertise."
                    )
                    
                    logger.debug(f"Sending command to General {general.my_name_is}...\n")
                    
                    # Envoyer le message au général
                    response_content = await dictator.send_message(general, imperative_message, task=task)
                    
                    logger.debug(f"General {general.my_name_is}'s response: {response_content}\n")
                    
                    # Ajouter la réponse au tableau des réponses
                    task.context.append({
                        "role": "assistant",
                        "content": response_content,
                        "metadata": {
                            "general": general.my_name_is,
                            "capabilities_used": general_relevant_capabilities
                        }
                    })
                except Exception as e:
                    # Gérer les erreurs et enregistrer la réponse d'erreur
                    logger.error(f"Error while communicating with General {general.my_name_is}: {e}")
                    responses.append({
                        "general": general.my_name_is,
                        "content": f"Error: {str(e)}",
                        "capabilities_used": []
                    })

            # Step 4: Dictator uses the responses to finalize the task resolution
            logger.debug(f"Dictator {dictator.my_name_is} is now resolving the task based on the responses...\n")
            async for chunk in dictator.solve_task(task):
                yield chunk

        except Exception as e:
            logger.error(f"An error occurred during the conversation: {e}")
            yield f"An error occurred: {e}"

    
    def get_general_relevant_capabilities(self, general, task) -> List[Dict[str, Any]]:
        """
        Extracts the relevant capabilities of a specific general for a given task.

        Args:
            general (General): The general whose capabilities are being queried.
            task (Task): The task object containing metadata about general contributions.

        Returns:
            List[Dict[str, Any]]: A list of relevant capabilities and their details for the general.
        """
        # Check if general_contributions metadata exists in the task
        if not hasattr(task, "metadata") or "general_contributions" not in task.metadata:
            raise ValueError("The task does not contain 'general_contributions' metadata.")

        general_contributions = task.metadata["general_contributions"]
        relevant_capabilities = []

        # Find the entry for the specified general
        for contribution in general_contributions:
            contribution_general = contribution["general"]
            if contribution_general == general or getattr(contribution_general, "my_name_is", None) == general.my_name_is:
                # Extract the relevant details for this general
                for detail in contribution.get("details", []):
                    relevant_capabilities.append({
                        "capability": detail.get("capability"),
                        "explanation": detail.get("explanation", "No explanation provided"),
                        "confidence": contribution.get("confidence", 0.0)
                    })
                break  # No need to check further once the general is found

        return relevant_capabilities

