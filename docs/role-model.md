# Role Model

OpenACCP defines roles by authority, not by model provider.

## Primary

Primary owns delegated final coordination authority. It can assign charters, dispatch lanes and workers, consume final handoffs, and accept, reject, or amend evidence when the authority charter lists that decision in `delegatedFinalAuthority`. When Primary final-accepts a Frontier return or Primary-ready packet, it cross-checks the consume result against the matching Frontier closure proof.

Primary also owns active closure. It should split work into lanes, dispatch bounded subagents, consume evidence, reclassify remaining gaps, and continue until the visible work is closed, explicitly out, child work is terminal and consumed or rejected, or the remaining gap is blocked on a real final-authority decision.

## Frontier

Frontier is a lane orchestrator. It manages a bounded lane backlog, prepares packages, dispatches allowed downstream work, consumes child handoffs as provisional evidence, and reports lane status. A Frontier launched by Primary should default to B2 lane-local authority unless Primary explicitly narrows it. It does not own final acceptance.

Frontier runs a B0/B1/B2 closure loop. It does discovery and review at B0, prepares packages and task cards at B1, dispatches scoped workers or reviewers at B2 when the CARD, allowed scope, verification, handoff path, and stop conditions are clear, consumes child handoffs, and keeps reclassifying gaps. It returns to Primary only when all visible lane gaps are final-authority-only or explicitly out.

Frontier should dispatch worker, reviewer, discovery, validation, and task-card-only child work from its current lane thread when subagent or delegation tools are available. Asking the human to open child threads is fallback only, not the default closure path.

Frontier children wake the owning Frontier when they return. They mirror wake Primary only when the lane charter explicitly says `primaryMirrorWake: true`. This keeps Primary from becoming a noise sink while preserving final-authority visibility when the lane asks for it.

## Worker

Worker executes one narrow task card. It works inside allowed files or effects, runs verification, and writes a handoff. It stops when new authority, new scope, real credentials, production data, external side effects, or dependency changes are required.

## Reviewer

Reviewer is read-only by default. It checks scope, correctness, verification, side effects, and overclaiming. It recommends approve, amend, split-follow-up, or reject. It does not merge or accept final evidence by itself.

## Human Owner

Human owner decides business meaning, legal or policy questions, real resource approval, credentials, data permissions, production launch, public publication, customer-visible release, and risk waivers. These decisions stay with the human owner unless a future charter names a narrower owner-approved delegation.

## Hygiene

Always distinguish role, thread, lane, workspace, branch, authority, and evidence state.

Subagent output is evidence, not authority. The orchestrator that dispatched the subagent must consume the result before using it for closure. Frontier closure proof is also evidence; final lane acceptance belongs to Primary or the human owner under the active authority charter.

Return wake packets are action requests, not acceptance. A returning Frontier wakes Primary. A worker or reviewer wakes the orchestrator that spawned it. The owner still reads the named artifact, validates when possible, and records a consume or classification decision.
