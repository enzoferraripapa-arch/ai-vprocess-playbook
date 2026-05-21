# Gate And Trace Review Example

This example shows the minimum distinction between a candidate, a reviewed
local result, and a formal record.

## Candidate Gate

| Field | Example |
| --- | --- |
| Gate | Requirements review gate |
| Entry condition | Requirement candidates exist and at least one source is present. |
| Pass condition | Required sources are linked, open assumptions are owned, and acceptance criteria are reviewable. |
| Fail action | Keep the gate open and create an issue for each missing source, owner, or acceptance criterion. |

Boundary:

```text
NO-GATE-CANDIDATE-AS-PASS
```

## Candidate Trace

| Field | Example |
| --- | --- |
| Source | requirement candidate |
| Target | design element, risk control, test case, or evidence artifact |
| Link role | satisfies, verifies, mitigates, derives, or documents |
| Rationale | Why the relationship is plausible and what evidence supports it. |
| Missing signal | What would prove the trace candidate is incomplete. |

Boundary:

```text
NO-TRACE-CANDIDATE-AS-TRACEABILITY
```

## Reviewed Local Result

A reviewer may accept or reject the gate or trace candidate locally. That local
state is useful for handoff, but it is not a formal approval unless entered
through the target organization's formal system.

Boundary:

```text
NO-LOCAL-ACCEPTED-AS-FORMAL-APPROVAL
```
