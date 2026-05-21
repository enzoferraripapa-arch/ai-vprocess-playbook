# ALM Vocabulary Mapping

This playbook uses vendor-neutral words where possible. Different ALM, RM,
issue-tracking, and QMS tools may use different labels for the same operating
concept.

The table below avoids vendor-specific names while still showing how terms tend
to move across tool styles.

| Playbook term | Typical meaning | Document-centric RM style | Item-centric ALM style | Issue-tracker style | QMS document-control style |
| --- | --- | --- | --- | --- | --- |
| Work item | A controlled unit of work, requirement, issue, test, risk, change, or review record. | object or requirement object | item or record | issue, ticket, or task | controlled form or record |
| Type | The category or class of a work item. | object type or module type | item type or artifact type | issue type | form type or record class |
| Field | A structured attribute on a work item. | attribute | field | field or custom field | metadata field |
| Link role | A typed relationship between two records. | link type | relationship type | issue link | reference or cross-reference |
| Workflow state | The lifecycle status of a record. | status attribute | workflow state | status | review/approval state |
| Baseline | A controlled snapshot or approved reference point. | baseline or module snapshot | baseline, version, or release package | release, milestone, or frozen issue set | approved revision or effective version |
| Review gate | A decision point where evidence is checked before progress. | review module or approval checkpoint | review workflow transition | review issue or approval task | approval route |
| Handoff package | A reviewed local package prepared for manual entry or approved import. | import package or review bundle | exchange package | attachment bundle or linked issue set | submission package |
| Trace candidate | A suggested relationship that still needs review. | proposed link | suspect/proposed relationship | issue link candidate | draft cross-reference |
| Evidence | Material used to support a claim. | attached source, test, or analysis object | evidence item | attachment or linked result | controlled record or attachment |

## Rule

Map the terms to your tool and organization before using the playbook. If the
tool label and the project rule differ, follow the approved project rule and
record the mapping.

Do not infer authority from vocabulary. A label that sounds official is still a
candidate until the target organization's formal process accepts it.
