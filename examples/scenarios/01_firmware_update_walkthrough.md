# Scenario 01: Sensor Timeout Firmware Update

Status: fictional example only.

This walkthrough shows how the playbook can be applied to one small V-process /
ALM-style change without naming a specific vendor tool.

## 1. Situation

A fictional robotics team maintains embedded controller firmware for a compact
motion-control product. The current firmware enters a safe stop when a position
sensor times out.

The next firmware update changes timeout handling:

- the timeout value becomes configurable by product profile;
- a new sensor type is supported;
- the safe-stop transition is unchanged in intent, but the trigger timing may
  change;
- the team uses an external formal system for official records, but wants a
  local review package before formal entry.

The team wants AI assistance to prepare candidate records, not to approve the
change.

## 2. Project Profile Facts

| Fact | Value |
| --- | --- |
| Product type | software-intensive embedded controller |
| Lifecycle stage | prototype-to-product transition |
| Change type | behavior-changing firmware update |
| Risk level | high |
| Reuse level | partial |
| Affected functions | sensor timeout detection, safe-stop transition, product profile configuration |
| Affected interfaces | sensor input, profile configuration file, diagnostic event output |
| Formal system | external ALM / QMS controlled by the project owner |
| Connector policy | read-only or handoff by default |
| Primary boundary | local accepted does not mean formal approved |

No-X boundary:

```text
NO-ROUTING-AS-APPROVAL
```

The profile can trigger activities. It cannot approve them.

## 3. Routing Result

The profile opens these activities:

| Route | Trigger | Activity opened | Output candidate |
| --- | --- | --- | --- |
| REQ-SOURCE | new sensor and configurable timeout affect source assumptions | source coverage review | requirement source register |
| REQ-BASELINE | requirement candidates exist | requirement analysis review | baseline candidate package |
| DESIGN-IMPACT | behavior-changing update | impact analysis | affected function/interface/design candidate set |
| TRACE-GAP | new source and changed timing create possible trace gaps | trace review | trace candidate report |
| GATE-READY | evidence package is incomplete | gate preparation | pass/fail recommendation candidate |
| HANDOFF | local accepted decisions may be exported later | handoff review | formal-system import package candidate |

No-X boundary:

```text
NO-ROUTING-AS-APPROVAL
```

The output of routing is work to inspect, not permission to proceed.

## 4. Candidate Work-Item-Like Records

| Candidate | Purpose | Minimum fields |
| --- | --- | --- |
| REQ-CAND-001 | Safe stop shall occur when sensor data is unavailable beyond the configured timeout. | source, rationale, acceptance condition, open assumptions |
| REQ-CAND-002 | Timeout value shall be controlled by a reviewed product profile. | owner, allowed range, configuration authority, verification method |
| DES-CAND-001 | Timeout handling design update. | function, behavior, structure, state transition, error handling |
| TEST-CAND-001 | Timeout boundary test. | setup, stimulus, expected transition, profile values, coverage target |
| TRACE-CAND-001 | Change request impacts safe-stop requirement. | source, target, rationale, missing signal |
| GATE-CAND-001 | Gate readiness for formal handoff. | entry condition, pass condition, fail action, reviewer |

No-X boundary:

```text
NO-CANDIDATE-AS-RECORD
```

These candidates are useful because they show what must be reviewed. They are
not controlled records.

## 5. Work-Item SOP Skeleton Applied

| Step | Operation | Confirmation | Evidence |
| --- | --- | --- | --- |
| WI-01 | Identify the changed behavior and source basis. | change affects timeout timing and profile authority | change note, source requirement, profile note |
| WI-02 | Draft candidate records for requirement, design, test, trace, and gate. | each candidate has owner and rationale | candidate package |
| WI-03 | Mark configuration authority as unresolved. | open issue exists for timeout owner/range | issue candidate |
| WI-04 | Run trace review. | impact link to safe-stop requirement is accepted or rejected locally | trace review record |
| WI-05 | Run gate review. | gate remains open if evidence is incomplete | gate review record |
| WI-06 | Prepare handoff only from locally reviewed records. | handoff package excludes unresolved candidates | package checksum and excluded count |

Boundary:

```text
NO-HANDOFF-AS-IMPORT
```

A package is only preparation for formal entry. It is not evidence that the
formal system was updated.

## 6. Gate Review Example

Candidate gate:

| Field | Value |
| --- | --- |
| Gate | Behavior-changing firmware handoff readiness |
| Entry condition | requirement, design, test, and trace candidates exist |
| Pass condition | timeout authority is defined, safe-stop requirement trace is reviewed, test evidence covers profile boundary values |
| Fail action | keep gate open and create issues for each missing owner/evidence item |
| Current result | fail / not ready |
| Reason | timeout configuration authority is unresolved |

No-X boundary:

```text
NO-GATE-CANDIDATE-AS-PASS
```

The gate candidate is not a passed gate. The useful result is the explicit
blocker.

## 7. Trace Review Example

| Trace candidate | Review result | Rationale |
| --- | --- | --- |
| change request -> safe-stop requirement | accepted locally | configurable timeout can affect when safe stop occurs |
| timeout requirement -> timeout boundary test | needs review | test values depend on allowed profile range |
| design update -> diagnostic event output | needs review | diagnostic behavior may change with new sensor type |

Boundary:

```text
NO-TRACE-CANDIDATE-AS-TRACEABILITY
NO-LOCAL-ACCEPTED-AS-FORMAL-APPROVAL
```

One link can be locally accepted for handoff preparation, but that does not
make it formal traceability.

## 8. Connector Permission Example

| Connector mode | Allowed use in this scenario | Not allowed |
| --- | --- | --- |
| Read-only | inspect existing requirements, tests, and open issues | modify official records |
| Dry-run | preview candidate link and field changes | claim update completion |
| Handoff | generate Markdown/JSON/CSV package for human review | bypass reviewer or formal import path |
| Write-capable | not enabled in this example | direct production write |

Boundary:

```text
NO-HANDOFF-AS-IMPORT
NO-STATE-SKIP
```

Write-capable operation would require explicit identity, scope, rollback,
audit, dry-run delta, and human gate. This scenario stops at handoff.

## 9. Handoff Package Shape

The handoff package should include:

- accepted local decision records;
- accepted local trace reviews;
- unresolved issues and excluded candidates;
- package checksum or version;
- target scope for manual entry or approved import;
- statement that formal system authority remains external.

Example excluded counts:

| Excluded item | Count | Reason |
| --- | --- | --- |
| non-accepted decisions | 1 | timeout authority still unresolved |
| non-accepted trace candidates | 2 | test boundary and diagnostic event links need review |
| gate candidates | 1 | gate not passed |

## 10. What Must Not Be Claimed

Do not claim:

- the firmware update is safe;
- the requirements are approved;
- the gate has passed;
- traceability is formally accepted;
- the formal system was updated;
- the product is ready to release.

The scenario only shows how to turn an AI-assisted change into reviewable
candidates and a bounded handoff package.

## 11. Minimal Next Actions

For a real project, the project owner would decide:

1. who owns timeout configuration authority;
2. which timeout ranges are allowed;
3. which tests prove the safe-stop behavior at boundary values;
4. whether diagnostic behavior changes with the new sensor type;
5. who may accept local trace and gate reviews;
6. how formal records are entered or imported.

Until those decisions are made, the correct state is candidate/open, not
approved.
