"""CORS configuration for the Flask app."""
from flask_cors import CORS


def init_cors(app):
    """Initialize CORS for the Flask app with development-friendly defaults."""
    
    CORS(
        app,
        origins=[
            "http://localhost:8080",      # Production build
            "http://127.0.0.1:8080",
            "http://localhost:5173",      # Vite dev server
            "http://127.0.0.1:5173",
            "http://192.168.1.20:8080",   # Local network access
            "http://192.168.56.1:8080",
        ],
        methods=["GET", "HEAD", "POST", "OPTIONS"],
        allow_headers="*",                # Allow all headers
        expose_headers="*",               # Expose all headers
        supports_credentials=True,        # Allow credentials
        max_age=3600                     # Cache preflight for 1 hour
    )
    
    app.logger.info("CORS initialized with development configuration")