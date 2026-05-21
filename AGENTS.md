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
3. `docs/02_responsibility_boundary.md`
4. `docs/03_project_profile_pattern.md`
5. `docs/05_gate_trace_review_example.md`
6. `docs/06_connector_permission_example.md`
7. `examples/sample_project_profile.json`
8. `examples/sample_routing.json`

## Working Rules

- Keep examples fictional and sanitized.
- Keep the repository vendor-neutral.
- Do not copy private source text, private paths, private hostnames, local DB
  names, credentials, customer names, or internal operating logs.
- Keep work-item-like records, gates, traces, connector permissions, and
  routing outputs as candidates until reviewed.
- Do not present examples as compliance, approval, certification, safety case,
  cybersecurity case, legal advice, or production readiness.
- Run `python tools/check_public_safety.py` before commit or publication.
