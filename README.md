# LeoChat — assistant étudiant

Prototype étudiant réalisé pour le **hackathon IBM × Pôle Léonard de Vinci (2025), groupe 17**. LeoChat explore une autre façon de consulter le Help Center : poser une question en langage naturel et recevoir une réponse produite avec IBM watsonx.ai à partir d’un jeu de questions/réponses.

**Projet en cours de développement.** La présentation est consultable sans compte IBM ; le chatbot connecté nécessite vos propres accès watsonx.ai. Les informations du CSV sont archivées et ne remplacent pas les règles actuelles de votre école.

## Deux interfaces

- **Présentation** : [site GitHub Pages](https://evanguennou29.github.io/Chatbot-PULV-Hackaton-IBM-v2/), dans `docs/`. Un espace d’exploration avec une conversation d’exemple, son extrait source et des vues dédiées à la vidéo, au projet et à l’équipe. Aucun appel à une IA n’est effectué sur cette page.
- **Chatbot Flask** : dans `source/`. Saisie libre d’une question, génération par watsonx.ai et enregistrement des réponses marquées comme utiles.

## Démarrage avec Docker

Prérequis : Docker Engine ou Docker Desktop **démarré**, avec Docker Compose v2 et les conteneurs Linux.

```bash
git clone https://github.com/Evanguennou29/Chatbot-PULV-Hackaton-IBM-v2.git
cd Chatbot-PULV-Hackaton-IBM-v2
cp .env.example .env
```

Sous PowerShell, remplacer la dernière commande par `Copy-Item .env.example .env`.

Pour les réponses réelles, éditer `.env` et renseigner :

- `IBM_CLOUD_API_KEY` : votre clé IBM Cloud ;
- **soit** `WATSONX_PROJECT_ID`, **soit** `SPACE_ID` : un seul des deux doit être défini ;
- `WATSONX_URL` : l’URL de votre région ;
- `WATSONX_MODEL_ID` : un modèle accessible dans votre projet ou espace.

Le modèle et la région proposés reprennent le prototype d’origine. Vérifier leur disponibilité dans votre compte ; ils ne garantissent pas qu’un modèle reste proposé par IBM. Voir le [guide officiel de configuration watsonx.ai](https://www.ibm.com/watsonx/developer/get-started/quick-start).

```bash
docker compose up --build -d
docker compose ps
```

| Service | Adresse locale |
| --- | --- |
| Présentation | [localhost:8080](http://localhost:8080) |
| Chatbot | [localhost:8000](http://localhost:8000) |
| Santé du chatbot | [localhost:8000/health](http://localhost:8000/health) |

Les ports peuvent être modifiés avec `CHATBOT_PORT` et `PRESENTATION_PORT` dans `.env`. Les services sont accessibles uniquement depuis la machine locale par défaut.

**Sans accès IBM**, laisser les identifiants vides permet tout de même de lancer les interfaces. Une question libre affiche alors un message de configuration (HTTP 503). Pour lancer uniquement la présentation : `docker compose up -d presentation`.

### Données et cycle de vie

Le chatbot utilise un volume nommé `knowledge`, initialisé avec le CSV de l’image au premier lancement. Les retours sont conservés après un redémarrage, une reconstruction ou un `docker compose down`. Un volume déjà créé n’est pas remplacé automatiquement par une nouvelle version du CSV du dépôt.

```bash
docker compose logs -f chatbot
docker compose restart chatbot
docker compose down
```

Sauvegarder le CSV utilisé par le conteneur avant toute réinitialisation :

```bash
docker compose cp chatbot:/app/dataset/data_pretraitee.csv ./data_pretraitee.backup.csv
```

La commande `docker compose down --volumes` supprime aussi les données et les retours du volume. Ne l’utiliser que pour une réinitialisation volontaire après sauvegarde.

L’image Python fonctionne avec un utilisateur non privilégié et Gunicorn. Un seul worker et quatre threads sont configurés pour partager le verrou d’écriture du CSV. Cette persistance convient à une seule instance ; une base de données est nécessaire avant de multiplier les workers ou les réplicas. Le service de présentation utilise Nginx sans privilèges.

## Développement sans Docker

Python **3.12 ou 3.13** est recommandé. Depuis la racine du dépôt :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
set -a
. ./.env
set +a
python source/main.py
```

Copier et remplir `.env.example` au préalable. Le fichier `.env` n’est pas chargé automatiquement par Python ; les commandes ci-dessus l’exportent dans un shell POSIX.

Sous PowerShell :

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$secret = Read-Host "Clé IBM Cloud" -AsSecureString
$env:IBM_CLOUD_API_KEY = [System.Net.NetworkCredential]::new("", $secret).Password
$env:WATSONX_PROJECT_ID = "votre_project_id"
$env:WATSONX_URL = "https://ca-tor.ml.cloud.ibm.com"
$env:WATSONX_MODEL_ID = "meta-llama/llama-3-2-11b-vision-instruct"
python source/main.py
```

Ouvrir [localhost:5000](http://localhost:5000). Le serveur local démarre sans mode debug. Gunicorn est utilisé dans le conteneur Linux ; il ne sert pas au lancement natif Windows.

Pour prévisualiser uniquement la présentation :

```bash
python -m http.server 8080 --directory docs
```

La page conserve la palette anthracite, jaune acide, rose et bleu du site d’origine. Elle utilise Space Grotesk via Google Fonts, avec des polices système de secours si le réseau est indisponible.

## Fonctionnement actuel

1. Le serveur lit `dataset/data_pretraitee.csv` (504 entrées initiales).
2. Il assemble **l’ensemble des exemples** en paires « Entrée / Sortie », puis ajoute la question.
3. Le SDK IBM transmet ce prompt au modèle configuré et renvoie une réponse textuelle.
4. Un retour « Je suis satisfait » ajoute la paire question/réponse au CSV, en préservant ses neuf colonnes.

Il n’y a actuellement ni recherche vectorielle ni sélection des documents pertinents. Le contexte complet peut dépasser la fenêtre du modèle ou augmenter le coût et la latence. Les retours étudiants ne sont pas une validation institutionnelle et ne réentraînent pas le modèle. Aucun historique partagé entre visiteurs n’est renvoyé par l’API.

### Routes

| Méthode | Route | Rôle |
| --- | --- | --- |
| GET | `/` | Interface du chatbot |
| GET | `/health` | Présence du fichier de données ; aucun appel IBM |
| POST | `/answer` | JSON `{"question":"…"}` ; renvoie question et réponse |
| POST | `/satisfied` | JSON `{"question":"…","answer":"…"}` ; ajoute un retour au CSV |

Les requêtes incorrectes reçoivent HTTP 400 ; une configuration IBM absente ou ambiguë, HTTP 503 ; un échec de génération, HTTP 502. La question est limitée à 2 000 caractères et le corps des requêtes à 16 Kio.

## Vérifications

```bash
python -m unittest discover -s tests -v
node --check docs/app.js
docker compose config --quiet
```

Les tests n’utilisent aucune clé IBM : configuration, validation des requêtes, génération simulée, erreurs du fournisseur, conservation des colonnes du CSV et écritures concurrentes. La CI exécute les tests Python puis construit les conteneurs et vérifie le démarrage, les deux interfaces et la persistance après recréation du chatbot. Un appel réel à watsonx.ai doit être vérifié séparément avec un compte et un modèle disponibles.

## Structure du dépôt

```text
├── compose.yaml / Dockerfile     Services locaux et image du chatbot
├── .env.example                 Configuration sans secrets
├── requirements.txt             Dépendances Python directes épinglées
├── source/                      Flask, génération et interface du chatbot
├── dataset/                     Jeu de connaissances initial
├── docs/                        Présentation statique GitHub Pages
├── tests/                       Tests fonctionnels sans accès IBM
├── Documention guideline ppt/   Rapport, présentation et vidéo d’origine
└── certification/               Certifications de l’équipe
```

Pour GitHub Pages : **Settings → Pages → Deploy from a branch → main → /docs**. Le déploiement du site statique ne déploie pas le serveur Flask.

## Suite du projet

- Sélectionner les sources pertinentes avant génération et afficher leurs références.
- Évaluer la qualité des réponses et prévoir une transmission vers la scolarité.
- Séparer les retours proposés des connaissances vérifiées ; ajouter leur modération.
- Ajouter authentification, limitation des requêtes et stockage adapté avant une ouverture publique du chatbot.

La clé IBM reste côté serveur. Ne jamais l’ajouter au dépôt, au JavaScript ou à une capture d’écran. Les questions et les exemples du CSV sont transmis à IBM lors de la génération : ne pas y inclure de données confidentielles.

## Équipe

Lucie Andacic · Evan Guennou · Iyad Hadife · Valentin Huet · Iliana Jaunay · Tiago Machado Monteiro
