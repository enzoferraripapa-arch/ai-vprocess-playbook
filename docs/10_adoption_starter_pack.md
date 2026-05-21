# Adoption Starter Pack

Use the starter pack when you want to apply the playbook to a new product,
customer project, or internal repository.

The starter pack creates the project-side boundary. It does not copy reusable
knowledge databases into the product repository.

## What To Copy

Copy `templates/starter_repo/` into a new project repository.

```bash
python tools/create_starter_project.py --target ../my-product-repo
```

The template contains:

| Path | Purpose |
| --- | --- |
| `README.md` | Local project entry point. |
| `AGENTS.md` | Instructions for AI coding agents. |
| `.aivprocess/project_profile.json` | Product-specific facts and scope. |
| `.aivprocess/knowledge_pack_lock.json` | Exact shared knowledge-pack versions used. |
| `.aivprocess/routing_matrix.json` | Local activity routing candidates. |
| `docs/no_x_rules.md` | Boundary rules adopted by the project. |
| `docs/responsibility_boundary.md` | What the project owner must still own. |
| `docs/handoff_template.md` | Bounded handoff package skeleton. |
| `tools/check_public_safety.py` | Local publication safety gate. |

## First Setup

1. Replace fictional product text in `README.md`.
2. Fill `.aivprocess/project_profile.json`.
3. Point `.aivprocess/knowledge_pack_lock.json` at the knowledge packs the
   project actually uses.
4. Review `.aivprocess/routing_matrix.json`.
5. Run the safety gate.

```bash
python tools/check_public_safety.py
```

## Product DB vs Knowledge DB

The starter repository is where product-specific facts live.

```text
This project repo:
  .aivprocess/project.db          product facts and review state
  .aivprocess/project_profile     product scope
  .aivprocess/knowledge_pack_lock versions used

Outside this repo:
  knowledge packs                 reusable methods and review prompts
```

Do not paste common standards text, private customer documents, or shared
knowledge-pack internals into the product repo unless the project is allowed to
own and disclose that material.

## Customer Installation Boundary

For customer work, install the starter pack as a local method layer:

```text
customer repo
  -> owns facts, evidence, decisions, approvals
shared knowledge packs
  -> provide reusable prompts and rules
formal ALM/QMS
  -> remains authority for official records
```

Start with read-only collection and Markdown handoff. Add direct connectors
only after the customer approves credentials, permissions, rollback handling,
and record ownership.

## No-X Rules

- `NO-STARTER-AS-PROCESS`: Copying the starter pack does not mean a process is
  implemented.
- `NO-TEMPLATE-AS-EVIDENCE`: Filling a template does not create evidence.
- `NO-LOCK-AS-APPROVAL`: Locking a knowledge pack version does not approve the
  project decision.
- `NO-HANDOFF-AS-IMPORT`: A handoff package is not a formal-system import.
- `NO-APP-AS-AUTHORITY`: A skill, app, or dashboard is not the knowledge or
  approval authority.

## Minimum Adoption Review

Before calling a project "set up", check:

- product profile has real owner, domain, lifecycle stage, and risk notes;
- knowledge pack lock names exact pack versions and hashes;
- routing matrix has project-specific triggers, not only template examples;
- responsibility boundary is accepted by the project owner;
- handoff route is defined as manual, dry-run, or approved connector;
- safety gate passes.
