import os
import logging
from src.services.blob_storage.blob_service import BlobService
from src.config.settings import (
    STORAGE_CONNECTION_STRING,
    STORAGE_ACCOUNT_NAME,
    STORAGE_ACCOUNT_KEY,
)

log = logging.getLogger("storage_client_config")


def init_blob_service():
    """Initialize and return a BlobService instance using centralized settings."""
    try:
        bs = BlobService(
            connection_string=STORAGE_CONNECTION_STRING,
            account_name=STORAGE_ACCOUNT_NAME,
            account_key=STORAGE_ACCOUNT_KEY,
        )
        log.info("Initialized BlobService")
        return bs
    except Exception as e:
        log.exception("Failed to initialize BlobService: %s", e)
        raise
