import os
import logging

from services.translate_service import Translator

# Load environment variables at import time (app calls load_dotenv)
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not AZURE_OPENAI_KEY or not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_DEPLOYMENT:
    logging.warning("One or more Azure OpenAI environment variables are missing. See .env.example")


# Create a singleton Translator that routes can import
translator = Translator(
    endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    deployment=AZURE_OPENAI_DEPLOYMENT,
)
