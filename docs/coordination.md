# ACP Coordination

ACP Coordination manages multi-agent work once a project has enough local facts.

## Flow

1. Confirm source pack.
2. Assign authority boundaries.
3. Create task cards.
4. Dispatch scoped workers or reviewers.
5. Collect handoffs.
6. Validate artifacts.
7. Run sidecar review.
8. Consume evidence through final authority.
9. Report status in human-readable form.

## Active Closure

OpenACP coordination is an active closure loop, not a passive status chain.

Primary and Frontier should repeatedly:

1. refresh facts,
2. classify gaps,
3. dispatch bounded subagents when useful,
4. consume handoffs and reviews,
5. update backlog,
6. continue B0/B1/B2-safe work,
7. reserve only true final-authority decisions for B3.

A lane is not closed because a seed checklist is complete. A lane closes only when the current visible gaps are resolved, delegated with handoff paths, explicitly out, or final-authority-only with a Primary-ready packet.

## Subagents

Use subagents for bounded work:

- discovery,
- reviewer sidecars,
- task-card preparation,
- scoped workers,
- validation or risk scan.

Each subagent needs a role, authority boundary, input facts, allowed scope, forbidden scope, stop conditions, and expected output. The parent orchestrator must consume the result before claiming progress.

Primary should create or refresh CARDs before Frontier dispatch. A Primary-launched Frontier should usually receive B2 lane-local authority so it can actively run B0 discovery, B1 packaging, B2 scoped worker or reviewer dispatch, child handoff consume, and closure proof inside the assigned lane.

## Parallel Work

Parallel work is safer when scopes are disjoint, handoff paths do not collide, reviewers know their targets, and final authority owns integration order.

Parallel work is risky when multiple agents edit the same contract, schema, dependency lock, migration, or runtime policy without a shared plan.
