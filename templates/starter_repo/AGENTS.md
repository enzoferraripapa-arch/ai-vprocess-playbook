# Agent Instructions

This repository uses the AI V-process starter layout.

## Read Order

1. `README.md`
2. `.aivprocess/project_profile.json`
3. `.aivprocess/knowledge_pack_lock.json`
4. `.aivprocess/routing_matrix.json`
5. `docs/no_x_rules.md`
6. `docs/responsibility_boundary.md`
7. `docs/handoff_template.md`

## Rules

- Keep project facts in `.aivprocess/project_profile.json` or the project DB.
- Keep reusable knowledge in external knowledge packs.
- Do not paste private standards text, customer material, credentials, local
  hostnames, or private source paths into public artifacts.
- Treat routes, decisions, traces, gates, and handoffs as candidates until a
  responsible human accepts them.
- A local accepted state is not a formal ALM/QMS approval.
- Run `python tools/check_public_safety.py` before publishing, handoff, or
  external sharing.
