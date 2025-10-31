import logging
from .client import DocumentIntelligenceClient
from src.exceptions.exceptions import DocumentAnalysisError

log = logging.getLogger("business_card_service")


class BusinessCardService:
    MODEL_ID = "prebuilt-businessCard"

    def __init__(self, client: DocumentIntelligenceClient):
        self.client = client

    def analyze(self, url: str) -> dict:
        try:
            log.info("Analyzing business card URL: %s", url)
            return self.client.analyze_from_url(self.MODEL_ID, url)
        except DocumentAnalysisError:
            raise
        except Exception as e:
            log.exception("Unexpected error in business card analysis")
            raise DocumentAnalysisError(str(e))
