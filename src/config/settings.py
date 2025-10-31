"""Centralized configuration settings loaded from environment variables."""
import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# Document Intelligence settings
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
DOCUMENT_INTELLIGENCE_KEY = os.getenv("DOCUMENT_INTELLIGENCE_KEY")

# Blob Storage settings
STORAGE_CONNECTION_STRING = os.getenv("STORAGE_CONNECTION_STRING")
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")  # Optional: only needed if not in connection string
STORAGE_ACCOUNT_KEY = os.getenv("STORAGE_ACCOUNT_KEY")    # Optional: only needed if not in connection string
SAS_EXPIRY_MINUTES = int(os.getenv("SAS_EXPIRY_MINUTES", "60"))  # Default 1 hour

# Container names for different document types
CONTAINER_BUSINESS_CARD = os.getenv("CONTAINER_BUSINESS_CARD", "business-cards")
CONTAINER_CONTRACT = os.getenv("CONTAINER_CONTRACT", "contracts")
CONTAINER_CREDIT_CARD = os.getenv("CONTAINER_CREDIT_CARD", "credit-cards")
CONTAINER_ID_DOCUMENT = os.getenv("CONTAINER_ID_DOCUMENT", "id-documents")
CONTAINER_INVOICE = os.getenv("CONTAINER_INVOICE", "invoices")
CONTAINER_RECEIPT = os.getenv("CONTAINER_RECEIPT", "receipts")

# Flask settings
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))  # Default 16MB
PORT = int(os.getenv("PORT", "5000"))