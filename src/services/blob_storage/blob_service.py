import os
import logging
import uuid
from datetime import datetime, timedelta

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import AzureError

from src.exceptions.exceptions import BlobUploadError


class BlobService:
    def __init__(self, connection_string: str = None, account_name: str = None, account_key: str = None):
        # Prefer connection string but allow account name/key
        self.log = logging.getLogger("BlobService")
        try:
            if connection_string:
                self.client = BlobServiceClient.from_connection_string(connection_string)
                self.account_name = None
                self.account_key = None
            elif account_name and account_key:
                account_url = f"https://{account_name}.blob.core.windows.net"
                self.client = BlobServiceClient(account_url=account_url, credential=account_key)
                self.account_name = account_name
                self.account_key = account_key
            else:
                raise ValueError("Provide either STORAGE_CONNECTION_STRING or STORAGE_ACCOUNT_NAME + STORAGE_ACCOUNT_KEY")
        except Exception as e:
            self.log.exception("Failed to initialize BlobService client")
            raise

    def upload_file(self, container_name: str, filename: str, data: bytes, content_type: str = None, sas_minutes: int = 60) -> str:
        """Upload bytes to the given container and return a read-only SAS URL.

        Creates the container if not present. Returns a URL with SAS token valid for sas_minutes.
        """
        try:
            container_client = self.client.get_container_client(container_name)
            try:
                container_client.create_container()
                self.log.info("Created container %s", container_name)
            except Exception:
                # container may already exist
                pass

            blob_name = f"{uuid.uuid4().hex}_{filename}"
            blob_client = container_client.get_blob_client(blob_name)
            self.log.info("Uploading blob %s to container %s", blob_name, container_name)
            blob_client.upload_blob(data, overwrite=True, content_settings=None)

            # Build a SAS token so Document Intelligence can fetch the document
            if hasattr(self, 'account_key') and self.account_key:
                sas_token = generate_blob_sas(
                    account_name=self.account_name,
                    container_name=container_name,
                    blob_name=blob_name,
                    account_key=self.account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(minutes=sas_minutes),
                )
                url = f"{blob_client.url}?{sas_token}"
            else:
                # If we used connection string we can still generate SAS if account key is available in settings
                try:
                    from config.config import STORAGE_ACCOUNT_NAME as _SA_NAME, STORAGE_ACCOUNT_KEY as _SA_KEY

                    account_name = _SA_NAME
                    account_key = _SA_KEY
                except Exception:
                    account_name = None
                    account_key = None

                if not account_name or not account_key:
                    # Fallback: return public URL (only works if container is public)
                    self.log.warning(
                        "No account key available; returning blob url without SAS. Ensure container is public or provide account key"
                    )
                    url = blob_client.url
                else:
                    sas_token = generate_blob_sas(
                        account_name=account_name,
                        container_name=container_name,
                        blob_name=blob_name,
                        account_key=account_key,
                        permission=BlobSasPermissions(read=True),
                        expiry=datetime.utcnow() + timedelta(minutes=sas_minutes),
                    )
                    url = f"{blob_client.url}?{sas_token}"

            self.log.info("Uploaded and generated URL: %s", url)
            return url
        except AzureError as e:
            self.log.exception("Azure error uploading blob")
            raise BlobUploadError(str(e))
        except Exception as e:
            self.log.exception("Unexpected error uploading blob")
            raise BlobUploadError(str(e))
