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

The next step must ask for:

- your working directory, which is required,
- your current source pack, PRD, spec, or facts path,
- your preferred language for future Primary, Frontier, worker, reviewer, and discovery replies.

If the user does not have a prepared facts path, the agent may ask the user to upload or attach the project materials. The working directory is still mandatory because the launchers need a concrete place where work can happen.

Use plain human-readable wording for the final ask. For example:

```text
OpenACCP is installed and validated. To build a useful Primary launcher, send one clear working directory. This is required. Also send your source pack, PRD, spec, design document, or facts path. If you have rough project materials instead of a clean facts path, upload or attach them and I will treat them as candidate facts while organizing the source pack. Please also tell me your preferred language; if you omit it, I will keep using your current language.
```

## After The User Provides Project Inputs

After the user provides a working directory, facts input, and preferred language or language fallback, the agent returns:

- one Primary Orchestrator launcher.

Use:

- `templates/primary-orchestrator-launcher.md`
- `templates/short-chat-launcher.md`

The launchers must name:

- role,
- authority level,
- working directory,
- source pack or facts input,
- preferred language,
- product repo path,
- base branch,
- source roots,
- test entrypoints,
- worktree policy,
- writable paths,
- read-only references,
- forbidden paths or side effects,
- validation expectations,
- handoff or report expectations.

The Primary prompt record must also include active closure rules:

- Primary dispatches bounded subagents and consumes evidence until only final-authority or explicitly-out gaps remain.
- Primary must inspect the working directory and facts input before dispatching Frontier.
- Primary must create or refresh `.openaccp/coordination/runtime-boundary.json` before dispatching Frontier. It must resolve or explicitly mark product repo path, base branch, source roots, test entrypoints, worktree policy, writable paths, read-only paths, forbidden paths, data risk, side-effect policy, and `b2DispatchGate`.
- Primary must create or refresh current manifest, source status registry, lane registry, decision registry, sequence registry, and CARD/task-card candidates.
- If product repo path, base branch, source roots, test entrypoints, or worktree policy are missing, Primary asks the user in the Primary report and continues B0/B1 packaging only. Primary keeps unresolved runtime questions out of Frontier immediate blockers. Frontier lanes launched before product-write readiness use `coordination_only` or `read_only_review`.
- Primary must cut enough CARDs for the actual project domains. Normal or medium/high-complexity product work usually needs 10-20 project-level CARDs before Frontier dispatch; fewer is acceptable only for a genuinely small project with an explicit reason.
- Primary must scan facts for product workflow, backend/API, data/storage, frontend/UI, desktop/mobile/native/Electron/Tauri surfaces, integrations, auth/security/privacy, migration, testing/QA, observability/CI, docs/release/ops, and any project-specific domain. Do not invent a domain that facts do not mention, but if facts mention UI, frontend, Electron, desktop shell, mobile, or another surface, Primary must create CARD coverage for it.
- Primary must decide Frontier lanes dynamically based on project complexity, CARD grouping, risk, and parallel safety. Default to at least two Frontier lanes when two safe independent CARD clusters exist; one Frontier requires a small-project, single-safe-lane, or explicit-user-request reason. Medium/high projects normally receive two to five Frontiers. More than five requires explicit user approval.
- Primary must grant each Frontier B2 lane-local authority by default unless a narrower authority is explicitly safer.

The full launcher prompt records must be written to disk first. Use the user's working directory, preferably:

```text
<working-directory>/.openaccp/launchers/
```

Write exactly one full Primary prompt record. It must include a stable Prompt ID, role, B3 authority, inputs, preferred language, scope, forbidden effects, validation expectations, output expectations, workspace review duties, CARD creation duties, and dynamic Frontier dispatch rules.

If the working directory is not writable, do not fall back to pasting full prompt bodies into chat. Stop and ask the user for a writable working directory or explicit permission to use another safe path.

Recommended file names:

- `<working-directory>/.openaccp/launchers/primary-orchestrator.prompt.md`
- `<working-directory>/.openaccp/launchers/primary-orchestrator.short.md`

The chat output must not contain the full prompt body. Chat must contain one short copyable Primary launcher that points to the on-disk prompt record.

Writing the `.short.md` file is required for audit, but it does not replace the chat launcher. The agent must read or construct the short launcher and paste its exact contents into the Codex chat as a fenced `prompt` block. A file link, file attachment, file list, or `Get-Content` command is not a usable launcher for a new Codex user.

Use this interaction shape:

1. Tell the user which full Primary prompt record file was written.
2. Tell the user: `Create a new thread from the left sidebar, paste the short Primary launcher below, and start that thread.`
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

1. Read the prompt record, working directory, facts input, and preferred language.
2. Create or refresh runtime boundary: product repo path, base branch, source roots, test entrypoints, worktree policy, writable/read-only/forbidden paths, data risk, side-effect policy, and `b2DispatchGate`.
3. Explain in the preferred language what B0/B1/B2/B3 mean for this project.
4. Inspect the working directory and facts input.
5. Create or refresh OpenACCP current manifest, source status registry, invalid or deprecated sources, decision registry, sequence registry, lane registry, and CARD/task-card candidates.
6. Create CARDs before Frontier dispatch. For normal or medium/high-complexity product work, prefer 10-20 project-level CARDs. Use fewer only for genuinely small projects and record why.
7. Scan the facts for domain coverage before finalizing CARDs: product workflow, backend/API, data/storage, frontend/UI, desktop/mobile/native/Electron/Tauri surfaces, integrations, auth/security/privacy, migration, testing/QA, observability/CI, docs/release/ops, and project-specific domains. Create CARDs only for domains present in the facts, but never miss a domain the facts explicitly name.
8. Group CARDs into Frontier lanes based on complexity, risk, dependencies, and parallel safety. Default to at least two Frontier lanes when two safe independent CARD clusters exist; use one only for small/single-lane/user-request cases with a stated reason; use two to five for medium/high complexity when parallel work is useful.
9. Write full Frontier prompt records to disk only for the lanes it decides are useful.
10. Validate each full Frontier prompt record with the `frontier-contract` ruleset before returning a short Frontier launcher.
11. Write each short Frontier launcher to disk for audit, then print each selected Frontier launcher in its own fenced `prompt` block in chat.

When Primary returns Frontier launchers, chat includes the preferred-language left-sidebar thread instruction and one copyable `prompt` block for each selected Frontier. If four Frontiers are selected, chat shows four copyable `prompt` blocks.

Frontier lanes default to B2 lane-local authority. A B2 Frontier may actively run B0 discovery, B1 packaging, B2 scoped worker/reviewer/subagent dispatch, child handoff consume, provisional lane evidence synthesis, and closure proof inside its assigned lane. B3 final acceptance, waiver, merge, release, publication, and cross-lane final decisions remain with Primary or the human owner.

Inside a Frontier lane, worker/reviewer/discovery/validation child work is dispatched by that Frontier through available subagent or delegation tools. Human-opened child worker or reviewer threads are fallback paths. If direct dispatch is unavailable or unsafe, the Frontier may return a short `Fallback launcher`, but it must write that launcher to disk, print it in chat as a fenced `prompt` block, explain why direct dispatch was unavailable or unsafe, and give one exact recommended next step.

Primary and Frontier maintain machine-readable coordination state:

- `runtime-boundary` records repo path, base branch, source roots, test entrypoints, worktree policy, writable/read-only/forbidden paths, side effects, data risk, and `b2DispatchGate`.
- `current-manifest` records current facts, invalid or deprecated sources, active lanes, superseded prompts, cancelled prompts, registry refs, and latest consume refs.
- `sequence-registry` records Prompt IDs, Response IDs, handoffs, consume results, active cards, active lanes, lifecycle status, and current/latest pointers.
- `lane-registry` records Primary/Frontier lanes, assigned CARDs, `child-ledgers/<lane-id>.json` refs, `frontier-closures/<lane-id>.json` refs, and return-gate status.
- `child-ledger` records child worker/reviewer/discovery/validation lifecycle, handoff status, consume status, and remaining risk.
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
