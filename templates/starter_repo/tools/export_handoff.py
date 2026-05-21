from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / ".aivprocess" / "project.db"
DEFAULT_OUTPUT_DIR = ROOT / "exports" / "handoff"


def connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"missing project DB: {db_path}; run tools/init_project_db.py first")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def rows(conn: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(query, params).fetchall()]


def one(conn: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any]:
    row = conn.execute(query, params).fetchone()
    if row is None:
        raise ValueError("no matching handoff candidate found")
    return dict(row)


def metadata(conn: sqlite3.Connection) -> dict[str, str]:
    return {row["key"]: row["value"] for row in conn.execute("SELECT key, value FROM metadata")}


def select_handoff_id(conn: sqlite3.Connection, requested: str | None) -> str:
    if requested:
        return requested
    row = conn.execute(
        """
        SELECT handoff_id
        FROM handoff_candidate
        ORDER BY created_at DESC, handoff_id DESC
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        raise ValueError("project DB has no handoff candidates")
    return str(row["handoff_id"])


def collect_handoff(conn: sqlite3.Connection, handoff_id: str | None = None) -> dict[str, Any]:
    selected_handoff_id = select_handoff_id(conn, handoff_id)
    handoff = one(
        conn,
        """
        SELECT
            h.handoff_id,
            h.title,
            h.status AS handoff_status,
            h.package_summary,
            h.excluded_counts_json,
            h.checksum_sha256,
            h.boundary AS handoff_boundary,
            h.created_at AS handoff_created_at,
            v.review_id,
            v.review_type,
            v.status AS review_status,
            v.reviewer,
            v.reviewed_at,
            v.rationale AS review_rationale,
            v.boundary AS review_boundary,
            d.decision_id,
            d.question,
            d.selected_option,
            d.status AS decision_status,
            d.decided_by,
            d.decided_at,
            d.rationale AS decision_rationale,
            d.boundary AS decision_boundary,
            r.route_event_id,
            r.route,
            r.trigger,
            r.activity,
            r.output_candidate,
            r.status AS route_status,
            r.boundary AS route_boundary,
            r.created_at AS route_created_at
        FROM handoff_candidate h
        JOIN review_state v ON v.review_id = h.source_review_id
        JOIN candidate_decision d ON d.decision_id = v.decision_id
        JOIN route_event r ON r.route_event_id = d.route_event_id
        WHERE h.handoff_id = ?
        """,
        (selected_handoff_id,),
    )

    return {
        "export_type": "aivprocess_project_handoff_candidate",
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "project": metadata(conn),
        "handoff": {
            "handoff_id": handoff["handoff_id"],
            "title": handoff["title"],
            "status": handoff["handoff_status"],
            "summary": handoff["package_summary"],
            "excluded_counts": json.loads(handoff["excluded_counts_json"]),
            "checksum_sha256": handoff["checksum_sha256"],
            "boundary": handoff["handoff_boundary"],
            "created_at": handoff["handoff_created_at"],
        },
        "route": {
            "route_event_id": handoff["route_event_id"],
            "route": handoff["route"],
            "trigger": handoff["trigger"],
            "activity": handoff["activity"],
            "output_candidate": handoff["output_candidate"],
            "status": handoff["route_status"],
            "boundary": handoff["route_boundary"],
            "created_at": handoff["route_created_at"],
        },
        "decision": {
            "decision_id": handoff["decision_id"],
            "question": handoff["question"],
            "selected_option": handoff["selected_option"],
            "status": handoff["decision_status"],
            "decided_by": handoff["decided_by"],
            "decided_at": handoff["decided_at"],
            "rationale": handoff["decision_rationale"],
            "boundary": handoff["decision_boundary"],
        },
        "review": {
            "review_id": handoff["review_id"],
            "review_type": handoff["review_type"],
            "status": handoff["review_status"],
            "reviewer": handoff["reviewer"],
            "reviewed_at": handoff["reviewed_at"],
            "rationale": handoff["review_rationale"],
            "boundary": handoff["review_boundary"],
        },
        "evidence": rows(
            conn,
            """
            SELECT evidence_id, title, location, owner, status, boundary
            FROM evidence
            ORDER BY evidence_id
            """,
        ),
        "knowledge_packs": rows(
            conn,
            """
            SELECT pack_id, version, manifest_sha256, accepted_at, accepted_by, rationale, boundary
            FROM knowledge_pack_adoption
            ORDER BY pack_id
            """,
        ),
        "no_x_boundary": [
            "NO-HANDOFF-AS-IMPORT",
            "NO-LOCAL-ACCEPTED-AS-FORMAL-APPROVAL",
            "NO-PACK-UPDATE-AS-PROJECT-APPROVAL",
            "NO-ROUTING-AS-APPROVAL",
        ],
    }


def cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def table(rows_to_render: list[dict[str, Any]], columns: list[tuple[str, str]]) -> list[str]:
    lines = [
        "| " + " | ".join(label for label, _ in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows_to_render:
        values = [cell(row.get(key, "")) for _, key in columns]
        lines.append("| " + " | ".join(values) + " |")
    return lines


def render_markdown(payload: dict[str, Any]) -> str:
    project = payload["project"]
    route = payload["route"]
    decision = payload["decision"]
    review = payload["review"]
    handoff = payload["handoff"]
    excluded = handoff["excluded_counts"]

    lines = [
        f"# {handoff['title']}",
        "",
        "This is a local handoff candidate for human review.",
        "",
        "It is not a formal-system import, formal ALM/QMS approval, compliance",
        "evidence, certification, or release authorization.",
        "",
        "## Project",
        "",
        f"- Project ID: `{project.get('project_id', '')}`",
        f"- Project schema: `{project.get('schema', '')}`",
        f"- Handoff ID: `{handoff['handoff_id']}`",
        f"- Handoff status: `{handoff['status']}`",
        f"- Created at: `{handoff['created_at']}`",
        f"- Package checksum: `{handoff['checksum_sha256']}`",
        "",
        "## Route",
        "",
        f"- Route: `{route['route']}`",
        f"- Trigger: {route['trigger']}",
        f"- Activity: {route['activity']}",
        f"- Output candidate: {route['output_candidate']}",
        f"- Boundary: `{route['boundary']}`",
        "",
        "## Included Local Decision",
        "",
        "| Decision | Status | Reviewer | Rationale |",
        "| --- | --- | --- | --- |",
        (
            f"| `{decision['decision_id']}` | `{decision['status']}` | "
            f"{cell(decision['decided_by'])} | {cell(decision['rationale'])} |"
        ),
        "",
        "## Local Review",
        "",
        f"- Review ID: `{review['review_id']}`",
        f"- Review status: `{review['status']}`",
        f"- Reviewer: {review['reviewer']}",
        f"- Reviewed at: `{review['reviewed_at']}`",
        f"- Rationale: {review['rationale']}",
        f"- Boundary: `{review['boundary']}`",
        "",
        "## Evidence References",
        "",
    ]
    lines.extend(
        table(
            payload["evidence"],
            [
                ("Evidence", "evidence_id"),
                ("Title", "title"),
                ("Location", "location"),
                ("Owner", "owner"),
                ("Status", "status"),
                ("Boundary", "boundary"),
            ],
        )
    )
    lines.extend(["", "## Knowledge Pack Lock", ""])
    lines.extend(
        table(
            payload["knowledge_packs"],
            [
                ("Pack", "pack_id"),
                ("Version", "version"),
                ("Accepted by", "accepted_by"),
                ("Boundary", "boundary"),
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Excluded Counts",
            "",
            f"- non-accepted decisions: `{excluded.get('non_accepted_decisions', 0)}`",
            f"- non-accepted trace candidates: `{excluded.get('non_accepted_trace_candidates', 0)}`",
            f"- gate candidates not passed: `{excluded.get('gate_candidates_not_passed', 0)}`",
            f"- connector actions not approved: `{excluded.get('connector_actions_not_approved', 0)}`",
            "",
            "## No-X Boundary",
            "",
        ]
    )
    for boundary in payload["no_x_boundary"]:
        lines.append(f"- `{boundary}`")
    lines.append("")
    return "\n".join(lines)


def write_outputs(payload: dict[str, Any], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    handoff_id = payload["handoff"]["handoff_id"]
    json_path = output_dir / f"{handoff_id}.json"
    md_path = output_dir / f"{handoff_id}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    return [json_path, md_path]


def main() -> int:
    parser = argparse.ArgumentParser(description="Export project handoff candidates from .aivprocess/project.db.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--handoff-id")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    with connect(args.db) as conn:
        payload = collect_handoff(conn, args.handoff_id)
    outputs = write_outputs(payload, args.output_dir)
    for path in outputs:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
