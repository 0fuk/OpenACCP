---
name: worker-openacp
description: Execute a narrow OpenACP task as a scoped worker. Use when an agent must work inside assigned files, effects, workspace or branch, run focused verification, and produce a structured handoff without expanding scope.
---

# Worker OpenACP

Confirm source pack, task card, authority source, workspace boundary, allowed scope, forbidden scope, verification, handoff path, and stop conditions before editing.

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

- task or task-card reference,
- workspace or branch,
- changed artifacts,
- verification commands and results,
- skipped checks and reasons,
- scope notes,
- risks and limitations,
- follow-up recommendations.

Keep the handoff factual. Worker results are provisional until consumed by the authorized orchestrator or owner.
