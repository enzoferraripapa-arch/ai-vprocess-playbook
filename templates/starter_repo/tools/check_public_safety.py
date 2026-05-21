from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}
TEXT_EXTENSIONS = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".toml"}
BLOCKED_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".p12", ".pem", ".key"}


def marker(*parts: str) -> str:
    return "".join(parts).lower()


PRIVATE_MARKERS = {
    marker("to", "rasan"),
    marker("kago", "ya"),
    marker("v", "133"),
    marker("po", "larion"),
    marker("reference", "_docs"),
    marker("confidential", "_guidelines"),
    marker("manual", "-architecture-db"),
}

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*['\"]?[^'\"\s]{8,}"),
    re.compile(r"(?i)https?://[^/\s]*v\d{2,}[-.][^/\s]+"),
]


def iter_files() -> list[Path]:
    paths: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            paths.append(path)
    return sorted(paths)


def read_text(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return None
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    paths = iter_files()
    for path in paths:
        rel = path.relative_to(ROOT)
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            errors.append(f"blocked file type: {rel}")
        text = read_text(path)
        if text is None:
            continue
        lowered = text.lower()
        for private_marker in PRIVATE_MARKERS:
            if private_marker in lowered:
                errors.append(f"private marker {private_marker!r}: {rel}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"secret-like pattern {pattern.pattern!r}: {rel}")
        if path.suffix.lower() == ".json":
            try:
                json.loads(text)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"invalid json: {rel}: {exc}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Public safety gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
