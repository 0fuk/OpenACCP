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

## Coordination Control Plane

OpenACCP uses a small `.openaccp/coordination/` control plane so separate threads can share facts without relying on chat memory.

Core artifacts:

- `runtime-boundary.json`: Primary runtime identity, notification bridge policy, bridge event queue, repo path, inferred base branch, inferred source roots, inferred test entrypoints, inferred worktree policy, writable/read-only/forbidden paths, side effects, data risk, inference evidence, ambiguity notes, and `b2DispatchGate`.
- `current-manifest.json`: current source pack, source status registry, runtime boundary, lane registry, CARD registry, active lanes, and latest consume refs.
- `sequence-registry.json`: Prompt IDs, Response IDs, handoffs, consumes, cards, active lanes, lifecycle states, and current/latest pointers.
- `lane-registry.json`: Primary and Frontier lane objectives, project complexity, Primary runtime, Frontier dispatch mode, dispatch channel, lane-count reason, lane runtime, same-runtime or cross-runtime relation, notification bridge policy, assigned CARDs, authority, child ledger refs, closure refs, return-gate state, and per-lane `b2DispatchGate`.
- `bridge-events.jsonl`: cross-runtime notification queue. `parent_to_child` events request Frontier startup; `child_to_parent` events request parent consume.
- `child-ledgers/<lane-id>.json`: child worker/reviewer/discovery/validation lifecycle, runtime relation, return event status, wake status, handoff status, and consume status for one lane.
- `source-status-registry.json`: current, reference, deprecated, invalid, and unknown source status with reasons.
- `decision-registry.json`: owner questions, Primary decisions, waivers, out-of-scope decisions, blockers, and safe defaults.
- `frontier-closures/<lane-id>.json`: proof that a Frontier lane can continue, close, or return to Primary. Open lanes use `laneProgressPacketRef`; `primaryReadyPacketRef` appears only when the return gate is ready for Primary.

Primary establishes the runtime boundary before B2 Frontier dispatch. The user provides the repo path; Primary infers base branch, source roots, test entrypoints, writable scope, and worktree policy from the repo before asking follow-up questions. If repo path is missing, ambiguous, or explicitly `no repo yet`, Primary asks for the repo path or records `no repo yet` and continues safe B0/B1 packaging. A Frontier can still run coordination-only or read-only B2 work, while product-write B2 dispatch requires both runtime `b2DispatchGate` and lane `b2DispatchGate` to be ready for product-write work. Frontier treats unresolved product-write readiness as an implementation-worker boundary, not as a reason to hand stage progress back to Primary.

Primary also declares its agent runtime during startup: `codex`, `claude-code`, `other`, or `unknown`. When Primary signs a Frontier lane, it declares the Frontier runtime too. Same-runtime lanes can use the runtime's native subagent/thread flow. Cross-runtime lanes use `runtime_bridge`, the notification bridge policy recorded in `runtime-boundary.json` and `lane-registry.json`, and the shared `bridge-events.jsonl` queue.

## Cross-Runtime Dispatch

OpenACCP supports both directions without making the human owner act as the event bus:

1. Primary writes the Frontier prompt record and short launcher to disk.
2. Primary records the Frontier runtime and `runtimeRelation` in `lane-registry.json`.
3. If the Frontier runtime differs from Primary, the effective `dispatchChannel` is `runtime_bridge` or `manual_paste`. Native `agent_thread_spawn` and `one_click` are same-runtime channels.
4. Primary calls or queues `openaccp notify-dispatch --lane-registry <path> --lane-id <lane> --event-log <working-directory>/.openaccp/coordination/bridge-events.jsonl`.
5. The bridge event records `direction: parent_to_child`, `eventType: frontier_dispatch_requested`, target runtime, prompt record, short launcher, and `busyPolicy: queue_until_safe_checkpoint`.
6. A runtime adapter may wake the target tool. If no adapter is available, the event remains visible in the queue and manual fallback can be used deliberately.

## Return Event Protocol

A returned child handoff is evidence, not acceptance. OpenACCP records the return event in the existing control plane:

1. The child ledger moves the child to `dispatchStatus: returned`.
2. If the handoff is present and not yet consumed, the ledger records `returnEventStatus: parent_consume_pending` or `parent_consuming`.
3. The ledger records `parentRuntime`, `childRuntime`, and `runtimeRelation`.
4. If the parent and child run in different tools, the ledger records `notificationBridgeRef`, `parentConsumeDuePolicy`, and a `wakeStatus` such as `queued_for_parent`, `wake_requested`, or `delivered`.
5. The bridge command `openaccp notify-return --child-ledger <path> --event-log <working-directory>/.openaccp/coordination/bridge-events.jsonl` reads the existing child ledger and appends a `child_to_parent` consume event. If the parent is busy, the event stays queued until the next safe checkpoint.
6. Parent consume records `parentConsumeRef` and moves the return event to `consume_result_recorded`, `closed`, or `blocked`.

This prevents the human owner from becoming the event bus. Humans still own authority decisions; routine returned-handoff delivery belongs to the coordination state and bridge policy.

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

Parallel work is risky when multiple agents edit the same contract, schema, dependency lock, migration, or runtime policy without a shared plan.
