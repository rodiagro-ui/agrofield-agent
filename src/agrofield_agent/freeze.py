from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_sha256(path: Path) -> str:
    """Hash UTF-8 text with normalized LF endings; hash binary files as-is."""

    raw = path.read_bytes()
    try:
        normalized = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeDecodeError:
        payload = raw
    else:
        payload = normalized.encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_manifest(manifest_path: Path, repository_root: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []
    for entry in manifest.get("files", []):
        relative_path = entry["path"]
        target = repository_root / relative_path
        if not target.exists():
            checks.append(
                {
                    "path": relative_path,
                    "status": "missing",
                    "expected_sha256": entry["canonical_sha256"],
                    "actual_sha256": None,
                }
            )
            continue
        actual = canonical_sha256(target)
        checks.append(
            {
                "path": relative_path,
                "status": "match" if actual == entry["canonical_sha256"] else "mismatch",
                "expected_sha256": entry["canonical_sha256"],
                "actual_sha256": actual,
            }
        )
    return {
        "manifest": str(manifest_path),
        "files": len(checks),
        "matched": sum(item["status"] == "match" for item in checks),
        "missing": sum(item["status"] == "missing" for item in checks),
        "mismatched": sum(item["status"] == "mismatch" for item in checks),
        "valid": bool(checks) and all(item["status"] == "match" for item in checks),
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a frozen AgroField benchmark manifest")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = verify_manifest(args.manifest, args.root)
    print(json.dumps(result, indent=2))
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
