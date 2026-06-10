# Validator

The OpenACCP validator is a structural and hygiene gate. It checks whether an artifact has the minimum shape needed for coordination, whether common unsafe claims appear, and whether a public package contains obvious private material.

The validator runs JSON Schema checks first, then applies OpenACCP semantic, cross-artifact, and public-package hygiene rules. Semantic review, code tests, CI, security review, legal review, and final owner acceptance remain visible owner decisions around that validator gate.

## Schemas, Templates, And Rules

- `schemas/*.schema.json` describe the machine-readable JSON artifact shape.
- `templates/*.md` help humans and agents draft the content.
- `tools/openaccp_validate.py` applies JSON Schema validation, cross-artifact checks, authority rules, launcher rules, report-format rules, and public-package hygiene checks.

## Rulesets

- `source-pack`: current, reference, and deprecated source grouping.
- `scope-boundary`: in-scope, out-of-scope, approval, forbidden action, and stop-condition coverage.
- `task-card`: executable slice, source refs, scope, verification plan, authority level, and B2/B3 authority charter reference.
- `authority-charter`: granted role, authority level, final authority reservation, machine-readable delegated final decisions, scope limits, data risk limit, resource use limit, allowed inputs/outputs, forbidden side effects, and stop conditions.
- `handoff`: non-final worker or role claims, `Response ID`, authority, base and result commits, worktree, data risk, effects preset, changed file scope, task ID match, verification evidence, and forbidden claims.
  Handoff scope patterns use Python `fnmatch` semantics after path normalization. Backslashes are normalized to `/`, matching is case-sensitive on every platform, and `*` may match across `/`.
- `review-report`: reviewer recommendation and review evidence shape.
- `consume-result`: provisional or final consume decision, target handoffs/reviews, accepted/rejected claims, evidence status, authority limits, and next actions.
- `machine-summary`: compact locator summary for worker, reviewer, discovery, Frontier, or Primary output with Prompt ID, Response ID, authority, effects, basisRefs, locators, claims, and next actions.
- `status-report`: current state, unverified claims, blockers, next actions, authority limits, and `responseId`. `reportId` is deprecated.
- `assumption-ledger`: assumptions, evidence, risk, and confirmation flags.
- `card-registry`: project-level CARD registry with domain coverage, 10-20 CARD expectation for normal or medium/high-complexity work, task-card candidates, Frontier lane grouping, and explicit small/single-lane/user-request exception when fewer CARDs are used.
- `prompt-record`: full on-disk orchestrator or worker prompt record with Prompt ID, role, authority, preferred language, and human-readable reply contract.
- `launcher`: short chat launcher that points to an on-disk prompt record, requires explicit UTF-8 reading, and does not paste the full prompt body into chat. Worker, reviewer, discovery, validation, and task-card-only launchers are rejected unless they are explicitly marked as fallback launchers with a direct-dispatch failure reason. Use `--prompt-record` to cross-check the launcher Prompt ID against the full prompt record.
- `launcher-output`: response-log or chat-output text that must include one or more copyable fenced `prompt` blocks, plus natural-language instruction to open a new left-sidebar thread and paste the launcher. It rejects file-link-only and `Get-Content` substitutes.
- `formal-report`: readable status report with `Response ID`, `Response log path`, standard `Item/Status` or `类型和状态` table header, stable role-aware table rows, numeric progress, basis, evidence details, a recommended next step, and no shell command dump. Chinese chat reports use pure Markdown tables and reject `<nobr>` or HTML no-wrap wrappers. `Checkpoint` rows are rejected.
- `frontier-contract`: Frontier prompt or report text with B2 lane-local authority, active B0/B1/B2 closure rules, gap decision matrix, branch return gate, worktree decision, subagent-first current-thread dispatch, child ledger, recommended next step, fallback-only child launcher rules, and a JSON `openaccp-frontier-orchestration-contract.v1` block.
- `runtime-boundary`: Primary startup boundary with working directory, product repo status/path, inferred base branch, source roots, test entrypoints, worktree policy, inference evidence, ambiguity notes, writable/read-only/forbidden paths, side effects, data risk, unresolved owner inputs, and `b2DispatchGate`.
- `current-manifest`: current fact anchor that records preferred language, facts input, current source pack, invalid sources, deprecated sources, sequence registry, lane registry, runtime boundary, source status registry, card registry, active lanes, superseded prompts, cancelled prompts, and latest consume refs.
- `sequence-registry`: registry of prompt records, responses, handoffs, consumes, active cards, active lanes, lifecycle states, and current/latest pointers.
- `lane-registry`: Primary/Frontier lane registry with project complexity, Frontier dispatch mode, lane-count reason, assigned CARDs, authority, runtime boundary ref, child ledger ref, consume refs, return-gate status, and per-lane `b2DispatchGate`.
- `child-ledger`: Frontier child lifecycle registry with promptId, taskId, authority, effects, dispatch status, handoff status, consume status, and remaining risk. Response ID and handoffId are lifecycle fields.
- `source-status-registry`: current, reference, deprecated, invalid, and unknown source status with reasons and locators.
- `decision-registry`: owner questions, Primary decisions, waivers, out-of-scope decisions, blockers, safe defaults, and required authority.
- `frontier-closure`: Frontier closure or return-gate proof. It rejects closed or blocked states while B0/B1/B2-safe work remains, while child work has not returned, while present handoffs are not consumed/rejected, while stage progress is mislabeled as a Primary-ready packet, or while a sibling lane registry still says the lane is not ready for Primary.
- `public-package`: UTF-8, common mojibake, local paths, internal identifier markers, lightweight secret markers, English-only root README, and internal formal reports placed in public report paths.

## Commands

```bash
python tools/openaccp_validate_selftest.py
python tools/openaccp_validate.py --artifact . --ruleset public-package --strict
```

Task-card validation should include the source pack:

```bash
python tools/openaccp_validate.py --artifact examples/single-worker-flow/task-card.json --ruleset task-card --source-pack examples/single-worker-flow/source-pack.json --strict
```

Handoff validation should include the task card:

```bash
python tools/openaccp_validate.py --artifact examples/single-worker-flow/handoff.json --ruleset handoff --task-card examples/single-worker-flow/task-card.json --strict
```

Frontier contracts can be checked directly:

```bash
python tools/openaccp_validate.py --artifact templates/frontier-orchestrator-launcher.md --ruleset frontier-contract --strict
```

Prompt records, short launchers, and formal reports can be checked before dispatch or status publication:

```bash
python tools/openaccp_validate.py --artifact .openaccp/launchers/primary-orchestrator.prompt.md --ruleset prompt-record --expect-prompt-id <prompt-id> --strict
python tools/openaccp_validate.py --artifact .openaccp/launchers/primary-orchestrator.short.md --ruleset launcher --prompt-record .openaccp/launchers/primary-orchestrator.prompt.md --expect-prompt-id <prompt-id> --strict
python tools/openaccp_validate.py --artifact .openaccp/reports/response-with-launcher.md --ruleset launcher-output --strict
python tools/openaccp_validate.py --artifact .openaccp/reports/response.md --ruleset formal-report --preferred-language Chinese --strict
```

CARD registries can be checked before Frontier dispatch:

```bash
python tools/openaccp_validate.py --artifact .openaccp/tasks/CARDS.md --ruleset card-registry --strict
```

Manifest and registry validation should run after Primary creates or refreshes coordination state:

```bash
python tools/openaccp_validate.py --artifact .openaccp/coordination/runtime-boundary.json --ruleset runtime-boundary --strict
python tools/openaccp_validate.py --artifact .openaccp/coordination/current-manifest.json --ruleset current-manifest --strict
python tools/openaccp_validate.py --artifact .openaccp/coordination/sequence-registry.json --ruleset sequence-registry --strict
python tools/openaccp_validate.py --artifact .openaccp/coordination/lane-registry.json --ruleset lane-registry --strict
python tools/openaccp_validate.py --artifact .openaccp/coordination/source-status-registry.json --ruleset source-status-registry --strict
python tools/openaccp_validate.py --artifact .openaccp/coordination/decision-registry.json --ruleset decision-registry --strict
```

Frontier lifecycle artifacts can be checked before a lane reports blocked, closed, or ready for Primary:

```bash
python tools/openaccp_validate.py --artifact .openaccp/coordination/child-ledgers/frontier-01.json --ruleset child-ledger --strict
python tools/openaccp_validate.py --artifact .openaccp/coordination/frontier-closures/frontier-01.json --ruleset frontier-closure --strict
```

Consume results and compact machine summaries can be checked after handoff consume, worker output, reviewer output, or discovery output:

```bash
python tools/openaccp_validate.py --artifact .openaccp/consume/consume-result.json --ruleset consume-result --strict
python tools/openaccp_validate.py --artifact .openaccp/summaries/machine-summary.json --ruleset machine-summary --strict
```

Individual project artifacts may contain that project's local working paths. The `public-package` ruleset is stricter and is intended for release packages, where private local paths, internal identifiers, and secret-like strings must not appear.

After editable install:

```bash
openaccp-validate --help
openaccp-validate --version
openaccp --help
openaccp --version
```

## Interpreting Results

A validator pass means the artifact is structurally usable for the selected ruleset. It does not mean:

- the product requirement is correct,
- the code works,
- the change is secure,
- the evidence is sufficient for release,
- the work is merged, accepted, waived, or complete.

Use validator output as one input to review and final consume, not as the final decision.
