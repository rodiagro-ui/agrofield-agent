import json
from pathlib import Path

from agrofield_agent.freeze import canonical_sha256, verify_manifest


def test_canonical_hash_ignores_text_line_endings(tmp_path: Path):
    lf = tmp_path / "lf.txt"
    crlf = tmp_path / "crlf.txt"
    lf.write_bytes(b"one\ntwo\n")
    crlf.write_bytes(b"one\r\ntwo\r\n")
    assert canonical_sha256(lf) == canonical_sha256(crlf)


def test_verify_manifest_reports_mismatch(tmp_path: Path):
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("frozen\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "artifact.txt",
                        "canonical_sha256": canonical_sha256(artifact),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    assert verify_manifest(manifest, tmp_path)["valid"] is True
    artifact.write_text("changed\n", encoding="utf-8")
    result = verify_manifest(manifest, tmp_path)
    assert result["valid"] is False
    assert result["mismatched"] == 1
