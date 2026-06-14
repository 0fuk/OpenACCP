# Codex And Claude Code Install Startup

This is the default OpenACCP startup path for an agent that can install skills or load workflow instructions.

## User Prompt

Ask Codex/Claude Code:

```text
Install https://github.com/0fuk/OpenACCP as a skill + workflow kit, then follow the README startup flow.
```

## Agent Startup Contract

The startup agent performs this setup:

1. Clone or open `https://github.com/0fuk/OpenACCP`.
2. Install or load all OpenACCP skills from `skills/`.
3. Install the Python workflow kit with `python -m pip install -e .`.
4. Run validation:
   - `python tools/openaccp_validate_selftest.py`
   - `python tools/openaccp_validate.py --artifact . --ruleset public-package --strict`
   - `openaccp --version`
   - `openaccp-validate --version`
5. Read:
   - `README.md`
   - `docs/getting-started.md`
   - `docs/role-model.md`
   - `docs/authority-boundary.md`
   - `docs/validator.md`
   - `skills/primary-orchestrator-openaccp/SKILL.md`
   - `skills/frontier-orchestrator-openaccp/SKILL.md`
   - `skills/formal-report-openaccp/SKILL.md`
   - `templates/primary-orchestrator-launcher.md`
   - `templates/frontier-orchestrator-launcher.md`
6. Produce a formal report automatically after installation and validation.
7. Ask the user for the real project inputs.

## Skills To Install Or Load

- `skills/primary-orchestrator-openaccp/`
- `skills/frontier-orchestrator-openaccp/`
- `skills/worker-openaccp/`
- `skills/reviewer-openaccp/`
- `skills/formal-report-openaccp/`
- `skills/human-explain-openaccp/`
- `skills/handoff-consume-openaccp/`
- `skills/source-pack-openaccp/`
- `skills/bootstrap-openaccp/`
- `skills/discovery-openaccp/`
- `skills/validator-openaccp/`

## Automatic Formal Report

The formal report is not a separate user command. It is the required post-install output.

The report includes:

- what was installed or loaded,
- whether validation passed or failed,
- whether OpenACCP skills are available,
- whether the CLI is available,
- current startup state,
- gaps,
- next step.

For chat readability, keep the report table short. Put long paths, commit hashes, URLs, and validation logs outside table cells.

The startup report must use `formal-report-openaccp` rows. For a Chinese post-install report, use this exact table shape:

```text
| 类型和状态 | 内容 |
|---|---|
| 做了什么 | |
| 总体进度 | |
| 验证 | 验证通过 / 验证失败。 |
| 范围 | |
| 目标 | |
| 缺口 | |
| 下一步 | |
```

Use only the OpenACCP report header: `| 类型和状态 | 内容 |` for Chinese or `| Item/Status | Content |` for English. Keep row labels to the standard OpenACCP set: `做了什么`, `总体进度`, `验证`, `范围`, `目标`, `缺口`, `下一步` for Chinese startup reports. Do not use `<nobr>`, HTML wrappers, invisible characters, or spacing tricks.

Keep PowerShell blocks, bash blocks, command lists, executable paths, local install paths, and temporary install directories out of the user-facing post-install report. The `验证` row simply says `验证通过` or `验证失败`; if a note is useful, write one short natural-language sentence after the table.

The next step must ask for exactly these three project inputs in numbered lines:

1. `Facts input / project facts`: source pack, PRD, spec, design document, facts folder, or uploaded project materials.
2. `Working directory / local agent coordination workbench`: where OpenACCP may write `.openaccp`, `launchers`, `coordination`, `reports`, `handoffs`, the CARD registry, and the source pack.
3. `Repo path / product code repository path`: the actual product Git repository. Primary uses it to infer the Git branch, base branch, writable scope, test entrypoints, worktree policy, and worker-editable files.

If the user does not have a prepared facts path, ask the user to upload or attach project materials. If the working directory and repo path are the same, the user can say that. If no product repo exists yet, the user should explicitly say `no repo yet`; Primary then stays in planning, packaging, and readiness mode. Preferred language is optional; when omitted, continue in the current conversation language.

Use plain human-readable wording for the final ask. For example:

```text
OpenACCP is installed and validated. Please send:

1. Facts input / project facts: a source pack, PRD, spec, design document, facts folder, or uploaded files.
2. Working directory / local agent coordination workbench: the folder where I can write `.openaccp`, launchers, coordination files, reports, handoffs, CARD registry, and source-pack artifacts.
3. Repo path / product code repository path: the real product Git repo. Primary will inspect it to infer branch, base branch, writable scope, test entrypoints, worktree policy, and worker-editable files.

If the working directory and repo path are the same, say so. If there is no repo yet, say `no repo yet`. If you want a specific language for all later replies, include it; otherwise I will keep using the current language.
```

## After The User Provides Project Inputs

After the user provides facts input, working directory, repo path or `no repo yet`, and preferred language or language fallback, the agent returns:

- one Primary Orchestrator launcher.

Use:

- `templates/primary-orchestrator-launcher.md`
- `templates/short-chat-launcher.md`

The launchers must name:

- role,
- authority level,
- facts input,
- working directory,
- product repo path or explicit `no repo yet`,
- preferred language or language fallback,
- Primary runtime identity and notification bridge policy,
- Primary-inferred base branch,
- Primary-inferred source roots,
- Primary-inferred test entrypoints,
- Primary-inferred worktree policy,
- writable paths,
- read-only references,
- forbidden paths or side effects,
- validation expectations,
- handoff or report expectations.

The Primary prompt record must also include active closure rules:

- Primary dispatches bounded subagents and consumes evidence until only final-authority or explicitly-out gaps remain.
- Primary must detect or declare whether it is running in `codex`, `claude-code`, `other`, or `unknown` and record that in runtime boundary before signing Frontier lanes.
- Primary must inspect the facts input, working directory, and repo path before dispatching Frontier.
- Primary must create or refresh `.openaccp/coordination/runtime-boundary.json` before dispatching Frontier. It must take the repo path as the product code entry point, then infer base branch, source roots, test entrypoints, worktree policy, writable paths, read-only paths, forbidden paths, data risk, side-effect policy, and `b2DispatchGate`. It must also record `runtimeIdentity` and `notificationBridge`.
- Primary must create or refresh current manifest, source status registry, lane registry, decision registry, sequence registry, and CARD/task-card candidates.
- If repo path is missing, ambiguous, or explicitly `no repo yet`, Primary asks for repo path or records `no repo yet` and continues B0/B1 packaging/readiness only. For base branch, source roots, test entrypoints, writable scope, and worktree policy, Primary infers first and asks only when inference is ambiguous, risky, or impossible. Primary keeps unresolved runtime questions out of Frontier immediate blockers. Frontier lanes launched before product-write readiness use `coordination_only` or `read_only_review`.
- Primary must cut enough CARDs for the actual project domains. Normal or medium/high-complexity product work usually needs 10-20 project-level CARDs before Frontier dispatch; fewer is acceptable only for a genuinely small project with an explicit reason.
- Primary must scan facts for product workflow, backend/API, data/storage, frontend/UI, desktop/mobile/native/Electron/Tauri surfaces, integrations, auth/security/privacy, migration, testing/QA, observability/CI, docs/release/ops, and any project-specific domain. Do not invent a domain that facts do not mention, but if facts mention UI, frontend, Electron, desktop shell, mobile, or another surface, Primary must create CARD coverage for it.
- Primary must decide Frontier lanes dynamically based on project complexity, CARD grouping, risk, and parallel safety. Default to at least two Frontier lanes when two safe independent CARD clusters exist; one Frontier requires a small-project, single-safe-lane, or explicit-user-request reason. Medium/high projects normally receive two to five Frontiers. More than five requires explicit user approval.
- Primary must grant each Frontier B2 lane-local authority by default unless a narrower authority is explicitly safer.
- Primary must record each Frontier runtime in `lane-registry`. If a Frontier runs in a different runtime from Primary, the lane must include `notificationBridgePolicy` with `busyPolicy: queue_until_safe_checkpoint`.

The full launcher prompt records must be written to disk first. Use the user's working directory, preferably:

```text
<working-directory>/.openaccp/launchers/
```

Write exactly one full Primary prompt record. It must include a stable Prompt ID, role, B3 authority, inputs, preferred language, scope, forbidden effects, validation expectations, output expectations, workspace review duties, CARD creation duties, and dynamic Frontier dispatch rules.

If the working directory is not writable, do not fall back to pasting full prompt bodies into chat. Stop and ask the user for a writable working directory or explicit permission to use another safe path.

Recommended file names:

- `<working-directory>/.openaccp/launchers/primary-orchestrator.prompt.md`
- `<working-directory>/.openaccp/launchers/primary-orchestrator.short.md`

The chat output must not contain the full prompt body. When the runtime supports agent/thread spawn, dispatch the Primary directly from the short launcher seed and record `dispatchChannel: agent_thread_spawn`. When direct dispatch is unavailable, chat contains one short copyable Primary launcher that points to the on-disk prompt record and is clearly labeled as the manual fallback.

Writing the `.short.md` file is required for audit. For `agent_thread_spawn` or `one_click`, the file is the dispatch seed and no human copy/paste is required. For `manual_paste`, the agent must read or construct the short launcher and paste its exact contents into the chat as a fenced `prompt` block. A file link, file attachment, file list, or `Get-Content` command is not a usable manual fallback.

Use this interaction shape for same-runtime direct dispatch:

1. Tell the user which full Primary prompt record file was written.
2. State `Dispatch channel: agent_thread_spawn` or `Dispatch channel: one_click`.
3. State `Runtime relation: same_runtime` when the output is launching a child or Frontier lane.
4. State a successful result line, such as `Spawn result: dispatched` for `agent_thread_spawn` or `Launch result: started` for `one_click`. If dispatch failed, switch to manual fallback instead of claiming direct dispatch.

Use this interaction shape for cross-runtime bridge dispatch:

1. Tell the user which full Frontier prompt record file was written.
2. State `Dispatch channel: runtime_bridge`.
3. State `Runtime relation: cross_runtime`.
4. State a successful bridge result line such as `Bridge result: queued`.
5. State the bridge event id or path, such as `Bridge event: .openaccp/coordination/bridge-events.jsonl#<event-id>`.

Use this interaction shape for manual fallback:

1. Tell the user which full Primary prompt record file was written.
2. Tell the user: `Direct dispatch is unavailable here. Create a new thread from the left sidebar, paste the short Primary launcher below, and start that thread.`
3. Print the exact short Primary launcher in a fenced `prompt` block.

The short chat launcher contains only:

- a short title and purpose,
- the full prompt record path,
- the Prompt ID,
- the preferred language or language fallback,
- an explicit UTF-8 read requirement,
- a stop rule if the file cannot be read cleanly, the Prompt ID is missing, or the text appears corrupted.

Launcher titles use one stable grammar. The first non-empty line is plain text, not a Markdown heading:

- `<Project> - Primary Orchestrator - <Short Task>`
- `<Project> - Frontier 01 - <Short Task>` through `<Project> - Frontier 05 - <Short Task>`
- `<Project> - F01 Worker - <Short Task>` through `<Project> - F05 Worker - <Short Task>` for child fallback launchers owned by a Frontier lane
- `<Project> - PO Worker - <Short Task>` for child fallback launchers owned by Primary

Use numeric Frontier slots. Do not use `Frontier A`, `Frontier B`, or a generic `Frontier Launcher` heading.

Example short chat launcher:

```prompt
<Project> - Primary Orchestrator - Startup
Purpose: start the Primary coordination thread.

Read and execute this OpenACCP prompt record:
- Prompt Record: <working-directory>/.openaccp/launchers/primary-orchestrator.prompt.md
- Prompt ID: openaccp-primary-startup
- Preferred language: <user-preferred-or-current-language>

Hard requirements:
1. Read the prompt record explicitly as UTF-8.
2. Execute only the named Prompt ID.
3. If the file cannot be read cleanly, the Prompt ID is missing, or the text appears corrupted, stop and report launcher-read failure.
```

If the user has no source pack, PRD, spec, facts path, or uploaded project materials, do not invent one. Offer the bootstrap path and use `openaccp init` only after the user explicitly approves creating starter artifacts.

## Primary Runtime Dispatch

The Primary thread, not the install startup thread, decides Frontier dispatch.

Primary must first:

1. Read the prompt record, facts input, working directory, repo path, and preferred language.
2. Detect or declare the Primary runtime and record `runtimeIdentity`.
3. Create or refresh runtime boundary: Primary runtime identity, notification bridge policy, repo path, inferred base branch, source roots, test entrypoints, worktree policy, writable/read-only/forbidden paths, data risk, side-effect policy, and `b2DispatchGate`.
4. Explain in the preferred language what B0/B1/B2/B3 mean for this project.
5. Inspect the working directory and facts input.
6. Create or refresh OpenACCP current manifest, source status registry, invalid or deprecated sources, decision registry, sequence registry, lane registry, and CARD/task-card candidates.
7. Create CARDs before Frontier dispatch. For normal or medium/high-complexity product work, prefer 10-20 project-level CARDs. Use fewer only for genuinely small projects and record why.
8. Scan the facts for domain coverage before finalizing CARDs: product workflow, backend/API, data/storage, frontend/UI, desktop/mobile/native/Electron/Tauri surfaces, integrations, auth/security/privacy, migration, testing/QA, observability/CI, docs/release/ops, and project-specific domains. Create CARDs only for domains present in the facts, but never miss a domain the facts explicitly name.
9. Group CARDs into Frontier lanes based on complexity, risk, dependencies, and parallel safety. Default to at least two Frontier lanes when two safe independent CARD clusters exist; use one only for small/single-lane/user-request cases with a stated reason; use two to five for medium/high complexity when parallel work is useful.
10. Declare each selected Frontier runtime, runtime relation, dispatch channel, and notification bridge policy in lane registry.
11. Write full Frontier prompt records to disk only for the lanes it decides are useful.
12. Validate each full Frontier prompt record with the `frontier-contract` ruleset before direct dispatch or manual fallback.
13. Write each short Frontier launcher to disk for audit, then dispatch each selected Frontier directly when the runtime supports it. If direct dispatch is unavailable, print each selected Frontier launcher in its own fenced `prompt` block in chat as manual fallback.

When Primary dispatches same-runtime Frontier lanes directly, the response records `dispatchChannel: agent_thread_spawn` or `dispatchChannel: one_click`, `Runtime relation: same_runtime`, and the lane IDs that were started. When Primary dispatches a cross-runtime Frontier, the response records `dispatchChannel: runtime_bridge`, `Runtime relation: cross_runtime`, `Bridge result`, and the bridge event locator. When no direct or bridge channel is available, the response records `dispatchChannel: manual_paste`, explains why fallback is needed, and includes the preferred-language left-sidebar thread instruction plus one copyable `prompt` block for each selected Frontier.

Frontier lanes default to B2 lane-local authority. A B2 Frontier may actively run B0 discovery, B1 packaging, B2 scoped worker/reviewer/subagent dispatch, child handoff consume, provisional lane evidence synthesis, and closure proof inside its assigned lane. B3 decisions go to Primary only when listed in Primary's `delegatedFinalAuthority`; production launch, public publication, customer-visible release, and risk waiver stay with the human owner by default.

Inside a Frontier lane, worker/reviewer/discovery/validation child work is dispatched by that Frontier through available subagent or delegation tools. Human-opened child worker or reviewer threads are fallback paths. If direct dispatch is unavailable or unsafe, the Frontier may return a short `Fallback launcher`, but it must write that launcher to disk, print it in chat as a fenced `prompt` block, explain why direct dispatch was unavailable or unsafe, and give one exact recommended next step.

Returned child evidence follows the return event protocol. If a child returns in another runtime, the child ledger records `parent_consume_pending`, `notificationBridgeRef`, and a wake state such as `queued_for_parent`; `openaccp notify-return --child-ledger <path> --event-log <working-directory>/.openaccp/coordination/bridge-events.jsonl` appends the parent consume event. Primary can also wake a cross-runtime Frontier with `openaccp notify-dispatch --lane-registry <path> --lane-id <lane> --event-log <working-directory>/.openaccp/coordination/bridge-events.jsonl`. The bridge wakes or queues lifecycle work while final authority stays with Primary or the human owner.

Primary and Frontier maintain machine-readable coordination state:

- `runtime-boundary` records Primary runtime identity, notification bridge policy, repo path, inferred base branch, source roots, test entrypoints, worktree policy, writable/read-only/forbidden paths, side effects, data risk, inference evidence, ambiguity notes, and `b2DispatchGate`.
- `current-manifest` records current facts, invalid or deprecated sources, active lanes, superseded prompts, cancelled prompts, registry refs, and latest consume refs.
- `sequence-registry` records Prompt IDs, Response IDs, handoffs, consume results, active cards, active lanes, lifecycle status, and current/latest pointers.
- `lane-registry` records Primary/Frontier lanes, selected runtime, runtime relation, notification bridge policy, assigned CARDs, `child-ledgers/<lane-id>.json` refs, `frontier-closures/<lane-id>.json` refs, and return-gate status.
- `child-ledger` records child worker/reviewer/discovery/validation lifecycle, runtime relation, return event status, wake status, handoff status, consume status, and remaining risk.
- `source-status-registry` records current, reference, deprecated, invalid, and unknown sources with reasons.
- `decision-registry` records owner questions, Primary decisions, waivers, out-of-scope decisions, blockers, and safe defaults.
- `frontier-closure` proves whether a Frontier can keep working, close, or return to Primary.
- `consume-result` records what handoff or review evidence has been provisionally or finally consumed.
- `machine-summary` gives compact locators for worker, reviewer, discovery, Frontier, or Primary output.

Validate launcher-bearing response logs with:

```bash
openaccp-validate --artifact <response-log-with-launcher.md> --ruleset launcher-output --strict
```

## Skill Install Notes

For Codex, install the directories under `skills/` as local skills if skill installation is available. If native skill installation is unavailable, load the relevant `SKILL.md` files as workflow instructions for the current session.

For Claude Code or another coding agent, treat `skills/*/SKILL.md` as the workflow instructions to load before starting orchestration.
