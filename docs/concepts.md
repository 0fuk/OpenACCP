# Concepts

OpenACP is built around artifacts that separate facts, scope, execution, review, and final authority.

## Core Artifacts

- `source pack`: current facts, reference-only material, deprecated material, reading order, and conflict policy.
- `scope boundary`: in scope, out of scope, deferred, approval-required actions, forbidden actions, stop conditions, and scope leak examples.
- `assumptions ledger`: visible assumptions, evidence, risk, whether work can proceed, and confirmation needs.
- `task card`: smallest safe executable unit with objective, allowed scope, forbidden scope, acceptance, verification, stop conditions, and handoff.
- `handoff`: structured evidence from a worker, reviewer, discovery thread, or lane orchestrator.
- `review report`: read-only assessment of scope, correctness, verification, side effects, and claims.
- `authority charter`: explicit role authority, allowed actions, forbidden actions, delegation rules, and final authority reserve.
- `status report`: human-readable project or lane status with basis, gaps, next action, and authority limits.

## Evidence States

- `proposed`: prepared but not implemented.
- `implemented`: changed artifacts exist.
- `verified`: verification evidence is recorded.
- `reviewed`: independent review evidence is recorded.
- `accepted`: final authority has consumed the evidence.
- `merged`: final authority has integrated the work.

Workers, reviewers, discovery threads, and lane orchestrators should not claim final states without final-authority evidence.
