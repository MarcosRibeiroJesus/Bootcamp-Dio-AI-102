import logging
from azure.core.credentials import AzureKeyCredential

from src.exceptions.exceptions import DocumentAnalysisError
from src.config.settings import DOCUMENT_INTELLIGENCE_ENDPOINT, DOCUMENT_INTELLIGENCE_KEY

# Discover a suitable SDK client class from known package names
SDKDocumentClient = None
for candidate in (
    "azure.ai.documentanalysis",
    "azure.ai.documentintelligence",
    "azure.ai.formrecognizer",
):
    try:
        module = __import__(candidate, fromlist=["DocumentAnalysisClient", "DocumentIntelligenceClient"])  # type: ignore
        if hasattr(module, "DocumentAnalysisClient"):
            SDKDocumentClient = getattr(module, "DocumentAnalysisClient")
            break
        if hasattr(module, "DocumentIntelligenceClient"):
            SDKDocumentClient = getattr(module, "DocumentIntelligenceClient")
            break
    except Exception:
        continue

if SDKDocumentClient is None:
    raise ImportError(
        "Could not find a suitable Azure Document Intelligence client in installed SDKs."
    )


class DocumentIntelligenceClient:
    def __init__(self, endpoint: str = None, key: str = None):
        self.log = logging.getLogger("DocumentIntelligenceClient")
        endpoint = endpoint or DOCUMENT_INTELLIGENCE_ENDPOINT
        key = key or DOCUMENT_INTELLIGENCE_KEY
        if not endpoint or not key:
            raise ValueError("DOCUMENT_INTELLIGENCE_ENDPOINT and DOCUMENT_INTELLIGENCE_KEY are required")
        try:
            credential = AzureKeyCredential(key)
            # Try common constructor signatures
            try:
                self.client = SDKDocumentClient(endpoint, credential)
            except TypeError:
                self.client = SDKDocumentClient(endpoint=endpoint, credential=credential)
        except Exception as e:
            self.log.exception("Failed to initialize Document Intelligence client")
            raise

    def analyze_from_url(self, model_id: str, url: str, **kwargs) -> dict:
        """Analyze a remote document accessible by URL using a prebuilt model.

        Tries multiple SDK method names/signatures to remain compatible across versions.
        """
        try:
            self.log.info("Starting analysis for model=%s url=%s", model_id, url)

            # Try newer SDK signature first (positional args)
            if hasattr(self.client, "begin_analyze_document"):
                method = getattr(self.client, "begin_analyze_document")
                try:
                    poller = method(model_id, {"urlSource": url})
                    result = poller.result()
                    return self._convert_result_to_dict(result)
                except Exception as e:
                    self.log.warning("Failed with positional args: %s", e)

            # Fallback to older SDK signatures
            candidates = [
                ("begin_analyze_document", {"model_id": model_id, "analyze_request": {"urlSource": url}}),
                ("begin_analyze_document", {"model_id": model_id, "document_url": url}),
                ("begin_analyze_document_from_url", {"model_id": model_id, "document_url": url}),
            ]

            poller = None
            last_exc = None
            for method_name, kwargs_dict in candidates:
                if hasattr(self.client, method_name):
                    method = getattr(self.client, method_name)
                    try:
                        poller = method(**kwargs_dict)
                        break
                    except (TypeError, KeyError) as te:
                        last_exc = te
                        continue
                    except Exception as e:
                        last_exc = e
                        continue

            if poller is None:
                msg = f"No suitable analyze method found on client (last error: {last_exc})"
                self.log.error(msg)
                raise DocumentAnalysisError(msg)

            result = poller.result()
            return self._convert_result_to_dict(result)
        except Exception as e:
            self.log.exception("Document analysis failed for url=%s model=%s", url, model_id)
            raise DocumentAnalysisError(str(e))
    
    def _convert_result_to_dict(self, result) -> dict:
        """Convert Azure SDK result object to dictionary."""
        # Try different conversion methods
        if hasattr(result, "to_dict"):
            return result.to_dict()
        if hasattr(result, "as_dict"):
            return result.as_dict()
        if hasattr(result, "__dict__"):
            return self._serialize_object(result)
        return {"raw_result": str(result)}
    
    def _serialize_object(self, obj):
        """Recursively serialize an object to dict."""
        if hasattr(obj, "as_dict"):
            return obj.as_dict()
        if hasattr(obj, "__dict__"):
            result = {}
            for key, value in obj.__dict__.items():
                if key.startswith("_"):
                    continue
                if isinstance(value, list):
                    result[key] = [self._serialize_object(item) for item in value]
                elif hasattr(value, "__dict__"):
                    result[key] = self._serialize_object(value)
                else:
                    result[key] = value
            return result
        return obj
