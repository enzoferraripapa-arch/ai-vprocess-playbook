from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools import knowledge_pack


class KnowledgePackAcceptTests(unittest.TestCase):
    def test_accept_updates_lock_and_project_db_adoption(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = root / "product"
            packs = root / "packs"
            project_aiv = project / ".aivprocess"
            project_aiv.mkdir(parents=True)

            self.write_json(
                project_aiv / "knowledge_pack_lock.json",
                {
                    "project_id": "demo-product",
                    "project_schema": "aivprocess-project/v1",
                    "knowledge_packs": [
                        {
                            "pack_id": "process-method",
                            "version": "0.1.0",
                            "manifest_sha256": "old-process-hash",
                            "accepted_at": "2026-05-21T00:00:00Z",
                            "accepted_by": "example-reviewer",
                            "rationale": "Initial process baseline.",
                        }
                    ],
                },
            )

            self.write_manifest(packs / "process-method" / "manifest.json", "process-method", "0.2.0")
            self.write_manifest(packs / "security-privacy" / "manifest.json", "security-privacy", "0.1.0")
            self.create_project_db(project_aiv / "project.db")

            plan = knowledge_pack.build_plan(project, packs)
            self.assertEqual([item["pack_id"] for item in plan["updates"]], ["process-method"])
            self.assertEqual([item["pack_id"] for item in plan["available_new"]], ["security-privacy"])

            staged = knowledge_pack.stage_plan(project, plan)
            knowledge_pack.accept_plan(
                project,
                staged,
                accepted_by="unit-test",
                rationale="Accepted for local rehearsal only; not product approval.",
            )

            lock = json.loads((project_aiv / "knowledge_pack_lock.json").read_text(encoding="utf-8"))
            locked_rows = [
                (item["pack_id"], item["version"], item["manifest_sha256"], item["accepted_by"])
                for item in lock["knowledge_packs"]
            ]
            self.assertEqual([row[0] for row in locked_rows], ["process-method", "security-privacy"])

            conn = sqlite3.connect(project_aiv / "project.db")
            try:
                db_rows = conn.execute(
                    """
                    SELECT pack_id, version, manifest_sha256, accepted_by, boundary
                    FROM knowledge_pack_adoption
                    ORDER BY pack_id
                    """
                ).fetchall()
                self.assertEqual(
                    [(row[0], row[1], row[2], row[3]) for row in db_rows],
                    locked_rows,
                )
                self.assertEqual(
                    {row[4] for row in db_rows},
                    {"NO-PACK-UPDATE-AS-PROJECT-APPROVAL"},
                )
                self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            finally:
                conn.close()

    def test_accept_without_project_db_updates_lock_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = root / "product"
            packs = root / "packs"
            project_aiv = project / ".aivprocess"
            project_aiv.mkdir(parents=True)

            self.write_json(
                project_aiv / "knowledge_pack_lock.json",
                {
                    "project_id": "demo-product",
                    "project_schema": "aivprocess-project/v1",
                    "knowledge_packs": [],
                },
            )
            self.write_manifest(packs / "process-method" / "manifest.json", "process-method", "0.1.0")

            plan = knowledge_pack.build_plan(project, packs)
            staged = knowledge_pack.stage_plan(project, plan)
            knowledge_pack.accept_plan(project, staged, accepted_by="unit-test", rationale="Lock-only accept.")

            lock = json.loads((project_aiv / "knowledge_pack_lock.json").read_text(encoding="utf-8"))
            self.assertEqual([item["pack_id"] for item in lock["knowledge_packs"]], ["process-method"])
            self.assertTrue(lock["knowledge_packs"][0]["db_sha256"])

    def test_locked_manifest_without_real_db_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = root / "product"
            packs = root / "packs"
            project_aiv = project / ".aivprocess"
            project_aiv.mkdir(parents=True)

            self.write_json(
                project_aiv / "knowledge_pack_lock.json",
                {
                    "project_id": "demo-product",
                    "project_schema": "aivprocess-project/v1",
                    "knowledge_packs": [
                        {
                            "pack_id": "security-privacy",
                            "version": "0.1.0",
                            "manifest_sha256": "example-only",
                            "accepted_at": "2026-05-21T00:00:00Z",
                            "accepted_by": "example-reviewer",
                            "rationale": "Example lock.",
                        }
                    ],
                },
            )
            self.write_json(
                packs / "security-privacy" / "manifest.json",
                {
                    "pack_id": "security-privacy",
                    "version": "0.1.0",
                    "schema_version": "knowledge-pack-manifest/v1",
                    "db_filename": "knowledge.db",
                    "db_sha256": "example-only-not-a-real-db-hash",
                    "status": "fictional_example_manifest",
                },
            )

            plan = knowledge_pack.build_plan(project, packs)
            self.assertEqual([item["pack_id"] for item in plan["invalid"]], ["security-privacy"])
            self.assertEqual(plan["invalid"][0]["status"], "invalid_locked_pack")

    @staticmethod
    def write_json(path: Path, data: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def write_manifest(path: Path, pack_id: str, version: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        db_path = path.parent / "knowledge.db"
        db_path.write_bytes(f"{pack_id}:{version}".encode("utf-8"))
        db_sha256 = knowledge_pack.sha256_file(db_path)
        path.write_text(
            json.dumps(
                {
                    "pack_id": pack_id,
                    "name": pack_id,
                    "version": version,
                    "schema_version": "knowledge-pack-manifest/v1",
                    "db_filename": "knowledge.db",
                    "db_sha256": db_sha256,
                    "status": "local_db_built",
                    "summary": f"{pack_id} test manifest",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def create_project_db(path: Path) -> None:
        conn = sqlite3.connect(path)
        try:
            conn.execute(
                """
                CREATE TABLE knowledge_pack_adoption (
                    pack_id TEXT PRIMARY KEY,
                    version TEXT NOT NULL,
                    manifest_sha256 TEXT NOT NULL,
                    accepted_at TEXT NOT NULL,
                    accepted_by TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    boundary TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO knowledge_pack_adoption(
                    pack_id, version, manifest_sha256, accepted_at, accepted_by, rationale, boundary
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "process-method",
                    "0.1.0",
                    "old-process-hash",
                    "2026-05-21T00:00:00Z",
                    "example-reviewer",
                    "Initial process baseline.",
                    "NO-PACK-UPDATE-AS-PROJECT-APPROVAL",
                ),
            )
            conn.commit()
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
