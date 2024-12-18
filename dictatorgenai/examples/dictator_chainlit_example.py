import asyncio
import logging
import sys
import os
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI
#from phoenix.otel import register

# tracer_provider = register(
#   project_name="smartlawyer 2",
#   endpoint="http://localhost:6006/v1/traces"
# )
#OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

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
        {
            "capability": "Code civil",
            "description": (
                "Expertise approfondie dans le Code civil, couvrant les obligations, les contrats, "
                "les responsabilités civiles, les successions, et les régimes matrimoniaux."
            ),
        },
        {
            "capability": "Code de la famille et de l'action sociale",
            "description": (
                "Maîtrise des règles relatives au droit de la famille, y compris le mariage, le divorce, "
                "la filiation, la garde des enfants, et les obligations alimentaires."
            ),
        },
        {
            "capability": "Code de procédure civile",
            "description": (
                "Compétence dans les procédures judiciaires civiles, y compris les règles de compétence, "
                "les recours, et les modalités de résolution des litiges."
            ),
        },
        {
            "capability": "Réglementation et lois sur les bailleurs preneurs",
            "description": (
                "Spécialiste des réglementations liées aux relations entre bailleurs et preneurs, "
                "y compris les baux résidentiels, commerciaux, et ruraux, ainsi que les droits et devoirs des parties."
            ),
        },
    ],
    nlp_model=nlp_model,
)


general2 = General(
    my_name_is="Rénéssance",
    iam="Expert en droit du travail et de la sécurité sociale",
    my_capabilities_are=[
        {
            "capability": "Code du travail",
            "description": (
                "Expertise dans les réglementations liées aux relations employeurs-employés, "
                "telles que les contrats de travail, les licenciements, les heures de travail, "
                "et les droits syndicaux."
            ),
        },
        {
            "capability": "Code de la sécurité sociale",
            "description": (
                "Maîtrise des lois et des règlements couvrant les assurances sociales, les retraites, "
                "les allocations chômage, et les prestations liées à la santé et à la famille."
            ),
        },
    ],
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
        {"capability": "Code pénal", "description": "Analyse des infractions pénales, telles que harcèlement et agressions."},
        {"capability": "Code de procédure pénale", "description": "Représentation et gestion des procédures judiciaires pénales."},
        {"capability": "Code de la sécurité intérieure", "description": "Conseils en matière de sécurité et gestion des risques."},
    ],
    nlp_model=nlp_model,
    tools=[estimate_damage],
)

general4 = General(
    my_name_is="Necteur",
    iam="Expert en droit financier et fiscal",
    my_capabilities_are=[
        {
            "capability": "Code monétaire et financier",
            "description": (
                "Spécialiste des règles relatives aux marchés financiers, aux institutions bancaires, "
                "à la régulation financière, aux services de paiement, et aux dispositifs de lutte contre le blanchiment d'argent."
            ),
        },
        {
            "capability": "Code général des impôts (annexes I, II, III, IV)",
            "description": (
                "Maîtrise des dispositions fiscales relatives aux entreprises et aux particuliers, "
                "y compris l'imposition des revenus, la TVA, les droits de succession, et les optimisations fiscales dans un cadre légal."
            ),
        },
    ],
    nlp_model=nlp_model,
)


general5 = General(
    my_name_is="Colberius",
    iam="Spécialiste en droit commercial et de la consommation",
    my_capabilities_are=[
        {
            "capability": "Code de commerce",
            "description": (
                "Expertise approfondie dans les règles relatives aux sociétés commerciales, aux contrats commerciaux, "
                "au droit des affaires, aux procédures collectives (faillite) et à la gouvernance des entreprises."
            ),
        },
        {
            "capability": "Code de la consommation",
            "description": (
                "Maîtrise des lois et régulations protégeant les consommateurs, y compris les contrats de vente, "
                "la publicité, la garantie des produits, et les pratiques commerciales déloyales."
            ),
        },
        {
            "capability": "Code des assurances",
            "description": (
                "Spécialiste des régulations encadrant les contrats d'assurance, les droits et obligations des assureurs "
                "et assurés, ainsi que les litiges liés aux sinistres ou à la validité des clauses contractuelles."
            ),
        },
    ],
    nlp_model=nlp_model,
)


general6 = General(
    my_name_is="Clem",
    iam="Expert en droit administratif et public",
    my_capabilities_are=[
        {
            "capability": "Code des relations entre le public et l'administration",
            "description": (
                "Expertise dans les interactions entre les citoyens et les administrations publiques, y compris "
                "les droits des usagers, la transparence administrative, et la réglementation des décisions publiques."
            ),
        },
        {
            "capability": "Code de la commande publique",
            "description": (
                "Spécialiste des marchés publics, des appels d'offres, des concessions, et des obligations juridiques "
                "liées aux contrats conclus par les administrations publiques."
            ),
        },
        {
            "capability": "Code général de la fonction publique",
            "description": (
                "Maîtrise des statuts des fonctionnaires, des droits et devoirs des agents publics, ainsi que des "
                "dispositions relatives à la mobilité, la discipline, et la gestion des carrières dans la fonction publique."
            ),
        },
        {
            "capability": "Code de justice administrative",
            "description": (
                "Expertise dans le contentieux administratif, les recours contre les décisions publiques, et les "
                "procédures devant les juridictions administratives, incluant les litiges en matière d'urbanisme, "
                "d'environnement, et de contrats publics."
            ),
        },
    ],
    nlp_model=nlp_model,
)


general7 = General(
    my_name_is="Haussmannus",
    iam="Spécialiste en droit de l'urbanisme et de la construction",
    my_capabilities_are=[
        {
            "capability": "Code de l'urbanisme",
            "description": (
                "Expertise dans la planification urbaine, la gestion des permis de construire, les zones protégées, "
                "et les régulations liées à l'aménagement du territoire. Intervient dans les litiges concernant les "
                "autorisations d'urbanisme ou les infractions au code de l'urbanisme."
            ),
        },
        {
            "capability": "Code de la construction et de l'habitation",
            "description": (
                "Spécialiste des normes de construction, de la sécurité des bâtiments, des contrats de maîtrise d'œuvre, "
                "et des obligations liées à la qualité des logements. Conseille sur les responsabilités des acteurs de la "
                "construction et les litiges liés à des défauts de construction ou à des désordres affectant les bâtiments."
            ),
        },
    ],
    nlp_model=nlp_model,
)


general8 = General(
    my_name_is="Ambrosius",
    iam=(
        "Expert en droit de l'environnement, en écologie, et en santé publique. "
        "Je possède une vaste expérience dans la consultation juridique sur les questions environnementales, "
        "la réglementation écologique, et la protection de la santé publique liée aux enjeux environnementaux. "
        "J'ai notamment représenté des communautés locales dans des litiges liés à la pollution industrielle, "
        "conseillé des municipalités sur la gestion des déchets, et collaboré avec des ONG pour protéger la biodiversité. "
        "J'ai également participé à l'élaboration de politiques sur la qualité de l'air et le climat, "
        "et je suis intervenu dans des cas de pollution de l'eau pour restaurer les écosystèmes aquatiques. "
        "Mon expertise s'étend également à la formation et à la sensibilisation des acteurs publics et privés "
        "sur les enjeux environnementaux actuels."
    ),
    my_capabilities_are=[
        {
            "capability": "Code de la santé publique",
            "description": (
                "Compétences en matière de réglementation liée à la santé publique, en particulier dans les cas où les "
                "enjeux environnementaux impactent la santé des populations, comme la pollution de l'air ou des sols."
            ),
        },
        {
            "capability": "Code de l'environnement",
            "description": (
                "Expertise dans l'application du Code de l'environnement, y compris la préservation des ressources naturelles, "
                "la gestion des sites protégés, et la prévention des pollutions et des risques environnementaux."
            ),
        },
        {
            "capability": "Réglementation sur la pollution de l'eau",
            "description": (
                "Spécialisation dans les normes et lois encadrant la qualité des eaux, la gestion des déchets liquides, "
                "et la restauration des écosystèmes aquatiques impactés par des pollutions."
            ),
        },
        {
            "capability": "Législation sur les déchets et les substances dangereuses",
            "description": (
                "Maîtrise des lois et régulations concernant la gestion des déchets, le traitement des substances dangereuses, "
                "et la mise en conformité des entreprises dans ces domaines."
            ),
        },
        {
            "capability": "Droit de l'air et du climat",
            "description": (
                "Intervention sur les questions relatives à la qualité de l'air, aux émissions de gaz à effet de serre, "
                "et à l'élaboration de politiques climatiques pour les acteurs publics et privés."
            ),
        },
        {
            "capability": "Réglementation des sites et sols pollués",
            "description": (
                "Expertise dans la gestion des sites pollués, incluant les obligations des propriétaires, les mesures de "
                "réhabilitation, et les litiges liés à la contamination des sols."
            ),
        },
        {
            "capability": "Législation sur les aires protégées et la biodiversité",
            "description": (
                "Connaissances approfondies dans la conservation de la biodiversité, la protection des habitats naturels, "
                "et la régulation des activités humaines dans les aires protégées."
            ),
        },
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




