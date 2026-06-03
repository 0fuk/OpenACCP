---
name: openacp-validator
description: Validate OpenACP artifacts for structure, encoding, required fields, source status, authority boundary, verification evidence, overclaiming, and public-package hygiene before dispatch, handoff consume, reports, or release packaging.
---

# OpenACP Validator

Run:

```bash
python tools/openacp_validate.py --artifact <path> --ruleset <ruleset> --strict
```

For cross-checks:

```bash
python tools/openacp_validate.py --artifact task-card.json --ruleset task-card --source-pack source-pack.json --strict
python tools/openacp_validate.py --artifact handoff.json --ruleset handoff --task-card task-card.json --strict
```

Validator pass is not work completion.
