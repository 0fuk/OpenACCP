# Codex And Claude Code Install Startup

This is the default OpenACP startup path for an agent that can install skills or load workflow instructions.

## User Prompt

Ask Codex/Claude Code:

```text
Install https://github.com/0fuk/OpenACP as a skill + workflow kit, then follow the README startup flow.
```

## Agent Startup Contract

The agent should:

1. Clone or open `https://github.com/0fuk/OpenACP`.
2. Install or load all OpenACP skills from `skills/`.
3. Install the Python workflow kit with `python -m pip install -e .`.
4. Run validation:
   - `python tools/openacp_validate_selftest.py`
   - `python tools/openacp_validate.py --artifact . --ruleset public-package --strict`
   - `openacp --version`
   - `openacp-validate --version`
5. Read:
   - `README.md`
   - `docs/getting-started.md`
   - `docs/role-model.md`
   - `docs/authority-boundary.md`
   - `docs/validator.md`
   - `skills/primary-orchestrator-openacp/SKILL.md`
   - `skills/frontier-orchestrator-openacp/SKILL.md`
   - `skills/formal-report-openacp/SKILL.md`
   - `templates/primary-orchestrator-launcher.md`
   - `templates/frontier-orchestrator-launcher.md`
6. Produce a formal report automatically after installation and validation.
7. Ask the user for the real project inputs.

## Skills To Install Or Load

- `skills/primary-orchestrator-openacp/`
- `skills/frontier-orchestrator-openacp/`
- `skills/worker-openacp/`
- `skills/reviewer-openacp/`
- `skills/formal-report-openacp/`
- `skills/human-explain-openacp/`
- `skills/handoff-consume-openacp/`
- `skills/source-pack-openacp/`
- `skills/bootstrap-openacp/`
- `skills/discovery-openacp/`
- `skills/validator-openacp/`

## Automatic Formal Report

The formal report is not a separate user command. It is the required post-install output.

The report should include:

- what was installed or loaded,
- which validation commands passed or failed,
- whether OpenACP skills are available,
- whether the CLI is available,
- current startup state,
- gaps,
- next step.

For chat readability, keep the report table short. Long paths, commands, commit hashes, URLs, and validation logs should go below the table in `Evidence Details`, not inside table cells.

The next step must ask for:

- your working directory, which is required,
- your current source pack, PRD, spec, or facts path,
- your preferred language for future Primary, Frontier, worker, reviewer, and discovery replies.

If the user does not have a prepared facts path, the agent may ask the user to upload or attach the project materials. The working directory is still mandatory because the launchers need a concrete place where work can happen.

Use plain human-readable wording for the final ask. For example:

```text
I have installed and validated OpenACP, but I cannot build a useful Primary launcher yet because I do not know where your project work should happen, which materials count as current facts, or which language you want future agents to use. Please send me one clear working directory. This is required. Also send your source pack, PRD, spec, design document, or facts path. If you do not have a clean facts path yet, you can upload the project materials instead and I will treat them as candidate facts, but I still need the working directory. Please also tell me your preferred language; if you do not specify one, I will keep using your current language.
```

## After The User Provides Project Inputs

After the user provides a working directory, facts input, and preferred language or language fallback, the agent should return:

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
- writable paths,
- read-only references,
- forbidden paths or side effects,
- validation expectations,
- handoff or report expectations.

The Primary prompt record must also include active closure rules:

- Primary should dispatch bounded subagents and consume evidence until only final-authority or explicitly-out gaps remain.
- Primary must inspect the working directory and facts input before dispatching Frontier.
- Primary must create or refresh current manifest, source status, sequence registry, and CARD/task-card candidates.
- Primary must cut enough CARDs for the actual project domains. Normal or medium/high-complexity product work usually needs 10-20 project-level CARDs before Frontier dispatch; fewer is acceptable only for a genuinely small project with an explicit reason.
- Primary must scan facts for product workflow, backend/API, data/storage, frontend/UI, desktop/mobile/native/Electron/Tauri surfaces, integrations, auth/security/privacy, migration, testing/QA, observability/CI, docs/release/ops, and any project-specific domain. Do not invent a domain that facts do not mention, but if facts mention UI, frontend, Electron, desktop shell, mobile, or another surface, Primary must create CARD coverage for it.
- Primary must decide Frontier lanes dynamically based on project complexity, CARD grouping, risk, and parallel safety. Default to at least two Frontier lanes when two safe independent CARD clusters exist; one Frontier requires a small-project, single-safe-lane, or explicit-user-request reason. Medium/high projects should normally receive two to five Frontiers. More than five requires explicit user approval.
- Primary must grant each Frontier B2 lane-local authority by default unless a narrower authority is explicitly safer.

The full launcher prompt records must be written to disk first. Use the user's working directory, preferably:

```text
<working-directory>/.openacp/launchers/
```

Write exactly one full Primary prompt record. It must include a stable Prompt ID, role, B3 authority, inputs, preferred language, scope, forbidden effects, validation expectations, output expectations, workspace review duties, CARD creation duties, and dynamic Frontier dispatch rules.

If the working directory is not writable, do not fall back to pasting full prompt bodies into chat. Stop and ask the user for a writable working directory or explicit permission to use another safe path.

Recommended file names:

- `<working-directory>/.openacp/launchers/primary-orchestrator.prompt.md`
- `<working-directory>/.openacp/launchers/primary-orchestrator.short.md`

The chat output must not contain the full prompt body. Chat must contain one short copyable Primary launcher that points to the on-disk prompt record.

Writing the `.short.md` file is required for audit, but it does not replace the chat launcher. The agent must read or construct the short launcher and paste its exact contents into the Codex chat as a fenced `prompt` block. A file link, file attachment, file list, or `Get-Content` command is not a usable launcher for a new Codex user.

Use this interaction shape:

1. Tell the user which full Primary prompt record file was written.
2. Tell the user: `Create a new thread from the left sidebar, paste the short Primary launcher below, and start that thread.`
3. Print the exact short Primary launcher in a fenced `prompt` block.

The short chat launcher should contain only:

- a short title and purpose,
- the full prompt record path,
- the Prompt ID,
- the preferred language or language fallback,
- an explicit UTF-8 read requirement,
- a stop rule if the file cannot be read cleanly, the Prompt ID is missing, or the text appears corrupted.

Example short chat launcher:

```prompt
<Project> - Primary Orchestrator - Startup
Purpose: start the Primary coordination thread.

Read and execute this OpenACP prompt record:
- Prompt Record: <working-directory>/.openacp/launchers/primary-orchestrator.prompt.md
- Prompt ID: openacp-primary-startup
- Preferred language: <user-preferred-or-current-language>

Hard requirements:
1. Read the prompt record explicitly as UTF-8.
2. Execute only the named Prompt ID.
3. If the file cannot be read cleanly, the Prompt ID is missing, or the text appears corrupted, stop and report launcher-read failure.
```

If the user has no source pack, PRD, spec, facts path, or uploaded project materials, do not invent one. Offer the bootstrap path and use `openacp init` only after the user explicitly approves creating starter artifacts.

## Primary Runtime Dispatch

The Primary thread, not the install startup thread, decides Frontier dispatch.

Primary must first:

1. Read the prompt record, working directory, facts input, and preferred language.
2. Explain in the preferred language what B0/B1/B2/B3 mean for this project.
3. Inspect the working directory and facts input.
4. Create or refresh OpenACP current manifest, source status, invalid or deprecated sources, sequence registry, and CARD/task-card candidates.
5. Create CARDs before Frontier dispatch. For normal or medium/high-complexity product work, prefer 10-20 project-level CARDs. Use fewer only for genuinely small projects and record why.
6. Scan the facts for domain coverage before finalizing CARDs: product workflow, backend/API, data/storage, frontend/UI, desktop/mobile/native/Electron/Tauri surfaces, integrations, auth/security/privacy, migration, testing/QA, observability/CI, docs/release/ops, and project-specific domains. Create CARDs only for domains present in the facts, but never miss a domain the facts explicitly name.
7. Group CARDs into Frontier lanes based on complexity, risk, dependencies, and parallel safety. Default to at least two Frontier lanes when two safe independent CARD clusters exist; use one only for small/single-lane/user-request cases with a stated reason; use two to five for medium/high complexity when parallel work is useful.
8. Write full Frontier prompt records to disk only for the lanes it decides are useful.
9. Validate each full Frontier prompt record with the `frontier-contract` ruleset before returning a short Frontier launcher.
10. Write each short Frontier launcher to disk for audit, then print each selected Frontier launcher in its own fenced `prompt` block in chat.

When Primary returns Frontier launchers, it must not return only links to `.short.md` files. It should say, in the preferred language, which new left-sidebar thread each prompt block belongs in, then show the copyable prompt block. If four Frontiers are selected, there should be four copyable `prompt` blocks, not just four file links.

Frontier lanes should default to B2 lane-local authority. A B2 Frontier may actively run B0 discovery, B1 packaging, B2 scoped worker/reviewer/subagent dispatch, child handoff consume, provisional lane evidence synthesis, and closure proof inside its assigned lane. Frontier must not perform B3 final acceptance, waiver, merge, release, publication, or cross-lane final decisions.

Inside a Frontier lane, worker/reviewer/discovery/validation child work should be dispatched by that Frontier through available subagent or delegation tools. Do not make the human open child worker or reviewer threads by default. If direct dispatch is unavailable or unsafe, the Frontier may return a short `Fallback launcher`, but it must write that launcher to disk, print it in chat as a fenced `prompt` block, explain why it could not dispatch the child itself, and give one exact human next step.

Primary and Frontier should maintain machine-readable coordination state:

- `current-manifest` records current facts, invalid or deprecated sources, active lanes, superseded prompts, cancelled prompts, and latest consume refs.
- `sequence-registry` records Prompt IDs, Response IDs, handoffs, consume results, active cards, active lanes, and current/latest pointers.
- `consume-result` records what handoff or review evidence has been provisionally or finally consumed.
- `machine-summary` gives compact locators for worker, reviewer, discovery, Frontier, or Primary output.

Validate launcher-bearing response logs with:

```bash
openacp-validate --artifact <response-log-with-launcher.md> --ruleset launcher-output --strict
```

## Skill Install Notes

For Codex, install the directories under `skills/` as local skills if skill installation is available. If native skill installation is unavailable, load the relevant `SKILL.md` files as workflow instructions for the current session.

For Claude Code or another coding agent, treat `skills/*/SKILL.md` as the workflow instructions to load before starting orchestration.
