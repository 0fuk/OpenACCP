# ADR-002: Keep The Validator Structural

## Status

Accepted

## Date

2026-06-03

## Context

Multi-agent workflows need checks for missing fields, overclaiming, source misuse, and incomplete handoffs. A validator still cannot judge product or code correctness.

## Decision

The OpenACP validator checks structure, hygiene, source status, authority boundaries, verification evidence, and overclaiming. It does not replace semantic review, CI, security review, human owners, or final authority.

## Consequences

Validator pass must not be described as work completion or final acceptance.
