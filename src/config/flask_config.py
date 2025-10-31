from .settings import (
    MAX_CONTENT_LENGTH,
    CONTAINER_BUSINESS_CARD,
    CONTAINER_CONTRACT,
    CONTAINER_CREDIT_CARD,
    CONTAINER_ID_DOCUMENT,
    CONTAINER_INVOICE,
    CONTAINER_RECEIPT,
)
from .cors_config import init_cors


def configure_flask(app):
    """Apply Flask configuration from the centralized settings module."""
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    # Expose container names as config for routes to read
    app.config["CONTAINER_BUSINESS_CARD"] = CONTAINER_BUSINESS_CARD
    app.config["CONTAINER_CONTRACT"] = CONTAINER_CONTRACT
    app.config["CONTAINER_CREDIT_CARD"] = CONTAINER_CREDIT_CARD
    app.config["CONTAINER_ID_DOCUMENT"] = CONTAINER_ID_DOCUMENT
    app.config["CONTAINER_INVOICE"] = CONTAINER_INVOICE
    app.config["CONTAINER_RECEIPT"] = CONTAINER_RECEIPT

    # Initialize CORS with development-friendly defaults
    init_cors(app)

    return app
