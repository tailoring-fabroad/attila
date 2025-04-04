import os
import tempfile
from datetime import timedelta

from fastapi import UploadFile
from google.cloud import storage

from app.core.config import get_app_settings

SETTINGS = get_app_settings()
GCP_CREDENTIAL = SETTINGS.gcp_credential
GCP_PROJECT_ID = SETTINGS.gcp_projectid
GCP_BUCKETNAME = SETTINGS.gcp_bucketname
GCP_PATH = SETTINGS.gcp_path


def generate_signed_url(bucket_name: str, blob_name: str, expiration_minutes: int = 10) -> str:
    client = storage.Client.from_service_account_json(GCP_CREDENTIAL)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET",
    )
    return url


async def upload_blob(file: UploadFile) -> str:
    suffix = os.path.splitext(file.filename)[-1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp.flush()
        tmp_path = tmp.name

    try:
        client = storage.Client.from_service_account_json(GCP_CREDENTIAL)
        bucket = client.bucket(GCP_BUCKETNAME)

        blob_path = f"{GCP_PATH}/{file.filename}"
        blob = bucket.blob(blob_path)

        with open(tmp_path, "rb") as f:
            blob.upload_from_file(f)

        signed_url = generate_signed_url(GCP_BUCKETNAME, blob_path)
        return signed_url

    finally:
        os.unlink(tmp_path)
