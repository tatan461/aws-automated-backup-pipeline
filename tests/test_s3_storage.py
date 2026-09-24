from pathlib import Path

import boto3
import pytest
from moto import mock_aws

from s3_storage import S3Storage


@pytest.fixture
def s3_setup() -> tuple[str, str]:
    bucket = "portfolio-backup-test"
    kms_key_id = "alias/portfolio-backup"

    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=bucket)
        yield bucket, kms_key_id


def test_upload_download_and_metadata(
    tmp_path: Path, s3_setup: tuple[str, str]
) -> None:
    bucket, kms_key_id = s3_setup
    local_file = tmp_path / "backup.tar.gz"
    local_file.write_bytes(b"backup-content")
    destination = tmp_path / "downloaded.tar.gz"

    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=bucket)
        storage = S3Storage(bucket=bucket, kms_key_id=kms_key_id, client=client)

        result = storage.upload_backup(
            local_file,
            "backups/backup.tar.gz",
            "abc123",
        )

        assert result["bucket"] == bucket
        assert result["key"] == "backups/backup.tar.gz"
        assert result["encryption"] == "aws:kms"

        metadata = storage.get_backup_metadata("backups/backup.tar.gz")
        assert metadata["checksum"] == "abc123"
        assert metadata["encryption"] == "aws:kms"

        storage.download_backup("backups/backup.tar.gz", destination)
        assert destination.read_bytes() == b"backup-content"


def test_rejects_invalid_object_keys(s3_setup: tuple[str, str]) -> None:
    bucket, kms_key_id = s3_setup

    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=bucket)
        storage = S3Storage(bucket=bucket, kms_key_id=kms_key_id, client=client)

        with pytest.raises(ValueError):
            storage.get_backup_metadata("/absolute/key")

        with pytest.raises(ValueError):
            storage.download_backup("", "output.tar.gz")
