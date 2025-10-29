import os
import logging
import os
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load env first
load_dotenv()

from config.cors import init_cors
from exceptions.errors import register_error_handlers

# Create app and apply basic configuration
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB

# Initialize CORS (configurable via CORS_ALLOW_ORIGINS env var)
init_cors(app)

# Register error handlers
register_error_handlers(app)

# Health endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

# Register blueprints (routes)
from routes.url_route import bp as url_bp
from routes.upload_route import bp as upload_bp

app.register_blueprint(url_bp)
app.register_blueprint(upload_bp)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("PORT", 8181))
    app.run(host="0.0.0.0", port=port)
