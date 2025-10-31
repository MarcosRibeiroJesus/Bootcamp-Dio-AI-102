import logging
from .client import DocumentIntelligenceClient
from src.exceptions.exceptions import DocumentAnalysisError

log = logging.getLogger("credit_card_service")


class CreditCardService:
    MODEL_ID = "prebuilt-creditCard"

    def __init__(self, client: DocumentIntelligenceClient):
        self.client = client

    def analyze(self, url: str) -> dict:
        try:
            log.info("Analyzing credit card URL: %s", url)
            return self.client.analyze_from_url(self.MODEL_ID, url)
        except DocumentAnalysisError:
            raise
        except Exception as e:
            log.exception("Unexpected error in credit card analysis")
            raise DocumentAnalysisError(str(e))
