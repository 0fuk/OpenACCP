# Handoff

schemaVersion: openacp-handoff.v1
artifactType: handoff
status: draft

- schemaVersion: openacp-handoff.v1
- artifactType: handoff
- handoffId:
- taskId:
- responseId:
- actorRole: worker / frontier / reviewer / discovery
- authority: B0 / B1 / B2
- workspaceRef:
- worktree:
- branchRef:
- baseCommit:
- commit:
- dataRisk: none / low / medium / high / sensitive
- effectsPreset: read_only_handoff / review_handoff / orchestration_local_write / docs_task_card_commit / implementation_local_commit / primary_only / custom_expanded
- stateClaim: proposed / implemented / verified / reviewed

## Changed Files

-

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
  "responseId": "RESP-DOCS-001",
  "actorRole": "worker",
  "authority": "B2",
  "workspaceRef": "demo-workspace",
  "worktree": "worktrees/docs-task-001",
  "branchRef": "docs/task-001",
  "baseCommit": "BASE-DOCS-001",
  "commit": "COMMIT-DOCS-001",
  "dataRisk": "low",
  "effectsPreset": "docs_task_card_commit",
  "changedFiles": ["docs/guide.md"],
  "changedArtifacts": [{ "path": "docs/guide.md", "changeType": "created" }],
  "stateClaim": "verified",
  "claims": ["Created the requested docs artifact."],
  "verificationEvidence": [
    { "check": "markdown review", "method": "manual read-through", "result": "pass" }
  ],
  "remainingWork": ["Final authority still needs to consume the reviewed evidence."]
}
```

A handoff can prove scoped work happened. It must not claim merge, release, final acceptance, or waiver.
