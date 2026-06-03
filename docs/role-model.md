# Role Model

OpenACP defines roles by authority, not by model provider.

## Primary

Primary owns final authority. It can assign charters, dispatch lanes and workers, consume final handoffs, decide merge or publication, grant waivers, and accept or reject evidence.

## Frontier

Frontier is a lane orchestrator. It manages a bounded lane backlog, prepares packages, dispatches allowed downstream work, consumes child handoffs as provisional evidence, and reports lane status. It does not own final acceptance by default.

## Worker

Worker executes one narrow task card. It works inside allowed files or effects, runs verification, and writes a handoff. It stops when new authority, new scope, real credentials, production data, external side effects, or dependency changes are required.

## Reviewer

Reviewer is read-only by default. It checks scope, correctness, verification, side effects, and overclaiming. It recommends approve, amend, split-follow-up, or reject. It does not merge or accept final evidence by itself.

## Human Owner

Human owner decides business meaning, legal or policy questions, real resource approval, credentials, data permissions, production launch, and risk waivers.

## Hygiene

Always distinguish role, thread, lane, workspace, branch, authority, and evidence state.
