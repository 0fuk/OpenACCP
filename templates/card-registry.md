# CARD Registry

schemaVersion: openacp-card-registry.v1
artifactType: card-registry
status: draft

## Coverage Rule

Primary creates CARDs before Frontier dispatch. A CARD is a project-level slice large enough for lane planning and broad enough to expand into several concrete task cards later.

For normal or medium/high-complexity product work, prefer 10-20 project-level CARDs. Use fewer only when the project is genuinely small, only one safe independent lane exists, or the user explicitly asked for a narrow run. Record the reason as `small-project-reason` or `single-lane-reason`.

Do not invent domains that are absent from the facts. If the source facts mention UI, frontend, Electron, desktop shell, mobile, or another product surface, this registry must include CARD coverage for that surface.

## Domain Coverage

| Domain | Present? | Source refs | CARD coverage | Notes |
|---|---|---|---|---|
| Product workflow / user journey | yes / no / unclear | | | |
| Backend / API / services | yes / no / unclear | | | |
| Data / storage / migration | yes / no / unclear | | | |
| Frontend / UI / design system | yes / no / unclear | | | |
| Desktop shell / Electron / Tauri | yes / no / unclear | | | |
| Mobile / native surfaces | yes / no / unclear | | | |
| Integrations / external systems | yes / no / unclear | | | |
| Auth / security / privacy | yes / no / unclear | | | |
| Testing / QA / validation | yes / no / unclear | | | |
| Observability / CI / release / ops | yes / no / unclear | | | |
| Docs / migration guide / launch materials | yes / no / unclear | | | |
| Other project-specific domain | yes / no / unclear | | | |

## CARD List

| CARD | Domain | Authority | Candidate lane | Status | Objective | Source refs | Task-card candidates |
|---|---|---|---|---|---|---|---|
| CARD-001 | | B0/B1/B2 | | draft | | | |
| CARD-002 | | B0/B1/B2 | | draft | | | |
| CARD-003 | | B0/B1/B2 | | draft | | | |
| CARD-004 | | B0/B1/B2 | | draft | | | |
| CARD-005 | | B0/B1/B2 | | draft | | | |
| CARD-006 | | B0/B1/B2 | | draft | | | |
| CARD-007 | | B0/B1/B2 | | draft | | | |
| CARD-008 | | B0/B1/B2 | | draft | | | |
| CARD-009 | | B0/B1/B2 | | draft | | | |
| CARD-010 | | B0/B1/B2 | | draft | | | |

## Lane Grouping

Group CARDs into Frontier lanes only after checking dependency, risk, allowed effects, and parallel safety.

| Lane candidate | CARDs | Why these belong together | Authority | Parallel safety | Notes |
|---|---|---|---|---|---|
| frontier-01 | | | B2 lane-local | safe / risky / unclear | |
| frontier-02 | | | B2 lane-local | safe / risky / unclear | |

## Exceptions

- small-project-reason:
- single-lane-reason:
- explicit-user-request:
- CARD coverage gaps:
