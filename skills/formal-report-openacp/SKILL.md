---
name: formal-report-openacp
description: Produce a structured OpenACP formal report for human owners and downstream agents. Use when reporting project, lane, bootstrap, handoff consume, review, validation, or release-readiness status with progress, gaps, authority limits, and next actions.
---

# Formal Report OpenACP

Report current state, completed work, unverified claims, blockers, next actions, authority limits, and basis references.

Use owner-readable language. Do not call validator pass semantic approval or reviewer recommendation final acceptance.

Every formal report must carry a `Response ID`, not `Report ID`. It must also include a `Response log path:` line. If there is no persisted log file, write `Response log path: chat reply` or the project-local status artifact path.

Use the user's preferred language when it is known. If the language is not known, keep the language consistent with the user's current conversation.

## Chat Table Fit Rule

Formal reports are often rendered in narrow chat panes. Keep the table readable:

- Use short first-column labels. Generic reports may use `Changed`, `Progress`, `Gate`, `Area`, `Goal`, `Gaps`, `Next`.
- Primary Chinese reports should use `做了什么`, `总体进度`, `Checkpoint`, `Frontier`, `目标`, `缺口`, `下一步`.
- Frontier Chinese reports should use `做了什么`, `总体进度`, `Checkpoint`, `Lane`, `目标`, `缺口`, `下一步`.
- Keep each table cell to a short summary.
- Do not put long paths, URLs, commit hashes, full commands, validation logs, or long inline-code snippets inside table cells.
- Put detailed evidence after the table under `Evidence Details` as normal bullets.
- For Chinese Primary or Frontier chat reports, pad the first-column labels with full-width ideographic spaces by default so the chat UI does not compress labels into vertical fragments. The visible label stays the same after validator normalization.

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
- your current source pack, PRD, spec, or facts path,
- your preferred language for future Primary, Frontier, worker, reviewer, and discovery replies.

If no prepared facts path exists, ask the user to upload or attach the project materials. Do not treat uploaded materials as a replacement for the working directory; the working directory is still required.

End the post-install report with human-readable wording, not a vague checklist. The meaning should be:

```text
I have installed and validated OpenACP, but I cannot build a useful Primary launcher yet because I do not know where your project work should happen, which materials count as current facts, or which language future agents should use. Please send me one clear working directory. This is required. Also send your source pack, PRD, spec, design document, or facts path. If you do not have a clean facts path yet, you can upload the project materials instead and I will treat them as candidate facts, but I still need the working directory. Please also tell me your preferred language; if you omit it, I will keep using your current language.
```

## Next Step Rule

The next step in a formal report must be actionable.

For Primary, name the decision, dispatch, consume, or closure action Primary should perform.

For Frontier, include a Frontier-owned B0/B1/B2 action when any safe lane-local work remains. Return to Primary only when the report includes closure proof showing every visible remaining gap is final-authority-only or explicitly out.

Avoid a next step that only says "wait". If waiting is unavoidable, name what evidence or user fact is missing and what prepared packet will be used when it arrives.
