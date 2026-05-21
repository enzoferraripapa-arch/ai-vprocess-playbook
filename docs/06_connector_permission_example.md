# Connector Permission Example

Connectors are useful only when their authority is explicit.

## Permission Tiers

| Tier | Meaning | Example use |
| --- | --- | --- |
| Read-only | The connector may read approved project data. | Search records, retrieve evidence pointers, inspect status. |
| Dry-run | The connector may compute intended changes without writing. | Preview field updates, link changes, or import deltas. |
| Handoff | The connector may generate a package for a human or approved import path. | Markdown, CSV, JSON, or review bundle. |
| Write-capable | The connector may write through an approved, audited route. | Only after explicit authority, rollback proof, and human gate. |

## Required Checks

- What identity is used?
- Which project or record scope is allowed?
- Is the connector read-only, dry-run, handoff, or write-capable?
- Where is the audit trail?
- What is the rollback or correction path?
- Which human gate is required before write-capable execution?

## Boundary

An assignment is not authority. A package is not import completion.

Use the No-X rules:

```text
NO-HANDOFF-AS-IMPORT
NO-STATE-SKIP
NO-CEREMONY-AS-ENGINEERING
```
