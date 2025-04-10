import os
from dictatorgenai import General, tool
from dictatorgenai.utils.task import Task
from dictatorgenai.models.openai_model import OpenaiModel
import asyncio
from dotenv import load_dotenv  # Optionnel si vous utilisez un fichier .env

# Chargement des variables d'environnement à partir d'un fichier .env
load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY") 
if not api_key:
    raise EnvironmentError(
        "OPENAI_API_KEY is not set in the environment. Please set it before running the script."
    )

class FrenchChefGeneral(General):
    def __init__(self):
        nlp_model_instance = OpenaiModel(api_key=api_key)

        super().__init__(
            my_name_is="French Chef",
            iam="a general specialized in French cuisine",
            my_capabilities_are=[
            {"capability": "cooking", "description": "Expert in preparing French dishes"},
            {"capability": "menu planning", "description": "Skilled in planning diverse menus"},
            {"capability": "kitchen management", "description": "Efficient in managing kitchen operations"}
            ],
            nlp_model=nlp_model_instance
        )
        self.specialties = ["French cuisine", "pastry", "wine pairing"]

if __name__ == "__main__":
    french_chef_general = FrenchChefGeneral()
    print(french_chef_general)

    while True:
        user_input = input("Posez votre question au chef (ou tapez 'exit' pour quitter) : ")
        if user_input.lower() == 'exit':
            break
        task = Task(request=user_input)
        async def main():
            async for chunk in french_chef_general.solve_task(task):
                print(chunk, end='', flush=True)  # Print each chunk as it is received
            print()  # Print a newline after all chunks are received

        asyncio.run(main())