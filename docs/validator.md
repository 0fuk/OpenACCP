# Validator

The OpenACP validator is a structural and hygiene gate. It checks whether an artifact has the minimum shape needed for coordination, whether common unsafe claims appear, and whether a public package contains obvious private material.

It is deliberately small and dependency-free. It does not replace semantic review, code tests, CI, security review, legal review, or final owner acceptance.

## Schemas, Templates, And Rules

- `schemas/*.schema.json` describe the machine-readable JSON artifact shape.
- `templates/*.md` help humans and agents draft the content.
- `tools/openacp_validate.py` applies schema-like required fields plus cross-artifact checks and public-package hygiene checks.

The validator is not a full JSON Schema engine. It uses hardcoded rules that match the current OpenACP v1 artifact contracts.

## Rulesets

- `source-pack`: current, reference, and deprecated source grouping.
- `scope-boundary`: in-scope, out-of-scope, approval, forbidden action, and stop-condition coverage.
- `task-card`: executable slice, source refs, scope, verification plan, authority level, and B2/B3 authority charter reference.
- `authority-charter`: granted role, authority level, final authority reservation, and scope limits.
- `handoff`: non-final worker or role claims, `Response ID`, authority, base and result commits, worktree, data risk, effects preset, changed file scope, task ID match, verification evidence, and forbidden claims.
- `review-report`: reviewer recommendation and review evidence shape.
- `status-report`: current state, unverified claims, blockers, next actions, and authority limits.
- `assumption-ledger`: assumptions, evidence, risk, and confirmation flags.
- `prompt-record`: full on-disk orchestrator or worker prompt record with Prompt ID, role, authority, preferred language, and human-readable reply contract.
- `launcher`: short chat launcher that points to an on-disk prompt record, requires explicit UTF-8 reading, and does not paste the full prompt body into chat.
- `formal-report`: readable status report with `Response ID`, stable table rows, numeric progress, basis, and evidence details.
- `frontier-contract`: Frontier prompt or report text with B2 lane-local authority, active B0/B1/B2 closure rules, gap decision matrix, branch return gate, worktree decision, and dispatch rules.
- `current-manifest`: current fact anchor that records preferred language, facts input, current source pack, invalid sources, deprecated sources, sequence registry, active cards, and active lanes.
- `sequence-registry`: registry of prompt records, responses, handoffs, active cards, and current/latest pointers.
- `public-package`: UTF-8, common mojibake, local paths, internal identifier markers, lightweight secret markers, and internal formal reports placed in public report paths.

## Commands

```bash
python tools/openacp_validate_selftest.py
python tools/openacp_validate.py --artifact . --ruleset public-package --strict
```

Task-card validation should include the source pack:

```bash
python tools/openacp_validate.py --artifact examples/single-worker-flow/task-card.json --ruleset task-card --source-pack examples/single-worker-flow/source-pack.json --strict
```

Handoff validation should include the task card:

```bash
python tools/openacp_validate.py --artifact examples/single-worker-flow/handoff.json --ruleset handoff --task-card examples/single-worker-flow/task-card.json --strict
```

Prompt records, short launchers, and formal reports can be checked before dispatch or status publication:

```bash
python tools/openacp_validate.py --artifact .openacp/launchers/primary-orchestrator.prompt.md --ruleset prompt-record --strict
python tools/openacp_validate.py --artifact .openacp/launchers/primary-orchestrator.short.md --ruleset launcher --strict
python tools/openacp_validate.py --artifact .openacp/reports/response.md --ruleset formal-report --strict
```

Manifest and registry validation should run after Primary creates or refreshes coordination state:

```bash
python tools/openacp_validate.py --artifact .openacp/current-manifest.json --ruleset current-manifest --source-pack .openacp/source-pack.json --strict
python tools/openacp_validate.py --artifact .openacp/sequence-registry.json --ruleset sequence-registry --strict
```

Individual project artifacts may contain that project's local working paths. The `public-package` ruleset is stricter and is intended for release packages, where private local paths, internal identifiers, and secret-like strings must not appear.

After editable install:

```bash
openacp-validate --help
openacp-validate --version
openacp --help
openacp --version
```

## Interpreting Results

A validator pass means the artifact is structurally usable for the selected ruleset. It does not mean:

- the product requirement is correct,
- the code works,
- the change is secure,
- the evidence is sufficient for release,
- the work is merged, accepted, waived, or complete.

Use validator output as one input to review and final consume, not as the final decision.
