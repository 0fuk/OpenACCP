---
name: human-explain-openacp
description: Explain OpenACP project, lane, handoff, review, blocker, authority, or multi-agent status in plain human language. Use when an owner needs to know what is proven, provisional, missing, and next.
---

# Human Explain OpenACP

Explain:

1. plain conclusion,
2. what is happening,
3. what is proven,
4. what is provisional,
5. what is missing,
6. next meaningful decision.

Do not invent progress or hide authority limits.

## Explain Orchestration Meaning

Translate coordination terms into delivery meaning:

- Primary: what final decision, dispatch, or consume action it owns.
- Frontier: what lane it is closing and which B0/B1/B2 work remains.
- worker: what bounded task it executed and what evidence it returned.
- reviewer: what it checked and whether the recommendation is final or provisional.
- handoff: what it proves, what it does not prove, and who still needs to consume it.
- subagent: what bounded question it answered and how the parent orchestrator used the result.

If the system is waiting, explain whether it is a real final-authority wait or whether B0/B1/B2-safe work can still continue. Do not describe passive waiting as progress.

## Frontier Human Next Step Rule

For every Frontier reply, include a practical human next step:

- If Frontier can keep closing the lane through B0/B1/B2 work, say that no human action is needed and name the next Frontier-owned action.
- If Frontier dispatched or will dispatch subagents, explain what they are checking or doing and how Frontier will consume the result.
- If human input is truly needed, name the exact missing decision, path, file, fact, approval, or authority boundary.
- Do not give the human a worker/reviewer/discovery launcher as the default next step. Human-managed child threads are fallback only when direct subagent dispatch is unavailable, unsafe, explicitly requested, or requires a separately user-managed session.

## Startup Input Ask

After OpenACP installation and validation, explain the missing inputs in practical terms:

- The working directory is required because launchers need a concrete project place where the agent is allowed to work.
- The facts input can be a source pack, PRD, spec, design document, facts path, or uploaded project materials.
- If the facts input is uploaded material instead of a path, say that it will be treated as candidate facts until the agent organizes or validates it.
- Preferred language matters because every Primary, Frontier, worker, reviewer, and discovery reply should stay in one consistent language.

Do not end with only "send paths". Say why the inputs matter and what will happen next: after the user provides them, the startup agent will write one full Primary prompt record to the working directory, then return one short copyable Primary chat launcher that points to that file.

The short launcher must appear directly in chat as a fenced `prompt` block with natural-language guidance to create a new thread from the left sidebar and paste that block there. A file link, file attachment, file list, or `Get-Content` command is not enough.

Frontier prompt records and short Frontier launchers are created later by Primary after workspace review, CARD creation, and lane analysis. When Primary creates Frontier launchers, each selected Frontier launcher also needs its own copyable fenced `prompt` block in chat.
