# Agent Instructions

This repository uses the AI V-process starter layout.

## Read Order

1. `README.md`
2. `.aivprocess/project_profile.json`
3. `.aivprocess/requirements.json`
4. `.aivprocess/knowledge_pack_lock.json`
5. `.aivprocess/routing_matrix.json`
6. `.aivprocess/project.db` if it exists
7. `docs/review_brief_YYYYMMDD.md` if it exists
8. `docs/no_x_rules.md`
9. `docs/responsibility_boundary.md`
10. `docs/handoff_template.md`

## Rules

- Keep project facts in `.aivprocess/project_profile.json` or the project DB.
- Keep functional/nonfunctional requirements in `.aivprocess/requirements.json`
  and the project DB. Nonfunctional requirements must identify whether they are
  driven by architecture, human factors/ergonomics, regulation, safety,
  security, operation, manufacturing, evidence, or mixed constraints.
- Keep reusable knowledge in external knowledge packs.
- Do not paste private standards text, customer material, credentials, local
  hostnames, or private source paths into public artifacts.
- Treat routes, decisions, traces, gates, and handoffs as candidates until a
  responsible human accepts them.
- A local accepted state is not a formal ALM/QMS approval.
- Use `tools/init_project_db.py`, `tools/record_local_handoff.py`, and
  `tools/export_handoff.py` for the starter DB workflow unless the project has
  adopted a different reviewed tool.
- Use `tools/generate_review_brief.py --record-db` to create the small
  human-facing packet after DB/handoff updates.
- Run `python tools/check_public_safety.py` before publishing, handoff, or
  external sharing.
