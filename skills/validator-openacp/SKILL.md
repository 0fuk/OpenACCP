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
python tools/openacp_validate.py --artifact primary-orchestrator.prompt.md --ruleset prompt-record --strict
python tools/openacp_validate.py --artifact primary.short-launcher.md --ruleset launcher --strict
python tools/openacp_validate.py --artifact status.md --ruleset formal-report --strict
python tools/openacp_validate.py --artifact current-manifest.json --ruleset current-manifest --source-pack source-pack.json --strict
python tools/openacp_validate.py --artifact sequence-registry.json --ruleset sequence-registry --strict
```

Validator pass is not work completion.
