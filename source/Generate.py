import csv
import os
from functools import lru_cache

from config import DATASET_PATH


class ConfigurationError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_model():
    """Connect only when a question is asked; the site can boot without IBM."""
    api_key = os.getenv("IBM_CLOUD_API_KEY", "").strip()
    project_id = os.getenv("WATSONX_PROJECT_ID", "").strip()
    space_id = os.getenv("SPACE_ID", "").strip()
    if not api_key or bool(project_id) == bool(space_id):
        raise ConfigurationError(
            "Configurez IBM_CLOUD_API_KEY et un seul identifiant : "
            "WATSONX_PROJECT_ID ou SPACE_ID."
        )

    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference

    return ModelInference(
        model_id=os.getenv("WATSONX_MODEL_ID", "meta-llama/llama-3-2-11b-vision-instruct"),
        params={"decoding_method": "greedy", "max_new_tokens": 200,
                "min_new_tokens": 0, "repetition_penalty": 1},
        credentials=Credentials(
            url=os.getenv("WATSONX_URL", "https://ca-tor.ml.cloud.ibm.com"),
            api_key=api_key,
        ),
        **({"project_id": project_id} if project_id else {"space_id": space_id}),
    )


def query(question):
    model = get_model()
    examples = []
    with DATASET_PATH.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            examples.append(f"Entrée : {row['Title'].strip()}\nSortie : {row['Content'].strip()}\n\n")
    prompt = "".join(examples) + f"\nEntrée : {question}\nSortie : \n"
    response = model.generate_text(prompt=prompt, guardrails=False)
    cleaned = response.split("\nEntrée")[0].replace("\n", " ").strip()
    if not cleaned or "Entrée : " in cleaned or "Sortie : " in cleaned:
        return "Je n’ai pas de réponse fiable. Contactez votre scolarité : scolarite-esilv@devinci.fr"
    return cleaned
