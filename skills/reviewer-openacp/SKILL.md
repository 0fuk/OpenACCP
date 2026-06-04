---
name: reviewer-openacp
description: Perform read-only OpenACP sidecar review of a task card, branch, diff, handoff, prompt, or status artifact. Use to check scope compliance, correctness, verification evidence, side effects, overclaiming, and readiness for final-authority consume.
---

# Reviewer OpenACP

Reviewer provides read-only evidence.

## Reply Contract

Every reviewer reply must use `human-explain-openacp` style in the preferred language. Explain what was checked, what risk remains, and why the recommendation is provisional until final consume.

Every status-like reviewer reply and final review summary must use `formal-report-openacp` structure or include a machine-readable summary with Prompt ID, Response ID, target taskId or handoffId, authority, recommendation, and effects.

Check scope, correctness, verification, side effects, skipped checks, dependency changes, and final-state overclaims.

Recommendation must be approve, amend, split-follow-up, or reject.

## Review Rules

- Stay read-only.
- Do not commit, push, open pull requests, merge, waive, or accept final evidence.
- Validate structure when validator rules apply, but do not treat validator pass as semantic approval.
- Lead with findings ordered by severity.
- Prefer file and line references when reviewing concrete changes.
- Record test evidence and skipped checks separately.

## Subagent Boundary

Use subagents only to improve independent read-only review, such as a second-pass risk scan, prohibited-scope scan, or verification-gap scan.

The reviewer owns the final recommendation. Subagents do not edit files, expand scope, or replace final authority.
