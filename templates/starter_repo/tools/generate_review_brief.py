from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / ".aivprocess" / "project.db"
LOCAL_TZ = dt.timezone(dt.timedelta(hours=9), "JST")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def today_stamp() -> str:
    return dt.datetime.now(LOCAL_TZ).strftime("%Y%m%d")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def cell(value: Any, limit: int = 180) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\n", " ").replace("|", "\\|").strip()
    if len(text) > limit:
        return text[: limit - 3].rstrip() + "..."
    return text


def table(rows_to_render: list[dict[str, Any]], columns: list[tuple[str, str]]) -> list[str]:
    if not rows_to_render:
        return ["No rows."]
    lines = [
        "| " + " | ".join(label for label, _ in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows_to_render:
        lines.append("| " + " | ".join(cell(row.get(key)) for _, key in columns) + " |")
    return lines


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"missing project DB: {db_path}; run tools/init_project_db.py first")
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def rows(conn: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(query, params).fetchall()]


def scalar(conn: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> Any:
    row = conn.execute(query, params).fetchone()
    return row[0] if row else None


def db_counts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    tables = [
        "project_fact",
        "evidence",
        "route_event",
        "candidate_decision",
        "review_state",
        "handoff_candidate",
    ]
    return [
        {"table": table_name, "count": int(scalar(conn, f"SELECT COUNT(*) FROM {table_name}") or 0)}
        for table_name in tables
    ]


def status_counts(conn: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    return rows(
        conn,
        f"""
        SELECT status, COUNT(*) AS count
        FROM {table_name}
        GROUP BY status
        ORDER BY count DESC, status
        """,
    )


def latest_handoffs(conn: sqlite3.Connection, limit: int) -> list[dict[str, Any]]:
    raw_rows = rows(
        conn,
        """
        SELECT handoff_id, status, created_at, package_summary, excluded_counts_json, boundary
        FROM handoff_candidate
        ORDER BY created_at DESC, handoff_id DESC
        LIMIT ?
        """,
        (limit,),
    )
    output = []
    for row in raw_rows:
        try:
            excluded = json.loads(row.get("excluded_counts_json") or "{}")
        except json.JSONDecodeError:
            excluded = {}
        output.append(
            {
                "handoff": row.get("handoff_id", ""),
                "status": row.get("status", ""),
                "created": row.get("created_at", ""),
                "excluded": ", ".join(f"{key}={value}" for key, value in sorted(excluded.items())) or "-",
                "boundary": row.get("boundary", ""),
                "summary": row.get("package_summary", ""),
            }
        )
    return output


def boundary_counts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    sources = [
        "SELECT boundary FROM project_fact",
        "SELECT boundary FROM evidence",
        "SELECT boundary FROM route_event",
        "SELECT boundary FROM candidate_decision",
        "SELECT boundary FROM review_state",
        "SELECT boundary FROM handoff_candidate",
        "SELECT boundary FROM knowledge_pack_adoption",
    ]
    return rows(
        conn,
        f"""
        SELECT boundary, COUNT(*) AS count
        FROM ({' UNION ALL '.join(sources)})
        WHERE boundary IS NOT NULL AND trim(boundary) != ''
        GROUP BY boundary
        ORDER BY count DESC, boundary
        LIMIT 10
        """,
    )


def project_profile() -> dict[str, Any]:
    profile = read_json(ROOT / ".aivprocess" / "project_profile.json")
    common = profile.get("common", {})
    project = profile.get("project", {})
    common = common if isinstance(common, dict) else {}
    project = project if isinstance(project, dict) else {}
    return {
        "project_id": profile.get("project_id", ROOT.name),
        "status": profile.get("status", ""),
        "domain": profile.get("domain", common.get("domain", "")),
        "lifecycle_stage": profile.get("lifecycle_stage", common.get("lifecycle_stage", "")),
        "release_intent": profile.get("release_intent", common.get("release_intent", "")),
        "known_gaps": profile.get("known_gaps", project.get("known_gaps", [])),
        "formal_systems": profile.get("formal_systems", {}),
    }


def route_coverage() -> dict[str, int]:
    routing = read_json(ROOT / ".aivprocess" / "routing_matrix.json")
    routes = sorted(
        {
            str(item.get("route", "")).strip()
            for item in routing.get("routes", [])
            if str(item.get("route", "")).strip() and str(item.get("route", "")).strip() != "HANDOFF"
        }
    )
    handoff_files = sorted((ROOT / "exports" / "handoff").glob("HANDOFF-*.md"))
    covered = 0
    for route in routes:
        if any(path.name.startswith(f"HANDOFF-{route}") for path in handoff_files):
            covered += 1
    return {
        "routes": len(routes),
        "handoff_exports": len(handoff_files),
        "covered_routes": covered,
        "missing_routes": max(0, len(routes) - covered),
    }


def pack_rows() -> list[dict[str, Any]]:
    lock = read_json(ROOT / ".aivprocess" / "knowledge_pack_lock.json")
    return [
        {
            "pack": item.get("pack_id", ""),
            "locked": item.get("version", ""),
            "accepted_by": item.get("accepted_by", ""),
            "accepted_at": item.get("accepted_at", ""),
        }
        for item in lock.get("knowledge_packs", [])
    ]


def attention(profile: dict[str, Any], coverage: dict[str, int], conn: sqlite3.Connection) -> list[str]:
    items: list[str] = []
    if coverage["missing_routes"]:
        items.append(f"{coverage['missing_routes']} route(s) still lack route-level handoff exports.")
    formal = profile.get("formal_systems", {})
    if isinstance(formal, dict):
        connector = str(formal.get("connector", formal.get("connector_mode", "")))
        if "disabled" in connector.casefold():
            items.append("Formal connector remains disabled; use manual handoff only.")
    gaps = profile.get("known_gaps", [])
    if isinstance(gaps, list):
        items.extend(str(gap) for gap in gaps[:5])
    non_accepted = int(scalar(conn, "SELECT COUNT(*) FROM candidate_decision WHERE status != 'accepted'") or 0)
    if non_accepted:
        items.append(f"{non_accepted} candidate decision(s) are not locally accepted.")
    if not items:
        items.append("No automatically detected blockers beyond the No-X boundaries in this brief.")
    return items


def render(db_path: Path, handoff_limit: int) -> str:
    profile = project_profile()
    coverage = route_coverage()
    with connect_readonly(db_path) as conn:
        count_rows = db_counts(conn)
        decisions = status_counts(conn, "candidate_decision")
        reviews = status_counts(conn, "review_state")
        handoff_status = status_counts(conn, "handoff_candidate")
        handoffs = latest_handoffs(conn, handoff_limit)
        boundaries = boundary_counts(conn)
        review_attention = attention(profile, coverage, conn)

    formal = profile.get("formal_systems", {})
    formal_connector = formal.get("connector", formal.get("connector_mode", "(not recorded)")) if isinstance(formal, dict) else "(not recorded)"
    lines = [
        f"# {profile['project_id']} Review Brief",
        "",
        f"Generated: `{utc_now()}`",
        "",
        "This Review Brief compresses the project-local DB, profile, routing matrix,",
        "knowledge-pack lock, and handoff exports into a small human review packet.",
        "",
        "It is not formal ALM/QMS import, formal approval, certification evidence,",
        "release authorization, shipment authorization, or return-to-service authority.",
        "",
        "## Project Snapshot",
        "",
        f"- Project DB: `{rel(db_path)}`",
        f"- Domain: {profile.get('domain') or '(not recorded)'}",
        f"- Status: `{profile.get('status') or '(not recorded)'}`",
        f"- Lifecycle stage: {profile.get('lifecycle_stage') or '(not recorded)'}",
        f"- Release intent: {profile.get('release_intent') or '(not recorded)'}",
        f"- Formal connector: {formal_connector}",
        "",
        "## What The Human Should Review First",
        "",
    ]
    lines.extend(f"- {item}" for item in review_attention[:8])
    lines.extend(
        [
            "",
            "## Route And Handoff Coverage",
            "",
            "| Item | Count |",
            "| --- | ---: |",
            f"| Routes in routing matrix | {coverage['routes']} |",
            f"| Handoff markdown exports | {coverage['handoff_exports']} |",
            f"| Routes with route-level handoff | {coverage['covered_routes']} |",
            f"| Missing route-level handoff | {coverage['missing_routes']} |",
            "",
            "## Project DB Compression",
            "",
        ]
    )
    lines.extend(table(count_rows, [("Table", "table"), ("Rows", "count")]))
    lines.extend(["", "## Knowledge Packs", ""])
    lines.extend(table(pack_rows(), [("Pack", "pack"), ("Locked", "locked"), ("Accepted by", "accepted_by"), ("Accepted at", "accepted_at")]))
    lines.extend(["", "## Review State Summary", "", "### Decisions", ""])
    lines.extend(table(decisions, [("Status", "status"), ("Count", "count")]))
    lines.extend(["", "### Reviews", ""])
    lines.extend(table(reviews, [("Status", "status"), ("Count", "count")]))
    lines.extend(["", "### Handoffs", ""])
    lines.extend(table(handoff_status, [("Status", "status"), ("Count", "count")]))
    lines.extend(["", "## Latest Handoff Candidates", ""])
    lines.extend(table(handoffs, [("Handoff", "handoff"), ("Status", "status"), ("Created", "created"), ("Excluded counts", "excluded"), ("Boundary", "boundary"), ("Summary", "summary")]))
    lines.extend(["", "## Dominant No-X Boundaries", ""])
    lines.extend(table(boundaries, [("Boundary", "boundary"), ("Rows", "count")]))
    lines.extend(
        [
            "",
            "## Next Actions",
            "",
            "1. Human reviewer reads the items in `What The Human Should Review First`.",
            "2. Open only the relevant handoff exports and evidence records for those items.",
            "3. Decide whether any candidate can move into a formal ALM/QMS workflow.",
            "4. Keep rejected, deferred, or unreviewed candidates visible; do not silently drop them.",
            "",
            "## Boundary",
            "",
            "- `NO-CANDIDATE-AS-RECORD`: generated candidates are not controlled records.",
            "- `NO-ROUTING-AS-APPROVAL`: routing suggestions are not approvals.",
            "- `NO-HANDOFF-AS-IMPORT`: handoff packages are not import completion.",
            "- `NO-LOCAL-ACCEPTED-AS-FORMAL-APPROVAL`: local acceptance is not formal approval.",
            "- `NO-CEREMONY-AS-ENGINEERING`: completing the brief does not prove engineering soundness.",
            "",
        ]
    )
    return "\n".join(lines)


def record_brief(db_path: Path, output: Path, generated_at: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        rel_output = rel(output)
        conn.execute(
            """
            INSERT OR REPLACE INTO project_fact
            (fact_id, category, name, value, source, status, boundary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "FACT-REVIEW-BRIEF-LATEST",
                "review_brief",
                "latest_review_brief",
                f"{rel_output} compresses project profile, route coverage, project DB counts, latest handoffs, review attention, and No-X boundaries for human review.",
                rel_output,
                "candidate_ready_for_manual_review",
                "NO-CANDIDATE-AS-RECORD",
            ),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO evidence
            (evidence_id, title, location, owner, status, boundary)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                f"EVID-REVIEW-BRIEF-{today_stamp()}",
                f"Review brief generated at {generated_at}",
                rel_output,
                "project owner + human reviewer",
                "candidate_ready_for_manual_review",
                "NO-CANDIDATE-AS-RECORD",
            ),
        )
        conn.commit()
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a compact review brief for this starter project.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output", type=Path, default=ROOT / "docs" / f"review_brief_{today_stamp()}.md")
    parser.add_argument("--handoff-limit", type=int, default=8)
    parser.add_argument("--record-db", action="store_true")
    args = parser.parse_args()

    generated_at = utc_now()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(args.db, args.handoff_limit), encoding="utf-8")
    if args.record_db:
        record_brief(args.db, args.output, generated_at)
        os.utime(args.output, None)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
