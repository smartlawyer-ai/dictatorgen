import asyncio
import logging
import sys
import os
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI
from phoenix.otel import register

tracer_provider = register(
  project_name="smartlawyer 2",
  endpoint="http://localhost:6006/v1/traces"
)
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dictatorgenai import General, tool
from dictatorgenai import Regime, RegimeExecutionError
from dictatorgenai import OpenaiModel
import chainlit as cl
from dotenv import load_dotenv  # Optionnel si vous utilisez un fichier .env

# Chargement des variables d'environnement à partir d'un fichier .env
load_dotenv()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError(
        "OPENAI_API_KEY is not set in the environment. Please set it before running the script."
    )

client = OpenAI()
conversation =[{"role": "system", "content": "just reply"}, {"role": "user", "content": "I need help with a legal issue."}]

#response = client.chat.completions.create(model= "gpt-4o-mini", messages=conversation)
# Création du modèle NLP
nlp_model = OpenaiModel(api_key=api_key)


# Modèle Pydantic pour les paramètres


# Création des agents avec les nouveaux attributs
general1 = General(
    my_name_is="Baudelin",
    iam="Spécialiste du droit civil et familial",
    my_capabilities_are=[
        "Code civil",
        "Code de la famille et de l'action sociale",
        "Code de procédure civile",
        "Réglementation et lois sur les bailleurs preneurs",
    ],
    nlp_model=nlp_model,
)

general2 = General(
    my_name_is="Rénéssance",
    iam="Expert en droit du travail et de la sécurité sociale",
    my_capabilities_are=["Code du travail", "Code de la sécurité sociale"],
    nlp_model=nlp_model,
)


@tool(description="Estime les dommages corporels.")
def estimate_damage(injury_type: str, severity_level: int) -> str:
    return (
        f"L'estimation des dommages corporels pour une blessure de type "
        f"'{injury_type}' avec un niveau de gravité {severity_level} est de 50 000 €. "
        f"(Test - réponse fixe)."
    )

general3 = General(
    my_name_is="Carrius",
    iam=(
        "Spécialiste en droit pénal, droit de la presse et sécurité intérieure, avec une expertise approfondie dans l'application "
        "du Code pénal, du Code de procédure pénale, du Code de la sécurité intérieure, du Code de la justice pénale des mineurs, "
        "et du Code des postes et des communications électroniques. \n"
        "Exemples de cas sur lesquels je peux intervenir : \n"
        "- Défense dans des affaires de crimes et délits (homicides, vols, cybercriminalité) \n"
        "- Gestion de procédures en matière de presse, comme la diffamation et les atteintes à la vie privée \n"
        "- Interventions sur des questions de sécurité intérieure et de terrorisme, incluant les procédures liées à la surveillance électronique \n"
        "- Représentation de mineurs en justice dans des affaires pénales \n"
        "- Réglementation et conformité des communications électroniques et des télécommunications, incluant les litiges liés à la protection des données."
        "- Les affaires pénales en général"
    ),
    my_capabilities_are=[
        "Code pénal",
        "Code de procédure pénale",
        "Code de la sécurité intérieure",
        "Code de la justice pénale des mineurs",
        "Code des postes et des communications électroniques",
    ],
    nlp_model=nlp_model,
    tools=[estimate_damage],
)

general4 = General(
    my_name_is="Necteur",
    iam="Expert en droit financier et fiscal",
    my_capabilities_are=[
        "Code monétaire et financier",
        "Code général des impôts (annexes I, II, III, IV)",
    ],
    nlp_model=nlp_model,
)

general5 = General(
    my_name_is="Colberius",
    iam="Spécialiste en droit commercial et de la consommation",
    my_capabilities_are=[
        "Code de commerce",
        "Code de la consommation",
        "Code des assurances",
    ],
    nlp_model=nlp_model,
)

general6 = General(
    my_name_is="Clem",
    iam="Expert en droit administratif et public",
    my_capabilities_are=[
        "Code des relations entre le public et l'administration",
        "Code de la commande publique",
        "Code général de la fonction publique",
        "Code de justice administrative",
    ],
    nlp_model=nlp_model,
)

general7 = General(
    my_name_is="Haussmannus",
    iam="Spécialiste en droit de l'urbanisme et de la construction",
    my_capabilities_are=[
        "Code de l'urbanisme",
        "Code de la construction et de l'habitation",
    ],
    nlp_model=nlp_model,
)

general8 = General(
    my_name_is="Ambrosius",
    iam="Expert en droit de l'environnement, en écologie, et en santé publique. "
        "Je possède une vaste expérience dans la consultation juridique sur les questions environnementales, "
        "la réglementation écologique, et la protection de la santé publique liée aux enjeux environnementaux. "
        "J'ai notamment représenté des communautés locales dans des litiges liés à la pollution industrielle, "
        "conseillé des municipalités sur la gestion des déchets, et collaboré avec des ONG pour protéger la biodiversité. "
        "J'ai également participé à l'élaboration de politiques sur la qualité de l'air et le climat, "
        "et je suis intervenu dans des cas de pollution de l'eau pour restaurer les écosystèmes aquatiques. "
        "Mon expertise s'étend également à la formation et à la sensibilisation des acteurs publics et privés "
        "sur les enjeux environnementaux actuels.",
    my_capabilities_are=[
        "Code de la santé publique",
        "Code de l'environnement",
        "Réglementation sur la pollution de l'eau",
        "Législation sur les déchets et les substances dangereuses",
        "Droit de l'air et du climat",
        "Réglementation des sites et sols pollués",
        "Législation sur les aires protégées et la biodiversité",
    ],
    nlp_model=nlp_model,
)

# Création du régime
regime = Regime(
    nlp_model=nlp_model,
    government_prompt="GOVERNMENT PROMPT",
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



# # Abonnement aux événements en utilisant des étapes Chainlit

# @cl.step(type="tool")
# async def on_task_started(event):
#     await cl.Message(content=f"Event: task_started - {event['message']}").send()

# @cl.step(type="tool")
# async def on_task_update(event):
#     await cl.Message(content=f"Event: task_update - {event['message']}").send()

# @cl.step(type="tool")
# async def on_task_completed(event):
#     await cl.Message(content=f"Event: task_completed - {event['message']}").send()

# @cl.step(type="tool")
# async def on_task_failed(event):
#     await cl.Message(content=f"Event: task_failed - {event['message']}").send()

# @cl.step(type="tool")
# async def on_coup_d_etat(event):
#     await cl.Message(content=f"Event: coup_d_etat - {event['message']}").send()

# # S'abonner aux événements
# regime.subscribe("task_started", lambda event: asyncio.create_task(on_task_started(event)))
# regime.subscribe("task_update", lambda event: asyncio.create_task(on_task_update(event)))
# regime.subscribe("task_completed", lambda event: asyncio.create_task(on_task_completed(event)))
# regime.subscribe("task_failed", lambda event: asyncio.create_task(on_task_failed(event)))
# regime.subscribe("coup_d_etat", lambda event: asyncio.create_task(on_coup_d_etat(event)))

@cl.step(type="tool", name="Fin de la tache")
async def on_task_completed(event):
    #await regime.wait_for_event("task_started")  # Attend que l'événement "coup_d_etat" soit publié
    return f"⚠️ **task_completed**: {event['message']}"

@cl.step(type="tool", name="Début de la tache")
async def on_task_started(event):
    #await regime.wait_for_event("task_started")  # Attend que l'événement "coup_d_etat" soit publié
    return f"⚠️ **task_started**: {event['message']}"

@cl.step(type="tool", name="Mise à jour de la tache")
async def on_task_updated(event):
    #await regime.wait_for_event("task_started")  # Attend que l'événement "coup_d_etat" soit publié
    return f"⚠️ **task_updated**: {event['message']}"

@cl.step(type="tool", name="Séléction du Dictator et des Généraux")
async def on_coup_d_etat(event):
    #await regime.wait_for_event("coup_d_etat")  # Attend que l'événement "coup_d_etat" soit publié
    print("coup d'etat")
    return f"⚠️ **Coup d'État détecté**: {event['message']}"

regime.subscribe("coup_d_etat", on_coup_d_etat)
regime.subscribe("task_started", on_task_started)
regime.subscribe("task_completed", on_task_completed)
regime.subscribe("task_update", on_task_updated)


# S'abonner aux événements
# regime.subscribe("task_started", on_task_started)
# regime.subscribe("task_update", on_task_update)
# regime.subscribe("task_completed", on_task_completed)
#regime.subscribe("task_failed", on_task_failed)

@cl.on_message
async def main(message: cl.Message):
        try:
            response = await nlp_model.chat_completion(messages=conversation)
            msg = cl.Message(content="")
            
            response_chunks = regime.chat(message.content)
            #await on_coup_d_etat()
            # Streamer la réponse à l'utilisateur
            async for chunk in response_chunks:
                await msg.stream_token(chunk)
            await msg.send()
                

        except RegimeExecutionError as e:
            print(f"All capable generals failed to complete the task: {e}")




