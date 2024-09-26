from typing import Callable

def tool(func: Callable) -> Callable:
    """Marque une fonction comme un tool utilisable par le modèle."""
    func.is_tool = True  # Ajoute un attribut pour indiquer que la fonction est un tool
    return func
