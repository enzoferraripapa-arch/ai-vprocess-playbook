# Knowledge Pack Architecture

Use separate databases for project facts and reusable knowledge.

The split is intentional:

```text
project database       = product-specific facts, decisions, evidence, reviews
knowledge pack DBs     = reusable methods, standards indexes, design rules
skills / apps / tools  = clients that read the DBs and create bounded outputs
```

Do not make a skill, app, or connector the source of truth for reusable
engineering knowledge. They may package prompts, UI, commands, and workflows,
but the reusable knowledge should live in versioned knowledge packs.

## Recommended Layout

```text
organization-knowledge-packs/
  process-method/
    knowledge.db
    manifest.json
    changelog.md
  security-privacy/
    knowledge.db
    manifest.json
    changelog.md

product-repository/
  .aivprocess/
    project.db
    project_profile.json
    knowledge_pack_lock.json
```

The public playbook keeps only example manifests and locks. It does not publish
real knowledge databases.

## Ownership

| Layer | Owns | Must not own |
| --- | --- | --- |
| Project DB | Product facts, decisions, evidence, review state, handoff events. | Reusable standards or method knowledge. |
| Knowledge pack DB | Reusable concepts, rules, failure modes, source references, review prompts. | Project approvals or product-specific decisions. |
| Skill | Agent behavior, read order, command conventions. | Knowledge authority. |
| App | Human UI, dashboards, review screens, connector controls. | Final engineering approval. |
| Connector | Read-only collection, dry-run, or bounded handoff. | Unreviewed writes into formal systems. |

## Manifest

Each knowledge pack needs a manifest.

```json
{
  "pack_id": "process-method",
  "version": "0.2.0",
  "schema_version": "knowledge-pack-manifest/v1",
  "db_filename": "knowledge.db",
  "db_sha256": "real-sha256-of-knowledge-db",
  "compatible_project_schema": "aivprocess-project/v1",
  "status": "local_db_built",
  "summary": "Reusable process-method rules and review prompts."
}
```

The manifest is the stable contract. A product may lock a pack only when the
referenced DB file exists and its SHA-256 matches `db_sha256`. Example-only
manifests are documentation fixtures, not adoptable knowledge packs.

## Project Lock

Each project records the exact knowledge pack versions it used.

```json
{
  "project_id": "fictional-starter-project",
  "knowledge_packs": [
    {
      "pack_id": "process-method",
      "version": "0.1.0",
      "manifest_sha256": "example-lock-hash",
      "db_sha256": "real-sha256-of-knowledge-db",
      "accepted_at": "2026-05-21T00:00:00Z",
      "accepted_by": "example-reviewer",
      "rationale": "Initial starter project baseline."
    }
  ]
}
```

Updating a pack changes the lock. It does not rewrite project decisions by
itself.

## Update Workflow

Use staged updates:

1. `check`: compare the project lock with available pack manifests.
2. `plan`: show what would change.
3. `stage`: write the update plan into `.aivprocess/update_staging/`.
4. `review`: let a human inspect the staged plan.
5. `accept`: update the lock and record who accepted the new pack version.

Example:

```bash
python tools/knowledge_pack.py check --project examples/starter_project --packs examples/knowledge_packs
python tools/knowledge_pack.py plan --project examples/starter_project --packs examples/knowledge_packs
python tools/knowledge_pack.py stage --project examples/starter_project --packs examples/knowledge_packs
```

## No-X Rules

- `NO-PACK-UPDATE-AS-PROJECT-APPROVAL`: Updating common knowledge does not
  approve a product decision.
- `NO-LATEST-AS-CORRECT`: The latest pack is not automatically right for a
  given project.
- `NO-KNOWLEDGE-PACK-AS-SOURCE-LICENSE`: A summarized pack is not a substitute
  for licensed standards, official source documents, or competent review.
- `NO-APP-AS-AUTHORITY`: A skill, app, or dashboard may surface knowledge, but
  it does not become the authority.

## Client Pattern

Skills and apps should take explicit inputs:

```text
project DB path
project profile path
knowledge pack lock path
knowledge pack search path
output mode: candidate / staged / handoff
```

That keeps the project-specific state separate from the shared knowledge state.
