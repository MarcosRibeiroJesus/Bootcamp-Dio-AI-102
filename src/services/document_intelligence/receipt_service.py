import logging
from .client import DocumentIntelligenceClient
from src.exceptions.exceptions import DocumentAnalysisError

log = logging.getLogger("receipt_service")


class ReceiptService:
    MODEL_ID = "prebuilt-receipt"

    def __init__(self, client: DocumentIntelligenceClient):
        self.client = client

    def analyze(self, url: str) -> dict:
        try:
            log.info("Analyzing receipt URL: %s", url)
            return self.client.analyze_from_url(self.MODEL_ID, url)
        except DocumentAnalysisError:
            raise
        except Exception as e:
            log.exception("Unexpected error in receipt analysis")
            raise DocumentAnalysisError(str(e))
