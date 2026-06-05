# Formal Report

schemaVersion: openacp-status-report.v1
artifactType: formal-report
status: draft

Response ID:
Response log path:

| Item/Status | Content |
|---|---|
| Changed | |
| Progress | Include a numeric estimate. |
| Gate | |
| Area | |
| Goal | |
| Gaps | |
| Next | |

## Role-Aware Rows

Use these rows for a Chinese Primary report:

| 类型/状态 | 内容 |
|---|---|
| 做了什么　　 | |
| 总体进度　　 | Include a numeric estimate. |
| Frontier | |
| 目标　　　　 | |
| 缺口　　　　 | |
| 下一步　　　 | |

Use these rows for a Chinese post-install or generic startup report:

| 类型/状态 | 内容 |
|---|---|
| 做了什么　　 | |
| 总体进度　　 | Include a numeric estimate. |
| 验证　　　　 | 验证通过 / 验证失败。 |
| 范围　　　　 | |
| 目标　　　　 | |
| 缺口　　　　 | |
| 下一步　　　 | |

Use these rows for a Chinese Frontier report:

| 类型/状态 | 内容 |
|---|---|
| 做了什么　　 | |
| 总体进度　　 | Include a numeric estimate. |
| Lane | |
| 目标　　　　 | |
| 缺口　　　　 | |
| 下一步　　　 | |

## Evidence and Validation

- Validation:
- Artifacts:
- Notes:

## Recommended Next Step

Explain what the human should do now. If no human action is needed, say that plainly and name the next Primary-owned or Frontier-owned action.

Do not claim final states without final-authority evidence.

Keep the table cells short. Put long paths, URLs, commit hashes, validation output, and evidence lists in `Evidence and Validation` instead of the table.

Do not include shell command blocks, PowerShell blocks, bash blocks, command dumps, executable paths, or local install paths in a chat formal report. For validation, write only a short status such as `验证通过` or `Validation passed`.

For Chinese reports, name the evidence section `依据与验证` and the final section `下一步建议`. For English reports, use `Evidence and Validation` and `Recommended Next Step`.

For Chinese chat reports, keep the header `类型/状态` and append full-width ideographic spaces to Chinese row labels in the first column. This preserves the requested visible labels while preventing the chat UI from compressing the left column.

## Post-Install Startup Note

When this report is used immediately after installing OpenACP, the `Next` cell must ask for a required working directory, a facts input, and the user's preferred language. The facts input can be a source pack, PRD, spec, design document, facts path, or uploaded project materials. Do not end with only "send paths"; explain that the working directory is required because launchers need a concrete project workspace, that the facts input is needed so the launcher can start from current evidence, and that the language choice keeps all later Primary, Frontier, worker, reviewer, and discovery replies consistent.

## Mini Example

| Item/Status | Content |
|---|---|
| Changed | A worker handoff and reviewer report are ready for final consume. |
| Progress | 70%. The work is implemented and reviewed, but final authority has not accepted it. |
| Gate | Reviewed evidence exists; final consume is pending. |
| Area | Handoff review. |
| Goal | Decide whether the reviewed evidence can be accepted. |
| Gaps | The final consume decision and release checks are still pending. |
| Next | Primary or the human owner should inspect the reviewed evidence and decide accept, amend, or reject. |
