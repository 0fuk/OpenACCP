# Handoff

schemaVersion: openacp-handoff.v1
artifactType: handoff
status: draft

- schemaVersion: openacp-handoff.v1
- artifactType: handoff
- handoffId:
- taskId:
- actorRole: worker / frontier / reviewer / discovery
- workspaceRef:
- branchRef:
- stateClaim: proposed / implemented / verified / reviewed

## Changed Artifacts

| Artifact | Change Type | In Allowed Scope? |
|---|---|---|
| | created / updated / deleted | yes / no |

## Claims

- 

## Verification Evidence

| Check | Method | Result | Exit Code | Skip Reason |
|---|---|---|---|---|
| | | pass / fail / skipped | | |

## Risks

- 

## Deviations

- 

## Assumptions Used

- 

## Remaining Work

- 

## Mini Example

```json
{
  "taskId": "TASK-DOCS-001",
  "actorRole": "worker",
  "stateClaim": "verified",
  "claims": ["Created the requested docs artifact."],
  "verificationEvidence": [
    { "check": "markdown review", "method": "manual read-through", "result": "pass" }
  ],
  "remainingWork": ["Final authority still needs to consume the reviewed evidence."]
}
```

A handoff can prove scoped work happened. It must not claim merge, release, final acceptance, or waiver.
