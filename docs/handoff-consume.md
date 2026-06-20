# Handoff Consume

Handoff consume decides what a handoff proves.

## Presence Is Not Acceptance

A handoff can exist while remaining incomplete, unverified, out of scope, or overclaimed.

A return wake can also exist before acceptance. The wake only tells the owning orchestrator that a handoff, review, closure, blocker, or report is ready to inspect. The owner still has to read it, validate it when possible, and record a consume or classification decision.

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
openaccp-validate --artifact <consume-result.json> --ruleset consume-result --strict
```

When Primary final-accepts a Frontier return or Primary-ready packet, cite the closure `closureId`, `laneId`, or path in `basisRefs`, then validate the consume result with that Frontier closure proof:

```bash
openaccp-validate --artifact <consume-result.json> --ruleset consume-result --frontier-closure <frontier-closure.json> --strict
```

The closure proof is evidence. A returned packet becomes accepted only after Primary or the human owner records an accepted consume decision inside the active authority boundary.
