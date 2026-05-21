# Agent Instructions

Use this repository as the applied-example companion to `ai-vprocess-ops`.
It is vendor-neutral. Do not introduce tool-vendor-specific naming unless the
user explicitly asks for a private adaptation.

## Core Rule

Applied examples are not authority.

```text
The playbook shows candidate structure.
The project owner supplies facts and evidence.
Human reviewers accept or reject the work.
Formal systems keep official records and approvals.
```

## Read Order

1. `README.md`
2. `docs/01_companion_relationship.md`
3. `docs/00_no_x_rules_quickref.md`
4. `docs/08_alm_vocabulary_mapping.md`
5. `docs/03_project_profile_pattern.md`
6. `docs/09_knowledge_pack_architecture.md`
7. `docs/10_adoption_starter_pack.md`
8. `docs/07_routing_matrix_example.md`
9. `docs/05_gate_trace_review_example.md`
10. `docs/06_connector_permission_example.md`
11. `docs/04_work_item_sop_skeleton.md`
12. `docs/02_responsibility_boundary.md`
13. `examples/scenarios/01_firmware_update_walkthrough.md`
14. `examples/sample_project_profile.json`
15. `examples/sample_routing.json`
16. `examples/starter_project/.aivprocess/knowledge_pack_lock.json`
17. `templates/starter_repo/`

## Working Rules

- Keep examples fictional and sanitized.
- Keep the repository vendor-neutral.
- Do not copy private source text, private paths, private hostnames, local DB
  names, credentials, customer names, or internal operating logs.
- Keep work-item-like records, gates, traces, connector permissions, and
  routing outputs as candidates until reviewed.
- Keep product-specific project DBs separate from shared knowledge-pack DBs.
- Do not treat a skill, app, connector, or dashboard as the knowledge authority.
- When adding starter templates, keep them fictional and generic enough to copy
  into a new repository without leaking private context.
- Prefer worked fictional examples over abstract placeholders when adding new
  material.
- Do not present examples as compliance, approval, certification, safety case,
  cybersecurity case, legal advice, or production readiness.
- Run `python tools/check_public_safety.py` before commit or publication.
