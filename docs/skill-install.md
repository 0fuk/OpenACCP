# Skill Installation

OpenACCP ships as a workflow kit plus a set of portable agent skills. The workflow kit gives you the CLI, validator, schemas, templates, docs, and examples. The skills give Codex, Claude Code, or another agent client the role behavior for Primary, Frontier, worker, reviewer, discovery, bootstrap, handoff consume, validation, formal reports, and human explanations.

## Install From GitHub

Ask your agent client:

```text
Install https://github.com/0fuk/OpenACCP as a skill + workflow kit, then follow the README startup flow.
```

The installer should do four things:

1. Clone or update the repository.
2. Copy each directory under `skills/` into the client skill directory.
3. Install the Python workflow kit with `python -m pip install -e .`.
4. Run validation and return the automatic startup formal report.

## Common Skill Paths

Use the path that matches your local agent client.

| Client | Common skill location |
|---|---|
| Codex | `~/.codex/skills/` |
| Claude Code | `~/.claude/skills/` |
| Project-local setup | `<project>/.codex/skills/` or `<project>/.claude/skills/` |

If your client uses a different skill location, copy the same skill directories there. Keep the directory names unchanged, such as `primary-orchestrator-openaccp`, `frontier-orchestrator-openaccp`, and `formal-report-openaccp`.

## Verify Installation

After installation, the agent should confirm:

- OpenACCP skills are visible to the current agent client.
- `openaccp --version` is available.
- `openaccp-validate --version` is available.
- The public package validation passes.
- The startup formal report asks for facts input, working directory, repo path, and preferred language.

After those checks pass, provide your project inputs. The agent should write the full Primary prompt record to disk and return a copyable short Primary launcher in chat.
