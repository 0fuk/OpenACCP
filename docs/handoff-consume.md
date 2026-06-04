# Handoff Consume

Handoff consume decides what a handoff proves.

## Presence Is Not Acceptance

A handoff can exist while remaining incomplete, unverified, out of scope, or overclaimed.

## Checklist

- task card exists,
- authority source is clear,
- changed artifacts fit allowed scope,
- forbidden scope is untouched,
- verification evidence exists,
- skipped checks are explained,
- reviewer recommendation is considered when required,
- risks and remaining work are visible,
- final claims have final-authority evidence.

## Outcomes

- `accepted`
- `amend`
- `split-follow-up`
- `rejected`
- `blocked`

Only final authority can turn provisional evidence into accepted evidence.

## Machine Result

Each consume should produce a `consume-result` artifact. That artifact separates provisional Frontier consume from final Primary or human-owner consume.

Validate it with:

```bash
openacp-validate --artifact <consume-result.json> --ruleset consume-result --strict
```
