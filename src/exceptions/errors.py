import logging
from flask import jsonify, request
from werkzeug.exceptions import BadRequest


def register_error_handlers(app):
    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        try:
            raw = request.get_data().decode("utf-8", errors="replace")
        except Exception:
            raw = "<unable to read body>"
        logging.exception("BadRequest: %s; raw body: %s", e, raw)
        return jsonify({
            "error": "bad_request",
            "message": str(e),
            "raw_body": raw,
        }), 400

    @app.errorhandler(Exception)
    def handle_exception(e):
        logging.exception("Unhandled exception: %s", e)
        return jsonify({
            "error": "internal_error",
            "message": str(e),
        }), 500
