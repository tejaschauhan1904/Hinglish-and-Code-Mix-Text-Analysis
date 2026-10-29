import os
import sys
import json
from flask import Flask, request, jsonify, send_from_directory

# Support running directly or as a module
try:
    from . import db
    from .analyzer import (
        analyze_text,
        analyze_ner,
        analyze_sentiment,
        translate_hinglish_to_english
    )
except (ImportError, ValueError):
    import db
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
    """Fetches datasets directly from Supabase PostgreSQL tables."""
    selected = request.args.get("name", "ner")
    try:
        dataset_info = db.get_dataset(selected)
        return jsonify(dataset_info)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Database query failed: {str(e)}"}), 500

@app.route("/api/presets", methods=["GET"])
def api_presets():
    """Fetches preset examples directly from Supabase PostgreSQL."""
    try:
        presets = db.get_preset_examples()
        return jsonify(presets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/db/status", methods=["GET"])
def api_db_status():
    """Returns live database status and table metrics from Supabase."""
    try:
        status = db.get_db_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/db/refresh", methods=["POST"])
def api_db_refresh():
    """Reloads in-memory cache directly from Supabase."""
    try:
        status = db.refresh_cache()
        return jsonify({"message": "Cache refreshed successfully from Supabase", "status": status})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

def main():
    port = int(os.environ.get("PORT", 8000))
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    print(f"Starting Hinglish NLP Web Server on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
