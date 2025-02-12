from typing import Any, AsyncGenerator, Dict, Generator, List
import logging
import asyncio
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
        The dictator sends an imperative message to all the generals asynchronously,
        gathers their responses in parallel, and then uses the input to resolve the task.
        """
        try:
            async def send_command_to_general(general: General):
                """Envoie une commande à un général et récupère sa réponse."""
                try:
                    # Obtenir les capacités pertinentes du général pour la tâche
                    general_relevant_capabilities = self.get_general_relevant_capabilities(general, task)

                    # Vérifier si le général n'a aucune capacité pertinente pour la tâche
                    if not general_relevant_capabilities:
                        logger.debug(f"General {general.my_name_is} has no relevant capabilities for this task.")
                        return None  # Retourne None pour les généraux non pertinents

                    # Générer une liste de capacités sous forme de texte
                    selected_capabilities = [
                        f"{cap['capability']} (Explanation: {cap['explanation']} Confidence: {cap['confidence']})"
                        for cap in general_relevant_capabilities
                    ]
                    selected_capabilities_str = "\n- ".join(selected_capabilities)
                    print(selected_capabilities_str, "\n")
                    # Construire le message impératif
                    imperative_message = (
                        f"I am {dictator.my_name_is}, and I have selected you, {general.my_name_is}, "
                        f"to assist with the task: '{task.request}'.\n"
                        f"You have been chosen based on the following capabilities:\n"
                        f"- {selected_capabilities_str}.\n\n"
                        f"Focus strictly on these capabilities and their details, and provide your input accordingly. "
                        f"Ignore any aspect of the task that falls outside your expertise."
                    )

                    logger.debug(f"Sending command to General {general.my_name_is}...\n")

                    # Envoyer le message au général (appel asynchrone)
                    response_content = await dictator.send_message(general, imperative_message, task=task)
                    print(f"General {general.my_name_is}'s response: {response_content}\n")
                    logger.debug(f"General {general.my_name_is}'s response: {response_content}\n")

                    # Retourner la réponse sous forme d'objet
                    return {
                        "general": general.my_name_is,
                        "content": response_content,
                        "capabilities_used": general_relevant_capabilities
                    }

                except Exception as e:
                    logger.error(f"Error while communicating with General {general.my_name_is}: {e}")
                    return {
                        "general": general.my_name_is,
                        "content": f"Error: {str(e)}",
                        "capabilities_used": []
                    }

            # ✅ Exécuter toutes les commandes en parallèle avec `asyncio.gather`
            responses = await asyncio.gather(
                *[send_command_to_general(general) for general in generals],
                return_exceptions=True  # ✅ Évite de planter si une erreur survient
            )

            # ✅ Filtrer les réponses valides (exclure `None` pour les généraux non pertinents)
            responses = [resp for resp in responses if resp is not None]

            # ✅ Ajouter les réponses dans le contexte de la tâche
            for response in responses:
                task.context.append({
                    "role": "assistant",
                    "content": response["content"],
                    "metadata": {
                        "general": response["general"],
                        "capabilities_used": response["capabilities_used"]
                    }
                })

            # ✅ Le dictateur utilise maintenant les réponses pour finaliser la tâche
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

