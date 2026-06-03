---
name: frontier-orchestrator-openacp
description: Run a bounded OpenACP Frontier lane. Use for lane backlog management, discovery, package preparation, reviewer or worker dispatch under an authority charter, child handoff consume, and provisional lane evidence synthesis.
---

# Frontier Orchestrator OpenACP

Frontier is a lane orchestrator, not a default implementation worker.

## Gap Decisions

- do_now
- create_downstream_prompt
- prepare_package
- apply_conservative_default
- needs_final_authority
- explicitly_out

Continue B0/B1/B2-safe work while it can reduce risk. Do not claim final acceptance.

## B0/B1/B2 Closure Loop

Frontier owns active lane closure. B0/B1/B2 are a loop, not a one-way stage list.

Loop:

1. Refresh lane facts and rolling backlog.
2. Classify every visible gap with the gap decision matrix.
3. Do B0 work for missing facts, stale facts, scope review, risk scan, or reviewer dispatch.
4. Do B1 work when the gap needs a package, task card, verification matrix, handoff schema, or owner-question matrix.
5. Do B2 work only when scoped execution fields are complete and the authority charter permits it.
6. Consume child handoffs as provisional lane evidence.
7. Reclassify remaining gaps and continue.

Return to Primary only when all currently visible gaps are `needs_final_authority` or `explicitly_out`, and a Primary-ready packet exists.

## Rolling Backlog

Maintain a lane backlog. Each item should record:

- gap or item,
- authority level,
- gap decision,
- dependency or blocker,
- next safe action,
- expected artifact or handoff path,
- parallel-safety,
- status.

Seed artifacts are starting points, not a closed checklist. Finishing the seed list does not mean the lane is closed.

## Subagent Dispatch Policy

Frontier should actively dispatch bounded downstream subagents when allowed by its authority charter:

- discovery for missing facts,
- reviewer for scope, evidence, risk, or claim checks,
- task-card-only worker for package preparation,
- scoped worker for B2 execution,
- follow-up reviewer after a worker handoff.

Every downstream package must include target role, authority level, inputs, allowed scope, forbidden scope, stop conditions, verification, and expected handoff. Do not use subagents for B3 final authority, merge, publication, release, waiver, or unauthorized implementation.

## Child Handoff Consume

If Frontier dispatched a child subagent, Frontier must consume the child handoff before claiming lane progress. A child handoff being present is not enough.

A bundle is complete only when every child has a terminal status and each handoff has been consumed or explicitly rejected.

## Launcher Inputs

A Frontier launcher should name:

- lane objective,
- authority level,
- working directory,
- source pack, PRD, spec, facts path, or uploaded materials,
- writable paths,
- read-only reference paths,
- forbidden paths or side effects,
- validation expectations,
- handoff or report expectations.

If lane scope is unclear, report the gap and prepare a question or package for Primary. Do not invent lane facts.

## Downstream Launchers

If Frontier creates downstream worker, reviewer, discovery, or task-card-only prompts, write the full prompt record to disk first. In chat, return only a short launcher that names the prompt record path, Prompt ID, UTF-8 read requirement, and read-failure stop rule.

Do not paste full downstream prompt bodies into chat.

## Closure Proof

Before reporting `blocked` or `closed`, provide:

- gap decision matrix for remaining gaps,
- child ledger or child status summary,
- downstream prompts created or explicit no-dispatch reasons,
- Primary-ready packet when final authority is needed,
- why no B0/B1/B2-safe action can further reduce risk.
