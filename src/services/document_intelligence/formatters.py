"""Response formatters for Document Intelligence analysis results."""
from .credit_card_validator import create as validate_card


def format_credit_card_response(raw_result: dict) -> dict:
    """Format credit card analysis result for frontend consumption."""
    documents = raw_result.get("documents", [])
    if not documents:
        return {"error": "No credit card data found"}
    
    doc = documents[0]
    fields = doc.get("fields", {})
    
    # Extract fields with confidence
    card_number_field = fields.get("CardNumber", {})
    cardholder_name_field = fields.get("CardHolderName", {})
    expiry_date_field = fields.get("ExpirationDate", {})
    bank_name_field = fields.get("IssuingBank", {})
    
    card_number = _extract_field(card_number_field)
    cardholder_name = _extract_field(cardholder_name_field)
    expiry_date = _extract_field(expiry_date_field)
    bank_name = _extract_field(bank_name_field)
    
    # Get field-level confidences
    card_number_conf = card_number_field.get("confidence", 0)
    cardholder_name_conf = cardholder_name_field.get("confidence", 0)
    expiry_date_conf = expiry_date_field.get("confidence", 0)
    
    # Fraud detection from Azure
    fraud_result = doc.get("fraudResult", {})
    is_fraud_detected = fraud_result.get("isFraud", False)
    fraud_reason = fraud_result.get("reason", [])
    
    # Apply confidence thresholds
    fraud_indicators = []
    
    if is_fraud_detected:
        fraud_indicators.extend(fraud_reason if isinstance(fraud_reason, list) else [fraud_reason])
    
    if card_number and card_number_conf < 0.85:
        fraud_indicators.append(f"Card number confidence too low: {card_number_conf:.2f}")
    
    if expiry_date and expiry_date_conf < 0.75:
        fraud_indicators.append(f"Expiry date confidence too low: {expiry_date_conf:.2f}")
    
    if cardholder_name and cardholder_name_conf < 0.70:
        fraud_indicators.append(f"Cardholder name confidence too low: {cardholder_name_conf:.2f}")
    
    if not card_number:
        fraud_indicators.append("Missing card number")
    
    if not cardholder_name:
        fraud_indicators.append("Missing cardholder name")
    
    is_fraud = is_fraud_detected or len(fraud_indicators) > 0
    
    # Run additional validation
    validation_result = validate_card({
        "holder_name": cardholder_name,
        "card_number": card_number or "",
        "expiration_date": expiry_date or "",
        "brand": bank_name
    })
    
    # Extract bounding regions for visual indicators
    fields_with_regions = {
        "card_number": {
            "value": card_number,
            "confidence": card_number_conf,
            "bounding_regions": card_number_field.get("bounding_regions", []),
            "spans": card_number_field.get("spans", [])
        },
        "cardholder_name": {
            "value": cardholder_name,
            "confidence": cardholder_name_conf,
            "bounding_regions": cardholder_name_field.get("bounding_regions", []),
            "spans": cardholder_name_field.get("spans", [])
        },
        "expiry_date": {
            "value": expiry_date,
            "confidence": expiry_date_conf,
            "bounding_regions": expiry_date_field.get("bounding_regions", []),
            "spans": expiry_date_field.get("spans", [])
        },
        "bank_name": {
            "value": bank_name,
            "confidence": bank_name_field.get("confidence", 0),
            "bounding_regions": bank_name_field.get("bounding_regions", []),
            "spans": bank_name_field.get("spans", [])
        }
    }
    
    return {
        "card_number": card_number,
        "cardholder_name": cardholder_name,
        "expiry_date": expiry_date,
        "bank_name": bank_name,
        "fields": fields_with_regions,
        "azure_confidence": {
            "card_number": card_number_conf,
            "cardholder_name": cardholder_name_conf,
            "expiry_date": expiry_date_conf
        },
        "azure_fraud_detected": is_fraud,
        "azure_fraud_indicators": fraud_indicators,
        "validation": validation_result,
        "raw_document": doc
    }


def format_id_document_response(raw_result: dict) -> dict:
    """Format ID document analysis result for frontend consumption."""
    documents = raw_result.get("documents", [])
    if not documents:
        return {"error": "No ID document data found"}
    
    doc = documents[0]
    fields = doc.get("fields", {})
    
    return {
        "document_number": _extract_field(fields.get("DocumentNumber")),
        "first_name": _extract_field(fields.get("FirstName")),
        "last_name": _extract_field(fields.get("LastName")),
        "date_of_birth": _extract_field(fields.get("DateOfBirth")),
        "expiration_date": _extract_field(fields.get("DateOfExpiration")),
        "address": _extract_field(fields.get("Address")),
        "confidence": doc.get("confidence", 0)
    }


def format_receipt_response(raw_result: dict) -> dict:
    """Format receipt analysis result for frontend consumption."""
    documents = raw_result.get("documents", [])
    if not documents:
        return {"error": "No receipt data found"}
    
    doc = documents[0]
    fields = doc.get("fields", {})
    
    items = []
    items_field = fields.get("Items")
    if items_field and items_field.get("value_array"):
        for item in items_field["value_array"]:
            item_fields = item.get("value_object", {})
            items.append({
                "description": _extract_field(item_fields.get("Description")),
                "quantity": _extract_field(item_fields.get("Quantity")),
                "price": _extract_field(item_fields.get("Price")),
                "total": _extract_field(item_fields.get("TotalPrice"))
            })
    
    return {
        "merchant_name": _extract_field(fields.get("MerchantName")),
        "transaction_date": _extract_field(fields.get("TransactionDate")),
        "total": _extract_field(fields.get("Total")),
        "subtotal": _extract_field(fields.get("Subtotal")),
        "tax": _extract_field(fields.get("TotalTax")),
        "items": items,
        "confidence": doc.get("confidence", 0)
    }


def format_invoice_response(raw_result: dict) -> dict:
    """Format invoice analysis result for frontend consumption."""
    documents = raw_result.get("documents", [])
    if not documents:
        return {"error": "No invoice data found"}
    
    doc = documents[0]
    fields = doc.get("fields", {})
    
    items = []
    items_field = fields.get("Items")
    if items_field and items_field.get("value_array"):
        for item in items_field["value_array"]:
            item_fields = item.get("value_object", {})
            items.append({
                "description": _extract_field(item_fields.get("Description")),
                "quantity": _extract_field(item_fields.get("Quantity")),
                "unit_price": _extract_field(item_fields.get("UnitPrice")),
                "amount": _extract_field(item_fields.get("Amount"))
            })
    
    return {
        "invoice_id": _extract_field(fields.get("InvoiceId")),
        "invoice_date": _extract_field(fields.get("InvoiceDate")),
        "due_date": _extract_field(fields.get("DueDate")),
        "vendor_name": _extract_field(fields.get("VendorName")),
        "customer_name": _extract_field(fields.get("CustomerName")),
        "total": _extract_field(fields.get("InvoiceTotal")),
        "subtotal": _extract_field(fields.get("SubTotal")),
        "tax": _extract_field(fields.get("TotalTax")),
        "items": items,
        "confidence": doc.get("confidence", 0)
    }


def format_business_card_response(raw_result: dict) -> dict:
    """Format business card analysis result for frontend consumption."""
    documents = raw_result.get("documents", [])
    if not documents:
        return {"error": "No business card data found"}
    
    doc = documents[0]
    fields = doc.get("fields", {})
    
    return {
        "contact_names": _extract_field(fields.get("ContactNames")),
        "company_names": _extract_field(fields.get("CompanyNames")),
        "job_titles": _extract_field(fields.get("JobTitles")),
        "emails": _extract_field(fields.get("Emails")),
        "phones": _extract_field(fields.get("WorkPhones")),
        "mobile_phones": _extract_field(fields.get("MobilePhones")),
        "websites": _extract_field(fields.get("Websites")),
        "addresses": _extract_field(fields.get("Addresses")),
        "confidence": doc.get("confidence", 0)
    }


def format_contract_response(raw_result: dict) -> dict:
    """Format contract analysis result for frontend consumption."""
    documents = raw_result.get("documents", [])
    if not documents:
        return {"error": "No contract data found"}
    
    doc = documents[0]
    fields = doc.get("fields", {})
    
    return {
        "parties": _extract_field(fields.get("Parties")),
        "contract_date": _extract_field(fields.get("ContractDate")),
        "effective_date": _extract_field(fields.get("EffectiveDate")),
        "expiration_date": _extract_field(fields.get("ExpirationDate")),
        "contract_type": _extract_field(fields.get("ContractType")),
        "confidence": doc.get("confidence", 0)
    }


def _extract_field(field):
    """Extract value from a field object."""
    if not field:
        return None
    
    if isinstance(field, dict):
        if "content" in field:
            return field["content"]
        if "value_string" in field:
            return field["value_string"]
        if "value_number" in field:
            return field["value_number"]
        if "value_date" in field:
            return field["value_date"]
        if "value_array" in field:
            return [_extract_field(item) for item in field["value_array"]]
    
    return field
