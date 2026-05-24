from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / ".aivprocess" / "project.db"
PROFILE = ROOT / ".aivprocess" / "project_profile.json"
LOCK = ROOT / ".aivprocess" / "knowledge_pack_lock.json"
ROUTING = ROOT / ".aivprocess" / "routing_matrix.json"
REQUIREMENTS = ROOT / ".aivprocess" / "requirements.json"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def connect_new(db_path: Path) -> sqlite3.Connection:
    if db_path.exists():
        raise FileExistsError(f"project DB already exists: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE project_fact (
            fact_id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            value TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN ('accepted_local','candidate_only','candidate_ready_for_manual_review','gate_not_passed','open','open_not_passed','open_tbd','planned','recorded','rejected_as_authority','resolved_local')
                OR status LIKE 'available_%'
                OR status LIKE 'accepted_local_%'
                OR status LIKE 'candidate_ready_for_manual_review_%'
            ),
            boundary TEXT NOT NULL CHECK (boundary LIKE 'NO-%' OR boundary LIKE 'MFG-NO-%' OR boundary LIKE 'SEC-NO-%')
        );

        CREATE TABLE evidence (
            evidence_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            owner TEXT NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN ('available','candidate_ready_for_manual_review','planned','recorded')
                OR status LIKE 'available_%'
                OR status LIKE 'candidate_ready_for_manual_review_%'
            ),
            boundary TEXT NOT NULL CHECK (boundary LIKE 'NO-%' OR boundary LIKE 'MFG-NO-%' OR boundary LIKE 'SEC-NO-%')
        );

        CREATE TABLE requirement_item (
            requirement_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            requirement_type TEXT NOT NULL CHECK (
                requirement_type IN ('functional','nonfunctional','interface','safety','security','regulatory','manufacturing','process')
            ),
            priority TEXT NOT NULL CHECK (priority IN ('P0','P1','P2','P3','deferred','unknown')),
            constraint_origin TEXT NOT NULL CHECK (
                constraint_origin IN (
                    'not_applicable',
                    'architecture_constraint',
                    'human_factors_constraint',
                    'regulatory_constraint',
                    'safety_constraint',
                    'security_constraint',
                    'operational_constraint',
                    'manufacturing_constraint',
                    'evidence_constraint',
                    'mixed_constraint',
                    'not_classified'
                )
            ),
            source TEXT NOT NULL,
            statement TEXT NOT NULL,
            acceptance_criteria TEXT NOT NULL,
            verification_method TEXT NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN ('accepted_local','candidate_only','candidate_ready_for_manual_review','gate_not_passed','open','open_not_passed','open_tbd','planned','recorded','rejected_as_authority','resolved_local')
                OR status LIKE 'available_%'
                OR status LIKE 'accepted_local_%'
                OR status LIKE 'candidate_ready_for_manual_review_%'
            ),
            boundary TEXT NOT NULL CHECK (boundary LIKE 'NO-%' OR boundary LIKE 'MFG-NO-%' OR boundary LIKE 'SEC-NO-%'),
            CHECK (
                requirement_type != 'nonfunctional'
                OR constraint_origin NOT IN ('not_applicable','not_classified')
            )
        );

        CREATE TABLE requirement_classification (
            requirement_id TEXT NOT NULL,
            classification_type TEXT NOT NULL CHECK (
                classification_type IN (
                    'requirement_level',
                    'source_authority',
                    'risk_impact',
                    'safety_class',
                    'security_impact',
                    'privacy_impact',
                    'usability_impact',
                    'applicability',
                    'baseline',
                    'data_freshness',
                    'formal_target',
                    'gate_tier',
                    'maturity'
                )
            ),
            value TEXT NOT NULL,
            rationale TEXT NOT NULL,
            source TEXT NOT NULL,
            boundary TEXT NOT NULL CHECK (boundary LIKE 'NO-%' OR boundary LIKE 'MFG-NO-%' OR boundary LIKE 'SEC-NO-%'),
            PRIMARY KEY (requirement_id, classification_type, value),
            FOREIGN KEY (requirement_id) REFERENCES requirement_item(requirement_id) ON DELETE CASCADE
        );

        CREATE TABLE requirement_allocation (
            requirement_id TEXT NOT NULL,
            target_layer TEXT NOT NULL CHECK (
                target_layer IN (
                    'stakeholder','system','software','hardware','mechanical','electrical','firmware',
                    'application','cloud','data','configuration','manufacturing','service','post_market','process','unknown'
                )
            ),
            target_component TEXT NOT NULL,
            owner TEXT NOT NULL,
            rationale TEXT NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN ('accepted_local','candidate_only','candidate_ready_for_manual_review','gate_not_passed','open','open_not_passed','open_tbd','planned','recorded','rejected_as_authority','resolved_local')
                OR status LIKE 'available_%'
                OR status LIKE 'accepted_local_%'
                OR status LIKE 'candidate_ready_for_manual_review_%'
            ),
            boundary TEXT NOT NULL CHECK (boundary LIKE 'NO-%' OR boundary LIKE 'MFG-NO-%' OR boundary LIKE 'SEC-NO-%'),
            PRIMARY KEY (requirement_id, target_layer, target_component),
            FOREIGN KEY (requirement_id) REFERENCES requirement_item(requirement_id) ON DELETE CASCADE
        );

        CREATE TABLE requirement_trace (
            requirement_id TEXT NOT NULL,
            target_type TEXT NOT NULL CHECK (
                target_type IN (
                    'requirement','design','risk','test','evidence','handoff','component','interface',
                    'document','issue','baseline','configuration'
                )
            ),
            target_id TEXT NOT NULL,
            relation TEXT NOT NULL CHECK (
                relation IN (
                    'satisfies','verifies','mitigates','allocates_to','depends_on','conflicts_with',
                    'assumes','derived_from','feeds_handoff','references_evidence'
                )
            ),
            status TEXT NOT NULL CHECK (
                status IN ('accepted_local','candidate_only','candidate_ready_for_manual_review','gate_not_passed','open','open_not_passed','open_tbd','planned','recorded','rejected_as_authority','resolved_local')
                OR status LIKE 'available_%'
                OR status LIKE 'accepted_local_%'
                OR status LIKE 'candidate_ready_for_manual_review_%'
            ),
            boundary TEXT NOT NULL CHECK (boundary LIKE 'NO-%' OR boundary LIKE 'MFG-NO-%' OR boundary LIKE 'SEC-NO-%'),
            PRIMARY KEY (requirement_id, target_type, target_id, relation),
            FOREIGN KEY (requirement_id) REFERENCES requirement_item(requirement_id) ON DELETE CASCADE
        );

        CREATE TABLE knowledge_pack_adoption (
            pack_id TEXT PRIMARY KEY,
            version TEXT NOT NULL,
            manifest_sha256 TEXT NOT NULL,
            db_sha256 TEXT NOT NULL DEFAULT '',
            accepted_at TEXT NOT NULL,
            accepted_by TEXT NOT NULL,
            rationale TEXT NOT NULL,
            boundary TEXT NOT NULL CHECK (boundary LIKE 'NO-%' OR boundary LIKE 'MFG-NO-%' OR boundary LIKE 'SEC-NO-%')
        );

        CREATE TABLE route_event (
            route_event_id TEXT PRIMARY KEY,
            route TEXT NOT NULL,
            trigger TEXT NOT NULL,
            activity TEXT NOT NULL,
            output_candidate TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('opened','resolved_local','blocked','deferred')),
            boundary TEXT NOT NULL CHECK (boundary LIKE 'NO-%' OR boundary LIKE 'MFG-NO-%' OR boundary LIKE 'SEC-NO-%'),
            created_at TEXT NOT NULL
        );

        CREATE TABLE candidate_decision (
            decision_id TEXT PRIMARY KEY,
            route_event_id TEXT NOT NULL,
            question TEXT NOT NULL,
            selected_option TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('draft','needs_review','accepted','rejected')),
            decided_by TEXT NOT NULL,
            decided_at TEXT NOT NULL,
            rationale TEXT NOT NULL,
            boundary TEXT NOT NULL CHECK (boundary LIKE 'NO-%' OR boundary LIKE 'MFG-NO-%' OR boundary LIKE 'SEC-NO-%'),
            FOREIGN KEY (route_event_id) REFERENCES route_event(route_event_id)
        );

        CREATE TABLE review_state (
            review_id TEXT PRIMARY KEY,
            decision_id TEXT NOT NULL,
            review_type TEXT NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN ('needs_review','rejected','blocked','accepted_local')
                OR status LIKE 'accepted_local_%'
            ),
            reviewer TEXT NOT NULL,
            reviewed_at TEXT NOT NULL,
            rationale TEXT NOT NULL,
            boundary TEXT NOT NULL CHECK (boundary LIKE 'NO-%' OR boundary LIKE 'MFG-NO-%' OR boundary LIKE 'SEC-NO-%'),
            FOREIGN KEY (decision_id) REFERENCES candidate_decision(decision_id)
        );

        CREATE TABLE handoff_candidate (
            handoff_id TEXT PRIMARY KEY,
            source_review_id TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN ('candidate_ready_for_manual_review','needs_review','rejected','blocked')
                OR status LIKE 'candidate_ready_for_manual_review_%'
            ),
            package_summary TEXT NOT NULL,
            excluded_counts_json TEXT NOT NULL,
            checksum_sha256 TEXT NOT NULL,
            boundary TEXT NOT NULL CHECK (boundary LIKE 'NO-%' OR boundary LIKE 'MFG-NO-%' OR boundary LIKE 'SEC-NO-%'),
            created_at TEXT NOT NULL,
            FOREIGN KEY (source_review_id) REFERENCES review_state(review_id)
        );
        """
    )


def seed_metadata(conn: sqlite3.Connection, profile: dict[str, Any], created_at: str) -> None:
    conn.executemany(
        "INSERT INTO metadata(key, value) VALUES (?, ?)",
        [
            ("project_id", str(profile.get("project_id", ""))),
            ("schema", "aivprocess-project/v1-local"),
            ("created_at", created_at),
            (
                "authority",
                "Project-local DB for facts, evidence, decisions, reviews, and handoff candidates.",
            ),
        ],
    )


def seed_project_facts(conn: sqlite3.Connection, profile: dict[str, Any], routing: dict[str, Any]) -> None:
    facts: list[tuple[str, str, str, str, str, str, str]] = []
    counter = 1

    def add(category: str, name: str, value: Any, source: str, boundary: str) -> None:
        nonlocal counter
        if value is None:
            return
        if isinstance(value, (list, dict)):
            value_text = json.dumps(value, sort_keys=True)
        else:
            value_text = str(value)
        facts.append(
            (
                f"FACT-{counter:03d}",
                category,
                name,
                value_text,
                source,
                "recorded",
                boundary,
            )
        )
        counter += 1

    for category in ("owner", "common", "organization", "project", "formal_systems", "evidence"):
        section = profile.get(category, {})
        if isinstance(section, dict):
            for name, value in sorted(section.items()):
                add(category, name, value, "project_profile.json", "NO-ROUTING-AS-APPROVAL")
    add("routing", "available_routes", len(routing.get("routes", [])), "routing_matrix.json", "NO-ROUTING-AS-APPROVAL")

    conn.executemany(
        """
        INSERT INTO project_fact(fact_id, category, name, value, source, status, boundary)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        facts,
    )


def seed_evidence(conn: sqlite3.Connection) -> None:
    conn.executemany(
        """
        INSERT INTO evidence(evidence_id, title, location, owner, status, boundary)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "EVID-001",
                "Project profile",
                ".aivprocess/project_profile.json",
                "project-owner",
                "available",
                "NO-TEMPLATE-AS-EVIDENCE",
            ),
            (
                "EVID-002",
                "Knowledge pack lock",
                ".aivprocess/knowledge_pack_lock.json",
                "project-owner",
                "available",
                "NO-LOCK-AS-APPROVAL",
            ),
            (
                "EVID-003",
                "Routing matrix",
                ".aivprocess/routing_matrix.json",
                "project-owner",
                "available",
                "NO-ROUTING-AS-APPROVAL",
            ),
            (
                "EVID-004",
                "Project database",
                ".aivprocess/project.db",
                "project-owner",
                "available",
                "NO-LOCAL-ACCEPTED-AS-FORMAL-APPROVAL",
            ),
        ],
    )


def seed_requirements(conn: sqlite3.Connection, requirements: dict[str, Any]) -> None:
    rows = []
    classification_rows = []
    allocation_rows = []
    trace_rows = []
    for item in requirements.get("requirements", []):
        requirement_id = str(item.get("requirement_id", ""))
        rows.append(
            (
                requirement_id,
                str(item.get("title", "")),
                str(item.get("requirement_type", "")),
                str(item.get("priority", "")),
                str(item.get("constraint_origin", "")),
                str(item.get("source", "")),
                str(item.get("statement", "")),
                str(item.get("acceptance_criteria", "")),
                str(item.get("verification_method", "")),
                str(item.get("status", "candidate_ready_for_manual_review")),
                str(item.get("boundary", "NO-CANDIDATE-AS-RECORD")),
            )
        )
        for classification in item.get("classifications", []):
            classification_rows.append(
                (
                    requirement_id,
                    str(classification.get("classification_type", "")),
                    str(classification.get("value", "")),
                    str(classification.get("rationale", "")),
                    str(classification.get("source", item.get("source", ""))),
                    str(classification.get("boundary", item.get("boundary", "NO-CANDIDATE-AS-RECORD"))),
                )
            )
        for allocation in item.get("allocations", []):
            allocation_rows.append(
                (
                    requirement_id,
                    str(allocation.get("target_layer", "")),
                    str(allocation.get("target_component", "")),
                    str(allocation.get("owner", "")),
                    str(allocation.get("rationale", "")),
                    str(allocation.get("status", item.get("status", "candidate_ready_for_manual_review"))),
                    str(allocation.get("boundary", item.get("boundary", "NO-CANDIDATE-AS-RECORD"))),
                )
            )
        for trace in item.get("traces", []):
            trace_rows.append(
                (
                    requirement_id,
                    str(trace.get("target_type", "")),
                    str(trace.get("target_id", "")),
                    str(trace.get("relation", "")),
                    str(trace.get("status", item.get("status", "candidate_ready_for_manual_review"))),
                    str(trace.get("boundary", item.get("boundary", "NO-CANDIDATE-AS-RECORD"))),
                )
            )
    conn.executemany(
        """
        INSERT INTO requirement_item(
            requirement_id, title, requirement_type, priority, constraint_origin, source,
            statement, acceptance_criteria, verification_method, status, boundary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.executemany(
        """
        INSERT INTO requirement_classification(
            requirement_id, classification_type, value, rationale, source, boundary
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        classification_rows,
    )
    conn.executemany(
        """
        INSERT INTO requirement_allocation(
            requirement_id, target_layer, target_component, owner, rationale, status, boundary
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        allocation_rows,
    )
    conn.executemany(
        """
        INSERT INTO requirement_trace(
            requirement_id, target_type, target_id, relation, status, boundary
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        trace_rows,
    )


def seed_knowledge_lock(conn: sqlite3.Connection, lock: dict[str, Any]) -> None:
    rows = []
    for item in lock.get("knowledge_packs", []):
        rows.append(
            (
                str(item.get("pack_id", "")),
                str(item.get("version", "")),
                str(item.get("manifest_sha256", "")),
                str(item.get("db_sha256", "")),
                str(item.get("accepted_at", "")),
                str(item.get("accepted_by", "")),
                str(item.get("rationale", "")),
                "NO-PACK-UPDATE-AS-PROJECT-APPROVAL",
            )
        )
    conn.executemany(
        """
        INSERT INTO knowledge_pack_adoption(
            pack_id, version, manifest_sha256, db_sha256, accepted_at, accepted_by, rationale, boundary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )


def initialize(db_path: Path) -> None:
    profile = read_json(PROFILE)
    lock = read_json(LOCK)
    routing = read_json(ROUTING)
    requirements = read_json(REQUIREMENTS)
    created_at = utc_now()
    with connect_new(db_path) as conn:
        create_schema(conn)
        seed_metadata(conn, profile, created_at)
        seed_project_facts(conn, profile, routing)
        seed_evidence(conn)
        seed_requirements(conn, requirements)
        seed_knowledge_lock(conn, lock)
        conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize .aivprocess/project.db for this starter project.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    initialize(args.db)
    print(args.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
