import asyncio
import logging
from typing import AsyncGenerator, List, Dict, Generator, Optional

from pydantic import ValidationError
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
        tools=None,
    ):
        super().__init__(my_name_is, tools=tools)
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

    async def can_execute_task(self, task: str) -> Dict:
        prompt = self.build_capabilities_prompt(task)
        try:
            response = await self.nlp_model.chat_completion(
                prompt, tools=[], response_format={"type": "json_object"}
            )
            message = response.message
            evaluation = json.loads(getattr(message, "content", ""))
            self.logger.debug(
                f"Evaluating task: {task} with prompt: {prompt} - Result: {evaluation}"
            )
            return evaluation
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {response}")
            raise TaskExecutionError(
                f"Failed to decode JSON response: {response}"
            ) from e
        except Exception as e:
            self.logger.error(f"An error occurred while evaluating the task: {str(e)}")
            raise TaskExecutionError(
                f"An error occurred while evaluating the task: {str(e)}"
            ) from e
    
    # Making the agent communicate with others
    async def send_message(self, recipient: 'General', message: str) -> str:
        # Store the outgoing message in the conversation history
        self.conversation_history.append({
            "role": "sender",
            "recipient": recipient.my_name_is,
            "message": message
        })
        self.logger.debug(f"{self.my_name_is} sends message to {recipient.my_name_is}: {message}")
        return await recipient.receive_message(self, message)

    async def receive_message(self, sender: 'General', message: str) -> str:
        # Store the incoming message in the conversation history
        self.conversation_history.append({
            "role": "receiver",
            "sender": sender.my_name_is,
            "message": message
        })
        self.logger.debug(f"{self.my_name_is} received message from {sender.my_name_is}: {message}")
        # Process the message and formulate a reply
        reply = await self.process_message(sender, message)
        return reply

    # def process_message(self, sender: 'General', message: str) -> str:
    #     # The agent processes the message and generates a response
    #     return f"{self.my_name_is} acknowledges the message from {sender.my_name_is}."


    async def _execute_tool(self, function_name: str, arguments: Dict) -> str:
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

    async def process_message(self, sender: 'General', message: str) -> str:
        """
        Analyse un message reçu et utilise les outils si nécessaire.
        """
        initial_messages = [
            {
                "role": "system",
                "content": (
                    f"My name is {self.my_name_is}. I am {self.iam}.\n"
                    f"My capabilities include: {', '.join(self.my_capabilities_are)}.\n"
                    f"I have received the following message from {sender.my_name_is}: \n'{message}'.\n"
                    "Please analyze this message and use available tools if needed.\n"
                ),
            },
        ]
        async for response in self._process_with_tools(initial_messages, streaming=False):
            return response  # Retourne la réponse complète sans streaming


    async def solve_task(self, task: str) -> AsyncGenerator[str, None]:
        """
        Résout une tâche en utilisant les outils disponibles, puis diffuse la réponse finale en streaming.
        """
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

        tools_definitions = self.generate_tool_schemas()

        # Étape 1 : Traiter les appels d'outils nécessaires
        while True:
            response = await self.nlp_model.chat_completion(messages, tools=tools_definitions)
            message = response.message
            tool_calls = getattr(message, "tool_calls", None)
            #if response.get("finish_reason") == "stop":
                #break

            if tool_calls:
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
                        #messages.append({"role": getattr(message, "role", "tool"), "tool_calls": tool_calls})
                        messages.append(message)
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

    def report_failure(self, task: str = None):
        self.failed_attempts += 1
        if task:
            self.logger.warning(f"Failed task: {task}")




    # async def solve_task(self, task: str) -> AsyncGenerator[str, None]:
    #     my_capabilities_str = ", ".join(self.my_capabilities_are)
    #     messages = [
    #         {
    #             "role": "system",
    #             "content": (
    #                 f"My name is {self.my_name_is}. I am {self.iam}. "
    #                 f"My capabilities include: {my_capabilities_str}. "
    #                 f"I am tasked with solving the following task."
    #             ),
    #         },
    #         {"role": "user", "content": f"The task to resolve is: '{task}'"},
    #     ]
    #     print('teub3')
    #     # Utilisation du modèle NLP pour générer la réponse de manière asynchrone
    #     async for chunk in self.nlp_model.stream_chat_completion(messages):
    #         yield chunk  # Renvoie chaque morceau de la réponse au fur et à mesure
