---
name: handoff-consume-openacp
description: Consume OpenACP handoffs and decide what they prove. Use before follow-up dispatch, integration planning, final acceptance, publication, merge, amendment, or rejection.
---

# Handoff Consume OpenACP

Validate structure, check scope against task card, review verification evidence, inspect risks, consider reviewer recommendation, and decide accepted, amend, split-follow-up, rejected, or blocked.

Handoff presence is not acceptance.

Every consume should produce or return a `consume-result` artifact. Frontier consume results are provisional unless Primary explicitly granted final authority, which should not be the default. Final consume results belong to Primary or the human owner.

## Consume Rules

Before consume, check:

- handoff exists and is readable,
- task card or source authority matches the claimed work,
- changed artifacts fit allowed scope,
- forbidden files or effects were not touched,
- verification evidence is present and specific,
- skipped checks are explained,
- reviewer recommendation is considered when available,
- final-state claims are not made by non-final roles.

Use consume results to drive the next dispatch. If the handoff is incomplete, send it back for amendment or dispatch reviewer/discovery work instead of treating it as done.

## Consume Result Fields

Record:

- consumeId,
- responseId,
- consumerRole,
- authorityScope,
- targetHandoffIds,
- targetReviewIds,
- decision,
- basisRefs,
- evidenceStatus,
- claimsAccepted,
- claimsRejected,
- remainingRisks,
- authorityLimits,
- nextActions.

Validate with:

```bash
openacp-validate --artifact <consume-result.json> --ruleset consume-result --strict
```
