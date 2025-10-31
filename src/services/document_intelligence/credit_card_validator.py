"""Credit card validation with Luhn algorithm and brand detection."""
import re
from datetime import datetime
from typing import Dict, Optional, List


CARD_BRANDS = {
    "visa": {"prefixes": ["4"], "lengths": [13, 16, 19]},
    "mastercard": {"prefixes": ["51", "52", "53", "54", "55", "2221-2720"], "lengths": [16]},
    "amex": {"prefixes": ["34", "37"], "lengths": [15]},
    "discover": {"prefixes": ["6011", "622126-622925", "644", "645", "646", "647", "648", "649", "65"], "lengths": [16, 19]},
    "diners": {"prefixes": ["300", "301", "302", "303", "304", "305", "36", "38"], "lengths": [14]},
    "jcb": {"prefixes": ["3528-3589"], "lengths": [16, 19]},
}


def luhn_check(card_number: str) -> bool:
    """Validate card number using Luhn algorithm."""
    digits = [int(d) for d in card_number if d.isdigit()]
    checksum = 0
    reverse_digits = digits[::-1]
    
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    
    return checksum % 10 == 0


def detect_brand(card_number: str) -> Optional[str]:
    """Detect card brand from BIN/IIN."""
    for brand, rules in CARD_BRANDS.items():
        for prefix in rules["prefixes"]:
            if "-" in prefix:
                start, end = prefix.split("-")
                prefix_len = len(start)
                card_prefix = card_number[:prefix_len]
                if start <= card_prefix <= end:
                    return brand
            elif card_number.startswith(prefix):
                return brand
    return None


def validate_length(card_number: str, brand: Optional[str]) -> bool:
    """Validate card number length for detected brand."""
    if not brand or brand not in CARD_BRANDS:
        return 13 <= len(card_number) <= 19
    return len(card_number) in CARD_BRANDS[brand]["lengths"]


def parse_expiration(exp_str: str) -> Optional[str]:
    """Parse expiration date to YYYY-MM format."""
    exp_str = exp_str.strip().replace(" ", "")
    
    patterns = [
        (r"^(\d{4})-(\d{2})$", lambda m: f"{m.group(1)}-{m.group(2)}"),
        (r"^(\d{2})-(\d{4})$", lambda m: f"{m.group(2)}-{m.group(1)}"),
        (r"^(\d{2})/(\d{4})$", lambda m: f"{m.group(2)}-{m.group(1)}"),
        (r"^(\d{2})(\d{2})$", lambda m: f"20{m.group(2)}-{m.group(1)}"),
        (r"^(\d{2})/(\d{2})$", lambda m: f"20{m.group(2)}-{m.group(1)}"),
        (r"^(\d{4})(\d{2})$", lambda m: f"{m.group(1)}-{m.group(2)}"),
        (r"^(\d{2})(\d{2})$", lambda m: f"20{m.group(2)}-{m.group(1)}"),
    ]
    
    for pattern, formatter in patterns:
        match = re.match(pattern, exp_str)
        if match:
            result = formatter(match)
            try:
                year, month = result.split("-")
                if 1 <= int(month) <= 12:
                    return result
            except:
                continue
    return None


def is_expired(exp_str: str) -> bool:
    """Check if expiration date is expired (end-of-month semantics)."""
    try:
        year, month = exp_str.split("-")
        exp_year, exp_month = int(year), int(month)
        now = datetime.now()
        
        if exp_year < now.year:
            return True
        if exp_year == now.year and exp_month < now.month:
            return True
        return False
    except:
        return True


def validate_holder_name(name: str) -> bool:
    """Validate holder name format."""
    if not name or len(name) < 2 or len(name) > 50:
        return False
    return bool(re.match(r"^[A-Za-z\s\-']+$", name))


def create(payload: Dict) -> Dict:
    """Create validation result from credit card payload."""
    holder_name = payload.get("holder_name", "").strip() if payload.get("holder_name") else None
    card_number = re.sub(r"[\s\-]", "", payload.get("card_number", ""))
    expiration_date = payload.get("expiration_date", "").strip() if payload.get("expiration_date") else None
    provided_brand = payload.get("brand", "").lower().strip() if payload.get("brand") else None
    
    observations = []
    fraud_indicators = []
    confidence = {}
    checks = {}
    
    # Card number validation
    luhn_pass = luhn_check(card_number) if card_number else False
    detected_brand = detect_brand(card_number) if card_number else None
    length_valid = validate_length(card_number, detected_brand) if card_number else False
    
    checks["luhn_pass"] = luhn_pass
    checks["brand_detected"] = detected_brand is not None
    checks["length_valid"] = length_valid
    
    if not luhn_pass:
        fraud_indicators.append("luhn_fail")
    if not length_valid:
        fraud_indicators.append("invalid_length")
    
    # Brand validation
    brand = detected_brand or provided_brand
    if provided_brand and detected_brand and provided_brand != detected_brand:
        fraud_indicators.append("brand_mismatch")
        observations.append(f"Provided brand '{provided_brand}' doesn't match detected '{detected_brand}'")
    elif detected_brand:
        observations.append(f"Brand detected: {detected_brand}")
    
    confidence["brand"] = 1.0 if detected_brand else (0.5 if provided_brand else 0.0)
    confidence["card_number"] = 1.0 if (luhn_pass and length_valid) else 0.0
    
    # Expiration validation
    normalized_exp = parse_expiration(expiration_date) if expiration_date else None
    exp_valid = normalized_exp is not None and not is_expired(normalized_exp) if normalized_exp else False
    
    checks["expiration_valid"] = exp_valid if expiration_date else None
    confidence["expiration_date"] = 1.0 if exp_valid else (0.0 if expiration_date else None)
    
    if expiration_date and not normalized_exp:
        fraud_indicators.append("invalid_expiration_format")
    elif normalized_exp and is_expired(normalized_exp):
        fraud_indicators.append("expired")
    
    # Holder name validation
    holder_valid = validate_holder_name(holder_name) if holder_name else None
    checks["holder_name_valid"] = holder_valid if holder_name else None
    confidence["holder_name"] = 1.0 if holder_valid else (0.0 if holder_name else None)
    
    if holder_name and not holder_valid:
        fraud_indicators.append("invalid_holder_name")
    elif not holder_name:
        observations.append("Holder name not provided")
    
    # Compute overall validity
    critical_checks = [luhn_pass, length_valid, checks["brand_detected"]]
    if expiration_date:
        critical_checks.append(exp_valid)
    
    valid = all(critical_checks) and len(fraud_indicators) == 0
    
    last4 = card_number[-4:] if len(card_number) >= 4 else card_number
    
    return {
        "valid": valid,
        "is_fraud": is_fraud({
            "valid": valid,
            "fraud_indicators": fraud_indicators,
            "confidence": confidence,
            "checks": checks
        }),
        "brand": brand,
        "last4": last4,
        "expiration": normalized_exp,
        "checks": checks,
        "confidence": confidence,
        "observations": observations,
        "fraud_indicators": {
            "count": len(fraud_indicators),
            "items": fraud_indicators
        }
    }


def is_fraud(result: Dict) -> str:
    """Determine fraud status: true, neutral, or false."""
    fraud_count = result.get("fraud_indicators", {}).get("count", 0) if isinstance(result.get("fraud_indicators"), dict) else len(result.get("fraud_indicators", []))
    confidence = result.get("confidence", {})
    checks = result.get("checks", {})
    
    # Critical checks
    luhn_pass = checks.get("luhn_pass", False)
    length_valid = checks.get("length_valid", False)
    brand_detected = checks.get("brand_detected", False)
    exp_valid = checks.get("expiration_valid")
    
    # All confidence scores == 1 (excluding None)
    all_confidence_full = all(v == 1.0 for v in confidence.values() if v is not None)
    
    # False (valid) - all checks pass, full confidence, no fraud indicators
    if luhn_pass and length_valid and brand_detected and fraud_count == 0 and all_confidence_full:
        if exp_valid is None or exp_valid:
            return "false"
    
    # True (fraud) - critical checks fail
    if not luhn_pass or not length_valid or fraud_count > 0:
        if exp_valid is False or "expired" in str(result.get("fraud_indicators", [])):
            return "true"
        if "luhn_fail" in str(result.get("fraud_indicators", [])) or "invalid_length" in str(result.get("fraud_indicators", [])):
            return "true"
    
    # Neutral - core checks pass but missing optional fields or lower confidence
    return "neutral"
