---
name: validator-openaccp
description: Validate OpenACCP artifacts for structure, encoding, required fields, source status, authority boundary, verification evidence, overclaiming, and public-package hygiene before dispatch, handoff consume, reports, or release packaging.
---

# Validator OpenACCP

Run:

```bash
python tools/openaccp_validate.py --artifact <path> --ruleset <ruleset> --strict
```

For cross-checks:

```bash
python tools/openaccp_validate.py --artifact task-card.json --ruleset task-card --source-pack source-pack.json --strict
python tools/openaccp_validate.py --artifact handoff.json --ruleset handoff --task-card task-card.json --strict
python tools/openaccp_validate.py --artifact primary-orchestrator.prompt.md --ruleset prompt-record --expect-prompt-id <prompt-id> --strict
python tools/openaccp_validate.py --artifact primary.short-launcher.md --ruleset launcher --prompt-record primary-orchestrator.prompt.md --expect-prompt-id <prompt-id> --strict
python tools/openaccp_validate.py --artifact response-with-launcher.md --ruleset launcher-output --strict
python tools/openaccp_validate.py --artifact status.md --ruleset formal-report --preferred-language <language> --strict
python tools/openaccp_validate.py --artifact frontier.prompt.md --ruleset frontier-contract --strict
python tools/openaccp_validate.py --artifact runtime-boundary.json --ruleset runtime-boundary --strict
python tools/openaccp_validate.py --artifact lane-registry.json --ruleset lane-registry --strict
python tools/openaccp_validate.py --artifact .openaccp/coordination/child-ledgers/<lane-id>.json --ruleset child-ledger --strict
python tools/openaccp_validate.py --artifact source-status-registry.json --ruleset source-status-registry --strict
python tools/openaccp_validate.py --artifact decision-registry.json --ruleset decision-registry --strict
python tools/openaccp_validate.py --artifact .openaccp/coordination/frontier-closures/<lane-id>.json --ruleset frontier-closure --strict
python tools/openaccp_validate.py --artifact CARDS.md --ruleset card-registry --strict
python tools/openaccp_validate.py --artifact current-manifest.json --ruleset current-manifest --source-pack source-pack.json --strict
python tools/openaccp_validate.py --artifact sequence-registry.json --ruleset sequence-registry --strict
python tools/openaccp_validate.py --artifact consume-result.json --ruleset consume-result --strict
python tools/openaccp_validate.py --artifact machine-summary.json --ruleset machine-summary --strict
```

Use `frontier-contract` before launching or reusing a Frontier prompt. It checks the B2 lane contract, `openaccp-frontier-orchestration-contract.v1` JSON block, subagent-first dispatch, child ledger, branch return gate, worktree decision, human-readable reporting, and fallback-only child launcher rule.

Use `runtime-boundary` during Primary startup before B2 Frontier dispatch. It records working directory, product repo status/path, Primary-inferred base branch, source roots, test entrypoints, worktree policy, inference evidence, ambiguity notes, writable/read-only/forbidden paths, side-effect level, data risk, unresolved owner inputs, and `b2DispatchGate`.

Use `lane-registry` for the active Primary/Frontier control plane. It records project complexity, Frontier dispatch mode, lane-count reason, lane ids, objectives, authority, assigned CARDs, runtime boundary, child ledger, latest consume refs, return gate status, and per-lane `b2DispatchGate`.

Use `child-ledger` inside each Frontier lane. It records every worker/reviewer/discovery/validation child with Prompt ID, taskId, authority, effects, dispatch status, handoff status, consume status, and remaining risk. Response ID and handoffId become required by lifecycle when a child returns or a handoff is present. B3 child authority is invalid.

Use `source-status-registry` to make current/reference/deprecated/invalid/unknown facts explicit. Deprecated, invalid, and unknown sources require a reason.

Use `decision-registry` for owner questions, Primary decisions, waivers, and out-of-scope decisions that block or unblock lanes.

Use `frontier-closure` before a Frontier reports closed or blocked-on-Primary. It rejects early return when B0/B1/B2-safe work remains, when child work is not terminal or consumed/rejected, when stage progress is mislabeled as a Primary-ready packet, when a Primary consume next step appears before the return gate is ready, or when the sibling lane registry still says the lane is not ready for Primary.

Use `card-registry` before Frontier dispatch. It checks that CARDs were cut from a broad domain scan, normal or medium/high-complexity projects have enough CARDs for useful parallelism, fewer CARDs have an explicit small/single-lane/user-request reason, and CARDs can map to task-card candidates and Frontier lane groups.

Use `launcher-output` when a response is supposed to give the human a Primary or Frontier launcher. It rejects responses that only link `.short.md` files or give `Get-Content` commands instead of copyable fenced `prompt` blocks.

Use `formal-report` before publishing a report-like chat output or response log. It requires `Response ID`, `Response log path`, the header `| 类型和状态 | 内容 |` or `| Item/Status | Content |`, role-aware rows, evidence outside the table, and a `Recommended Next Step` / `下一步建议` ending. Chinese chat reports should stay pure Markdown and must not use `<nobr>`, HTML wrappers, invisible characters, or spacing tricks. It rejects `Checkpoint`, free-form install rows such as `Skill` or `CLI`, legacy row labels, missing progress percentages, long English-dominant Chinese reports, and shell command dumps.

Use `public-package` before release packaging. It checks UTF-8, mojibake, local path leaks, internal identifier markers, lightweight secret markers, English-only root README, and public report hygiene.

Validator pass is not work completion.
