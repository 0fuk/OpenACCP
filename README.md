# OpenACCP

**OpenACCP: Agentic Continuous Coordination Protocol**

OpenACCP is an open workflow protocol for coordinating multi-agent software work.

OpenACCP focuses on the coordination layer around agent runtimes, model frameworks, IDE tools, and graph frameworks. It works alongside Codex, Claude Code, Aider, OpenHands, SWE-agent, LangGraph, CrewAI, AutoGen, and the OpenAI Agents SDK. Those tools help agents run, code, call tools, or build graphs. OpenACCP keeps parallel agent work organized once several threads start moving at the same time:

- Which materials are current facts, reference-only material, deprecated material, or invalid sources.
- Which agent may only read, which agent may prepare packages, and which agent may execute scoped work.
- What a worker handoff proves, and which acceptance step remains.
- Whether a reviewer recommendation is final, or only provisional evidence.
- How multiple threads, worktrees, handoffs, review reports, and launchers connect.
- When the human owner must make a final decision, and when agents can keep moving without interrupting the human.

In one sentence: **AI agents can do work; OpenACCP keeps the work coordinated, reviewable, and recoverable.**

## Who This Is For

OpenACCP is for people who have moved beyond one-off prompts and are starting to use AI agents like a small project team.

| You are | Common pain | What OpenACCP gives you |
|---|---|---|
| An independent developer running several agent threads | One thread reads the spec, another edits code, another reviews, and soon nobody knows which result still counts. | Each thread gets a role, scope, authority, handoff, and status path. |
| A startup founder or engineering lead | Agents can move quickly, but merge, release, customer impact, and risk acceptance still need a clear owner. | Execution authority and final authority are kept separate. |
| A large repo maintainer | Migration, refactor, testing, docs, and release prep happen across branches, PRs, CI, and chat history. | Source packs, CARDs, authority charters, handoffs, review reports, and consume results connect the work. |
| An AI coding workflow owner | The team already uses Codex, Claude Code, Aider, OpenHands, or other tools, but handoff and review practices differ by tool. | A tool-neutral coordination layer that different agents can share. |
| A complex delivery owner | Backend, frontend, tests, security, docs, and launch work move in parallel, but only some agent output should be accepted. | A clean distinction between "an agent produced this" and "the project accepted this." |
| A team with only a PRD or rough product idea | There is no source pack, spec, scope boundary, or task card, so agents start guessing. | Bootstrap turns rough material into a minimal source pack, scope boundary, assumptions ledger, open questions, starter spec, and first CARDs. |

OpenACCP keeps tests, CI, code review, security review, legal review, release ownership, and engineering judgment visible inside one coordination flow.

## Quick Start

Ask Codex or Claude Code:

```text
Install https://github.com/0fuk/OpenACCP as a skill + workflow kit, then follow the README startup flow.
```

Startup performs three setup steps:

1. Install or load every OpenACCP skill under `skills/`.
2. Install the Python workflow kit and run basic validation.
3. Produce a formal report automatically as part of startup.

The post-install formal report stays short and human-readable. It summarizes validation in words and keeps command output, executable paths, local install paths, and temporary directories out of chat.

After installation and validation, the agent asks you for:

- **Working directory**: required. Launchers need a concrete project workspace where the agent is allowed to work.
- **Facts input**: a source pack, PRD, spec, design document, facts path, or uploaded project materials.
- **Preferred language**: the language that every Primary, Frontier, worker, reviewer, and discovery reply uses consistently.

When the facts path is still rough, upload or attach the project materials. The agent treats them as candidate facts until it organizes and validates them. A working directory is still required.

After you provide those inputs:

1. Startup writes one full Primary prompt record to your working directory.
2. Startup writes one short Primary launcher file beside it.
3. Startup returns one copyable short Primary launcher in the current chat as a fenced `prompt` block.
4. Startup tells you, in natural language, to create a new thread from the left sidebar and paste only that short launcher there.

The full prompt body belongs on disk. Chat contains the copyable short launcher itself, with file links or attachments used only as supporting references.

## What Happens After Startup

GitHub install startup creates **one Primary launcher first**. Primary creates Frontier launchers later after workspace review, CARD creation, and lane analysis.

The Primary thread starts after you paste the short Primary launcher into a new thread. Primary then reviews the real workspace and facts before deciding how much parallel coordination is useful.

Primary does the coordination work:

1. Read the working directory and facts input.
2. Classify sources as `current`, `reference`, `deprecated`, or `invalid`.
3. Create or refresh the source pack, scope boundary, assumptions ledger, runtime boundary, current manifest, source status registry, lane registry, decision registry, sequence registry, and CARD registry.
4. Resolve or explicitly mark product repo path, base branch, source roots, test entrypoints, worktree policy, writable/read-only/forbidden paths, side effects, and data risk before B2 Frontier dispatch.
5. Split the project into CARDs before dispatching Frontier lanes.
6. Decide how many Frontier lanes are useful based on project complexity, dependencies, risk, and parallel safety.
7. Write full Frontier prompt records and short Frontier launchers for selected lanes.
8. Print each selected Frontier launcher in chat as a copyable fenced `prompt` block.

Primary defaults to **at least two Frontier lanes** for normal or medium-complexity projects when two safe independent CARD clusters exist. It launches one Frontier only when the project is clearly small, only one safe lane exists, or the user explicitly asks for a single lane. Broad or medium-high-complexity projects normally receive two to five Frontier lanes. More than five requires explicit user approval.

## Manual Primary And Frontier Startup

After the skills are installed, you can also manually start a new Primary or Frontier.

Manual Primary launcher:

```prompt
Use primary-orchestrator-openaccp to start OpenACCP coordination for this project.

Working directory: <your project path>
Facts input: <source pack, PRD, spec, design document, facts path, or uploaded materials>
Preferred language: <English / Chinese / your choice>

First review the workspace and facts. Create or refresh the source pack, scope boundary, assumptions ledger, runtime boundary, current manifest, source status registry, lane registry, decision registry, sequence registry, and CARD registry. Resolve or explicitly mark product repo path, base branch, source roots, test entrypoints, and worktree policy before B2 Frontier dispatch. Split the project into enough CARDs to support useful parallel Frontier lanes. Then return a human-readable status report and copyable short Frontier launchers for selected lanes.
```

Manual Frontier launcher:

```prompt
Use frontier-orchestrator-openaccp for this lane.

Lane objective: <what this lane closes>
Authority: B2 lane-local unless explicitly narrowed
Working directory: <project path>
Facts/source pack: <path or artifact>
Assigned CARDs: <CARD ids or task cards>
Preferred language: <same as Primary>

Continue B0/B1/B2 lane-local closure. Dispatch worker, reviewer, discovery, or validation subagents when safe. Stay inside the lane until only final authority or missing user facts remain.
```

If a full prompt record already exists, use a short launcher. The short launcher tells the new thread which prompt record to read, which Prompt ID to execute, which language to use, and how to report a clean read failure.

## How Orchestrators Communicate

OpenACCP uses project artifacts as the shared memory between orchestrators.

```text
Primary
  -> writes CARDs, authority charters, and Frontier prompt records
  -> returns short Frontier launchers

Frontier
  -> reads assigned CARDs and source pack
  -> runs B0/B1/B2 lane-local closure
  -> dispatches worker/reviewer/discovery subagents when safe
  -> consumes child handoffs
  -> writes lane status, child ledger, frontier closure, and Primary-ready packet

worker / reviewer / discovery
  -> returns handoff, review report, machine summary, or evidence summary

Primary
  -> consumes handoffs and reviewer evidence
  -> accepts, rejects, amends, splits follow-up, or asks for a B3 human decision
```

Important artifacts:

| Artifact | Plain meaning |
|---|---|
| `source pack` | The current fact list. It tells agents what may drive implementation and what is only background. |
| `scope boundary` | The line between allowed work and forbidden work. |
| `assumptions ledger` | Explicit assumptions that are not fully proven yet. |
| `runtime boundary` | Repo path, base branch, source roots, test entrypoints, worktree policy, writable/read-only/forbidden paths, side effects, data risk, and the `b2DispatchGate` that says whether product-write B2 work is ready, blocked, or coordination-only. |
| `current manifest` | The current coordination anchor: source pack, runtime boundary, source status registry, lane registry, CARD registry, and active lanes. |
| `sequence registry` | Prompt IDs, Response IDs, handoffs, consumes, cards, active lanes, lifecycle states, and current/latest pointers. |
| `source status registry` | Current, reference, deprecated, invalid, and unknown sources with reasons and locators. |
| `lane registry` | Primary and Frontier lanes, project complexity, Frontier dispatch mode, lane-count reason, assigned CARDs, authority, child ledger refs, consume refs, closure refs, return-gate state, and per-lane B2 dispatch mode. |
| `child ledger` | Worker, reviewer, discovery, validation, or task-card-only child lifecycle, handoff status, consume status, and remaining risk. |
| `decision registry` | Owner questions, Primary decisions, waivers, out-of-scope decisions, blockers, and safe defaults. |
| `CARD` | A project-level work slice large enough for lane planning. A CARD can later become several task cards. |
| `task card` | A bounded executable task with scope, acceptance, verification, and stop conditions. |
| `authority charter` | The permission contract: who can read, who can write, allowed effects, forbidden effects, and data risk. |
| `prompt record` | The full role prompt saved on disk and executed by Prompt ID. |
| `short launcher` | The copyable chat block that points a new thread to the full prompt record. |
| `handoff` | Evidence from a worker, reviewer, or discovery agent. It proves some things and leaves other things unproven. |
| `consume result` | The orchestrator decision about what a handoff actually proves before acceptance. |
| `frontier closure` | The gate proof for whether a Frontier can keep working, close, or return to Primary. |
| `formal report` | Human-readable status: what changed, progress, area, goal, gaps, next action, and evidence. |
| `machine summary` | Compact locators for downstream agents and validators. |

## Role Model

| Role | What it does | Authority boundary |
|---|---|---|
| `Primary` | Owns project-level coordination, CARD decomposition, lane dispatch, final consume, and final acceptance decisions. | Keeps final acceptance separate from worker claims, reviewer recommendations, and validator pass. |
| `Frontier` | Owns one lane. It keeps closing B0/B1/B2-safe work by refreshing backlog, dispatching subagents, consuming child handoffs, and preparing Primary-ready packets. | Runs lane orchestration and reserves B3 final authority for Primary or the human owner. |
| `worker` | Executes one bounded task card and returns verification evidence. | Stays inside the assigned task card, authority charter, and stop conditions. |
| `reviewer` | Performs read-only review of scope, correctness, verification, side effects, and overclaiming. | Stays read-only and returns recommendations as evidence. |
| `discovery` | Reads facts, classifies gaps, and prepares safe next actions. | Keeps source promotion under explicit authority. |
| `human owner` | Decides product intent, risk acceptance, release, and high-risk exceptions. | Receives questions only when the next useful step needs owner facts or final authority. |

## B0 / B1 / B2 / B3

These levels answer one practical question: **how much authority does this agent have right now?**

| Level | Plain meaning | Typical actions |
|---|---|---|
| `B0` | Read-only discovery and review. | Source discovery, risk scan, evidence review, backlog refresh, source classification. |
| `B1` | Package preparation. | CARD shaping, task-card drafts, verification matrices, owner questions, handoff schema, dispatch-ready packets. |
| `B2` | Scoped execution under an authority charter. | Worker dispatch, worktree setup, bounded implementation, focused verification, child handoff consume. |
| `B3` | Final authority. | Final acceptance, PR/CI/merge, release, publication, final waiver, cross-lane final decisions. |

The key rule: **a B3 blocker still leaves B0/B1/B2 work available.** If agents can still discover facts, narrow scope, prepare packages, dispatch scoped workers, or add review evidence, they keep moving.

## CARD Decomposition

Good CARDs are the difference between one overloaded Frontier and several useful lanes.

For a normal product or medium-high-complexity project, Primary usually creates **10-20 project-level CARDs**, and those CARDs may later expand into dozens or hundreds of concrete task cards. That gives Frontier lanes enough independent surface area to work in parallel.

Primary scans the facts for product domains before cutting CARDs. Examples include:

- product workflow and user journeys,
- backend/API and service contracts,
- frontend/UI surfaces when the facts mention them,
- desktop/mobile/native/Electron/Tauri surfaces when the facts mention them,
- data model, storage, migration, import/export, or analytics,
- integrations, external systems, and platform runtime,
- authentication, authorization, privacy, compliance, and data risk,
- testing, QA, accessibility, performance, observability, and CI,
- docs, release, operations, deployment, and rollback.

Create frontend, UI, Electron, mobile, or compliance lanes when the project facts name those surfaces. If the PRD, spec, or source pack explicitly names Electron, UI, frontend, desktop shell, mobile, or another surface, Primary should create CARD coverage for that surface instead of treating the project as backend-only.

CARDs are then grouped into Frontier lanes. A lane can own several related CARDs, and each lane has a clear objective plus enough independence to make parallel work useful.

## Skills

OpenACCP skills are installable agent workflow instructions. Each skill maps to a real coordination role or governance action.

| Skill | When to use it | Why it matters |
|---|---|---|
| `primary-orchestrator-openaccp` | Start or run project-level coordination. Use it for CARD decomposition, lane dispatch, final handoff consume, and acceptance decisions. | Keeps the project moving without mixing provisional agent output with final acceptance. |
| `frontier-orchestrator-openaccp` | Run one bounded lane. Use it for lane backlog, discovery, package preparation, worker/reviewer dispatch, and child handoff consume. | Prevents Frontier from returning to the human too early when B0/B1/B2 work can still continue. |
| `worker-openaccp` | Execute one narrow task under a task card and authority charter. | Keeps implementation scoped and evidence-backed. |
| `reviewer-openaccp` | Review a task card, diff, branch, handoff, prompt, or status artifact. | Turns "looks okay" into an approve/amend/reject/split-follow-up recommendation with evidence. |
| `discovery-openaccp` | Run read-only fact discovery when scope, source status, risk, or next safe action is unclear. | Prevents agents from treating guesses as facts. |
| `source-pack-openaccp` | Create, review, or update source packs and manifests. | Keeps current, reference, deprecated, and invalid sources separate. |
| `bootstrap-openaccp` | Start from a rough PRD, idea, issue list, or scattered notes. | Builds the first source pack, scope boundary, assumptions ledger, starter spec, and CARDs. |
| `handoff-consume-openaccp` | Decide what a handoff proves before merge, release, follow-up dispatch, or acceptance. | Prevents "a file exists" from becoming "the project accepted it." |
| `formal-report-openaccp` | Report project, lane, review, validation, or release-readiness status. | Gives humans stable, readable status without machine-log noise. |
| `human-explain-openaccp` | Explain orchestration status in plain language. | Translates Prompt IDs, lanes, handoffs, and B0/B1/B2/B3 into delivery meaning. |
| `validator-openaccp` | Validate artifacts before dispatch, consume, reports, launchers, or release packaging. | Checks structure, encoding, source status, authority boundary, overclaiming, and public package hygiene. |

## Language Contract

If the user chooses a preferred language, all Primary, Frontier, worker, reviewer, discovery, and formal report replies use that language as the main language.

For example, if the preferred language is Chinese, the reply is Chinese-first. Keep fixed technical terms in English only when they are useful as terms: `Primary`, `Frontier`, `worker`, `reviewer`, `handoff`, `validator`, `source pack`, `authority boundary`, `Prompt ID`, `Response ID`, `CARD`, `task-card`, `B0/B1/B2/B3`, `CI`, `README`, `CLI`, `JSON`, `schema`, `Electron`, or exact file names. A Chinese report keeps long explanatory paragraphs in Chinese.

## Core Technology

OpenACCP is a reusable coordination layer for agent work.

### Source-Driven Coordination

Work starts from current facts. A PRD, old spec, screenshot, chat note, or draft becomes current truth only after source classification. OpenACCP asks agents to classify source status:

- `current`: may drive implementation.
- `reference`: may provide background while current sources continue to define scope.
- `deprecated`: replaced by newer material.
- `invalid`: unreadable, contaminated, role-mismatched, stale, or untrusted.

### Authority Boundary

Worker output, reviewer recommendations, Frontier synthesis, and validator pass remain evidence until B3 final authority accepts them.

### Active Closure

Primary and Frontier turn blockers into the next safe B0/B1/B2 action whenever possible:

- Can this gap be reduced by B0 discovery?
- Can it be turned into a B1 package?
- Can a scoped B2 worker or reviewer handle it?
- Is the remaining issue truly B3 final authority?

Frontier returns the lane to Primary only when all visible remaining gaps are final-authority-only or explicitly out.

### Handoff Consume

A handoff is evidence that becomes completion only after consume and acceptance. The consuming orchestrator checks scope, changed files, verification evidence, skipped checks, reviewer findings, data risk, authority limits, and overclaims.

### Human-Readable Status

OpenACCP rejects machine-log replies as the main user-facing answer. A useful status says what changed, what is proven, what is provisional, what is missing, and what happens next.

Every Primary, Frontier, worker, reviewer, discovery, bootstrap, and validation reply uses `human-explain-openaccp` style. Status-like replies end with a practical recommended next step. If the agent can continue, the answer names the next Primary-owned or Frontier-owned action. If human input is needed, it names the exact path, fact, repo boundary, branch, source root, test entrypoint, approval, or decision.

## Minimum Useful Setup

The smallest useful OpenACCP package contains:

```text
source pack
scope boundary
assumptions ledger
CARD registry
runtime boundary
current manifest
sequence registry
lane registry
child ledger
source status registry
decision registry
task card
authority charter
worker handoff
review report
consume result
frontier closure
formal report
```

When these inputs are missing, start with `bootstrap-openaccp` so implementation begins from task cards, acceptance criteria, verification plans, and stop conditions.

## Repository Map

```text
docs/        Concepts, role model, authority model, bootstrap, coordination, validator rules.
templates/   Reusable Markdown templates for source packs, specs, prompts, reports, handoffs.
schemas/     Minimal JSON Schemas for machine-checkable coordination artifacts.
tools/       Validator and helper CLI.
skills/      Portable agent skills for using OpenACCP workflows.
examples/    Strict fixtures and concept examples.
```

## Examples

- `examples/single-worker-flow/`: complete strict-validation fixture.
- `examples/prd-only-bootstrap/`: bootstrap fixture for teams starting from rough material.
- `examples/primary-two-frontier-kickoff/`: concept example for Primary-generated Frontier launchers after CARD and lane analysis.
- `examples/primary-orchestrator-flow/`: concept example for final-authority dispatch and consume.
- `examples/frontier-lane-flow/`: concept example for lane authority.
- `examples/multi-frontier-closure/`: strict fixture for runtime boundary, lane registry, child ledger, source status, decision registry, and Frontier closure.
- `examples/multi-worktree-review/`: concept example for multiple workers and reviewer sidecars.

The first two are best for direct validation. The other examples show shape and vocabulary for larger project packages.

## Local CLI

For a local trial:

```bash
git clone https://github.com/0fuk/OpenACCP.git
cd OpenACCP
python -m pip install -e .
openaccp --version
openaccp-validate --version
```

If you only have a rough PRD or scattered material, create a starter package:

```bash
openaccp init ./my-openaccp-package
openaccp init ./my-openaccp-package --write
```

`openaccp init` is a dry run by default. It is a bootstrap fallback. For real projects, install the skills first, then let Primary create project-specific prompt records and launchers from your working directory and facts input.

## Positioning

OpenACCP can be used with Claude Workflow, SuperClaude, Aider, OpenHands, SWE-agent, LangGraph, CrewAI, AutoGen, the OpenAI Agents SDK, Codex, or a custom agent stack.

The difference:

- Runtime and coding-agent tools make agents run, call tools, and write code.
- OpenACCP makes multi-agent work traceable, reviewable, handoff-ready, and authority-aware.

One layer executes work. The other coordinates project truth.

## Public Package Hygiene

The public repository contains public-safe docs, templates, schemas, examples, CLI, and validator code. Keep private response logs, private source packs, local absolute paths, customer material, credentials, and production logs in ignored local paths such as `.openaccp-local/` or your team's private workspace.

Before release, run:

```bash
python tools/openaccp_validate_selftest.py
python tools/openaccp_validate.py --artifact . --ruleset public-package --strict
python -m build
python -m twine check dist/*
```

Then install the built wheel or sdist in a clean environment and run a small validator smoke test. The validator checks structure, common leakage patterns, and common overclaims. Pair it with a dedicated secret scanner and human review before a formal release.
