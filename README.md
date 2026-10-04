# LeoChat Projet hackathon IBM

Prototype de chatbot basé sur IBM watsonx.ai et un jeu de questions/réponses. 

## Lancer le prototype Python

Prérequis : Python 3.9+, un projet watsonx.ai actif et une clé IBM Cloud.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install flask ibm-watsonx-ai
$secret = Read-Host "Clé IBM Cloud" -AsSecureString
$env:IBM_CLOUD_API_KEY = [System.Net.NetworkCredential]::new("", $secret).Password
$env:SPACE_ID = "votre_space_id"
python source/main.py
```

La variable `IBM_CLOUD_API_KEY` est lue depuis l’environnement. Ne place jamais sa valeur dans le code, un fichier suivi par Git ou le JavaScript du site. L’application utilise `dataset/data_pretraitee.csv` avec un chemin relatif au dépôt.

## Présentation GitHub Pages

Dans **Settings → Pages**, sélectionne **Deploy from a branch**, `main`, puis `/docs`. Le site est statique et ne requiert aucune clé IBM.


