# Role Model

OpenACP defines roles by authority, not by model provider.

## Primary

Primary owns final authority. It can assign charters, dispatch lanes and workers, consume final handoffs, decide merge or publication, grant waivers, and accept or reject evidence.

Primary also owns active closure. It should split work into lanes, dispatch bounded subagents, consume evidence, reclassify remaining gaps, and continue until the visible work is closed, explicitly out, delegated with a handoff path, or blocked on a real final-authority decision.

## Frontier

Frontier is a lane orchestrator. It manages a bounded lane backlog, prepares packages, dispatches allowed downstream work, consumes child handoffs as provisional evidence, and reports lane status. A Frontier launched by Primary should default to B2 lane-local authority unless Primary explicitly narrows it. It does not own final acceptance.

Frontier runs a B0/B1/B2 closure loop. It does discovery and review at B0, prepares packages and task cards at B1, dispatches scoped workers or reviewers at B2 when the CARD, allowed scope, verification, handoff path, and stop conditions are clear, consumes child handoffs, and keeps reclassifying gaps. It returns to Primary only when all visible lane gaps are final-authority-only or explicitly out.

## Worker

Worker executes one narrow task card. It works inside allowed files or effects, runs verification, and writes a handoff. It stops when new authority, new scope, real credentials, production data, external side effects, or dependency changes are required.

## Reviewer

Reviewer is read-only by default. It checks scope, correctness, verification, side effects, and overclaiming. It recommends approve, amend, split-follow-up, or reject. It does not merge or accept final evidence by itself.

## Human Owner

Human owner decides business meaning, legal or policy questions, real resource approval, credentials, data permissions, production launch, and risk waivers.

## Hygiene

Always distinguish role, thread, lane, workspace, branch, authority, and evidence state.

Subagent output is evidence, not authority. The orchestrator that dispatched the subagent must consume the result before using it for closure.
