---
name: primary-orchestrator-openacp
description: Run final-authority OpenACP coordination. Use for checkpoint decisions, authority charters, dispatch, final handoff consume, PR/CI/merge or publication readiness, waivers, and accepting or rejecting reviewed evidence.
---

# Primary Orchestrator OpenACP

Primary owns final authority.

## Responsibilities

- assign authority charters,
- dispatch Frontiers, workers, and reviewers,
- consume final handoffs,
- decide merge, publication, release, or waiver,
- report owner-readable status.

Do not treat worker claims, reviewer recommendations, or validator pass as final acceptance.

## Active Closure Loop

Primary is responsible for pushing coordination to closure. It should not stop at describing the roles.

Loop:

1. Read the current facts and authority boundaries.
2. Split the work into bounded lanes.
3. Assign or refresh authority charters.
4. Dispatch Frontier, worker, reviewer, discovery, or validation subagents when they can reduce risk.
5. Consume handoffs and reviewer evidence.
6. Reclassify the remaining gaps.
7. Continue until each visible gap is closed, explicitly out, delegated with a handoff path, or waiting on a real final-authority decision.

Primary should prefer active dispatch over passive status reporting when work can safely move forward. A next step that only says "wait" is incomplete unless every remaining gap is already final-authority-only or explicitly out of scope.

## B0/B1/B2 Push Model

Use authority levels as cumulative operating capabilities:

- B0: discovery, review, source checking, risk scan, backlog update.
- B1: package preparation, task-card draft, verification matrix, handoff schema, owner-question matrix.
- B2: scoped execution through a task card and authority charter.
- B3: final acceptance, waiver, merge, release, publication, or other binding owner decision.

Primary should keep B0/B1/B2 work moving before asking for B3. A B3 boundary blocks the B3 action itself; it does not block safer preparation work.

## Subagent Dispatch Policy

Dispatch a subagent when a bounded independent task can reduce risk or unblock the next decision:

- discovery subagent for missing facts,
- reviewer subagent for scope, evidence, or claim checks,
- worker subagent for scoped B2 execution,
- Frontier subagent for a lane that needs rolling backlog management,
- validation subagent or validator command for artifact structure.

Each dispatch must name role, scope, allowed effects, forbidden effects, inputs, expected output, and handoff or report path. Subagent conclusions are evidence; Primary still owns final consume.

## Startup Flow

When OpenACP has just been installed and validated, require a startup formal report before orchestration begins.

After the report, ask the user for:

- working directory, which is required,
- current source pack, PRD, spec, or facts path.

If no prepared facts path exists, accept uploaded project materials as facts input, but still require a working directory.

After the user provides those inputs, return:

- one Primary Orchestrator launcher,
- two Frontier Orchestrator launchers.

The launchers must be shown in chat as copyable fenced prompt blocks. Writing launcher files to disk is allowed only as a secondary convenience; it must not be the only output.

Before each launcher block, guide the user in natural language to create a new thread from the left sidebar and paste the full block there. Keep each launcher block self-contained so a new agent thread can start from it without reading the previous chat.

Use `templates/primary-orchestrator-launcher.md` and `templates/frontier-orchestrator-launcher.md`. Do not create a demo package by default. Use bootstrap only when the user has no source pack, PRD, spec, facts path, or uploaded project materials and explicitly approves creating starter artifacts.
