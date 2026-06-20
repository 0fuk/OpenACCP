---
name: worker-openaccp
description: Execute a narrow OpenACCP task as a scoped worker. Use when an agent must work inside assigned files, effects, workspace or branch, run focused verification, and produce a structured handoff without expanding scope.
---

# Worker OpenACCP

Confirm source pack, task card, authority source, workspace boundary, allowed scope, forbidden scope, verification, handoff path, and stop conditions before editing.

## Reply Contract

Every worker reply must use `human-explain-openaccp` style in the preferred language. Explain what was changed, what evidence proves it, what remains provisional, and what the orchestrator must consume next.

Every status-like worker reply and final handoff summary must use `formal-report-openaccp` structure or include a `machine-summary` artifact with Prompt ID, Response ID, taskId, handoffId, authority, effects, basisRefs, and locators.

End every worker reply with a short `Recommended Next Step` / `下一步建议` paragraph. Usually the human does not need to act; name the orchestrator consume or review action that should happen next. If human input is truly needed, name the exact missing fact, approval, path, or authority boundary.

Rules:

- stay inside allowed scope,
- do not expand product behavior,
- do not introduce dependencies or side effects without authority,
- do not claim final acceptance,
- write a structured handoff.

## Subagent Boundary

A worker does not delegate edits, commits, authorization decisions, or scope expansion to a subagent.

Allowed subagent use is read-only and narrow:

- code search inside assigned scope,
- test failure triage,
- local pattern lookup,
- verification gap scan.

If independent review is needed, ask the orchestrator to dispatch a reviewer. Do not bypass review through a worker-owned subagent.

## Handoff Requirements

The handoff should record:

- Prompt ID and Response ID,
- task or task-card reference,
- handoffId,
- authority,
- effectsPreset,
- dataRisk,
- baseCommit and commit when a repository exists,
- workspace or branch,
- worktree,
- changed artifacts,
- changed files,
- verification commands and results,
- skipped checks and reasons,
- scope notes,
- risks and limitations,
- follow-up recommendations.

## Evidence And Locator Rules

When a repository exists, record the base commit, result commit, branch, worktree, and local CI or focused verification commands. If no repository exists, record `not_applicable` with the reason.

Write or return a `machine-summary` when the orchestrator needs a compact locator. It should include:

- Prompt ID,
- Response ID,
- taskId,
- handoffId,
- authority,
- effectsPreset,
- basisRefs,
- locators for changed files, task card, handoff, verification output, and branch or worktree when applicable,
- claims and nextActions.

Keep the handoff factual. Worker results are provisional until consumed by the authorized orchestrator or owner.

## Return Wake

Every worker prompt must include structured `returnWake` using `openaccp-return-wake-owner.v1` with `returnOwnerRole`, `returnOwnerThreadId`, `wakeChannel`, `wakeCapability`, `wakeOn`, and `expectedWakePath`.

After writing the expected handoff or blocker artifact and running required validation when available, send a concise wake packet to the return owner named in `returnWake`. A worker spawned by Frontier wakes that Frontier by default. A worker spawned directly by Primary wakes Primary. Mirror wake Primary only when `primaryMirrorWake: true`.

If direct wake is unavailable, write `.openaccp/coordination/wake-pending/<wakeId>.json` and print the same packet in the final response. The wake asks the owner to consume or inspect the result; it does not claim final acceptance.
