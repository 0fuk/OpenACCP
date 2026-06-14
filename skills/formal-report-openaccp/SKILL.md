---
name: formal-report-openaccp
description: Produce a structured OpenACCP formal report for human owners and downstream agents. Use when reporting project, lane, bootstrap, handoff consume, review, validation, or release-readiness status with progress, gaps, authority limits, and next actions.
---

# Formal Report OpenACCP

Report current state, completed work, unverified claims, blockers, next actions, authority limits, and basis references.

Use owner-readable language. Do not call validator pass semantic approval or reviewer recommendation final acceptance.

Every formal report must carry a `Response ID`, not `Report ID`. It must also include a `Response log path:` line. If there is no persisted log file, write `Response log path: chat reply` or the project-local status artifact path.

Use the user's preferred language when it is known. If the language is not known, keep the language consistent with the user's current conversation.

When the preferred language is Chinese, use Chinese as the main language for headings, summaries, table cells, evidence explanations, and next actions. Keep English only for stable technical terms and exact names such as `Primary`, `Frontier`, `worker`, `reviewer`, `handoff`, `validator`, `source pack`, `Prompt ID`, `Response ID`, `CARD`, `task-card`, `B0/B1/B2/B3`, `CI`, `CLI`, `JSON`, `schema`, exact file names, or project-specific product terms. Do not write long English sentences or paragraphs in a Chinese report.

## Chat Table Fit Rule

Formal reports are often rendered in narrow chat panes. Keep the table readable:

- Use short first-column labels. Generic reports may use `Changed`, `Progress`, `Gate`, `Area`, `Goal`, `Gaps`, `Next`.
- Chinese post-install and generic startup reports should use `做了什么`, `总体进度`, `验证`, `范围`, `目标`, `缺口`, `下一步`.
- Primary Chinese reports should use `做了什么`, `总体进度`, `Frontier`, `目标`, `缺口`, `下一步`.
- Frontier Chinese reports should use `做了什么`, `总体进度`, `Lane`, `目标`, `缺口`, `下一步`.
- Use `类型和状态` as the Chinese first-column header. It avoids the `/` line-break point and keeps the table pure Markdown.
- Keep each table cell to a short summary.
- Do not use free-form row labels such as `安装`, `Skill`, `CLI`, `项目`, `状态`, `What changed`, `Lane or area`, `Next step`, `Validation`, or `Checkpoint`.
- Do not put long paths, URLs, commit hashes, full commands, validation logs, executable paths, local install paths, or long inline-code snippets inside table cells.
- Do not include PowerShell blocks, bash blocks, shell command blocks, command lists, or command dumps anywhere in a chat formal report. Validation evidence should be a short status only, such as `验证通过` or `Validation passed`.
- Put only short evidence notes after the table. Chinese reports use `依据与验证`; English reports use `Evidence and Validation`.
- Always use the exact table header `| 类型和状态 | 内容 |` for Chinese reports or `| Item/Status | Content |` for English reports. Legacy slash headers, short Chinese headers, mixed status headers, field/content headers, and custom headers are invalid.
- Do not use `<nobr>`, HTML wrappers, invisible characters, or spacing tricks in formal-report tables.
- Keep validation, gate, or checkpoint-like information in the `验证` / `Gate` row for generic reports or in the evidence section outside the table. The table row set excludes `Checkpoint`.

## Post-Install Startup Report

After installing OpenACCP as a skill + workflow kit, produce a formal report automatically as part of startup.

The startup formal report states:

- what was installed or loaded,
- whether validation passed or failed,
- whether the OpenACCP skills are available,
- whether `openaccp` and `openaccp-validate` are available,
- current startup state,
- gaps,
- next step.

The startup report keeps validation commands, shell snippets, PowerShell snippets, local executable paths, skill install paths, and temporary install directories out of chat. The `验证` or `Gate` row says only whether validation passed or failed. If details are needed, use one short sentence outside the table, not a command block.

The next step must ask for exactly these setup inputs in numbered lines:

1. Current project facts input: source pack, PRD, spec, design document, facts folder, or uploaded project materials.
2. Working directory / local agent coordination workbench: where OpenACCP may write `.openaccp`, launchers, coordination files, reports, handoffs, CARD registry, and source-pack artifacts.
3. `repo path` / product code repository path: the actual product Git repo. Primary uses it to infer Git branch, base branch, writable scope, test entrypoints, worktree policy, and which files scoped workers may edit.

If no prepared facts path exists, ask the user to upload or attach the project materials. Uploaded materials become candidate facts. If the working directory and repo path are the same, the user can say so. If no product repo exists yet, the user should say `no repo yet`. Preferred language is optional; if omitted, continue in the current conversation language.

End the post-install report with human-readable wording, not a vague checklist. The meaning is:

```text
OpenACCP is installed and validated. Please send:

1. 当前项目事实源：source pack、PRD、spec、设计文档、facts 文件夹，或者直接上传项目材料。
2. 工作路径 / 本地 agent 编排工作台：这里会放 `.openaccp`、launchers、coordination、reports、handoffs、CARD registry、source pack 等协调文件。
3. `repo path` / 产品代码仓库路径：真正的产品 Git repo。Primary 会用它判断当前 Git branch、base branch、可写范围、测试入口、worktree policy，以及哪些文件可以交给 worker 改。

如果工作路径和 repo path 是同一个目录，直接说明即可。如果现在还没有产品 repo，请写 `no repo yet`。如果你想固定后续回复语言，也可以一起告诉我；不写的话我继续使用当前语言。
```

After the user provides those setup inputs, the startup agent writes one full Primary prompt record to the working directory. It starts Primary directly when the agent tool supports agent/thread spawn or one-click launch. If direct dispatch is unavailable, it returns one short copyable Primary launcher as a fenced `prompt` block and clearly labels it as manual fallback.

## Next Step Rule

The next step in a formal report must be actionable.

For Primary, name the decision, dispatch, consume, or closure action Primary should perform.

For Frontier, include a Frontier-owned B0/B1/B2 action when any safe lane-local work remains. Return to Primary only when the report includes closure proof showing every visible remaining gap is final-authority-only or explicitly out.

Avoid a next step that only says "wait". If waiting is unavoidable, name what evidence or user fact is missing and what prepared packet will be used when it arrives.

## Required Human Ending

Every formal report must end with a short human-readable section named `Recommended Next Step` for English or `下一步建议` for Chinese.

This section is outside the table. It should say the practical current situation and the next action in plain language:

- If the user needs to do something, name the exact path, fact, approval, or manual fallback thread action.
- If no user action is needed, say that no human action is needed and name the next Primary-owned or Frontier-owned action.
- Do not end with validation details, command output, file lists, or links alone.
