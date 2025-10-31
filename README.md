# Document Intelligence Anti-Fraud Service

![Validation Results](image.png)

<img width="3840" height="5608" alt="Valid Card Screen" src="https://github.com/user-attachments/assets/6f64a848-3c65-4444-a08c-4bc70f42a668" />

Small Python service that uploads documents to Azure Blob Storage and uses Azure Document Intelligence (prebuilt models) to analyze documents for 'anti-fraud' checks.

Quick start
1. Copy `.env.example` to `.env` and fill values.
2. Create a virtualenv and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

3. Run the example Flask app:

```powershell
python -m src.app.py
```

Endpoints (example):
- POST /upload-and-analyze - form-data: file, doc_type (one of: credit_card, id_document, invoice, receipt, business_card, contract)

Notes
- This is a starter scaffold. You must secure the storage container (permissions) and the generated SAS URLs according to your security requirements.
