# Reviewable AI-Assisted Engineering Starter

This repository uses an AI V-process starter layout.

It separates:

```text
project facts and decisions      -> this repository
shared knowledge packs           -> external versioned packs
formal ALM / SOP / QMS records   -> the approved customer or organization system
```

Use this repository like a working method layer, not like a permit. Local
candidate decisions, traces, routes, and handoff packages are not formal
approvals.

## First Files

1. `AGENTS.md`
2. `.aivprocess/project_profile.json`
3. `.aivprocess/knowledge_pack_lock.json`
4. `.aivprocess/routing_matrix.json`
5. `docs/no_x_rules.md`
6. `docs/responsibility_boundary.md`
7. `docs/handoff_template.md`

## Local Project DB

Create the project-local DB after the profile, lock, and routing matrix are
reviewed:

```bash
python tools/init_project_db.py
```

Record one accepted local review and a bounded handoff candidate:

```bash
python tools/record_local_handoff.py \
  --reviewer example-reviewer \
  --decision-rationale "Local reviewer accepted this record for handoff rehearsal."
```

Export the handoff candidate:

```bash
python tools/export_handoff.py
```

The generated `.aivprocess/project.db` is local project state. Exported handoff
files are candidate review material, not formal-system imports.

## Local Checks

```bash
python tools/check_public_safety.py
```

## Ownership

The project owner must supply facts, evidence, review decisions, formal
approval, and release authority. The AI agent may help organize candidates and
draft handoff material, but it does not become the authority.
