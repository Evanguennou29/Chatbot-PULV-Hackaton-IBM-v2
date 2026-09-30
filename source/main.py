from flask import Flask, render_template, request, jsonify
from Generate import query
import csv
import os
app = Flask(__name__, static_folder='static', template_folder='templates')

history = []  # history of questions and answers
#
def generate_answer(question):
    return query(question)

@app.route('/', methods=['GET'])
def ask():
    return render_template('ask.html')

@app.route('/answer', methods=['POST'])
def answer():
    data = request.get_json()
    question = data.get("question", "").strip()
    if question:
        answer_text = generate_answer(question)
        history.append({ "question": question, "answer": answer_text })
        return jsonify({"question": question, "answer": answer_text, "history": history})
    return jsonify({"error": "Aucune question reçue"}), 400



@app.route('/satisfied', methods=['POST'])
def satisfied():
    data = request.get_json()
    question = data.get("question", "").strip()
    answer = data.get("answer", "").strip()

    if question and answer:
        csv_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset", "data_pretraitee.csv"))

        # Read the last id
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                last_id = int(rows[-1]['id']) if rows else 0
        except FileNotFoundError:
            # If the file does not exist yet
            last_id = 0

        new_id = last_id + 1

        # Writing the new row
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'Title', 'Content']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # if empty, write header
            if f.tell() == 0:
                writer.writeheader()

            writer.writerow({'id': new_id, 'Title': question, 'Content': answer})

        return jsonify({"success": True, "id": new_id})

    return jsonify({"error": "Question ou réponse manquante"}), 400

if __name__ == '__main__':
    app.run(debug=True)
