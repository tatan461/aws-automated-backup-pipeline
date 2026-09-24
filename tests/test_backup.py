from pathlib import Path

from backup import calculate_sha256, create_archive, restore_archive, verify_archive


def test_create_checksum_verify_and_restore(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "example.txt").write_text("backup test data\n", encoding="utf-8")

    archive = tmp_path / "backup.tar.gz"
    restored = tmp_path / "restored"

    create_archive(source, archive)
    checksum = calculate_sha256(archive)

    assert archive.exists()
    assert len(checksum) == 64
    assert verify_archive(archive, checksum)

    restore_archive(archive, restored)
    restored_file = restored / source.name / "example.txt"
    assert restored_file.read_text(encoding="utf-8") == "backup test data\n"


def test_checksum_detects_modified_file(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("original", encoding="utf-8")
    checksum = calculate_sha256(file_path)

    file_path.write_text("modified", encoding="utf-8")

    assert not verify_archive(file_path, checksum)
