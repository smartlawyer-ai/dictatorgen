from transformers import DistilBertTokenizer, DistilBertForMaskedLM
import torch


class DistilBERTModel:
    def __init__(self):
        self.tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
        self.model = DistilBertForMaskedLM.from_pretrained("distilbert-base-uncased")

    def evaluate(self, capabilities, task):
        context = " ".join(capabilities)
        masked_sentence = (
            f"The following capabilities {context} can [MASK] help solve the task: {task}. "
            "The options are entirely, partially, or no."
        )
        inputs = self.tokenizer(masked_sentence, return_tensors="pt")
        mask_token_index = torch.where(
            inputs["input_ids"] == self.tokenizer.mask_token_id
        )[1]

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        mask_token_logits = logits[0, mask_token_index, :]
        top_tokens = torch.topk(mask_token_logits, 3, dim=1).indices[0].tolist()

        token_scores = {
            self.tokenizer.decode([token])
            .strip(): logits[0, mask_token_index, token]
            .item()
            for token in top_tokens
        }
        score_entirely = token_scores.get("entirely", 0)
        score_partially = token_scores.get("partially", 0)
        score_no = token_scores.get("no", 0)

        if score_entirely > max(score_partially, score_no):
            return "entirely", score_entirely
        elif score_partially > max(score_entirely, score_no):
            return "partially", score_partially
        else:
            return "no", score_no

    def can_perform_coup(self, capabilities, task):
        evaluation, score = self.evaluate(capabilities, task)
        return evaluation in ["entirely", "partially"], score
