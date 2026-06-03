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
- your current source pack, PRD, spec, or facts path.

If the user does not have a prepared facts path, the agent may ask the user to upload or attach the project materials. The working directory is still mandatory because the launchers need a concrete place where work can happen.

Use plain human-readable wording for the final ask. For example:

```text
I have installed and validated OpenACP, but I cannot build useful project launchers yet because I do not know where your project work should happen or which materials count as current facts. Please send me one clear working directory. This is required. Also send your source pack, PRD, spec, design document, or facts path. If you do not have a clean facts path yet, you can upload the project materials instead and I will treat them as candidate facts, but I still need the working directory.
```

## After The User Provides Project Inputs

After the user provides a working directory and facts input, the agent should return:

- one Primary Orchestrator launcher,
- two Frontier Orchestrator launchers.

Use:

- `templates/primary-orchestrator-launcher.md`
- `templates/frontier-orchestrator-launcher.md`
- `examples/primary-two-frontier-kickoff/`

The launchers must name:

- role,
- authority level,
- working directory,
- source pack or facts input,
- writable paths,
- read-only references,
- forbidden paths or side effects,
- validation expectations,
- handoff or report expectations.

The launchers must also include active closure rules:

- Primary should dispatch bounded subagents and consume evidence until only final-authority or explicitly-out gaps remain.
- Frontier should run the B0/B1/B2 closure loop, maintain a rolling backlog, dispatch allowed downstream subagents, consume child handoffs, and provide closure proof before returning to Primary.

The launchers must be returned in chat as copyable fenced prompt blocks. Writing launcher files into the user's working directory is optional and must not replace the chat output.

Use this interaction shape:

1. Tell the user: `Create a new thread from the left sidebar, paste the full Primary Orchestrator launcher below, and start that thread.`
2. Print the full Primary launcher in a fenced `prompt` block.
3. Tell the user: `Create another new thread from the left sidebar, paste the full Frontier A launcher below, and start that thread.`
4. Print the full Frontier A launcher in a fenced `prompt` block.
5. Tell the user: `Create another new thread from the left sidebar, paste the full Frontier B launcher below, and start that thread.`
6. Print the full Frontier B launcher in a fenced `prompt` block.

If the user has no source pack, PRD, spec, facts path, or uploaded project materials, do not invent one. Offer the bootstrap path and use `openacp init` only after the user explicitly approves creating starter artifacts.

## Skill Install Notes

For Codex, install the directories under `skills/` as local skills if skill installation is available. If native skill installation is unavailable, load the relevant `SKILL.md` files as workflow instructions for the current session.

For Claude Code or another coding agent, treat `skills/*/SKILL.md` as the workflow instructions to load before starting orchestration.
