# Coordination Templates

Use these templates for the `.openaccp/coordination/` control plane. Human-readable reports explain state to the owner; coordination artifacts make that state reusable by Primary, Frontier, worker, reviewer, and validator threads.

Recommended order:

1. `source-pack.json`: current, reference, deprecated, invalid, and unknown source facts.
2. `card-registry.md`: project-level CARDs and lane grouping candidates.
3. `runtime-boundary.json`: Primary runtime identity, notification bridge policy, working directory, product repo path, inferred base branch, source roots, test entrypoints, worktree policy, inference evidence, ambiguity notes, writable/read-only/forbidden paths, side effects, data risk, and `b2DispatchGate`.
4. `authority-charter.json`: role authority and scope boundaries.
5. `lane-registry.json`: active Primary and Frontier lanes, lane runtime, same-runtime or cross-runtime relation, notification bridge policy, assigned CARDs, runtime boundary reference, child ledger reference, consume refs, return-gate state, and per-lane `b2DispatchGate`.
6. `frontier prompt record`: full on-disk lane prompt with `openaccp-frontier-orchestration-contract.v1`.
7. `child-ledgers/<lane-id>.json`: worker/reviewer/discovery/validation child lifecycle, runtime relation, return event status, wake status, response and handoff status, consume status, and remaining risk.
8. `handoff.json` and `review-report.json`: provisional evidence from workers and reviewers.
9. `consume-result.json`: Primary or Frontier consume decision for handoff evidence.
10. `frontier-closures/<lane-id>.json`: proof that a Frontier lane can continue, close, or return to Primary. Open lanes use `laneProgressPacketRef`; `primaryReadyPacketRef` is reserved for true return-gate closure.
11. `formal-report.md`: short owner-facing report with evidence notes and a recommended next step.

Do not use a chat formal report as the only coordination state. When a lane is active, keep the machine-readable registries current enough that another agent can understand what is current, what is provisional, what is invalid, and what still needs final authority.
