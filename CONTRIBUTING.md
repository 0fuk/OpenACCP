# Contributing To OpenACCP

OpenACCP contributions should improve reusable multi-agent coordination, not encode a private project's workflow.

## Contribution Guidelines

- Keep examples project-neutral.
- Do not include local absolute paths.
- Do not include internal run logs, customer data, credentials, private branches, or production evidence.
- Prefer generic IDs such as `taskId`, `artifactId`, `reportId`, and `runId`.
- Keep validator checks structural and explain their limits.
- Add or update examples when adding a new template or schema.
- Run the validator self-test before submitting changes.
- Keep strict fixtures and concept examples clearly labeled.
- Keep local reports in ignored paths such as `.openaccp-local/`.
- Write commit messages in imperative mood with a capitalized first word; conventional-commit prefixes are optional.

## Local Validation

```bash
python tools/openaccp_validate_selftest.py
python tools/openaccp_validate.py --artifact . --ruleset public-package --strict
```

For task cards and handoffs, run cross-artifact validation when possible:

```bash
python tools/openaccp_validate.py --artifact examples/single-worker-flow/task-card.json --ruleset task-card --source-pack examples/single-worker-flow/source-pack.json --strict
python tools/openaccp_validate.py --artifact examples/single-worker-flow/handoff.json --ruleset handoff --task-card examples/single-worker-flow/task-card.json --strict
```

## Review Standard

Review should check:

- scope is generic and reusable,
- templates are understandable without private context,
- schemas prevent missing evidence and overclaiming,
- validator checks do not imply semantic approval,
- examples cover the intended user path.

## License

OpenACCP v1 uses the MIT License. Contributors agree that submitted changes are provided under the project license.
