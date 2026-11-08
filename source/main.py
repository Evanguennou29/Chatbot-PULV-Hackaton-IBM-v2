import csv
from threading import Lock

from flask import Flask, jsonify, render_template, request
from Generate import ConfigurationError, query
from config import DATASET_PATH

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
feedback_lock = Lock()


def generate_answer(question):
    return query(question)


def payload():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def text_field(data, key):
    value = data.get(key)
    return value.strip() if isinstance(value, str) else ""


@app.get("/")
def ask():
    return render_template("ask.html")


@app.get("/health")
def health():
    # Liveness only: never makes a paid IBM request.
    if not DATASET_PATH.is_file():
        return jsonify(status="error", error="Jeu de données introuvable"), 503
    return jsonify(status="ok")


@app.post("/answer")
def answer():
    question = text_field(payload(), "question")
    if not question:
        return jsonify(error="Aucune question reçue"), 400
    if len(question) > 2000:
        return jsonify(error="La question est limitée à 2 000 caractères"), 400
    try:
        answer_text = generate_answer(question)
    except ConfigurationError as error:
        return jsonify(error=str(error)), 503
    except Exception:
        app.logger.exception("Échec de génération watsonx.ai")
        return jsonify(error="Le service de réponse est indisponible. Réessayez plus tard."), 502
    return jsonify(question=question, answer=answer_text)


@app.post("/satisfied")
def satisfied():
    data = payload()
    question, answer_text = text_field(data, "question"), text_field(data, "answer")
    if not question or not answer_text:
        return jsonify(error="Question ou réponse manquante"), 400
    if len(question) > 2000 or len(answer_text) > 10000:
        return jsonify(error="Question ou réponse trop longue"), 400

    # A single Gunicorn worker owns this CSV; threads share this lock.
    with feedback_lock:
        with DATASET_PATH.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fieldnames = reader.fieldnames
            if not fieldnames or not {"id", "Title", "Content"}.issubset(fieldnames):
                return jsonify(error="Structure du jeu de données invalide"), 500
            last_id = max((int(row["id"]) for row in reader), default=0)
        new_id = last_id + 1
        with DATASET_PATH.open("a", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writerow({"id": new_id, "Title": question, "Content": answer_text})
    return jsonify(success=True, id=new_id)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
