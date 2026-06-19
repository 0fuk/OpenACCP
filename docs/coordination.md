# OpenACCP Coordination

OpenACCP Coordination manages multi-agent work once a project has enough local facts.

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

OpenACCP coordination is an active closure loop that keeps safe work moving until the lane reaches closure proof or a true final-authority boundary.

Primary and Frontier repeatedly:

1. refresh facts,
2. classify gaps,
3. dispatch bounded subagents when useful,
4. consume handoffs and reviews,
5. update backlog,
6. continue B0/B1/B2-safe work,
7. reserve only true final-authority decisions for B3.

A lane closes when the current visible gaps are resolved, child dispatches have returned, failed, or been cancelled, present child handoffs are consumed or rejected by the parent orchestrator, remaining gaps are explicitly out, or the only remaining work is final-authority-only with a Primary-ready packet. Stage evidence is a `lane-progress packet` or `frontier-progress packet`; it keeps the Frontier moving and does not require Primary consume by default.

A `primaryReadyPacketRef` is evidence for Primary to check. It is not acceptance by itself. Before Primary records a final accepted consume for a Frontier return, the consume result should cite the closure `closureId`, `laneId`, or path in `basisRefs` and validate with that `frontier-closure` so an open lane cannot be accepted as closed.

## Coordination Control Plane

OpenACCP uses a small `.openaccp/coordination/` control plane so separate threads can share facts without relying on chat memory.

Core artifacts:

- `execution-boundary.json`: repo path, inferred base branch, inferred source roots, inferred test entrypoints, inferred worktree policy, writable/read-only/forbidden paths, side effects, data risk, inference evidence, ambiguity notes, and `b2DispatchGate`.
- `current-manifest.json`: current source pack, source status registry, execution boundary, lane registry, CARD registry, active lanes, and latest consume refs.
- `sequence-registry.json`: Prompt IDs, Response IDs, handoffs, consumes, cards, active lanes, lifecycle states, and current/latest pointers.
- `lane-registry.json`: Primary and Frontier lane objectives, project complexity, Frontier dispatch mode, lane-count reason, assigned CARDs, authority, child ledger refs, closure refs, return-gate state, and per-lane `b2DispatchGate`.
- `child-ledgers/<lane-id>.json`: child worker/reviewer/discovery/validation lifecycle status and consume status for one lane.
- `source-status-registry.json`: current, reference, deprecated, invalid, and unknown source status with reasons.
- `decision-registry.json`: owner questions, Primary decisions, waivers, out-of-scope decisions, blockers, and safe defaults.
- `frontier-closures/<lane-id>.json`: proof that a Frontier lane can continue, close, or return to Primary. Open lanes use `laneProgressPacketRef`; `primaryReadyPacketRef` appears only when the return gate is ready for Primary. Primary final consume should cross-check this file with `--frontier-closure`.

Primary establishes the execution boundary before B2 Frontier dispatch. The user provides the repo path; Primary infers base branch, source roots, test entrypoints, writable scope, and worktree policy from the repo before asking follow-up questions. If repo path is missing, ambiguous, or explicitly `no repo yet`, Primary asks for the repo path or records `no repo yet` and continues safe B0/B1 packaging. A Frontier can still run coordination-only or read-only B2 work, while product-write B2 dispatch requires both execution `b2DispatchGate` and lane `b2DispatchGate` to be ready for product-write work. Frontier treats unresolved product-write readiness as an implementation-worker boundary, not as a reason to hand stage progress back to Primary.

## Subagents

Use subagents for bounded work:

- discovery,
- reviewer sidecars,
- task-card preparation,
- scoped workers,
- validation or risk scan.

Each subagent needs a role, authority boundary, input facts, allowed scope, forbidden scope, stop conditions, and expected output. The parent orchestrator must consume the result before claiming progress.

Primary creates or refreshes CARDs before Frontier dispatch. A Primary-launched Frontier usually receives B2 lane-local authority so it can actively run B0 discovery, B1 packaging, B2 scoped worker or reviewer dispatch, child handoff consume, and closure proof inside the assigned lane.

Frontier keeps worker, reviewer, discovery, validation, and task-card-only child work inside its current lane thread when direct subagent or delegation tools are available and the work is B0/B1/B2-safe. Full child prompt records may still be written to disk for audit and reproducibility, while the Frontier dispatches and consumes that child work itself. Short child launchers are fallback artifacts only; when used, they state why direct dispatch was unavailable or unsafe and what the human must do next.

## Parallel Work

Parallel work is safer when scopes are disjoint, handoff paths do not collide, reviewers know their targets, and final authority owns integration order.

Parallel work is risky when multiple agents edit the same contract, schema, dependency lock, migration, or execution policy without a shared plan.
