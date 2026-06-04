# OpenACP

OpenACP, short for Open Agent Coordination Protocol, is an open workflow kit for coordinating multiple AI agents across planning, implementation, review, and delivery. It is not an agent runtime, model framework, IDE plugin, or prompt collection. It gives teams a reusable way to decide who can act, what counts as evidence, how work is handed off, and when a result is only provisional.

OpenACP is designed around active closure. Primary and Frontier orchestrators should keep pushing B0/B1/B2-safe work forward, dispatch bounded subagents when they reduce risk, consume handoffs and reviews, and reserve only true final-authority decisions for B3.

## Who This Is For

OpenACP is for teams that want agents to work in parallel without losing control of scope, facts, review, or final authority. It is especially useful when a project has more than one worker, multiple branches or worktrees, reviewer sidecars, changing source material, or a human owner who needs readable status instead of raw logs.

It also helps teams that only have a rough PRD or product idea. In that case, ACP Bootstrap turns the idea into a minimal source pack, scope boundary, assumptions ledger, starter spec, and first task card before implementation begins.

OpenACP is not for replacing tests, CI, code review, security review, legal review, release ownership, or engineering judgment. The validator checks structure and common unsafe claims; it does not decide whether the product is correct or whether a change should merge.

## Start With Codex Or Claude Code

Ask Codex/Claude Code:

```text
Install https://github.com/0fuk/OpenACP as a skill + workflow kit, then follow the README startup flow.
```

The agent should install the OpenACP skills and Python workflow kit, run validation, and then produce a formal report automatically. The formal report is part of the startup flow; the user should not need to ask for it separately.

After installation and validation, there will be a formal report. In the next step, I will ask you for:

- your working directory, which is required
- your current source pack, PRD, spec, or facts path
- your preferred language for all future agent replies

If you do not have a prepared facts path, you can upload or attach the project materials instead. A clear working directory is still required.

After you provide those, I will write one full Primary prompt record to your working directory, then return one short copyable Primary chat launcher that points to that file. The full prompt body belongs on disk, not in the chat launcher.

Expected agent startup flow:

1. Clone `https://github.com/0fuk/OpenACP`.
2. Install or load every skill under `skills/`.
3. Install the Python workflow kit with `python -m pip install -e .`.
4. Run validation:
   - `python tools/openacp_validate_selftest.py`
   - `python tools/openacp_validate.py --artifact . --ruleset public-package --strict`
   - `openacp --version`
   - `openacp-validate --version`
5. Read the installed skills plus the shortest docs path.
6. Produce a formal report using `templates/formal-report.md`.
7. Ask for the user's real working directory, source pack, PRD, spec, or facts path, and preferred language. The working directory is mandatory; if the user has no facts path, accept uploaded project materials as the facts input. If preferred language is omitted, use the user's current language consistently.
8. After the user provides those inputs, write exactly one full Primary prompt record under `<working-directory>/.openacp/launchers/`, then return exactly one short Primary chat launcher. Before the short launcher, tell the user to create a new thread from the left sidebar and paste only that short launcher there.
9. Do not create Frontier launchers during GitHub install startup. The Primary thread inspects the workspace and facts, creates CARDs, then dynamically decides whether to launch 1-5 B2 Frontier lanes.

Skills to install or load:

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

Do not create a demo package by default. Use `openacp init` only when the user has no current source pack, PRD package, spec, facts path, or uploaded project materials and explicitly wants bootstrap artifacts.

Read the detailed startup contract in `docs/codex-install-and-start.md`.

## Developer Validation

Prerequisite: Python 3.10 or newer.

```bash
git clone https://github.com/0fuk/OpenACP.git
cd OpenACP
python tools/openacp_validate_selftest.py
python tools/openacp_validate.py --artifact . --ruleset public-package --strict
```

Validate the complete single-worker fixture:

```bash
python tools/openacp_validate.py --artifact examples/single-worker-flow/source-pack.json --ruleset source-pack --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/authority-charter.json --ruleset authority-charter --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/task-card.json --ruleset task-card --source-pack examples/single-worker-flow/source-pack.json --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/handoff.json --ruleset handoff --task-card examples/single-worker-flow/task-card.json --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/review-report.json --ruleset review-report --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/status-report.json --ruleset status-report --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/machine-summary.json --ruleset machine-summary --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/formal-report-example.md --ruleset formal-report --strict
python tools/openacp_validate.py --artifact examples/primary-orchestrator-flow/final-consume-result.json --ruleset consume-result --strict
```

Install local CLI entry points during development:

```bash
python -m pip install -e .
openacp --help
openacp --version
openacp-validate --help
openacp-validate --version
```

If you do not have a source pack, PRD package, spec, facts path, or uploaded project materials, create a starter package from a vague PRD or product note:

```bash
openacp init ./my-openacp-package
openacp init ./my-openacp-package --write
```

`openacp init` is a dry run by default. It is a bootstrap fallback, not the default startup path. Use `--write` only when the target directory is correct.

## Core Flow

```text
rough idea or PRD
  -> source pack
  -> scope boundary + assumptions
  -> task card + authority charter
  -> worker in a bounded workspace
  -> handoff with verification evidence
  -> reviewer report
  -> final consume by Primary or human owner
```

Read the shortest path first:

1. `docs/codex-install-and-start.md`
2. `docs/getting-started.md`
3. `docs/role-model.md`
4. `docs/authority-boundary.md`
5. `docs/validator.md`
6. `examples/primary-two-frontier-kickoff/README.md`
7. `examples/single-worker-flow/README.md`

Do not read every template before starting. Use the source pack and task card to decide what context is actually needed.

## Two Layers

### ACP Bootstrap

Use ACP Bootstrap when a project has only a rough product idea, lightweight PRD, or scattered notes. Bootstrap creates the first working package: PRD intake, current source pack, scope boundary, assumptions ledger, open questions, starter spec, and initial task cards.

The pain it solves is premature execution. A worker should not guess a spec, invent authority, or treat brainstorming as current truth.

### ACP Coordination

Use ACP Coordination when the project already has enough local facts to dispatch agents. Coordination defines Primary, Frontier, worker, reviewer, authority boundaries, task cards, independent worktrees or branches, handoffs, sidecar reviews, validator gates, formal reports, and human-readable status.

The pain it solves is coordination drift. In multi-agent work, the hard problem is often not writing code; it is keeping facts current, scope bounded, claims reviewable, and final authority separate from provisional evidence.

## Role And Authority Model

- `Primary`: owns final consume, merge or release decisions, and final authority.
- `Primary active closure`: splits work into lanes, dispatches bounded subagents, consumes evidence, and reclassifies remaining gaps until the work is closed, delegated, explicitly out, or truly final-authority-only.
- `Frontier`: orchestrates a lane, prepares packages, and defaults to B2 lane-local authority when launched by Primary unless Primary explicitly narrows it.
- `Frontier B0/B1/B2 loop`: runs discovery and review at B0, package preparation at B1, scoped worker dispatch at B2, child handoff consume, rolling backlog updates, and closure proof before returning to Primary.
- `Frontier subagent-first closure`: worker, reviewer, discovery, validation, and task-card-only child work should be dispatched by Frontier inside its current lane thread when tools allow it. Human-managed child launchers are fallback only.
- `worker`: executes a bounded task card and produces a handoff.
- `reviewer`: checks scope, evidence, and claims without becoming final authority.
- `human owner`: decides product intent, risk tolerance, and release acceptance when required.

Authority levels:

- `B0`: read-only discovery and review.
- `B1`: packaging, task-card drafting, verification matrix preparation.
- `B2`: scoped execution under a task card and authority charter.
- `B3`: final authority such as accept, waive, merge, release, or publish.

## Templates And Validation

Markdown templates are authoring aids. JSON artifacts are the machine-checkable form used by the validator.

Prompt records and short launchers should be checked together so the copyable chat launcher cannot drift from the full on-disk prompt:

```bash
python tools/openacp_validate.py --artifact primary-orchestrator.prompt.md --ruleset prompt-record --expect-prompt-id <prompt-id> --strict
python tools/openacp_validate.py --artifact primary-orchestrator.short.md --ruleset launcher --prompt-record primary-orchestrator.prompt.md --expect-prompt-id <prompt-id> --strict
```

Frontier prompt records should include the machine-readable `openacp-frontier-orchestration-contract.v1` block and pass the Frontier contract ruleset:

```bash
python tools/openacp_validate.py --artifact frontier.prompt.md --ruleset frontier-contract --strict
```

Task-card strict validation should include the source pack:

```bash
python tools/openacp_validate.py --artifact task-card.json --ruleset task-card --source-pack source-pack.json --strict
```

Handoff strict validation should include the task card:

```bash
python tools/openacp_validate.py --artifact handoff.json --ruleset handoff --task-card task-card.json --strict
```

For B2/B3 task cards, strict validation requires `authorityCharterRef`. This keeps execution authority and final authority visible instead of implicit.

After consume or child output, validate the machine artifacts:

```bash
python tools/openacp_validate.py --artifact consume-result.json --ruleset consume-result --strict
python tools/openacp_validate.py --artifact machine-summary.json --ruleset machine-summary --strict
```

## Examples

- `examples/single-worker-flow/`: complete strict-validation fixture.
- `examples/prd-only-bootstrap/`: strict bootstrap fixture for teams starting from a rough PRD.
- `examples/primary-two-frontier-kickoff/`: concept example for Primary-generated Frontier launchers after CARD and lane analysis, not default install startup.
- `examples/primary-orchestrator-flow/`: concept example for final-authority dispatch and consume.
- `examples/frontier-lane-flow/`: concept example for lane authority.
- `examples/multi-worktree-review/`: concept example for multiple workers and reviewer sidecars.

Only the first two are intended as ready-to-run validation fixtures. The concept examples show shape and vocabulary, not a complete artifact bundle.

## Repository Map

```text
docs/        Concepts, role model, authority model, bootstrap, coordination, validator rules.
templates/   Reusable Markdown templates for PRD intake, source packs, specs, prompts, reports.
schemas/     Minimal JSON Schemas for machine-checkable coordination artifacts.
tools/       Validator and helper CLI.
skills/      Portable agent skills for using OpenACP workflows.
examples/    Strict fixtures and concept examples.
```

Internal reports, local logs, private source packs, and release working notes belong in ignored local paths such as `.openacp-local/`, not in the public package.

## Positioning

OpenACP can be used with Claude Workflow, SuperClaude, Aider, OpenHands, SWE-agent, LangGraph, CrewAI, AutoGen, the OpenAI Agents SDK, Codex, or a custom agent stack. Those projects help agents run, reason, code, or orchestrate. OpenACP focuses on reusable coordination artifacts: source packs, authority boundaries, task cards, handoffs, review reports, validator gates, and final consume decisions.

## Minimum Useful Setup

The smallest useful OpenACP setup is one source pack, one scope boundary, one task card, one authority charter for executable work, one worker handoff, one reviewer report, one machine summary, and one final consume result by the authorized owner.
