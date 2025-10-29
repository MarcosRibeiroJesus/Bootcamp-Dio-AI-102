from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from io import BytesIO
import logging

from utils.extractors import extract_text_from_pdf, extract_text_from_docx
from services.services import translator

bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx"}


def allowed_filename(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/translate/upload", methods=["POST"])
def translate_upload():
    if "file" not in request.files:
        return jsonify({"error": "Missing file field"}), 400
    file = request.files["file"]
    lang = request.form.get("lang", "português")

    logging.info("Language for translation: %s", lang)

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_filename(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()

    try:
        file_bytes = file.read()
        if ext == "pdf":
            text = extract_text_from_pdf(BytesIO(file_bytes))
        else:
            text = extract_text_from_docx(BytesIO(file_bytes))

        if not text:
            return jsonify({"error": "No text extracted from file"}), 422

        translated = translator.translate_text(text, lang)
        return jsonify({"translation": translated}), 200
    except Exception as e:
        logging.exception("Error translating uploaded file")
        return jsonify({"error": str(e)}), 500
