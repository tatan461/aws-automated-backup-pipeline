"""Backup, S3 upload/download, verification, and restore CLI."""

from __future__ import annotations

import argparse
import hashlib
import tarfile
from pathlib import Path

from s3_storage import S3Storage


def create_archive(source: str | Path, destination: str | Path) -> Path:
    source_path = Path(source).resolve()
    destination_path = Path(destination).resolve()
    if not source_path.is_dir():
        raise ValueError(f"Source directory does not exist: {source_path}")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(destination_path, "w:gz") as archive:
        archive.add(source_path, arcname=source_path.name)
    return destination_path


def calculate_sha256(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(path: str | Path, expected_sha256: str) -> bool:
    return calculate_sha256(path).lower() == expected_sha256.lower()


def restore_archive(archive_path: str | Path, destination: str | Path) -> Path:
    archive_path = Path(archive_path).resolve()
    destination_path = Path(destination).resolve()
    if not archive_path.is_file():
        raise ValueError(f"Archive does not exist: {archive_path}")
    destination_path.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as archive:
        archive.extractall(destination_path, filter="data")
    return destination_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AWS backup pipeline CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("source")
    create.add_argument("-o", "--output", default="backup-output/backup.tar.gz")

    verify = subparsers.add_parser("verify")
    verify.add_argument("archive")
    verify.add_argument("checksum")

    restore = subparsers.add_parser("restore")
    restore.add_argument("archive")
    restore.add_argument("destination")

    upload = subparsers.add_parser("upload")
    upload.add_argument("archive")
    upload.add_argument("--key", default=None)

    download = subparsers.add_parser("download")
    download.add_argument("key")
    download.add_argument("destination")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "create":
        archive = create_archive(args.source, args.output)
        print(f"Created: {archive}")
        print(f"SHA-256: {calculate_sha256(archive)}")
        return 0

    if args.command == "verify":
        valid = verify_archive(args.archive, args.checksum)
        print("Checksum valid" if valid else "Checksum mismatch")
        return 0 if valid else 1

    if args.command == "restore":
        destination = restore_archive(args.archive, args.destination)
        print(f"Restored to: {destination}")
        return 0

    storage = S3Storage()

    if args.command == "upload":
        archive = Path(args.archive)
        checksum = calculate_sha256(archive)
        key = args.key or f"backups/{archive.name}"
        result = storage.upload_backup(archive, key, checksum)
        print(f"Uploaded: s3://{result['bucket']}/{result['key']}")
        print(f"SHA-256: {checksum}")
        print("Encryption: aws:kms")
        return 0

    if args.command == "download":
        destination = storage.download_backup(args.key, args.destination)
        metadata = storage.get_backup_metadata(args.key)
        checksum = metadata.get("checksum")
        if not checksum:
            print("Downloaded, but no checksum metadata was found")
            return 1
        if not verify_archive(destination, checksum):
            print("Downloaded file failed checksum verification")
            return 1
        print(f"Downloaded and verified: {destination}")
        print(f"SHA-256: {checksum}")
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())