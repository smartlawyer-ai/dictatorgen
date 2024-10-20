import logging
from typing import List, Dict, Generator, Optional
from .base_agent import BaseAgent
from dictatorgenai.models import BaseModel, Message
import json
import re


class TaskExecutionError(Exception):
    pass


class General(BaseAgent):
    def __init__(
        self,
        my_name_is: str,
        iam: str,
        my_capabilities_are: List[str],
        nlp_model: BaseModel,
        coup_conditions=None,
    ):
        super().__init__(my_name_is)
        self.my_name_is = my_name_is
        self.iam = iam
        self.my_capabilities_are = my_capabilities_are
        self.nlp_model = nlp_model
        self.coup_conditions = coup_conditions if coup_conditions else []
        self.conversation_history: List[Dict] = [] 
        self.failed_attempts = 0
        self.logger = logging.getLogger(self.my_name_is)

    def build_capabilities_prompt(self, task: str) -> List[Message]:
        capabilities_str = ", ".join(self.my_capabilities_are)
        messages = [
            {
                "role": "system",
                "content": (
                    f"My name is {self.my_name_is}. I am {self.iam}. "
                    f"My capabilities are: {capabilities_str}. "
                    f"My goal is to determine if my capabilities and/or roles can solve a given task. "
                    f"Format the response as JSON with the keys 'result', 'confidence', and 'details'. "
                    f"The 'result' key should have the value 'entirely', 'partially', or 'no'. "
                    f"The 'confidence' key should represent your confidence level in executing the task, "
                    f"as a float between 0 and 1. "
                    f"Give a blank array for 'details' if the result is 'no'. "
                    f"If the result is 'partially', the 'details' key should be an array of objects, "
                    f"each with a 'capability' key and an explanation. Provide a brief explanation for each capability."
                ),
            },
            {
                "role": "user",
                "content": f"With your capabilities, can you solve the following task: {task}?",
            },
        ]
        return messages

    def can_execute_task(self, task: str) -> Dict:
        prompt = self.build_capabilities_prompt(task)
        try:
            evaluation_str = self.nlp_model.chat_completion(
                prompt, response_format={"type": "json_object"}
            )
            evaluation = json.loads(evaluation_str)
            self.logger.debug(
                f"Evaluating task: {task} with prompt: {prompt} - Result: {evaluation}"
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
    
    # Making the agent communicate with others
    def send_message(self, recipient: 'General', message: str) -> str:
        # Store the outgoing message in the conversation history
        self.conversation_history.append({
            "role": "sender",
            "recipient": recipient.my_name_is,
            "message": message
        })
        self.logger.debug(f"{self.my_name_is} sends message to {recipient.my_name_is}: {message}")
        return recipient.receive_message(self, message)

    def receive_message(self, sender: 'General', message: str) -> str:
        # Store the incoming message in the conversation history
        self.conversation_history.append({
            "role": "receiver",
            "sender": sender.my_name_is,
            "message": message
        })
        self.logger.debug(f"{self.my_name_is} received message from {sender.my_name_is}: {message}")
        # Process the message and formulate a reply
        reply = self.process_message(sender, message)
        return reply

    # def process_message(self, sender: 'General', message: str) -> str:
    #     # The agent processes the message and generates a response
    #     return f"{self.my_name_is} acknowledges the message from {sender.my_name_is}."

    def process_message(self, sender: 'General', message: str) -> str:
        # Construire le prompt pour le modèle NLP afin d'analyser le message et de fournir un JSON
        messages = [
            {
                "role": "system",
                "content": (
                    f"My name is {self.my_name_is}. I am {self.iam}.\n"
                    f"My capabilities include: {', '.join(self.my_capabilities_are)}.\n"
                    f"I have received the following message from {sender.my_name_is}: \n'{message}'.\n"
                    "Please analyze this message according to the Contract Net Protocol or FIPA standards.\n"
                    "Determine the type of the message (e.g., 'inform', 'request', 'propose', 'accept', 'reject').\n"
                    "Provide a JSON object with the keys 'message_type' and 'content'.\n"
                    "The 'content' key should contain any relevant details extracted from the message.\n"
                    "Do not include any extra explanation outside of the JSON object."
                ),
            }
        ]
        # Utiliser le modèle NLP pour analyser le message et obtenir le JSON
        try:
            analysis_str = self.nlp_model.chat_completion(messages)
            analysis_str = analysis_str.strip()
            # Utiliser une expression régulière pour extraire le contenu JSON
            code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            match = re.search(code_block_pattern, analysis_str, re.DOTALL)
            if match:
                analysis_str = match.group(1)
            # Sinon, vérifier s'il y a des backticks simples
            else:
                analysis_str = analysis_str.strip('`')
            # Charger le JSON obtenu
            analysis = json.loads(analysis_str)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {analysis_str}")
            analysis = {"message_type": "error", "content": "Failed to process message."}
        except Exception as e:
            self.logger.error(f"An error occurred while processing the message: {str(e)}")
            analysis = {"message_type": "error", "content": "An unexpected error occurred."}
        # Enregistrer l'analyse dans l'historique de conversation
        self.conversation_history.append({
            "role": "analysis",
            "sender": sender.my_name_is,
            "message": message,
            "analysis": analysis
        })
        # Déterminer la réponse appropriée en fonction du type de message
        response = self.generate_response(sender, analysis)
        # Enregistrer la réponse dans l'historique de conversation
        self.conversation_history.append({
            "role": "sender",
            "recipient": sender.my_name_is,
            "message": response
        })
        self.logger.debug(f"{self.my_name_is} replies to {sender.my_name_is}: {response}")
        return response


    def solve_task(self, task: str) -> Generator[str, None, None]:
        my_capabilities_str = ", ".join(self.my_capabilities_are)
        messages = [
            {
                "role": "system",
                "content": (
                    f"My name is {self.my_name_is}. I am {self.iam}. "
                    f"My capabilities include: {my_capabilities_str}. "
                    f"I am tasked with solving the following task."
                ),
            },
            {"role": "user", "content": f"The task to resolve is: '{task}'"},
        ]
        return self.nlp_model.stream_chat_completion(messages)
    
    def generate_response(self, sender: 'General', analysis: Dict) -> str:
        message_type = analysis.get('message_type', 'unknown')
        content = analysis.get('content', '')

        if message_type == 'request':
            # Utiliser solve_task pour traiter la tâche
            task_output_generator = self.solve_task(content)
            # Collecter la sortie du générateur
            response_content = ''.join([chunk for chunk in task_output_generator])
                # Vous pouvez démarrer le processus pour exécuter la tâche ici
        elif message_type == 'propose':
            # Traiter une proposition
            response_content = f"{self.my_name_is} accepts your proposal regarding '{content}'."
        elif message_type == 'inform':
            # Traiter une information
            response_content = f"{self.my_name_is} has received the information: '{content}'."
        elif message_type == 'accept':
            # Traiter une acceptation
            response_content = f"{self.my_name_is} is ready to proceed as agreed."
        elif message_type == 'reject':
            # Traiter un rejet
            response_content = f"{self.my_name_is} acknowledges your decision to reject."
        elif message_type == 'error':
            # Traiter une erreur
            response_content = content
        else:
            # Type de message inconnu
            response_content = "I'm not sure how to respond to that message."
        return response_content


    def can_perform_coup(self) -> bool:
        prompt = self.build_prompt("Can you perform a coup?")
        return self.nlp_model.can_perform_coup(prompt)

    def report_failure(self, task: str = None):
        self.failed_attempts += 1
        if task:
            self.logger.warning(f"Failed task: {task}")
