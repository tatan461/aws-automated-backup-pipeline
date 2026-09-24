"""Amazon S3 storage operations for encrypted backup archives."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import boto3
from botocore.client import BaseClient


class S3Storage:
    """Small S3 adapter for uploading and downloading backup archives."""

    def __init__(
        self,
        bucket: str | None = None,
        kms_key_id: str | None = None,
        client: BaseClient | None = None,
    ) -> None:
        self.bucket = bucket or os.getenv("BACKUP_BUCKET")
        self.kms_key_id = kms_key_id or os.getenv("BACKUP_KMS_KEY_ID")
        self.client = client or boto3.client("s3")

        if not self.bucket:
            raise ValueError("BACKUP_BUCKET is required")
        if not self.kms_key_id:
            raise ValueError("BACKUP_KMS_KEY_ID is required")

    def upload_backup(
        self,
        local_path: str | Path,
        object_key: str,
        checksum: str,
    ) -> dict[str, Any]:
        """Upload a backup using SSE-KMS and store its checksum as metadata."""
        path = Path(local_path)
        if not path.is_file():
            raise ValueError(f"Backup file does not exist: {path}")
        if not object_key or object_key.startswith("/"):
            raise ValueError("object_key must be a non-empty relative S3 key")

        extra_args = {
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": self.kms_key_id,
            "Metadata": {"sha256": checksum},
            "ContentType": "application/gzip",
        }
        self.client.upload_file(str(path), self.bucket, object_key, ExtraArgs=extra_args)
        return {
            "bucket": self.bucket,
            "key": object_key,
            "checksum": checksum,
            "encryption": "aws:kms",
        }

    def download_backup(self, object_key: str, destination: str | Path) -> Path:
        """Download a backup archive from S3."""
        if not object_key or object_key.startswith("/"):
            raise ValueError("object_key must be a non-empty relative S3 key")

        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        self.client.download_file(self.bucket, object_key, str(destination_path))
        return destination_path

    def get_backup_metadata(self, object_key: str) -> dict[str, Any]:
        """Return S3 metadata for a backup object."""
        if not object_key or object_key.startswith("/"):
            raise ValueError("object_key must be a non-empty relative S3 key")

        response = self.client.head_object(Bucket=self.bucket, Key=object_key)
        return {
            "bucket": self.bucket,
            "key": object_key,
            "checksum": response.get("Metadata", {}).get("sha256"),
            "etag": response.get("ETag", "").strip('"'),
            "size": response.get("ContentLength", 0),
            "encryption": response.get("ServerSideEncryption"),
        }
