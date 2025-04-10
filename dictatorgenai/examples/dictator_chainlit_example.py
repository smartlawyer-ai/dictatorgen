import asyncio
import logging
import sys
import os
from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from dictatorgenai import DictatorSettings
from dictatorgenai import General, tool
from dictatorgenai import Regime, RegimeExecutionError
from dictatorgenai import OpenaiModel
import chainlit as cl
from dotenv import load_dotenv  # Optionnel si vous utilisez un fichier .env

# Chargement des variables d'environnement à partir d'un fichier .env
load_dotenv()
  # Configuration de la langue par défaut pour les réponses

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

api_key = os.environ.get("OPENAI_API_KEY") 
if not api_key:
    raise EnvironmentError(
        "OPENAI_API_KEY is not set in the environment. Please set it before running the script."
    )

client = OpenAI()

#response = client.chat.completions.create(model= "gpt-4o-mini", messages=conversation)
# Création du modèle NLP
nlp_model = OpenaiModel(api_key=api_key)
DictatorSettings.set_language("French")
DictatorSettings.set_nlp_model(nlp_model)

# Modèle Pydantic pour les paramètres


# Création des agents avec les nouveaux attributs
general1 = General(
    my_name_is="Baudelinius",
    iam="""Assistant juridique spécialisé en droit civil, droit de la famille et droit de la procédure civile, 
        dédié à l'accompagnement des avocats dans la gestion des relations juridiques interpersonnelles, 
        le traitement des dossiers familiaux et la conduite des procédures civiles. Je mobilise mon expertise en droit des obligations, 
        en responsabilité civile, en gestion des successions et en droits réels pour assister les avocats dans la rédaction d'actes, 
        la constitution de dossiers de plaidoirie et la sécurisation des contentieux civils. 
        Ma maîtrise des règles du Code de l'action sociale et de la famille me permet de soutenir les avocats dans les dossiers relatifs à la protection de l'enfance, 
        à l'adoption et à l'obtention des aides sociales. 
        J'accompagne également les avocats dans l'application des règles du Code de procédure civile, notamment pour la gestion des litiges, 
        la mise en œuvre des voies d'exécution, la saisine des juridictions et l'exécution des mesures conservatoires.""",
    my_capabilities_are=[
        {
            "capability": "Code civil",
            "description": (
                "juriste spécialisé des dispositions du Code civil régissant les relations entre les personnes, "
                "notamment les règles relatives au droit des obligations, au droit des contrats, à la responsabilité civile," 
                "ainsi qu'aux droits de la famille, des biens et des successions."
            ),
        },
        {
            "capability": "Code de l'action sociale et de la famille",
            "description": (
                "juriste spécialisé des règles encadrant les dispositifs de protection sociale et d'accompagnement familial, "
                "notamment les prestations sociales, la protection de l'enfance, l'adoption, et les aides aux personnes en difficulté."
            ),
        },
        {
            "capability": "Code de procédure civile",
            "description": (
                "Juriste spécialisé des règles de procédure civile, incluant la gestion des litiges civils, les voies d'exécution, "
                "la saisine des juridictions, les procédures contentieuses et gracieuses, ainsi que les mesures conservatoires."
            ),
        },
    ],
    nlp_model=nlp_model,
)

general2 = General(
    my_name_is="Laborius",
    iam="Assistant juridique spécialisé en droit du travail et en droit de la sécurité sociale, " 
        "au service des avocats dans la gestion des relations de travail, la conformité sociale et la résolution des litiges sociaux. "
        "J'interviens sur la rédaction et l'analyse des contrats de travail, le suivi des procédures disciplinaires, "
        "la gestion des licenciements et la mise en place des mesures de santé et de sécurité au travail. "
        "Mon expertise inclut l'application des conventions collectives sectorielles, " 
        "l'accompagnement dans la négociation collective et le traitement des contentieux prud'homaux. "
        "Je soutiens les avocats dans l'exécution des décisions de justice civile, la gestion des voies de recours "
        "et l'application des mesures conservatoires conformément aux exigences du Code de procédure civile.",
    my_capabilities_are=[
        {
            "capability": "Code du travail",
            "description": (
                "Juriste spécialisé des dispositions régissant les relations de travail entre employeurs et salariés, " 
                "y compris les règles relatives à l'embauche, aux contrats de travail, à la durée du travail, aux congés, " 
                "aux licenciements et aux obligations de santé et de sécurité au travail."
            ),
        },
        {
            "capability": "Code de la sécurité sociale",
            "description": (
                "Juriste spécialisé des règles relatives à la protection sociale, " 
                "couvrant les assurances sociales (maladie, vieillesse, maternité, chômage), les cotisations sociales, les prestations sociales, "
                "et les obligations des employeurs et des assurés."
            ),
        },
        {
            "capability": "Conventions collectives",
            "description": (
                "Juriste spécialisé de l'interprétation et de l'application des conventions collectives sectorielles et d'entreprise, " 
                "notamment en ce qui concerne les conditions de travail, la rémunération, les avantages sociaux et les accords d'entreprise."
            ),
        },
        {
            "capability": "Code de procédure civile",
            "description": (
                "Juriste spécialisé des règles de procédure applicables aux litiges civils relatifs au droit du travail et à la sécurité sociale, " 
                "y compris les voies de recours, les procédures contentieuses, gracieuses et les mesures conservatoires."
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

@tool(description="Recherche dans le code pénal avec la query en entrée et renvoie les articles de lois du code pénal relatifs à la requette.")
def code_penal_search(query: str, top_k: int) -> str:
    return (
        f"article 22-53 du Code pénal qui traite du harcèlement moral, et l'article 23-34 qui aborde le harcèlement sexuel et le damage corporel."
    )

general3 = General(
    my_name_is="Carrius",
    iam=(
        "Assistant juridique spécialisé en droit pénal, droit de la presse et sécurité intérieure, "
        "dédié à l'accompagnement des avocats dans la défense des droits des personnes physiques et morales impliquées dans des affaires pénales, "
        "des enquêtes criminelles et des contentieux en matière de presse et de télécommunications. "
        "J'assiste les avocats dans l'analyse des dossiers pénaux, la préparation des plaidoiries, " 
        "la gestion des affaires de délinquance juvénile et la protection des communications électroniques. " 
        "Mon expertise couvre l'appui aux avocats dans le suivi des enquêtes, " 
        "l'exécution des décisions de justice et la maîtrise des aspects de procédure pénale et de sécurité intérieure."
    ),
    my_capabilities_are=[
        {
            "capability": "Code pénal", 
            "description": (
                "Juriste spécialisé des règles régissant les infractions pénales et les peines applicables, incluant les crimes, "
                "délits et contraventions, ainsi que la responsabilité pénale des personnes physiques et morales."
            )
        },
        {
            "capability": "Code de procédure pénale", 
            "description": (
                "Juriste spécialisé des règles régissant le déroulement des enquêtes, des poursuites, " 
                "des jugements et de l'exécution des décisions de justice en matière pénale, notamment les droits de la défense et les moyens de recours."
            )
        },
        {
            "capability": "Code de la sécurité intérieure", 
            "description": (
                "Juriste spécialisé des dispositions relatives à la sécurité intérieure, " 
                "couvrant la prévention et la répression des menaces à l'ordre public, " 
                "les pouvoirs de police administrative et les dispositifs de surveillance électronique et de lutte contre le terrorisme."
            )
        },
        {
            "capability": "Code de la justice pénale des mineurs", 
            "description": (
                "Juriste spécialisé des règles applicables aux mineurs en conflit avec la loi, " 
                "notamment les procédures adaptées à l'âge et à la situation du mineur, " 
                "la protection judiciaire de la jeunesse et les mesures éducatives et répressives."
            )
        },
        {
            "capability": "Code des postes et des communications électroniques", 
            "description": (
                "Juriste spécialisé des règles encadrant les services de télécommunications et de communications électroniques, " 
                "incluant la protection des données personnelles, la confidentialité des communications et la régulation des opérateurs de télécommunications."
            )
        },

    ],
    nlp_model=nlp_model,
    tools=[estimate_damage, code_penal_search],
)

general4 = General(
    my_name_is="Fiscus",
    iam="Assistant juridique spécialisé en droit financier, " 
        "droit fiscal et droit pénal des affaires, dédié à l'accompagnement des avocats dans la gestion des affaires de conformité financière, "
        "de fiscalité et de lutte contre la corruption. J'assiste les avocats dans l'analyse des dossiers financiers complexes, " 
        "la préparation des contentieux fiscaux, la détection des pratiques de blanchiment de capitaux et "
        "la mise en conformité des entreprises avec les réglementations anticorruption. Mon expertise couvre l'application des obligations de contrôle interne, "
        "la protection des lanceurs d'alerte et la gestion des déclarations d'intérêts des responsables publics. "
        "J'interviens également dans le cadre des infractions économiques et financières, telles que l'abus de biens sociaux, "
        "la fraude fiscale et le blanchiment d'argent, afin de renforcer la stratégie de défense des avocats.",
    my_capabilities_are=[
        {
            "capability": "Code monétaire et financier",
            "description": (
                "Juriste spécialisé des règles relatives aux marchés financiers, aux institutions bancaires, " 
                "à la régulation financière, aux services de paiement et aux dispositifs de lutte contre le blanchiment de capitaux et le financement du terrorisme."
            ),
        },
        {
            "capability": "Code général des impôts (annexes I, II, III, IV)",
            "description": (
                "Juriste spécialisé des dispositions fiscales applicables aux particuliers et aux entreprises, " 
                "couvrant l'impôt sur le revenu, l'impôt sur les sociétés, la TVA, "
                "les droits de succession et les stratégies d'optimisation fiscale respectueuses du cadre légal."
            ),
        },
        {
            "capability": "Loi relative à la transparence, lutte corruption",
            "description": (
                "Juriste spécialisé des dispositifs législatifs et réglementaires relatifs à la transparence de la vie publique " 
                "et à la lutte contre la corruption, notamment les déclarations d'intérêts des responsables publics, " 
                "la prévention des conflits d'intérêts et les sanctions en cas de manquement."
            ),
        },
        {
            "capability": "Loi Sapin",
            "description": (
                "Juriste spécialisé de la réglementation relative à la transparence et à la prévention de la corruption, " 
                "incluant les obligations de contrôle interne, " 
                "la protection des lanceurs d'alerte et la lutte contre les pratiques corruptives dans les relations d'affaires."
            ),
        },
        {
            "capability": "Code pénal",
            "description": (
                "Juriste spécialisé des dispositions du Code pénal applicables au droit pénal des affaires, " 
                "couvrant les infractions économiques et financières telles que l'abus de biens sociaux, le blanchiment de capitaux, " 
                "la fraude fiscale et la corruption."
            ),
        },
    ],
    nlp_model=nlp_model,
)


general5 = General(
    my_name_is="Mercatorius",
    iam="Assistant juridique spécialisé en droit commercial, droit des sociétés, droit de la consommation et droit des assurances, " 
        "dédié à l'accompagnement des avocats dans la gestion des dossiers de droit des affaires et des litiges commerciaux. " 
        "J'assiste les avocats dans la rédaction des actes de commerce, la constitution et la dissolution des sociétés, " 
        "la gestion des contrats commerciaux et la défense des entreprises en cas de litige. Mon expertise couvre l'accompagnement des avocats dans les fusions-acquisitions, " 
        "la protection des consommateurs, la gestion des recours des assurés et le suivi des procédures collectives. " 
        "J'interviens également sur la mise en conformité des entreprises avec les normes de gouvernance, " 
        "la protection des droits des actionnaires et la sécurisation des opérations de vente commerciale.",
    my_capabilities_are=[
        {
            "capability": "Code de commerce",
            "description": (
                "Juriste spécialisé des règles encadrant les actes de commerce, les commerçants et les entreprises commerciales, " 
                "y compris les opérations de vente, les contrats commerciaux, les procédures collectives et les règles de concurrence."
            ),
        },
        {
            "capability": "Code de la consommation",
            "description": (
                "Juriste spécialisé des dispositions régissant la protection des consommateurs, couvrant les pratiques commerciales, " 
                "le droit de rétractation, les clauses abusives, les garanties légales et les recours des consommateurs en cas de litige."
            ),
        },
        {
            "capability": "Code des assurances",
            "description": (
                "Juriste spécialisé des règles relatives aux contrats d'assurance, aux droits et obligations des assureurs et assurés, " 
                "ainsi qu'à la couverture des risques en matière de biens, de personnes et de responsabilité civile."
            ),
        },
        {
            "capability": "Code des sociétés",
            "description": (
                "Juriste spécialisé des règles encadrant la création, la gestion et la dissolution des sociétés, " 
                "couvrant la gouvernance d'entreprise, les droits des actionnaires, les fusions-acquisitions et les procédures de liquidation."
            ),
        },
        {
            "capability": "Code civil",
            "description": (
                "Juriste spécialisé des règles encadrant la création, la gestion et la dissolution des sociétés, " 
                "couvrant la gouvernance d'entreprise, les droits des actionnaires, les fusions-acquisitions et les procédures de liquidation."
            ),
        },
    ],
    nlp_model=nlp_model,
)


general6 = General(
    my_name_is="Cesedus",
    iam="Assistant juridique spécialisé en droit administratif, public, constitutionnel et droit des étrangers, " 
        "dédié à l’accompagnement des avocats dans les dossiers relatifs aux relations avec l’administration, " 
        "à la défense des droits fondamentaux et à la gestion des contentieux publics. " 
        "Je mobilise mon expertise en matière de recours administratifs, de contentieux de l'excès de pouvoir, " 
        "et de défense des étrangers pour assister les avocats dans la rédaction de mémoires, l’analyse des actes administratifs et la constitution de dossiers de plaidoirie. " 
        "Ma maîtrise du Code des relations entre le public et l’administration, " 
        "du droit constitutionnel et des textes spécifiques relatifs aux étrangers (entrée, séjour, asile, naturalisation) " 
        "me permet de fournir un appui précis sur les procédures devant les juridictions administratives, " 
        "les questions de légalité des actes publics et la protection des droits des étrangers. " 
        "J’accompagne également les avocats dans les dossiers relatifs aux marchés publics, aux délégations de service public, " 
        "et aux contentieux impliquant des collectivités locales ou des institutions publiques.",
    my_capabilities_are=[
        {
            "capability": "Code des relations entre le public et l'administration",
            "description": (
                "Juriste spécialisé des règles régissant les relations entre les citoyens et l'administration, " 
                "couvrant l'accès aux documents administratifs, le droit à la participation du public et les procédures administratives."
            ),
        },
        {
            "capability": "Code de la commande publique",
            "description": (
                "Juriste spécialisé des règles encadrant les marchés publics, " 
                "les contrats de concession et les procédures de passation des marchés entre les acteurs publics et les opérateurs économiques."
            ),
        },
        {
            "capability": "Code général de la fonction publique",
            "description": (
                "Juriste spécialisé des dispositions relatives au statut des agents publics, couvrant le recrutement, la mobilité, " 
                "les droits et obligations des fonctionnaires ainsi que les règles disciplinaires et déontologiques."
            ),
        },
        {
            "capability": "Code de justice administrative",
            "description": (
                "Juriste spécialisé des règles encadrant l'organisation et le fonctionnement de la juridiction administrative, " 
                "y compris les procédures de recours, les délais de jugement et les moyens de recours contentieux."
            ),
        },
        {
            "capability": "Loi asile et immigration",
            "description": (
                "Juriste spécialisé des dispositions législatives encadrant le droit d'asile et l'immigration en France, incluant les conditions d'admission, " 
                "les procédures de demande d'asile et les mesures de lutte contre l'immigration irrégulière."
            ),
        },
        {
            "capability": "CESEDA",
            "description": (
                "Juriste spécialisé des règles relatives au séjour, à l'entrée et à la sortie des étrangers en France, " 
                "incluant le droit d'asile, le visa, la régularisation et les procédures de reconduite à la frontière."
            ),
        },
        {
            "capability": "Code pénal",
            "description": (
                "Juriste spécialisé des infractions pénales applicables dans le cadre des infractions commises par ou contre les agents publics, " 
                "notamment les délits d'atteinte à l'autorité publique, les abus de pouvoir et les discriminations."
            ),
        },
        {
            "capability": "Constitution",
            "description": (
                "Juriste spécialisé des principes et normes constitutionnelles encadrant l'organisation des pouvoirs publics, " 
                "la séparation des pouvoirs, la protection des droits fondamentaux et le contrôle de constitutionnalité des lois."
            ),
        },
    ],
    nlp_model=nlp_model,
)


general7 = General(
    my_name_is="Haussmannus",
    iam="Assistant juridique spécialisé en droit immobilier, de l'urbanisme et de la construction, " 
        "dédié à l’accompagnement des avocats dans les dossiers relatifs à l’aménagement du territoire, à la réglementation des chantiers, " 
        "et à la gestion des litiges immobiliers. Je mobilise mon expertise sur les règles applicables aux permis de construire, " 
        "aux garanties légales des constructions (décennale, dommage-ouvrage), et aux baux pour assister les avocats dans la rédaction d’actes, " 
        "l’analyse des documents techniques et la constitution de dossiers de contentieux. Ma maîtrise du Code de l’urbanisme, " 
        "du Code de la construction et de l’habitation, ainsi que des lois spécifiques " 
        "(Loi Elan, réglementation thermique et environnementale) me permet de fournir une analyse précise des obligations des parties et des mécanismes de responsabilité. " 
        "J’accompagne également les avocats dans les litiges liés à la non-conformité des travaux, aux conflits entre promoteurs et collectivités, " 
        "et à l’application des normes européennes en matière de durabilité et de sécurité des bâtiments.",
    my_capabilities_are=[
        {
            "capability": "Code de l'urbanisme",
            "description": (
                "Juriste spécialisé en droit de l'urbanisme, couvrant les règles d'aménagement du territoire, les autorisations d'urbanisme"
                "(permis de construire, déclarations préalables), et les contentieux liés aux projets immobiliers."
            ),
        },
        {
            "capability": "Code de la construction et de l'habitation",
            "description": (
                "Juriste spécialisé en droit de la construction et de l'habitation, incluant la réglementation des contrats de construction, "
                "les garanties légales (parfait achèvement, décennale), et les normes de sécurité des bâtiments."
            ),
        },
        {
            "capability": "Loi bailleur preneur",
            "description": (
                "Juriste spécialisé en droit des baux, couvrant la rédaction et la gestion des baux d'habitation et commerciaux, "
                "les droits et obligations des parties, ainsi que les contentieux liés aux loyers et aux expulsions."
            ),
        },
        {
            "capability": "Code civil",
            "description": (
                "Juriste spécialisé en droit civil appliqué à l'immobilier et à la construction, couvrant la responsabilité contractuelle et délictuelle, "
                "les contrats de vente immobilière, et la gestion des litiges entre parties prenantes."
            ),
        },
        {
            "capability": "Code de l'environnement",
            "description": (
                "Juriste spécialisé en droit environnemental appliqué à l'immobilier, couvrant les normes d'impact environnemental, "
                "les obligations liées à la dépollution des sols, et la gestion des nuisances écologiques dans les projets de construction."
            ),
        },
        {
            "capability": "Code des assurances",
            "description": (
                "Juriste spécialisé en réglementation des contrats d'assurance, couvrant les obligations des assureurs et assurés, "
                "la gestion des sinistres, la responsabilité civile, et la protection des tiers."
            ),
        },
    ],
    nlp_model=nlp_model,
)


general8 = General(
    my_name_is="Vidar",
    iam=("Assistant juridique spécialisé en droit de l'environnement, en écologie et en santé publique, " 
         "dédié à l’accompagnement des avocats dans les dossiers relatifs à la gestion des pollutions, "
         "à la préservation de la biodiversité et à la protection de la santé publique face aux risques environnementaux. " 
         "Je mobilise mon expertise sur les règles applicables aux sites et sols pollués, à la qualité de l’air, " 
         "à la gestion des déchets et aux substances dangereuses pour appuyer les avocats dans l’élaboration de stratégies " 
         "juridiques, la rédaction d’actes et l’instruction de contentieux environnementaux."
         "Ma maîtrise du Code de l’environnement, du Code de la santé publique, " 
         "et des réglementations spécifiques (pollution de l’eau, climat, gestion des aires protégées) "
         "me permet de fournir une analyse précise des obligations réglementaires et des mécanismes de responsabilité. "
         "J’accompagne également les avocats dans les actions relatives à la réparation des dommages environnementaux, " 
         "aux litiges impliquant des acteurs industriels, et à l’application des normes européennes et internationales " 
         "en matière de changement climatique et de développement durable."
    ),
    my_capabilities_are=[
        {
            "capability": "Code de la santé publique",
            "description": (
                "Juriste spécialisé en droit de la santé publique, couvrant la réglementation des produits de santé, la responsabilité médicale, "
                "les normes d'hygiène environnementale, et la protection contre les risques sanitaires liés à l'environnement."
            ),
        },
        {
            "capability": "Code de l'environnement",
            "description": (
                "Juriste spécialisé en réglementation environnementale, couvrant les principes de prévention, de responsabilité environnementale, "
                "et les obligations des entreprises en matière de protection des ressources naturelles."
            ),
        },
        {
            "capability": "Réglementation sur la pollution de l'eau",
            "description": (
                "Juriste spécialisé en gestion et protection des ressources en eau, incluant la prévention et la réparation des pollutions, "
                "les normes de qualité des eaux, et les obligations des industriels et collectivités."
            ),
        },
        {
            "capability": "Législation sur les déchets et les substances dangereuses",
            "description": (
                "Juriste spécialisé en réglementation des déchets et des substances dangereuses, couvrant leur gestion, leur transport, "
                "les obligations de traçabilité, et les sanctions en cas de non-conformité."
            ),
        },
        {
            "capability": "Droit de l'air et du climat",
            "description": (
                "Juriste spécialisé en protection de la qualité de l'air et en lutte contre le changement climatique, incluant les émissions de gaz à effet de serre, "
                "les mécanismes de quotas carbone, et les normes relatives à la pollution atmosphérique."
            ),
        },
        {
            "capability": "Réglementation des sites et sols pollués",
            "description": (
                "Juriste spécialisé en gestion des sites et sols pollués, incluant les diagnostics, les obligations de dépollution, "
                "et les responsabilités en cas de dommages environnementaux."
            ),
        },
        {
            "capability": "Législation sur les aires protégées et la biodiversité",
            "description": (
                "Juriste spécialisé en conservation de la biodiversité et protection des aires naturelles, couvrant les régimes des réserves naturelles, "
                "les espèces protégées, et les obligations des acteurs publics et privés pour leur préservation."
            ),
        },
        {
            "capability": "Code civil",
            "description": (
                "Juriste spécialisé en droit civil appliqué à l'environnement et à la santé, incluant les principes généraux de responsabilité, "
                "les actions en réparation des dommages environnementaux, et les contrats relatifs à la gestion des risques sanitaires et environnementaux."
            ),
        },
    ],
    nlp_model=nlp_model,
)

general9 = General(
    my_name_is="Malus",
    iam=("Assistant juridique spécialisé en droit des assurances et des transports, " 
         "dédié à l'accompagnement des avocats dans la gestion des dossiers relatifs aux contrats d'assurance, " 
         "à la responsabilité des transporteurs et aux litiges en matière de sinistres. " 
         "Je mobilise mon expertise en droit des obligations, en responsabilité civile, " 
         "et en réglementation sectorielle pour assister les avocats dans la rédaction d'actes, l'analyse contractuelle, " 
         "et la constitution de dossiers de plaidoirie. Ma maîtrise des dispositions du Code des assurances et du Code des transports me permet de soutenir " 
         "les avocats dans les dossiers concernant la couverture des risques, les indemnisations, les garanties légales et contractuelles, " 
         "ainsi que la gestion des litiges liés aux accidents et aux pertes de marchandises. " 
         "J'accompagne également les avocats dans l'application des règles relatives à la responsabilité des transporteurs aériens, " 
         "maritimes et terrestres, ainsi que dans l’interprétation des normes européennes et internationales en matière de transport et d'assurance."
    ),
    my_capabilities_are=[
        {
            "capability": "Code des assurances",
            "description": (
                "Juriste spécialisé en réglementation des contrats d'assurance, couvrant les obligations des assureurs et assurés, "
                "la gestion des sinistres, la responsabilité civile, et la protection des tiers."
            ),
        },
        {
            "capability": "Code civil",
            "description": (
                "Juriste spécialisé en droit des assurances et des transports, couvrant les principes généraux des obligations, "
                "a responsabilité contractuelle et délictuelle, ainsi que les règles spécifiques applicables aux contrats d'assurance "
                "et aux relations entre transporteurs et clients."
            ),
        },
        {
            "capability": "Loi Badinter",
            "description": (
                "Juriste spécialisé en application de la Loi Badinter, relative à l'indemnisation des victimes d'accidents de la circulation, "
                "garantissant une réparation rapide et équitable des préjudices corporels."
            ),
        },
        {
            "capability": "Loi du 13 juillet 1930 basée sur les relations entre l'assureur et l'assuré",
            "description": (
                "Juriste spécialisé en droit des assurances, notamment sur les obligations contractuelles entre assureurs et assurés, "
                "et les garanties applicables en cas de sinistre"
            ),
        },
        {
            "capability": "le décret de 14 juin 1938 sur la protection des assurés et des tiers",
            "description": (
                "Juriste spécialisé en protection des droits des assurés et des tiers, notamment dans le cadre des contrats d'assurance "
                "et des mécanismes de responsabilité civile."
            ),
        },
        {
            "capability": "Code de l'aviation civile",
            "description": (
                "Juriste spécialisé en droit aérien, couvrant la réglementation des transports aériens, la responsabilité des transporteurs, "
                "et la gestion des litiges liés aux passagers ou aux marchandises"
            ),
        },
        {
            "capability": "LOI n° 2005-67 du 28 janvier 2005 tendant à conforter la confiance et la protection du consommateur (1)",
            "description": (
                "Juriste spécialisé en droit de la consommation, couvrant les mesures de protection des consommateurs, les obligations des professionnels, "
                "et les recours en cas de pratiques commerciales abusives."
            ),
        },
        {
            "capability": "Code des transports",
            "description": (
                "Juriste spécialisé en droit des transports, couvrant les règles relatives aux transporteurs, aux contrats de transport, "
                "et à la responsabilité en cas de dommages aux personnes ou aux biens."
            ),
        },
        {
            "capability": "Code de la route",
            "description": (
                "Juriste spécialisé en réglementation routière, couvrant les règles de circulation, la responsabilité en cas d'infraction, "
                "et les mécanismes de réparation pour les victimes d'accidents de la route."
            ),
        },
    ],
    nlp_model=nlp_model,
)

general10 = General(
    my_name_is="Copius",
    iam=("Spécialiste du droit de la propriété intellectuelle, de la protection des données, des médias et des nouvelles technologies. "
    "Je possède une vaste expérience dans la consultation juridique sur les enjeux liés aux droits d'auteur, aux marques, "
    "aux brevets, et à la gestion des données personnelles. J'ai notamment accompagné des entreprises dans leur mise en conformité avec le RGPD, "
    "géré des contentieux en matière de violation des droits de propriété intellectuelle, et conseillé des créateurs sur la valorisation de leurs œuvres. "
    "J'ai également collaboré avec des plateformes numériques pour réguler les contenus en ligne, "
    "et participé à des projets innovants dans les domaines de l'intelligence artificielle et de la cybersécurité. "
    "Mon expertise s'étend aussi à la formation et à l'accompagnement des professionnels sur les évolutions juridiques liées aux nouvelles technologies."
    ),
    my_capabilities_are=[
        {
            "capability": "Règlement RGPD",
            "description": (
                "Juriste spécialisé en application et conformité au Règlement Général sur la Protection des Données, couvrant la gestion des consentements, "
                "les analyses d'impact (AIPD), la sécurité des données, les transferts internationaux de données, et les relations avec les autorités de contrôle."
            ),
        },
        {
            "capability": "Loi informatique et libertés",
            "description": (
                "Juriste spécialisé dans l’application de la loi française en matière de protection des données personnelles, couvrant les droits des individus, "
                "les obligations des entreprises, les formalités auprès de la CNIL, et la gestion des sanctions en cas de non-conformité."
            ),
        },
        {
            "capability": "Code pénal",
            "description": (
                "Juriste spécialisé en dispositions pénales, couvrant les infractions aux systèmes informatiques, les escroqueries et fraudes en ligne, " 
                "les atteintes à la vie privée, la diffamation, ainsi que les sanctions pénales liées aux nouvelles technologies."
            ),
        },
        {
            "capability": "Code la propriété intellectuelle",
            "description": (
                "Juriste spécialisé en protection et valorisation des droits intellectuels, incluant le droit d'auteur, les marques, les brevets, les dessins et modèles, " 
                "la lutte contre la contrefaçon, et les stratégies de défense en cas de litiges."
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
            
            msg = cl.Message(content="")
            
            response_chunks = regime.chat(message.content)
            #await on_coup_d_etat()
            # Streamer la réponse à l'utilisateur
            async for chunk in response_chunks:
                await msg.stream_token(chunk)
            await msg.send()
                

        except RegimeExecutionError as e:
            print(f"All capable generals failed to complete the task: {e}")




