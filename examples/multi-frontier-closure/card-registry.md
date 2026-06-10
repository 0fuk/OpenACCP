# CARD Registry - Multi Frontier Closure Fixture

schemaVersion: openaccp-card-registry.v1
artifactType: card-registry

## Domain Coverage

| Domain | Present? | Source refs | CARD coverage | Decision |
|---|---|---|---|---|
| Product workflow | no | Fixture focuses on documentation closure mechanics. | none | out of scope for this strict fixture |
| Backend API | no | No backend source exists in this fixture. | none | out of scope for this strict fixture |
| Data storage | no | No data/storage source exists in this fixture. | none | out of scope for this strict fixture |
| Frontend UI | no | No UI source exists in this fixture. | none | out of scope for this strict fixture |
| Desktop / Electron | no | No desktop shell source exists in this fixture. | none | out of scope for this strict fixture |
| Integrations | no | No integration source exists in this fixture. | none | out of scope for this strict fixture |
| Security / privacy | no | No security or privacy behavior is in scope. | none | out of scope for this strict fixture |
| Testing / QA | yes | SRC-DEMO-PRD | CARD-001 | covered |
| CI / release / ops | no | Release and CI behavior are not modeled here. | none | out of scope for this strict fixture |

## Complexity Assessment

- complexity: small
- small-project-reason: this strict fixture demonstrates one closed Frontier lane, not a full product decomposition.

## CARD List

| CARD | Domain | Authority | Lane | Status | Objective | Source | Task-card candidates |
|---|---|---|---|---|---|---|---|
| CARD-001 | docs | B2 | frontier-docs | ready | Prepare reviewed documentation evidence. | SRC-DEMO-PRD | TASK-DOCS-001 |

## Lane Grouping

- Frontier lane candidate `frontier-docs`: CARD-001 is safe as one small fixture lane.
