"""
Tests for app.ingestion.archive.extract_archive — previously uncovered security paths.

The zip-slip (path traversal) and absolute-path-in-zip cases are already covered in
test_ingestion_security.py.  This file targets the completely untested codepaths:

  1. Tar archive: symlink/hardlink members must be rejected (m.issym(), m.islnk())
  2. Tar archive: path traversal via '../' must be caught by safe_member_path()
  3. Extraction file-count limit is enforced for both zip and tar archives
     (the limit is shared logic, tested once through each format)
  4. Extraction *size* limit per-file is enforced for zip archives
  5. A valid tar archive extracts successfully (sanity / happy-path)
"""
import gzip
import io
import tarfile
import zipfile

import pytest

from app.ingestion.archive import ArchiveSecurityError, extract_archive
from app.ingestion.limits import IngestionLimits


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tar_gz(members: list[tuple[str, bytes | None, str | None]]) -> bytes:
    """
    Build an in-memory .tar.gz.

    members: list of (name, content_bytes_or_None, link_target_or_None)
      - If link_target is set the entry is a symlink (tarfile.SYMTYPE).
      - If content_bytes is None and link_target is None the entry is a regular dir.
      - Otherwise it is a regular file.
    """
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for name, content, link_target in members:
            info = tarfile.TarInfo(name=name)
            if link_target is not None:
                info.type = tarfile.SYMTYPE
                info.linkname = link_target
                tf.addfile(info)
            elif content is None:
                info.type = tarfile.DIRTYPE
                tf.addfile(info)
            else:
                info.size = len(content)
                tf.addfile(info, io.BytesIO(content))
    return buf.getvalue()


def _make_zip(members: list[tuple[str, bytes]]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in members:
            zf.writestr(name, content)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Test 1 — Tar: symlink members are rejected
# ---------------------------------------------------------------------------

class TestTarSymlinkRejection:
    """Tar archives containing symlinks or hardlinks must raise ArchiveSecurityError."""

    def test_symlink_member_raises(self, tmp_path):
        data = _make_tar_gz([
            ("safe.txt", b"hello", None),
            ("link_to_etc", None, "/etc/passwd"),   # symlink → absolute target
        ])
        with pytest.raises(ArchiveSecurityError):
            extract_archive(data, tmp_path, IngestionLimits())

    def test_relative_symlink_member_raises(self, tmp_path):
        """Even a relative symlink pointing elsewhere must be blocked."""
        data = _make_tar_gz([
            ("dir/real.txt", b"content", None),
            ("dir/link", None, "../outside.txt"),   # relative symlink
        ])
        with pytest.raises(ArchiveSecurityError):
            extract_archive(data, tmp_path, IngestionLimits())

    def test_hardlink_member_raises(self, tmp_path):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tf:
            # First add a normal file so there is something to hard-link to
            info = tarfile.TarInfo(name="original.txt")
            info.size = 5
            tf.addfile(info, io.BytesIO(b"hello"))
            # Now add a hard link
            hlink = tarfile.TarInfo(name="hardlink.txt")
            hlink.type = tarfile.LNKTYPE
            hlink.linkname = "original.txt"
            tf.addfile(hlink)
        with pytest.raises(ArchiveSecurityError):
            extract_archive(buf.getvalue(), tmp_path, IngestionLimits())


# ---------------------------------------------------------------------------
# Test 2 — Tar: path traversal (../  prefix) must be caught
# ---------------------------------------------------------------------------

class TestTarPathTraversal:
    """Tar archives with directory-escaping paths must raise ArchiveSecurityError."""

    def test_dotdot_path_raises(self, tmp_path):
        data = _make_tar_gz([("../escaped.txt", b"evil", None)])
        with pytest.raises(ArchiveSecurityError):
            extract_archive(data, tmp_path, IngestionLimits())

    def test_nested_dotdot_path_raises(self, tmp_path):
        data = _make_tar_gz([("subdir/../../escaped.txt", b"evil", None)])
        with pytest.raises(ArchiveSecurityError):
            extract_archive(data, tmp_path, IngestionLimits())


# ---------------------------------------------------------------------------
# Test 3 — Extraction file-count limit
# ---------------------------------------------------------------------------

class TestExtractionFileCountLimit:
    """Both zip and tar archives must respect IngestionLimits.max_extraction_files."""

    def test_zip_file_count_limit_raises(self, tmp_path):
        tight = IngestionLimits(max_extraction_files=2)
        data = _make_zip([
            ("a.txt", b"a"),
            ("b.txt", b"b"),
            ("c.txt", b"c"),  # third file exceeds limit of 2
        ])
        with pytest.raises(ArchiveSecurityError, match="file limit"):
            extract_archive(data, tmp_path, tight)

    def test_tar_file_count_limit_raises(self, tmp_path):
        tight = IngestionLimits(max_extraction_files=2)
        data = _make_tar_gz([
            ("a.txt", b"a", None),
            ("b.txt", b"b", None),
            ("c.txt", b"c", None),  # third file exceeds limit of 2
        ])
        with pytest.raises(ArchiveSecurityError):
            extract_archive(data, tmp_path, tight)


# ---------------------------------------------------------------------------
# Test 4 — Per-file size limit (zip)
# ---------------------------------------------------------------------------

class TestExtractionSizeLimit:
    """A single oversize file in a zip must raise ArchiveSecurityError."""

    def test_oversize_file_in_zip_raises(self, tmp_path):
        # max_file_size_mb=1 → limit = 1 MiB = 1 048 576 bytes
        tight = IngestionLimits(max_file_size_mb=1)
        big = b"x" * (1 * 1024 * 1024 + 1)  # 1 byte over the limit
        data = _make_zip([("big.bin", big)])
        with pytest.raises(ArchiveSecurityError, match="size limit"):
            extract_archive(data, tmp_path, tight)


# ---------------------------------------------------------------------------
# Test 5 — Happy path: valid tar.gz extracts correctly
# ---------------------------------------------------------------------------

class TestValidTarExtraction:
    """A well-formed tar.gz with safe paths must extract without errors."""

    def test_valid_tar_gz_extracts_files(self, tmp_path):
        data = _make_tar_gz([
            ("src/main.py", b"print('hello')", None),
            ("README.md", b"# Project", None),
        ])
        extract_archive(data, tmp_path, IngestionLimits())
        assert (tmp_path / "src" / "main.py").read_bytes() == b"print('hello')"
        assert (tmp_path / "README.md").read_bytes() == b"# Project"
