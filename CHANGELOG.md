# Changelog

## Unreleased

### Added

- `consume-result` and `machine-summary` schemas, templates, examples, and validator rulesets.
- Machine-readable Frontier contract block `openacp-frontier-orchestration-contract.v1` for B2 lane closure, subagent-first dispatch, child ledger, and branch return gates.
- Prompt launcher cross-check support with `--prompt-record` and `--expect-prompt-id`.

### Changed

- Formal reports now require `Response ID`, `Response log path`, role-aware rows, numeric progress, and evidence details.
- Authority charters now include data risk limits, resource-use limits, allowed inputs/outputs, forbidden side effects, and stop conditions.
- Current manifests and sequence registries now track active lanes, superseded or cancelled prompts, consume records, and latest consume refs.

## [0.1.0] - 2026-06-03

### Added

- Initial OpenACP release candidate with Bootstrap and Coordination paths.
- JSON schemas, Markdown templates, portable skills, examples, and validator CLI.
- Public-package hygiene scan for local paths, internal identifiers, common mojibake, lightweight secret markers, and internal formal reports placed in public report paths.
- `openacp init` dry-run starter package command and `openacp-validate` console entry point.
- GitHub Actions CI for validator self-tests, public scan, and strict example validation.

### Changed

- B2/B3 task cards now require `authorityCharterRef` in strict validation.
- Single-worker example is the full strict-validation fixture; Frontier and multi-worktree examples are marked as concept examples.
- Python package namespace changed to `openacp`; source-tree `tools/` scripts remain as compatibility wrappers.

### Notes

- This release candidate is intended for public review before a stable v1.0.0 tag.
