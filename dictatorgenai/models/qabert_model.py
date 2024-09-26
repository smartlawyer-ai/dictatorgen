from transformers import pipeline


class QABERTModel:
    def __init__(self):
        self.model = pipeline(
            "question-answering", model="distilbert-base-cased-distilled-squad"
        )

    def evaluate(self, capabilities: list[str], task: str):
        concat_capabilities = ",".join(capabilities)
        context = f"i have the followings capabilities : {concat_capabilities}. Can i solve this task : {task} ? Yes ? No ? Partially"
        question = "What are you capabilities ?"
        result = self.model(question=question, context=context)
        answer = result["answer"].lower()

        # Interpretation logic for yes, partially, or no
        if "yes" in answer or "definitely" in answer:
            return "entirely"
        elif "maybe" in answer or "possibly" in answer:
            return "partially"
        else:
            return "no"

    def can_perform_coup(self, capabilities, task):
        evaluation = self.evaluate(capabilities, task)
        return evaluation in ["entirely", "partially"]
