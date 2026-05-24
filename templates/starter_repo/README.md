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
3. `.aivprocess/requirements.json`
4. `.aivprocess/knowledge_pack_lock.json`
5. `.aivprocess/routing_matrix.json`
6. `.aivprocess/project.db` after it exists
7. `docs/review_brief_YYYYMMDD.md` after it exists
8. `docs/no_x_rules.md`
9. `docs/responsibility_boundary.md`
10. `docs/handoff_template.md`

## Local Project DB

Create the project-local DB after the profile, requirements, lock, and routing
matrix are reviewed. Functional and nonfunctional requirements must include
priority and acceptance/verification notes. Nonfunctional requirements must also
name whether the constraint is architectural, human-factors/ergonomics,
regulatory, safety, security, operational, manufacturing, evidence-related, or
mixed:

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

Generate the compact Review Brief:

```bash
python tools/generate_review_brief.py --record-db
```

The generated `.aivprocess/project.db` is local project state. Exported handoff
files are candidate review material, not formal-system imports.
The generated Review Brief is the preferred first packet for human review; it
compresses the project DB, route coverage, handoff candidates, knowledge-pack
lock, requirement summary, priority summary, nonfunctional constraint origins,
review attention, and No-X boundaries before reviewers open the larger document
set.

## Local Checks

```bash
python tools/check_public_safety.py
python -m py_compile tools/generate_review_brief.py
```

## Ownership

The project owner must supply facts, evidence, review decisions, formal
approval, and release authority. The AI agent may help organize candidates and
draft handoff material, but it does not become the authority.
