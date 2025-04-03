import json
from typing import Any, AsyncGenerator, Dict, List
import logging
from dictatorgenai.agents.general import General
from dictatorgenai.models.base_model import BaseModel, Message
from dictatorgenai.steps.action_steps import PlanningStep
from dictatorgenai.utils.task import Task


class ColonelFragmenter(General):
    def __init__(
        self,
        my_name_is: str,
        iam: str,
        my_capabilities_are: List[Dict[str, str]],
        nlp_model: BaseModel,
        tools=None,
    ):
        super().__init__(my_name_is, iam, my_capabilities_are, nlp_model, tools=tools)
        self.logger = logging.getLogger(self.my_name_is)
    
    async def solve_task(self, task: Task, **kwargs: Any) -> Dict:
        """
        Résout la tâche en la découpant en sous-tâches et renvoie directement les sous-tâches.
        """
        # Construire le prompt pour décomposer la tâche
        prompt = self.build_task_decomposition_prompt(task)
        
        # Appeler le modèle NLP pour obtenir la décomposition
        response = await self.nlp_model.chat_completion(
            [Message(role="system", content=prompt), Message(role="user", content=task.request)],
            tools=[],
            response_format={"type": "json_object"}
        )

        # Analyser les sous-tâches obtenues
        subtasks = json.loads(getattr(response.message, "content", "{}"))
        
        return subtasks


    def build_task_decomposition_prompt(self, task: Task) -> str:
        """
        Construit le prompt pour analyser une requête juridique et la décomposer en sous-problèmes distincts.
        
        :param task: La tâche que nous devons découper en sous-tâches.
        :return: Un prompt structuré pour une IA d'analyse juridique.
        """
        # Filtrer les messages utiles dans l'historique de la conversation
        conversation_history = [
            {"role": step.role, "content": step.content}
            for step in task.steps
            if step.step_type in ("user_message", "assistant_message")  # Filtrage des messages pertinents
        ]

        # 🔹 Conversion en JSON formaté
        formatted_history = json.dumps(conversation_history, ensure_ascii=False, indent=2)

        # 🔹 Construction du prompt avec échappement des accolades
        prompt_template = f"""
    # Contexte
    Tu es un assistant juridique expert dans la planification et la structuration des dossiers juridiques.  
    Ton rôle est d’analyser la demande utilisateur qui est une **requête juridique** et son contexte afin de la décomposer en **sous-problèmes juridiques distincts**.

    # Historique de la conversation
    Voici les échanges récents entre l’utilisateur et l’assistant juridique :  
    {formatted_history}

    # Objectif
    Décompose la demande utilisateur en plusieurs sous-tâches juridiques et attribue chaque sous-tâche à un **expert juridique spécialisé**.  
    Si certaines parties nécessitent une expertise particulière, précise **le domaine du droit applicable**.
    Tu ajoutes toujours une sous-tache qui mentionnent les recherches d'articles de droits ou de jurisprudences à effectuer**.

    # Format attendu (JSON)
    Retourne une réponse sous le format suivant :
    {{
    "main_legal_issue": "Résumé global de la problématique juridique",
    "subtasks": [
        {{
        "id": 1,
        "description": "Première sous-tâche juridique à résoudre",
        "required_expert": "Nom du spécialiste en droit concerné",
        "applicable_law": "Code ou loi applicable"
        }},
        {{
        "id": 2,
        "description": "Deuxième sous-tâche juridique",
        "required_expert": "Nom du spécialiste en droit concerné",
        "applicable_law": "Code ou loi applicable"
        }}
    ]
    }}
        """
        return prompt_template.strip()
