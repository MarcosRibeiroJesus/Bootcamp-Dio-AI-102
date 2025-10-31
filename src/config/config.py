import os
from dotenv import load_dotenv

# Load .env at import time so other modules can read values
load_dotenv()

# Flask / app
PORT = int(os.getenv("PORT", "8181"))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(30 * 1024 * 1024)))

# Storage
STORAGE_CONNECTION_STRING = os.getenv("STORAGE_CONNECTION_STRING")
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
STORAGE_ACCOUNT_KEY = os.getenv("STORAGE_ACCOUNT_KEY")

# Document Intelligence
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
DOCUMENT_INTELLIGENCE_KEY = os.getenv("DOCUMENT_INTELLIGENCE_KEY")

# Containers
CONTAINER_BUSINESS_CARD = os.getenv("CONTAINER_BUSINESS_CARD")
CONTAINER_CONTRACT = os.getenv("CONTAINER_CONTRACT")
CONTAINER_CREDIT_CARD = os.getenv("CONTAINER_CREDIT_CARD")
CONTAINER_ID_DOCUMENT = os.getenv("CONTAINER_ID_DOCUMENT")
CONTAINER_INVOICE = os.getenv("CONTAINER_INVOICE")
CONTAINER_RECEIPT = os.getenv("CONTAINER_RECEIPT")

# SAS
SAS_EXPIRY_MINUTES = int(os.getenv("SAS_EXPIRY_MINUTES", "60"))

# Misc
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")
