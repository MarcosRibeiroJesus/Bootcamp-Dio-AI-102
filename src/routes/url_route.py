from flask import Blueprint, request, jsonify
import logging

from utils.extractors import extract_text_from_url
from services.services import translator

bp = Blueprint("url", __name__)


@bp.route("/translate/url", methods=["POST"])
def translate_url():
    logging.info("Received /translate/url request")

    # Accept JSON body; let error handlers surface parse errors as JSON
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    lang = data.get("lang", "português")

    logging.info("Language for translation: %s", lang)

    if not url:
        return jsonify({"error": "Missing 'url' in JSON body"}), 400

    try:
        logging.info("Extracting text from URL: %s", url)
        text = extract_text_from_url(url)
        if not text:
            return jsonify({"error": "No text extracted from URL"}), 422

        logging.info("Translating extracted text (len=%d)...", len(text))
        translated = translator.translate_text(text, lang)
        return jsonify({"translation": translated}), 200
    except Exception as e:
        logging.exception("Error translating URL: %s", url)
        return jsonify({"error": str(e)}), 500
