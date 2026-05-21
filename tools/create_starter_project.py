from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "starter_repo"
SKIP_PARTS = {"__pycache__", ".pytest_cache"}


def copy_template(target: Path, force: bool) -> None:
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"missing template: {TEMPLATE}")
    if target.exists() and any(target.iterdir()) and not force:
        raise FileExistsError(f"target is not empty: {target}; use --force to merge")
    target.mkdir(parents=True, exist_ok=True)
    for source in TEMPLATE.rglob("*"):
        if any(part in SKIP_PARTS for part in source.relative_to(TEMPLATE).parts):
            continue
        rel = source.relative_to(TEMPLATE)
        destination = target / rel
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        if destination.exists() and not force:
            raise FileExistsError(f"target file exists: {destination}; use --force to overwrite")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a starter AI V-process project layout.")
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--force", action="store_true", help="merge into an existing directory and overwrite files")
    args = parser.parse_args()
    copy_template(args.target, args.force)
    print(args.target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
