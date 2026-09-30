import os
from ibm_watsonx_ai import Credentials
import csv

api_key = os.getenv("IBM_CLOUD_API_KEY")
if not api_key:
    raise RuntimeError("Définis la variable d’environnement IBM_CLOUD_API_KEY avant de lancer l’application.")

credentials = Credentials(
    url="https://ca-tor.ml.cloud.ibm.com",
    api_key=api_key
)

model_id = "meta-llama/llama-3-2-11b-vision-instruct"

parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 200,
    "min_new_tokens": 0,
    "repetition_penalty": 1
}

project_id = "978cff27-80af-4f9f-9f5f-3635cd18feef"
space_id = os.getenv("SPACE_ID")

from ibm_watsonx_ai.foundation_models import ModelInference

model = ModelInference(
    model_id = model_id,
    params = parameters,
    credentials = credentials,
    project_id = project_id,
    space_id = space_id
    )



def query(question):

    # path csv file
    csv_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset", "data_pretraitee.csv"))

    prompt_input = ""

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row['Title'].strip()
            content = row['Content'].strip()
            # add to prompt_input
            prompt_input += f"Entrée : {title}\nSortie : {content}\n\n"


    prompt_input += f"\nEntrée : {question}\nSortie : \n"


    generated_response = model.generate_text(prompt=prompt_input, guardrails=False)
    cleaned_response = generated_response.split('\nEntrée')[0].replace("\n",' ')
    cleaned_response= cleaned_response if ("Entrée : " not in cleaned_response and "Sortie : " not in cleaned_response)  else "Sorry, I don't have the answer.\n Please contact: scolarite-esilv@devinci.fr"
    return cleaned_response
