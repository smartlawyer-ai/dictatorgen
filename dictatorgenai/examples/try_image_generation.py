from diffusers import DiffusionPipeline
import torch
from PIL import Image

# Charger le modèle stable-diffusion
# pipeline = DiffusionPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float16)
# pipeline.to("cpu")  # Utiliser le GPU si disponible

# # Générer une image à partir de la description
# prompt = "An image of a squirrel in Picasso style"
# image = pipeline(prompt).images[0]  # Obtenir la première image générée

# # Afficher l'image avec PIL
# image.show()

# # Sauvegarder l'image si nécessaire
# # image.save("generated_image.png")
