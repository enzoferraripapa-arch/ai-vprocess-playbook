# No-X Rules Quick Reference

The canonical pattern lives in
[ai-vprocess-ops/docs/15_no_x_rule_pattern.md](https://github.com/enzoferraripapa-arch/ai-vprocess-ops/blob/main/docs/15_no_x_rule_pattern.md).

This quick reference makes the playbook readable without switching repositories
first.

| Rule | Plain meaning |
| --- | --- |
| `NO-ROUTING-AS-APPROVAL` | A recommendation or route only opens work. It does not approve the work. |
| `NO-CANDIDATE-AS-RECORD` | A generated candidate is not a controlled project record. |
| `NO-GATE-CANDIDATE-AS-PASS` | A gate candidate is not a passed gate. |
| `NO-TRACE-CANDIDATE-AS-TRACEABILITY` | A suggested link is not accepted traceability. |
| `NO-HANDOFF-AS-IMPORT` | A handoff package is not proof that a formal system was updated. |
| `NO-LOCAL-ACCEPTED-AS-FORMAL-APPROVAL` | A local accepted decision is not formal ALM/QMS approval. |
| `NO-STATE-SKIP` | State cannot advance just because the next state is convenient or implied. |
| `NO-CEREMONY-AS-ENGINEERING` | Completing a form or checklist does not prove the engineering decision is sound. |

## Empty Evidence Sections

An empty future evidence slot should be marked as absence, not as a promise:

```text
Not implemented / no event rows recorded yet.
Boundary: absence marker only; not evidence, not transition, not approval.
```

The useful habit is simple: write down what must not be inferred.
