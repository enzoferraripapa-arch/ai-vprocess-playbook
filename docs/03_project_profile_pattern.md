# Project Profile Pattern

A project profile turns a vague project into explicit routing facts. It tells
an AI agent and a human reviewer which activities, gates, evidence packs, and
handoff boundaries are relevant.

## Profile Layers

| Layer | Purpose | Examples |
| --- | --- | --- |
| Common | Facts that every project should know. | domain, product type, lifecycle stage, change type, release intent |
| Organization | Local operating rules. | approval roles, review independence, retention policy, tool boundary |
| Project | Project-specific facts. | risk level, affected subsystems, interfaces, evidence gaps |
| Evidence | What is known versus missing. | source docs, tests, logs, decisions, open issues, trace candidates |

## Required Boundary

Profile values are routing inputs, not approvals. A profile can open a gate,
suggest a trace review, or request evidence. It cannot close the gate by
itself.

Use the No-X rule from `ai-vprocess-ops`:

```text
NO-ROUTING-AS-APPROVAL
```

## Minimal Profile Shape

See [../examples/sample_project_profile.json](../examples/sample_project_profile.json).
