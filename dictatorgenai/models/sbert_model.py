from sentence_transformers import SentenceTransformer, util
import torch


class SBERTModel:
    def __init__(self):
        self.model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

    def evaluate(self, capabilities: list[str], task: str):
        task_embedding = self.model.encode(task, convert_to_tensor=True)
        capability_embeddings = self.model.encode(
            ",".join(capabilities), convert_to_tensor=True
        )

        # Calculer les similarités cosinus
        similarities = util.pytorch_cos_sim(task_embedding, capability_embeddings)
        max_similarity = torch.max(similarities).item()

        if max_similarity > 0.8:
            return "entirely"
        elif max_similarity > 0.5:
            return "partially"
        else:
            return "no"

    def can_perform_coup(self, capabilities, task):
        evaluation = self.evaluate(capabilities, task)
        return evaluation in ["entirely", "partially"]
