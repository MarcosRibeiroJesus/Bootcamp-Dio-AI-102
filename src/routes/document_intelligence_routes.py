from flask import Blueprint, request, jsonify, current_app
import logging
from src.services.document_intelligence.client import DocumentIntelligenceClient
from src.services.document_intelligence.credit_card_service import CreditCardService
from src.services.document_intelligence.id_document_service import IdDocumentService
from src.services.document_intelligence.receipt_service import ReceiptService
from src.services.document_intelligence.invoice_service import InvoiceService
from src.services.document_intelligence.business_card_service import BusinessCardService
from src.services.document_intelligence.contract_service import ContractService
from src.services.document_intelligence.formatters import (
    format_credit_card_response,
    format_id_document_response,
    format_receipt_response,
    format_invoice_response,
    format_business_card_response,
    format_contract_response
)
from src.exceptions.exceptions import BlobUploadError, DocumentAnalysisError

log = logging.getLogger("document_intel_routes")


def create_document_intelligence_blueprint(blob_service, di_client: DocumentIntelligenceClient):
    bp = Blueprint("document_intel", __name__)

    # instantiate per-type services with the provided client
    credit_card_service = CreditCardService(di_client)
    id_document_service = IdDocumentService(di_client)
    receipt_service = ReceiptService(di_client)
    invoice_service = InvoiceService(di_client)
    business_card_service = BusinessCardService(di_client)
    contract_service = ContractService(di_client)


    @bp.route("/upload-and-analyze", methods=["POST"])
    def upload_and_analyze():
        log.info("Received upload-and-analyze request (blueprint)")
        if "file" not in request.files:
            return jsonify({"error": "Missing file field"}), 400

        file = request.files["file"]
        doc_type = request.form.get("doc_type")
        if not doc_type:
            return jsonify({"error": "Missing doc_type form field"}), 400

        # map doc types to container names from env
        mapping = {
            "credit_card": current_app.config.get("CONTAINER_CREDIT_CARD"),
            "id_document": current_app.config.get("CONTAINER_ID_DOCUMENT"),
            "invoice": current_app.config.get("CONTAINER_INVOICE"),
            "receipt": current_app.config.get("CONTAINER_RECEIPT"),
            "business_card": current_app.config.get("CONTAINER_BUSINESS_CARD"),
            "contract": current_app.config.get("CONTAINER_CONTRACT"),
        }

        container = mapping.get(doc_type)
        if not container:
            return jsonify({"error": "Unsupported or unconfigured doc_type"}), 400

        filename = file.filename or "upload"
        data = file.read()

        try:
            url = blob_service.upload_file(container, filename, data)
        except BlobUploadError as e:
            return jsonify({"error": "Upload failed", "detail": str(e)}), 500

        # Choose analyzer and format response
        try:
            if doc_type == "credit_card":
                raw_result = credit_card_service.analyze(url)
                result = format_credit_card_response(raw_result)
            elif doc_type == "id_document":
                raw_result = id_document_service.analyze(url)
                result = format_id_document_response(raw_result)
            elif doc_type == "invoice":
                raw_result = invoice_service.analyze(url)
                result = format_invoice_response(raw_result)
            elif doc_type == "receipt":
                raw_result = receipt_service.analyze(url)
                result = format_receipt_response(raw_result)
            elif doc_type == "business_card":
                raw_result = business_card_service.analyze(url)
                result = format_business_card_response(raw_result)
            elif doc_type == "contract":
                raw_result = contract_service.analyze(url)
                result = format_contract_response(raw_result)
            else:
                return jsonify({"error": "Unsupported doc_type"}), 400
        except DocumentAnalysisError as e:
            return jsonify({"error": "Document analysis failed", "detail": str(e)}), 500

        return jsonify(result), 200

    return bp
