# Multi Worktree Review Example

This is a concept example, not a complete strict-validation fixture.

Workers use disjoint scopes and separate branches.

| Worker | Scope | Branch | Handoff |
|---|---|---|---|
| docs worker | `docs/**` | `docs/guide` | `handoff-docs.json` |
| schema worker | `schemas/**` | `schemas/contracts` | `handoff-schema.json` |

Reviewers check each handoff independently. Final authority decides integration order.

To turn this into a strict fixture, add one source pack, one authority charter per executable lane, task cards, handoffs, and review reports for each worker.
