"""Local backup and restore primitives for the AWS backup pipeline."""

from __future__ import annotations

import hashlib
import tarfile
from pathlib import Path


def create_archive(source: str | Path, destination: str | Path) -> Path:
    """Create a gzip-compressed tar archive from a source directory."""
    source_path = Path(source).resolve()
    destination_path = Path(destination).resolve()

    if not source_path.is_dir():
        raise ValueError(f"Source directory does not exist: {source_path}")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(destination_path, "w:gz") as archive:
        archive.add(source_path, arcname=source_path.name)

    return destination_path


def calculate_sha256(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 checksum of a file."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(path: str | Path, expected_sha256: str) -> bool:
    """Compare a file checksum with an expected SHA-256 value."""
    actual = calculate_sha256(path)
    return actual.lower() == expected_sha256.lower()


def restore_archive(archive_path: str | Path, destination: str | Path) -> Path:
    """Extract an archive into a destination directory."""
    archive_path = Path(archive_path).resolve()
    destination_path = Path(destination).resolve()

    if not archive_path.is_file():
        raise ValueError(f"Archive does not exist: {archive_path}")

    destination_path.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as archive:
        archive.extractall(destination_path, filter="data")

    return destination_path
