import os
import sys
import json
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory

# Support running directly or as a module
try:
    from .analyzer import (
        analyze_text,
        analyze_ner,
        analyze_sentiment,
        translate_hinglish_to_english
    )
except (ImportError, ValueError):
    from analyzer import (
        analyze_text,
        analyze_ner,
        analyze_sentiment,
        translate_hinglish_to_english
    )

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
if not os.path.exists(FRONTEND_DIR):
    FRONTEND_DIR = os.path.abspath("frontend")

DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_DIR):
    DATA_DIR = os.path.abspath("data")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    result = analyze_text(text)
    return jsonify(result)

@app.route("/api/ner", methods=["POST"])
def api_ner():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    return jsonify(analyze_ner(text))

@app.route("/api/sentiment", methods=["POST"])
def api_sentiment():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    return jsonify(analyze_sentiment(text))

@app.route("/api/translate", methods=["POST"])
def api_translate():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    return jsonify(translate_hinglish_to_english(text))

@app.route("/api/datasets", methods=["GET"])
def api_datasets():
    datasets = {
        "ner": {
            "title": "Named Entity Recognition (NER) Dataset",
            "file": os.path.join(DATA_DIR, "hinglish_ner_dataset.csv")
        },
        "sentiment": {
            "title": "Sentiment Analysis Dataset",
            "file": os.path.join(DATA_DIR, "hinglish_sentiment_dataset.csv")
        },
        "translation": {
            "title": "Hinglish to English Translation Dataset",
            "file": os.path.join(DATA_DIR, "hinglish_translation_dataset.csv")
        },
        "sample": {
            "title": "Sample Hinglish Corpus",
            "file": os.path.join(DATA_DIR, "sample_hinglish.csv")
        }
    }

    selected = request.args.get("name", "ner")
    if selected not in datasets:
        return jsonify({"error": "Invalid dataset name"}), 404

    target = datasets[selected]
    if not os.path.exists(target["file"]):
        return jsonify({"error": f"File {target['file']} not found"}), 404

    df = pd.read_csv(target["file"])
    records = df.to_dict(orient="records")
    columns = list(df.columns)

    return jsonify({
        "dataset_name": selected,
        "title": target["title"],
        "columns": columns,
        "total_records": len(records),
        "data": records
    })

def main():
    port = int(os.environ.get("PORT", 8000))
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    print(f"Starting Hinglish NLP Web Server on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
