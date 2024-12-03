import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dictatorgenai import General
from dictatorgenai import Regime, RegimeExecutionError
from dictatorgenai import OpenaiModel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Récupération de la clé API à partir des variables d'environnement
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Veuillez définir la variable d'environnement OPENAI_API_KEY avec votre clé API OpenAI.")

# Création du modèle NLP en utilisant la clé API depuis les variables d'environnement
nlp_model = OpenaiModel(api_key=api_key)

# Création des agents (généraux en médecine) avec les nouveaux attributs
general1 = General(
    my_name_is="Hippocrate",
    iam="Spécialiste en médecine générale",
    my_capabilities_are=[
        "Diagnostic des maladies courantes",
        "Soins préventifs",
        "Gestion des maladies chroniques",
        "Éducation du patient",
    ],
    nlp_model=nlp_model,
)

general2 = General(
    my_name_is="Galenus",
    iam="Expert en chirurgie",
    my_capabilities_are=[
        "Chirurgie générale",
        "Chirurgie traumatique",
        "Chirurgie oncologique",
        "Procédures mini-invasives",
    ],
    nlp_model=nlp_model,
)

general3 = General(
    my_name_is="Nightingale",
    iam="Spécialiste en soins infirmiers et en prise en charge du patient",
    my_capabilities_are=[
        "Évaluation du patient",
        "Administration des médicaments",
        "Advocatie du patient",
        "Planification des soins",
    ],
    nlp_model=nlp_model,
)

general4 = General(
    my_name_is="Pasteur",
    iam="Expert en microbiologie et maladies infectieuses",
    my_capabilities_are=[
        "Prévention des maladies",
        "Vaccinologie",
        "Traitements antimicrobiens",
        "Contrôle des infections",
    ],
    nlp_model=nlp_model,
)

general5 = General(
    my_name_is="Curie",
    iam="Spécialiste en radiologie et imagerie médicale",
    my_capabilities_are=[
        "Imagerie par rayons X",
        "Tomodensitométrie (CT)",
        "Imagerie par résonance magnétique (IRM)",
        "Échographie diagnostique",
    ],
    nlp_model=nlp_model,
)

general6 = General(
    my_name_is="Freud",
    iam="Expert en psychiatrie et santé mentale",
    my_capabilities_are=[
        "Psychothérapie",
        "Diagnostic des troubles mentaux",
        "Psychopharmacologie",
        "Conseil en santé mentale",
    ],
    nlp_model=nlp_model,
)

general7 = General(
    my_name_is="Watson",
    iam="Spécialiste en oncologie",
    my_capabilities_are=[
        "Diagnostic du cancer",
        "Chimiothérapie",
        "Radiothérapie",
        "Soins palliatifs",
    ],
    nlp_model=nlp_model,
)

general8 = General(
    my_name_is="Fleming",
    iam="Expert en pharmacologie",
    my_capabilities_are=[
        "Développement de médicaments",
        "Pharmacocinétique",
        "Interactions médicamenteuses",
        "Surveillance thérapeutique",
    ],
    nlp_model=nlp_model,
)

# Création du régime avec les généraux en médecine
regime = Regime(
    nlp_model=nlp_model,
    government_prompt="PROMPT GOUVERNEMENTAL",
    generals=[
        general1,
        general2,
        general3,
        general4,
        general5,
        general6,
        general7,
        general8,
    ],
)

# Abonnement aux événements
def on_task_started(message):
    print("Événement : tâche commencée -", message)

def on_task_update(message):
    print("Événement : mise à jour de la tâche -", message)

def on_task_completed(message):
    print("Événement : tâche terminée -", message)

def on_task_failed(message):
    print("Événement : échec de la tâche -", message)

regime.subscribe("task_started", on_task_started)
regime.subscribe("task_update", on_task_update)
regime.subscribe("task_completed", on_task_completed)
regime.subscribe("task_failed", on_task_failed)

while True:
    # Demander à l'utilisateur de saisir une nouvelle tâche
    task = input("Entrez une nouvelle tâche (ou tapez 'exit' pour quitter) : ")
    if task.lower() == "exit":
        break
    try:
        result = regime.run(task)
        for chunk in result:
            print(chunk, end="", flush=True)
    except RegimeExecutionError as e:
        print(f"Tous les généraux capables ont échoué à exécuter la tâche : {e}")

    print("\nExécution de la tâche terminée.")
