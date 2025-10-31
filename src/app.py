import os
import logging
from flask import Flask

from .config.logging_config import configure_logging
from dotenv import load_dotenv

from .config.flask_config import configure_flask
from .config.storage_client_config import init_blob_service
from .services.document_intelligence.client import DocumentIntelligenceClient
from .routes.document_intelligence_routes import create_document_intelligence_blueprint

configure_logging()
log = logging.getLogger("anti_fraud_app")

load_dotenv()

# Create Flask app and apply configuration
app = Flask(__name__)
configure_flask(app)

# Initialize services
blob_service = init_blob_service()
di_client = DocumentIntelligenceClient()

# Register document intelligence blueprint
doc_bp = create_document_intelligence_blueprint(blob_service, di_client)
app.register_blueprint(doc_bp)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8181))
    log.info("Starting anti-fraud app on port %s", port)
    app.run(host="0.0.0.0", port=port)
