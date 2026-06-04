---
name: discovery-openacp
description: Run read-only OpenACP discovery and planning. Use when facts, scope, source status, task readiness, risk, or next safe action are unclear and implementation is not yet authorized.
---

# Discovery OpenACP

Read facts, classify gaps, and prepare safe next steps without implementation.

Do not edit, commit, merge, or treat reference material as current fact.

## Reply Contract

Every discovery reply must use `human-explain-openacp` style in the preferred language. Explain what facts were found, what is still unproven, and which B0/B1/B2 action becomes possible next.

Every status-like discovery reply must use `formal-report-openacp` structure or include a `machine-summary` artifact with Prompt ID, Response ID, source ids, authority, effects, basisRefs, locators, claims, and nextActions.

## Evidence And Locator Rules

Discovery output should name current, reference, deprecated, invalid, and unknown sources separately. Include locators for each material read, plus the exact next B0/B1/B2 action unlocked by those facts. Discovery does not claim implementation readiness unless a task card, authority charter, and verification plan already exist.
