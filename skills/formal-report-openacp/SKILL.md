---
name: formal-report-openacp
description: Produce a structured OpenACP formal report for human owners and downstream agents. Use when reporting project, lane, bootstrap, handoff consume, review, validation, or release-readiness status with progress, gaps, authority limits, and next actions.
---

# Formal Report OpenACP

Report current state, completed work, unverified claims, blockers, next actions, authority limits, and basis references.

Use owner-readable language. Do not call validator pass semantic approval or reviewer recommendation final acceptance.

## Post-Install Startup Report

After installing OpenACP as a skill + workflow kit, produce a formal report automatically. The user should not need to request it separately.

The startup formal report should state:

- what was installed or loaded,
- which validation commands passed or failed,
- whether the OpenACP skills are available,
- whether `openacp` and `openacp-validate` are available,
- current startup state,
- gaps,
- next step.

The next step must ask for:

- your working directory, which is required,
- your current source pack, PRD, spec, or facts path.

If no prepared facts path exists, ask the user to upload or attach the project materials. Do not treat uploaded materials as a replacement for the working directory; the working directory is still required.

End the post-install report with human-readable wording, not a vague checklist. The meaning should be:

```text
I have installed and validated OpenACP, but I cannot build useful project launchers yet because I do not know where your project work should happen or which materials count as current facts. Please send me one clear working directory. This is required. Also send your source pack, PRD, spec, design document, or facts path. If you do not have a clean facts path yet, you can upload the project materials instead and I will treat them as candidate facts, but I still need the working directory.
```

## Next Step Rule

The next step in a formal report must be actionable.

For Primary, name the decision, dispatch, consume, or closure action Primary should perform.

For Frontier, include a Frontier-owned B0/B1/B2 action when any safe lane-local work remains. Return to Primary only when the report includes closure proof showing every visible remaining gap is final-authority-only or explicitly out.

Avoid a next step that only says "wait". If waiting is unavoidable, name what evidence or user fact is missing and what prepared packet will be used when it arrives.
