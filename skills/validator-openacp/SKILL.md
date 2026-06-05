---
name: validator-openacp
description: Validate OpenACP artifacts for structure, encoding, required fields, source status, authority boundary, verification evidence, overclaiming, and public-package hygiene before dispatch, handoff consume, reports, or release packaging.
---

# Validator OpenACP

Run:

```bash
python tools/openacp_validate.py --artifact <path> --ruleset <ruleset> --strict
```

For cross-checks:

```bash
python tools/openacp_validate.py --artifact task-card.json --ruleset task-card --source-pack source-pack.json --strict
python tools/openacp_validate.py --artifact handoff.json --ruleset handoff --task-card task-card.json --strict
python tools/openacp_validate.py --artifact primary-orchestrator.prompt.md --ruleset prompt-record --expect-prompt-id <prompt-id> --strict
python tools/openacp_validate.py --artifact primary.short-launcher.md --ruleset launcher --prompt-record primary-orchestrator.prompt.md --expect-prompt-id <prompt-id> --strict
python tools/openacp_validate.py --artifact response-with-launcher.md --ruleset launcher-output --strict
python tools/openacp_validate.py --artifact status.md --ruleset formal-report --strict
python tools/openacp_validate.py --artifact frontier.prompt.md --ruleset frontier-contract --strict
python tools/openacp_validate.py --artifact CARDS.md --ruleset card-registry --strict
python tools/openacp_validate.py --artifact current-manifest.json --ruleset current-manifest --source-pack source-pack.json --strict
python tools/openacp_validate.py --artifact sequence-registry.json --ruleset sequence-registry --strict
python tools/openacp_validate.py --artifact consume-result.json --ruleset consume-result --strict
python tools/openacp_validate.py --artifact machine-summary.json --ruleset machine-summary --strict
```

Use `frontier-contract` before launching or reusing a Frontier prompt. It checks the B2 lane contract, `openacp-frontier-orchestration-contract.v1` JSON block, subagent-first dispatch, child ledger, branch return gate, worktree decision, human-readable reporting, and fallback-only child launcher rule.

Use `card-registry` before Frontier dispatch. It checks that CARDs were cut from a broad domain scan, normal or medium/high-complexity projects have enough CARDs for useful parallelism, fewer CARDs have an explicit small/single-lane/user-request reason, and CARDs can map to task-card candidates and Frontier lane groups.

Use `launcher-output` when a response is supposed to give the human a Primary or Frontier launcher. It rejects responses that only link `.short.md` files or give `Get-Content` commands instead of copyable fenced `prompt` blocks.

Use `public-package` before release packaging. It checks UTF-8, mojibake, local path leaks, internal identifier markers, lightweight secret markers, English-only root README, and public report hygiene.

Validator pass is not work completion.
