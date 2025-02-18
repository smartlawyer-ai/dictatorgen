import asyncio
import logging
from typing import AsyncGenerator, List, Dict, Generator, Optional

from pydantic import ValidationError

from dictatorgenai.utils.task import Task 
from .base_agent import BaseAgent
from dictatorgenai.models import BaseModel, Message
from dictatorgenai.config import DictatorSettings
import json
import re


class TaskExecutionError(Exception):
    """
    Custom exception raised when a task execution fails.
    
    Attributes:
        message (str): The error message describing the reason for failure.
        clarification_request (str): The clarification message sent to the user.
    """
    def __init__(self, message: str, clarification_request: str = None):
        """
        Initialize the TaskExecutionError with a message and an optional clarification request.

        Args:
            message (str): The error message.
            clarification_request (str, optional): The clarification message sent to the user.
        """
        super().__init__(message)
        self.clarification_request = clarification_request

    def __str__(self):
        base_message = super().__str__()
        if self.clarification_request:
            return f"{base_message}\nClarification Request: {self.clarification_request}"
        return base_message



class General(BaseAgent):
    def __init__(
        self,
        my_name_is: str,
        iam: str,
        my_capabilities_are: List[Dict[str, str]],
        nlp_model: BaseModel,
        coup_conditions=None,
        tools=None,
        is_dictator: bool = False,
    ):
        super().__init__(my_name_is, my_capabilities_are=my_capabilities_are ,tools=tools)
        self.my_name_is = my_name_is
        self.iam = iam
        self.nlp_model = nlp_model
        self.coup_conditions = coup_conditions if coup_conditions else []
        self.is_dictator = is_dictator
        self.conversation_history: List[Dict] = [] 
        self.failed_attempts = 0
        self.logger = logging.getLogger(self.my_name_is)

    # def build_capabilities_prompt(self, task: Task) -> List[Message]:
    #     """
    #     Construit un prompt pour évaluer si les capacités de l'agent sont suffisantes pour résoudre une tâche donnée
    #     avec le contexte associé.

    #     Args:
    #         task (Task): L'objet Task contenant la demande et le contexte de discussion.

    #     Returns:
    #         List[Message]: Une liste de messages structurés pour l'évaluation des capacités.
    #     """
        
    #     # Construire le contexte de la discussion
    #     context_messages = [
    #         {"role": msg["role"], "content": msg["content"]} for msg in task.context
    #     ]
    #     reply_language = f"Provide details in {DictatorSettings.get_language()} language."
        
    #     # Ajouter les informations de base au début du prompt
    #     system_message = {
    #         "role": "system",
    #         "content": (
    #             f"My name is {self.my_name_is}. I am {self.iam}. "
    #             "I have the following capabilities:\n" +
    #             "\n".join([f"- {cap['capability']}: {cap.get('description', 'No description provided')}" 
    #                     for cap in self.my_capabilities_are]) +
    #             "\n\nBased on the context of the discussion and the user's latest request, "
    #             "determine if I can solve the task / user's latest input. Evaluate my capabilities against the latest user input.\n"
    #             "Reply in JSON format with 'result', 'confidence', and 'details'.\n"
    #             "'result' should be 'entirely', 'partially', or 'no'.\n"
    #             "'confidence' is a float between 0 and 1.\n"
    #             "If 'result' is 'partially' or 'entirely', provide an array of objects in 'details', "
    #             "each with 'capability' and 'explanation'.\n"
    #             "Be aware that assistant messages in the discussion history may come from various agents, "
    #             "not necessarily from me. When evaluating my capabilities, focus solely on my own skills and expertise, "
    #             "disregarding assistant messages that do not originate from me."
    #             f"{reply_language}"
    #         )
    #     }
        
    #     # Ajouter la tâche spécifique comme dernière demande utilisateur
    #     task_message = {
    #         "role": "user",
    #         "content": f"{task.request}",
    #     }
        
    #     # Combiner les messages dans l'ordre
    #     messages = [system_message] + context_messages + [task_message]
        
    #     return messages


    # async def can_execute_task(self, task: Task) -> Dict:
    #     prompt = self.build_capabilities_prompt(task=task)
    #     try:
    #         if self.my_name_is == 'Carrius':
    #             print('prompt', prompt)

    #         response = await self.nlp_model.chat_completion(
    #             prompt, tools=[], response_format={"type": "json_object"}
    #         )
    #         message = response.message
    #         if self.my_name_is == 'Carrius':
    #             print('message', message)
    #         evaluation = json.loads(getattr(message, "content", ""))
    #         self.logger.debug(
    #             f"Evaluating task: {task.request} with prompt: {prompt} - Result: {evaluation}"
    #         )
    #         return evaluation
    #     except json.JSONDecodeError as e:
    #         self.logger.error(f"Failed to decode JSON response: {response}")
    #         raise TaskExecutionError(
    #             f"Failed to decode JSON response: {response}"
    #         ) from e
    #     except Exception as e:
    #         self.logger.error(f"An error occurred while evaluating the task: {str(e)}")
    #         raise TaskExecutionError(
    #             f"An error occurred while evaluating the task: {str(e)}"
    #         ) from e
    
    # Making the agent communicate with others
    async def send_message(self, recipient: 'General', message: str, task: Task) -> str:
        # Store the outgoing message in the conversation history
        self.conversation_history.append({
            "role": "sender",
            "recipient": recipient.my_name_is,
            "message": message
        })
        self.logger.debug(f"{self.my_name_is} sends message to {recipient.my_name_is}: {message}")
        return await recipient.receive_message(self, message, task=task)

    async def receive_message(self, sender: 'General', message: str, task: Task) -> str:
        # Store the incoming message in the conversation history
        self.conversation_history.append({
            "role": "receiver",
            "sender": sender.my_name_is,
            "message": message
        })
        self.logger.debug(f"{self.my_name_is} received message from {sender.my_name_is}: {message}")
        # Process the message and formulate a reply
        reply = await self.process_message(sender, message, task=task)
        return reply

    # def process_message(self, sender: 'General', message: str) -> str:
    #     # The agent processes the message and generates a response
    #     return f"{self.my_name_is} acknowledges the message from {sender.my_name_is}."


    async def _execute_tool(self, function_name: str, arguments: Dict) -> str:
        print('execute tool', function_name, arguments)
        """
        Executes a tool based on its name and the provided arguments.

        Args:
            function_name (str): The name of the tool to execute.
            arguments (Dict): The arguments for the tool as a dictionary.

        Returns:
            str: The result of the tool execution as a JSON string, or an error message if the tool is not found or arguments are invalid.
        """
        tool = self.tools.get(function_name)
        if not tool:
            return json.dumps({"error": f"Tool '{function_name}' not found."})

        # Validate arguments and execute the tool
        try:
            # Use Pydantic model for argument validation if provided
            if hasattr(tool, "tool_model") and tool.tool_model:
                tool_model = tool.tool_model
                validated_args = tool_model(**arguments)  # Validate arguments using Pydantic
                arguments = validated_args.dict()

            # Check if the tool is a coroutine and execute it
            if asyncio.iscoroutinefunction(tool):
                result = await tool(**arguments)
            else:
                result = tool(**arguments)

            return json.dumps({"result": result})

        except Exception as e:
            # Handle exceptions during tool execution or argument validation
            self.logger.error(f"Error executing tool '{function_name}': {e}")
            return json.dumps({"error": f"Error executing tool '{function_name}': {str(e)}"})




    async def _process_with_tools(self, initial_messages: List[Dict], streaming: bool = False) -> AsyncGenerator[str, None]:
        """
        Gère les appels successifs de fonctions (tools) et retourne la réponse finale,
        ou diffuse les réponses au fur et à mesure si `streaming` est True.
        """
        messages = initial_messages.copy()
        tools_definitions = self.generate_tool_schemas()

        while True:
            # Appel avec ou sans streaming
            if streaming:
                async for chunk in self.nlp_model.stream_chat_completion(messages, tools=tools_definitions):
                    yield chunk  # Diffuse les fragments au fur et à mesure
                break  
            else:
                response = await self.nlp_model.chat_completion(messages, tools=tools_definitions)
                message = response.message
                tool_calls = getattr(message, "tool_calls", None)

                if tool_calls:
                    for call in tool_calls:
                        call_id = call.id
                        function = call.function
                        if not function:
                            continue  # Skip if no function is defined

                        # Extract name and arguments
                        function_name = function.name
                        arguments = json.loads(function.arguments)

                        # Execute the tool
                        try:
                            result = await self._execute_tool(function_name, arguments)
                            # Append the tool's result to the messages
                            #messages.append({"role": getattr(message, "role", "tool"), "tool_calls": tool_calls})
                            messages.append(message)
                            messages.append({"role": "tool", "content": json.dumps(result), "tool_call_id": call_id})
                        except Exception as e:
                            self.logger.error(f"Error executing tool {function_name}: {e}")
                            messages.append({"role": "tool", "content": json.dumps({"error": str(e)})})
                else:
                    # Pas de tools, retourner la réponse finale
                    message = response.message
                    yield getattr(message, "content", "")
                    break

    async def process_message(self, sender: 'General', message: str, task: Task) -> str:
        """
        Analyse un message reçu et utilise les outils si nécessaire en prenant en compte le contexte de la discussion.
        
        Args:
            sender (General): L'agent qui a envoyé le message.
            message (str): Le message reçu.
            task (Task): L'objet Task contenant la requête et le contexte de discussion.
        
        Returns:
            str: La réponse complète après traitement.
        """
        capabilities_str = "\n".join(
            [f"- {cap['capability']}: {cap.get('description', 'No description provided')}" for cap in self.my_capabilities_are]
        )
        reply_language = f"Reply in {DictatorSettings.get_language()} language."

        # Construire le contexte à partir de la discussion
        context_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in task.context
        ]

        # Ajouter le message reçu et les informations de base
        initial_messages = [
            {
                "role": "system",
                "content": (
                    f"My name is {self.my_name_is}. I am {self.iam}.\n"
                    f"You have been selected to contribute to the task given by last user message.\n"
                    f"Your capabilities are :\n"
                    f"{capabilities_str}\n\n"
                    f"{reply_language}\n"
                    "Focus strictly on these capabilities and their details. Please analyze the message "
                    "in the context of the discussion and provide your response accordingly. Use available tools if needed.\n"
                ),
            }
        ]

        # Combiner contexte, message initial, et tâche
        all_messages = initial_messages + context_messages + [
            {"role": "user", "content": message}
        ]

        # Traitement avec les outils
        async for response in self._process_with_tools(all_messages, streaming=False):
            return response  # Retourne la réponse complète sans streaming



    async def solve_task(self, task: Task) -> AsyncGenerator[str, None]:
        """
        Résout une tâche en utilisant les outils disponibles, en tenant compte des messages assistants
        si l'agent est un dictateur, puis diffuse la réponse finale en streaming.
        """
        role_description = (
            "As the dictator, your role is to lead and coordinate the resolution of this task (the last user message), leveraging the inputs and support of your generals provided in assistants messages."
            if self.is_dictator
            else "As a general, your role is to provide expertise and utilize your capabilities to contribute to the resolution of this task (the last user message)."
        )
        capabilities_str = "\n".join(
            [f"- {cap['capability']}: {cap.get('description', 'No description provided')}" for cap in self.my_capabilities_are]
        )
        reply_language = f"Reply in {DictatorSettings.get_language()} language."
        
        # Ajouter les messages assistants si l'agent est un dictateur
        assistant_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in task.context
            if msg["role"] == "assistant" or msg["role"] == "user"
        ]
        
        # Construire les messages contextuels
        messages = [
            {
                "role": "system",
                "content": (
                    f"My name is {self.my_name_is}. I am {self.iam}. "
                    f"My capabilities include: {capabilities_str}. "
                    f"{role_description} "
                    f"{reply_language}\n"
                    f"Your task is to resolve the user's latest request based on the combined expertise and context provided. "
                    f"Do not reference individual assistants or their contributions explicitly. "
                    f"Provide a single, cohesive response as if all expertise was directly available to you.\n\n"
                    f"Focus solely on resolving the latest user request while incorporating all relevant details from the discussion and assistant messages."
                ),
            },
            *[
                {"role": "assistant", "content": msg["content"]}
                for msg in assistant_messages  # Inclure les messages assistants anonymisés
            ],
            {"role": "user", "content": f"The latest task/request to resolve is: '{task.request}' use the context and assistant messages to resolve it."},
        ]
        #print('messages', messages)
        tools_definitions = self.generate_tool_schemas()

        # Étape 1 : Traiter les appels d'outils nécessaires
        while True:
            response = await self.nlp_model.chat_completion(messages, tools=tools_definitions)
            message = response.message
            tool_calls = getattr(message, "tool_calls", None)

            if tool_calls:
                messages.append(message)
                for call in tool_calls:
                    function = call.function
                    call_id = call.id
                    if not function:
                        continue  # Skip if no function is defined

                    # Extract name and arguments
                    function_name = function.name
                    arguments = json.loads(function.arguments)

                    # Execute the tool
                    try:
                        result = await self._execute_tool(function_name, arguments)
                        # Append the tool's result to the messages
                        messages.append({"role": "tool", "content": json.dumps(result), "tool_call_id": call_id})
                    except Exception as e:
                        self.logger.error(f"Error executing tool {function_name}: {e}")
                        messages.append({"role": "tool", "content": json.dumps({"error": str(e)})})
            else:
                # Étape 2 : Diffuser la réponse finale en streaming
                async for chunk in self.nlp_model.stream_chat_completion(messages):
                    yield chunk  # Diffuse chaque fragment de la réponse au fur et à mesure
                break



    
    async def generate_response(self, sender: 'General', analysis: Dict) -> str:
        message_type = analysis.get('message_type', 'unknown')
        content = analysis.get('content', '')

        if message_type == 'request':
            # Utiliser solve_task pour traiter la tâche
            response_content = ""
            async for chunk in self.solve_task(content):
                response_content += chunk
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
    
    def perform_coup_detat(self, is_dictator: bool):
        """
        Définit ou réinitialise le rôle de dictator pour le général.

        Args:
            is_dictator (bool): True pour définir le général comme dictator, False pour le réinitialiser.
        """
        self.is_dictator = is_dictator
        role = "Dictator" if is_dictator else "General"
        self.logger.info(f"{self.my_name_is} has been set as {role}.")

    def report_failure(self, task: str = None):
        self.failed_attempts += 1
        if task:
            self.logger.warning(f"Failed task: {task}")

