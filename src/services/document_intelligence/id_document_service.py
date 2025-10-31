import logging
from .client import DocumentIntelligenceClient
from src.exceptions.exceptions import DocumentAnalysisError

log = logging.getLogger("id_document_service")


class IdDocumentService:
    MODEL_ID = "prebuilt-idDocument"

    def __init__(self, client: DocumentIntelligenceClient):
        self.client = client

    def analyze(self, url: str) -> dict:
        try:
            log.info("Analyzing ID document URL: %s", url)
            return self.client.analyze_from_url(self.MODEL_ID, url)
        except DocumentAnalysisError:
            raise
        except Exception as e:
            log.exception("Unexpected error in ID document analysis")
            raise DocumentAnalysisError(str(e))
