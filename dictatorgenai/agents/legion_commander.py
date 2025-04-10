import json
import logging
from typing import Any, AsyncGenerator, Dict, List, TypedDict
from dictatorgenai.agents.general import General, TaskExecutionError
from dictatorgenai.models.base_model import BaseModel, Message
from dictatorgenai.utils.task import Task
from dictatorgenai.config import DictatorSettings
from dictatorgenai.steps import GeneralEvaluationStep
from dictatorgenai.agents.assigned_general import AssignedGeneral

class LegionCommander(General):
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

    async def solve_task(self, task: Task, **kwargs: Any) -> List[AssignedGeneral]:
        """
        Résout la tâche en sélectionnant les généraux pour résoudre les sous-tâches.

        Args:
            task (Task): La tâche à résoudre.
            **kwargs: Les généraux à évaluer sont passés dans **kwargs.

        Returns:
            List[AssignedGeneral]: La liste des généraux sélectionnés pour résoudre la tâche.
        """
        # Récupérer les généraux à partir de kwargs
        generals = kwargs.get('generals', [])
        subtasks = kwargs.get('subtasks', [])
        if not generals:
            raise TaskExecutionError(message="No generals provided to solve the task.")

        # Construire le prompt pour évaluer tous les généraux par rapport aux sous-tâches
        prompt = self.build_evaluation_prompt_for_generals(generals, subtasks)
        #print(prompt)
        # Appeler le modèle NLP pour obtenir la réponse d'évaluation
        response = await self.nlp_model.chat_completion(
            [Message(role="system", content=prompt), Message(role="user", content="Can these generals solve the task?")],
            tools=[],
            response_format={"type": "json_object"}
        )

        # Analyser la réponse du modèle
        evaluation = json.loads(getattr(response.message, "content", "{}"))
        selected_generals: List[AssignedGeneral] = []

        # Processus de sélection des généraux selon leur évaluation
        for general_name, eval_data in evaluation.items():
            if eval_data["result"] == "entirely" or eval_data["result"] == "partially":
                general = self.get_general_by_name(general_name, generals)
                if general:
                    selected_generals.append(
                        AssignedGeneral( 
                            base_general=general, 
                            assigned_subtasks=subtasks, 
                            capabilities_used=eval_data["details"], 
                            confidence=eval_data["confidence"]
                        )
                    )
                        
                    task.add_step(
                        GeneralEvaluationStep(
                            request_id=len(task.steps) + 1, 
                            general=general.my_name_is, 
                            evaluation=getattr(response.message, "content", "{}"), 
                            metadata={"general": general.my_name_is, "evaluation": evaluation}
                        )
                    )

        if selected_generals:
            # Organiser les généraux sélectionnés
            selected_generals = self._rank_generals_by_capabilities(selected_generals)

            # Retourner les généraux sélectionnés sous forme de texte
            return selected_generals
        else:
            raise TaskExecutionError(message="No general is capable of solving this task.")

    def build_evaluation_prompt_for_generals(self, generals: List[General], subtasks: List[Dict]) -> str:
        """
        Construit un prompt unique pour évaluer les capacités de tous les généraux par rapport aux sous-tâches.

        Args:
            generals (List[General]): Liste des généraux à évaluer.
            subtasks (List[Dict]): Liste des sous-tâches à résoudre.

        Returns:
            str: Un prompt structuré pour évaluer tous les généraux par rapport aux sous-tâches.
        """
        subtasks_str = json.dumps(subtasks, ensure_ascii=False, indent=2)

        # Création du prompt pour chaque général
        generals_str = "\n".join([f"My name is {general.my_name_is}. I am an expert in {general.iam}." for general in generals])

        reply_language = f"Provide details in {DictatorSettings.get_language()} language."

        # Format du prompt
        prompt_template = f"""
# Contexte
Voici les sous-tâches qui doivent être résolues : 
{subtasks_str}

# Objectif
Évaluez si chaque général dans la liste suivante peut résoudre une ou plusieurs des sous-tâches en fonction de ses compétences et connaissances.  
Les généraux sont les suivants :
{generals_str}

Pour chaque général, répondez par :
- 'result' qui peut être 'entirely', 'partially', ou 'no'
- 'confidence' qui est un nombre flottant entre 0 et 1 représentant la confiance dans la capacité à résoudre la tâche
- 'details' qui comprend une liste des compétences utilisées pour résoudre les sous-tâches mentionnées
- 'legal_queries' : des formulations de recherche que vous utiliseriez pour retrouver les bons textes de loi ou décisions de justice (exemples : "articles du code civil sur le divorce par consentement mutuel", "jurisprudence récente sur le partage des biens en cas de divorce")

Répondez en format JSON pour chaque général, par exemple :
{{
    "general_name": {{
        "result": "entirely",
        "confidence": 0.9,
        "details": [
            {{
                "capability": "Expertise in family law",
                "explanation": "Able to analyze divorce-related issues."
                "subtasks": ["Analyze divorce case", "Provide legal advice"],
                "legal_queries": [
                    "articles du code civil concernant le divorce par consentement mutuel",
                    "jurisprudence récente sur la garde alternée"
                ]
            }}
        ]
    }}
}}

{reply_language}
"""
        return prompt_template.strip()

    def _rank_generals_by_capabilities(self, selected_generals: List[AssignedGeneral]) -> List[AssignedGeneral]:
        """
        Classe les généraux en fonction de leurs capacités à résoudre les sous-tâches.
        """
        # Ordonner les généraux en fonction de leur niveau de confiance
        selected_generals.sort(key=lambda x: x.confidence, reverse=True)
        return selected_generals

    def get_general_by_name(self, name: str, generals: List[General]) -> General:
        """
        Recherche et retourne un général complet par son nom dans la liste des généraux.

        Args:
            name (str): Le nom du général à rechercher.
            generals (List[General]): La liste des généraux avec toutes leurs informations.

        Returns:
            General: L'objet général complet correspondant au nom, ou None si non trouvé.
        """
        for general in generals:
            if general.my_name_is == name:  # Comparer avec le nom du général
                return general
        return None  # Retourner None si le général n'est pas trouvé
