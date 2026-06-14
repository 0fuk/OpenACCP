# Changelog

## Unreleased

### Compatibility

- Before v1.0, breaking artifact schema changes bump that artifact's `schemaVersion` suffix. After upgrading, re-run the validator on stored artifacts and use this changelog as the migration record.

### Added

- `consume-result` and `machine-summary` schemas, templates, examples, and validator rulesets.
- Machine-readable Frontier contract block `openaccp-frontier-orchestration-contract.v1` for B2 lane closure, subagent-first dispatch, child ledger, and branch return gates.
- Prompt launcher cross-check support with `--prompt-record` and `--expect-prompt-id`.
- `launcher-output` validator ruleset for response logs with explicit dispatch channels: direct agent/thread dispatch where supported, and strict copyable fenced `prompt` blocks for manual fallback.

### Changed

- Formal reports now require `Response ID`, `Response log path`, role-aware rows, numeric progress, and evidence details.
- Authority charters now include data risk limits, resource-use limits, allowed inputs/outputs, forbidden side effects, and stop conditions.
- Current manifests and sequence registries now track active lanes, superseded or cancelled prompts, consume records, and latest consume refs.
- Coordination readiness now uses `execution-boundary` and `executionBoundaryRef` across schemas, templates, examples, validator rules, and startup docs.
- Startup and Frontier launcher instructions now use on-disk launcher files as the audit source, direct agent/thread dispatch as the default when available, and copyable chat `prompt` blocks as manual fallback. File links or `Get-Content` commands are rejected as manual fallback substitutes.
- Launcher-output validation now requires explicit direct-dispatch success evidence. Bare mentions such as a failed `agent_thread_spawn` attempt no longer bypass manual fallback launcher checks.
- README now uses a human-readable onboarding flow with concrete user personas, manual Primary/Frontier startup guidance, skill descriptions, artifact communication, B0/B1/B2/B3 explanations, and core OpenACCP technology summaries.

## [0.1.0] - 2026-06-04

### Added

- Initial OpenACCP release candidate with Bootstrap and Coordination paths.
- JSON schemas, Markdown templates, portable skills, examples, and validator CLI.
- Public-package hygiene scan for local paths, internal identifiers, common mojibake, lightweight secret markers, and internal formal reports placed in public report paths.
- `openaccp init` dry-run starter package command and `openaccp-validate` console entry point.
- GitHub Actions CI for validator self-tests, public scan, and strict example validation.

### Changed

- B2/B3 task cards now require `authorityCharterRef` in strict validation.
- Single-worker example is the full strict-validation fixture; Frontier and multi-worktree examples are marked as concept examples.
- Python package namespace changed to `openaccp`; source-tree `tools/` scripts remain as compatibility wrappers.

### Notes

- This release candidate is intended for public review before a stable v1.0.0 tag.
