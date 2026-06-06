---
name: human-explain-openaccp
description: Explain OpenACCP project, lane, handoff, review, blocker, authority, or multi-agent status in plain human language. Use when an owner needs to know what is proven, provisional, missing, and next.
---

# Human Explain OpenACCP

Use the user's preferred language when it is known. If the preferred language is Chinese, use Chinese as the main language and keep English only for stable technical terms and exact names such as `Primary`, `Frontier`, `worker`, `reviewer`, `handoff`, `validator`, `source pack`, `Prompt ID`, `Response ID`, `CARD`, `task-card`, `B0/B1/B2/B3`, `CI`, `CLI`, `JSON`, `schema`, exact file names, or project-specific product terms. Do not write long English sentences or paragraphs in a Chinese explanation.

Explain:

1. plain conclusion,
2. what is happening,
3. what is proven,
4. what is provisional,
5. what is missing,
6. next meaningful decision.

Do not invent progress or hide authority limits.

## Required Response Ending

Every OpenACCP role response should end with a short human-readable next-step paragraph. This applies to Primary, Frontier, worker, reviewer, discovery, validator, and bootstrap replies.

The ending should say:

1. what the situation means right now,
2. whether the human needs to act,
3. the exact next action.

If no human action is needed, say that plainly and name the next agent-owned action, for example: `No human action is needed right now; Frontier will continue B0/B1/B2 lane-local closure and consume the next child handoff.`

If human input is needed, name the exact missing path, fact, decision, approval, repo boundary, branch, source root, test entrypoint, or authority boundary. Do not end with a file list, validator result, command output, or vague "wait for Primary" statement.

## Explain Orchestration Meaning

Translate coordination terms into delivery meaning:

- Primary: what final decision, dispatch, or consume action it owns.
- Frontier: what lane it is closing and which B0/B1/B2 work remains.
- worker: what bounded task it executed and what evidence it returned.
- reviewer: what it checked and whether the recommendation is final or provisional.
- handoff: what it proves, what it does not prove, and who still needs to consume it.
- subagent: what bounded question it answered and how the parent orchestrator used the result.

If the system is waiting, explain whether it is a real final-authority wait or whether B0/B1/B2-safe work can still continue. Do not describe passive waiting as progress.

## Frontier Recommended Next Step Rule

For every Frontier reply, include a practical recommended next step:

- If Frontier can keep closing the lane through B0/B1/B2 work, say that no human action is needed and name the next Frontier-owned action.
- If Frontier dispatched or will dispatch subagents, explain what they are checking or doing and how Frontier will consume the result.
- If human input is truly needed, name the exact missing decision, path, file, fact, approval, or authority boundary.
- Do not give the human a worker/reviewer/discovery launcher as the default next step. Human-managed child threads are fallback only when direct subagent dispatch is unavailable, unsafe, explicitly requested, or requires a separately user-managed session.

## Startup Input Ask

After OpenACCP installation and validation, explain the missing inputs in practical terms:

- The facts input can be a source pack, PRD, spec, design document, facts folder, or uploaded project materials.
- The working directory is the local agent coordination workbench. Explain that OpenACCP writes `.openaccp`, launchers, coordination files, reports, handoffs, CARD registry, and source-pack artifacts there.
- The `repo path` is the product code repository path. Explain that this is the real product Git repo. Primary uses it to infer Git branch, base branch, writable scope, test entrypoints, worktree policy, and worker-editable files.
- If the working directory and repo path are the same, say that is acceptable. If no product repo exists yet, ask the user to say `no repo yet`.
- If the facts input is uploaded material instead of a path, say that it will be treated as candidate facts until the agent organizes or validates it.
- Preferred language matters because every Primary, Frontier, worker, reviewer, and discovery reply should stay in one consistent language.

Do not end with only "send paths". Ask in numbered lines for facts input, working directory, and repo path. Say why the inputs matter and what will happen next: after the user provides them, the startup agent will write one full Primary prompt record to the working directory, then return one short copyable Primary chat launcher that points to that file. Preferred language is optional; if omitted, keep the current conversation language.

The short launcher must appear directly in chat as a fenced `prompt` block with natural-language guidance to create a new thread from the left sidebar and paste that block there. A file link, file attachment, file list, or `Get-Content` command is not enough.

Frontier prompt records and short Frontier launchers are created later by Primary after workspace review, CARD creation, and lane analysis. When Primary creates Frontier launchers, each selected Frontier launcher also needs its own copyable fenced `prompt` block in chat.
