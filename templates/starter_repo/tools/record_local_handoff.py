from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / ".aivprocess" / "project.db"
ROUTING = ROOT / ".aivprocess" / "routing_matrix.json"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"missing project DB: {db_path}; run tools/init_project_db.py first")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def route_defaults(route_name: str | None) -> dict[str, Any]:
    routing = read_json(ROUTING)
    routes = routing.get("routes", [])
    if not routes:
        raise ValueError("routing_matrix.json has no routes")
    if route_name:
        for route in routes:
            if route.get("route") == route_name:
                return route
        raise ValueError(f"route not found in routing_matrix.json: {route_name}")
    for route in routes:
        if route.get("route") == "HANDOFF":
            return route
    return routes[0]


def checksum_payload(args: argparse.Namespace, excluded: dict[str, int]) -> str:
    payload = {
        "handoff_id": args.handoff_id,
        "review_id": args.review_id,
        "decision_id": args.decision_id,
        "excluded_counts": excluded,
        "boundary": "NO-HANDOFF-AS-IMPORT",
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def record(args: argparse.Namespace) -> None:
    route = route_defaults(args.route)
    created_at = utc_now()
    excluded = {
        "non_accepted_decisions": args.non_accepted_decisions,
        "non_accepted_trace_candidates": args.non_accepted_trace_candidates,
        "gate_candidates_not_passed": args.gate_candidates_not_passed,
        "connector_actions_not_approved": args.connector_actions_not_approved,
    }
    checksum = checksum_payload(args, excluded)

    with connect(args.db) as conn:
        conn.execute(
            """
            INSERT INTO route_event(
                route_event_id, route, trigger, activity, output_candidate, status, boundary, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                args.route_event_id,
                route.get("route", ""),
                args.trigger,
                route.get("activity", ""),
                route.get("output_candidate", ""),
                "opened",
                route.get("boundary", "NO-ROUTING-AS-APPROVAL"),
                created_at,
            ),
        )
        conn.execute(
            """
            INSERT INTO candidate_decision(
                decision_id, route_event_id, question, selected_option, status,
                decided_by, decided_at, rationale, boundary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                args.decision_id,
                args.route_event_id,
                args.question,
                args.selected_option,
                "accepted",
                args.reviewer,
                created_at,
                args.decision_rationale,
                "NO-LOCAL-ACCEPTED-AS-FORMAL-APPROVAL",
            ),
        )
        conn.execute(
            """
            INSERT INTO review_state(
                review_id, decision_id, review_type, status, reviewer, reviewed_at, rationale, boundary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                args.review_id,
                args.decision_id,
                "local_review",
                "accepted_local",
                args.reviewer,
                created_at,
                args.review_rationale,
                "NO-LOCAL-ACCEPTED-AS-FORMAL-APPROVAL",
            ),
        )
        conn.execute(
            """
            INSERT INTO handoff_candidate(
                handoff_id, source_review_id, title, status, package_summary,
                excluded_counts_json, checksum_sha256, boundary, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                args.handoff_id,
                args.review_id,
                args.title,
                "candidate_ready_for_manual_review",
                args.package_summary,
                json.dumps(excluded, sort_keys=True),
                checksum,
                "NO-HANDOFF-AS-IMPORT",
                created_at,
            ),
        )
        conn.commit()
    print(args.handoff_id)
    print(checksum)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record one accepted local review and handoff candidate.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--route", help="Route ID from .aivprocess/routing_matrix.json. Defaults to HANDOFF, then first route.")
    parser.add_argument("--route-event-id", default="ROUTE-001")
    parser.add_argument("--decision-id", default="DEC-001")
    parser.add_argument("--review-id", default="REV-001")
    parser.add_argument("--handoff-id", default="HANDOFF-001")
    parser.add_argument("--trigger", default="accepted_local_decision_ready_for_handoff")
    parser.add_argument("--question", default="Should this accepted local decision be included in a handoff candidate?")
    parser.add_argument("--selected-option", default="Prepare a manual handoff candidate for human-controlled review.")
    parser.add_argument("--title", default="Local review handoff candidate")
    parser.add_argument(
        "--package-summary",
        default="Accepted local review record prepared as a bounded handoff candidate; no formal-system import is claimed.",
    )
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--decision-rationale", required=True)
    parser.add_argument(
        "--review-rationale",
        default="Accepted for local handoff rehearsal only; formal-system authority remains external.",
    )
    parser.add_argument("--non-accepted-decisions", type=int, default=0)
    parser.add_argument("--non-accepted-trace-candidates", type=int, default=0)
    parser.add_argument("--gate-candidates-not-passed", type=int, default=0)
    parser.add_argument("--connector-actions-not-approved", type=int, default=0)
    args = parser.parse_args()
    record(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
