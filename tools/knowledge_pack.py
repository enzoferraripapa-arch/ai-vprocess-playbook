from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


LOCK_RELATIVE_PATH = Path(".aivprocess") / "knowledge_pack_lock.json"
PROJECT_DB_RELATIVE_PATH = Path(".aivprocess") / "project.db"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def version_key(version: str) -> tuple[int, tuple[int, ...] | str]:
    parts = version.split(".")
    if all(part.isdigit() for part in parts):
        return (0, tuple(int(part) for part in parts))
    return (1, version)


def load_lock(project: Path) -> dict[str, Any]:
    lock_path = project / LOCK_RELATIVE_PATH
    if not lock_path.exists():
        raise FileNotFoundError(f"missing project lock: {lock_path}")
    return read_json(lock_path)


def load_manifests(packs: Path) -> dict[str, dict[str, Any]]:
    manifests: dict[str, dict[str, Any]] = {}
    for manifest_path in sorted(packs.rglob("manifest.json")):
        manifest = read_json(manifest_path)
        pack_id = str(manifest.get("pack_id", ""))
        version = str(manifest.get("version", ""))
        if not pack_id or not version:
            raise ValueError(f"manifest needs pack_id and version: {manifest_path}")
        current = manifests.get(pack_id)
        if current is None or version_key(version) > version_key(str(current["version"])):
            manifest["_manifest_path"] = str(manifest_path)
            manifests[pack_id] = manifest
    return manifests


def build_plan(project: Path, packs: Path) -> dict[str, Any]:
    lock = load_lock(project)
    manifests = load_manifests(packs)
    locked = {item["pack_id"]: item for item in lock.get("knowledge_packs", [])}

    updates: list[dict[str, Any]] = []
    unchanged: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    available_new: list[dict[str, Any]] = []

    for pack_id, locked_item in sorted(locked.items()):
        manifest = manifests.get(pack_id)
        if manifest is None:
            missing.append(
                {
                    "pack_id": pack_id,
                    "locked_version": locked_item.get("version"),
                    "status": "missing_available_manifest",
                }
            )
            continue
        locked_version = str(locked_item.get("version", ""))
        latest_version = str(manifest["version"])
        record = {
            "pack_id": pack_id,
            "locked_version": locked_version,
            "available_version": latest_version,
            "manifest_path": manifest["_manifest_path"],
            "manifest_sha256": sha256_file(Path(manifest["_manifest_path"])),
            "summary": manifest.get("summary", ""),
        }
        if version_key(latest_version) > version_key(locked_version):
            record["status"] = "update_available"
            updates.append(record)
        else:
            record["status"] = "unchanged"
            unchanged.append(record)

    for pack_id, manifest in sorted(manifests.items()):
        if pack_id not in locked:
            available_new.append(
                {
                    "pack_id": pack_id,
                    "available_version": manifest["version"],
                    "manifest_path": manifest["_manifest_path"],
                    "manifest_sha256": sha256_file(Path(manifest["_manifest_path"])),
                    "summary": manifest.get("summary", ""),
                    "status": "available_not_locked",
                }
            )

    return {
        "project": str(project),
        "packs": str(packs),
        "lock_path": str(project / LOCK_RELATIVE_PATH),
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "updates": updates,
        "unchanged": unchanged,
        "missing": missing,
        "available_new": available_new,
        "no_x_boundary": [
            "NO-PACK-UPDATE-AS-PROJECT-APPROVAL",
            "NO-LATEST-AS-CORRECT",
            "NO-KNOWLEDGE-PACK-AS-SOURCE-LICENSE",
        ],
    }


def print_check(plan: dict[str, Any]) -> None:
    rows: list[tuple[str, str, str, str]] = []
    for item in plan["updates"]:
        rows.append((item["pack_id"], item["locked_version"], item["available_version"], "update_available"))
    for item in plan["unchanged"]:
        rows.append((item["pack_id"], item["locked_version"], item["available_version"], "unchanged"))
    for item in plan["missing"]:
        rows.append((item["pack_id"], str(item["locked_version"]), "-", "missing_manifest"))
    for item in plan["available_new"]:
        rows.append((item["pack_id"], "-", item["available_version"], "available_not_locked"))

    print("| Pack | Locked | Available | Status |")
    print("| --- | --- | --- | --- |")
    for pack_id, locked, available, status in sorted(rows):
        print(f"| {pack_id} | {locked} | {available} | {status} |")


def stage_plan(project: Path, plan: dict[str, Any]) -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stage_dir = project / ".aivprocess" / "update_staging" / stamp
    write_json(stage_dir / "knowledge_pack_update_plan.json", plan)
    return stage_dir


def accept_plan(project: Path, staged: Path, accepted_by: str, rationale: str) -> None:
    plan_path = staged / "knowledge_pack_update_plan.json"
    plan = read_json(plan_path)
    lock = load_lock(project)
    locked = {item["pack_id"]: item for item in lock.get("knowledge_packs", [])}
    accepted_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    for update in plan.get("updates", []):
        item = locked[update["pack_id"]]
        item["version"] = update["available_version"]
        item["manifest_sha256"] = update["manifest_sha256"]
        item["accepted_at"] = accepted_at
        item["accepted_by"] = accepted_by
        item["rationale"] = rationale

    for new_item in plan.get("available_new", []):
        locked[new_item["pack_id"]] = {
            "pack_id": new_item["pack_id"],
            "version": new_item["available_version"],
            "manifest_sha256": new_item["manifest_sha256"],
            "accepted_at": accepted_at,
            "accepted_by": accepted_by,
            "rationale": rationale,
        }

    lock["knowledge_packs"] = [locked[pack_id] for pack_id in sorted(locked)]
    write_json(project / LOCK_RELATIVE_PATH, lock)
    sync_project_db_adoption(project, lock)


def sync_project_db_adoption(project: Path, lock: dict[str, Any]) -> None:
    db_path = project / PROJECT_DB_RELATIVE_PATH
    if not db_path.exists():
        return

    conn = sqlite3.connect(db_path)
    try:
        table_exists = conn.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = 'knowledge_pack_adoption'
            """
        ).fetchone()
        if table_exists is None:
            return

        conn.execute("DELETE FROM knowledge_pack_adoption")
        rows = [
            (
                str(item.get("pack_id", "")),
                str(item.get("version", "")),
                str(item.get("manifest_sha256", "")),
                str(item.get("accepted_at", "")),
                str(item.get("accepted_by", "")),
                str(item.get("rationale", "")),
                "NO-PACK-UPDATE-AS-PROJECT-APPROVAL",
            )
            for item in lock.get("knowledge_packs", [])
        ]
        conn.executemany(
            """
            INSERT INTO knowledge_pack_adoption(
                pack_id, version, manifest_sha256, accepted_at, accepted_by, rationale, boundary
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check, plan, stage, or accept knowledge-pack updates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("check", "plan", "stage"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--project", type=Path, required=True)
        sub.add_argument("--packs", type=Path, required=True)

    accept = subparsers.add_parser("accept")
    accept.add_argument("--project", type=Path, required=True)
    accept.add_argument("--staged", type=Path, required=True)
    accept.add_argument("--accepted-by", required=True)
    accept.add_argument("--rationale", required=True)

    args = parser.parse_args()

    if args.command in {"check", "plan", "stage"}:
        plan = build_plan(args.project, args.packs)
        if args.command == "check":
            print_check(plan)
        elif args.command == "plan":
            print(json.dumps(plan, indent=2, ensure_ascii=False))
        else:
            stage_dir = stage_plan(args.project, plan)
            print(stage_dir)
        return 0

    if args.command == "accept":
        accept_plan(args.project, args.staged, args.accepted_by, args.rationale)
        print(f"updated {args.project / LOCK_RELATIVE_PATH}")
        return 0

    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"knowledge_pack.py: {exc}", file=sys.stderr)
        raise SystemExit(1)
