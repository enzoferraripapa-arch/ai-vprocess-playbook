# Routing Matrix Example

A routing matrix turns project facts into review activities. It should open
work, not close it.

| Route | Trigger | Activity opened | Output candidate |
| --- | --- | --- | --- |
| REQ-SOURCE | external requirement source present | source coverage review | requirement source register |
| REQ-BASELINE | requirement candidates exist | requirement analysis review | baseline candidate package |
| DESIGN-IMPACT | behavior-changing update | impact analysis | affected interface and design candidate set |
| TRACE-GAP | missing source or target links | trace review | trace candidate report |
| GATE-READY | evidence package present | gate review | pass/fail recommendation |
| HANDOFF | accepted local decisions exist | handoff package review | formal-system import package candidate |

## Boundary

A route is only a reason to inspect work. It is not proof that the activity is
complete, correct, approved, or sufficient.

Use the No-X rule:

```text
NO-ROUTING-AS-APPROVAL
```

See [../examples/sample_routing.json](../examples/sample_routing.json).
