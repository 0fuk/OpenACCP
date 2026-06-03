# Task Card

schemaVersion: openacp-task-card.v1
artifactType: task-card
status: draft

- schemaVersion: openacp-task-card.v1
- artifactType: task-card
- taskId:
- lane:
- objective:
- riskLevel: low / medium / high
- authorityRequired: B0 / B1 / B2 / B3
- authorityCharterRef: required for B2/B3

## Inputs

- Source pack:
- Spec:
- Scope boundary:

## Allowed Scope

- allowedScope.filesOrArtifacts:
- allowedScope.effects:

## Forbidden Scope

- forbiddenScope.filesOrArtifacts:
- forbiddenScope.effects:
- forbiddenScope.claims:

## Acceptance Criteria

- 

## Verification Plan

| Check | Method | Required? | Evidence |
|---|---|---|---|
| | | yes / no | |

## Stop Conditions

- 

## Expected Handoff

- 

## Mini Example

```json
{
  "taskId": "TASK-DOCS-001",
  "authorityRequired": "B2",
  "authorityCharterRef": "authority-charter.json",
  "allowedScope": { "filesOrArtifacts": ["docs/**"], "effects": ["docs-only"] },
  "forbiddenScope": { "filesOrArtifacts": ["src/**"], "effects": ["dependency-change"], "claims": ["accepted", "merged", "released"] }
}
```

B2/B3 cards need a charter because execution and final authority are separate decisions.
