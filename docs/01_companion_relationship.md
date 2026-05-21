# Companion Relationship

`ai-vprocess-ops` defines the abstract pattern. This repository shows a small
applied playbook for using that pattern in V-process and ALM-style work.

The relationship is:

```text
ai-vprocess-ops -> method and prototype
ai-vprocess-playbook -> applied examples
your project -> owned facts, evidence, reviews, tools, approvals
formal system -> official records and audit trail
```

The playbook is intentionally thin. It is not a synchronized mirror of any
private workspace. Treat it as a stable public snapshot of reusable operating
patterns.

## Ownership Split

| Layer | Owns | Does not own |
| --- | --- | --- |
| `ai-vprocess-ops` | No-X rules, local graph idea, reviewable AI-assisted engineering pattern. | Project-specific examples or official records. |
| `ai-vprocess-playbook` | Vendor-neutral applied examples and starter shapes. | Tool-specific configuration, certification, or production approval. |
| Your project | Real facts, constraints, evidence, owners, decisions, and review results. | Automatic correctness from this public playbook. |
| Formal system | Official workflow state, baselines, signatures, and audit records. | Unreviewed AI-generated candidates. |

## Continuation Strategy

This repository should grow by deliberate additions, not by continuous syncing
from a private workspace. A good public addition should be:

- sanitized;
- vendor-neutral;
- useful without private context;
- small enough to review;
- clear about candidate versus official-record boundaries.
