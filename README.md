# OpenACP

OpenACP, short for **Open Agent Coordination Protocol**, is a workflow kit for coordinating multiple AI agents around real project work.

It is not an agent runtime, model framework, IDE plugin, or prompt pack. OpenACP does not replace Codex, Claude Code, Aider, OpenHands, SWE-agent, LangGraph, CrewAI, AutoGen, or the OpenAI Agents SDK. Those tools help agents run, code, call tools, or build graphs. OpenACP handles the coordination layer that gets messy once several agents start working at the same time:

- Which materials are current facts, reference-only material, deprecated material, or invalid sources.
- Which agent may only read, which agent may prepare packages, and which agent may execute scoped work.
- What a worker handoff proves, and what it does not prove.
- Whether a reviewer recommendation is final, or only provisional evidence.
- How multiple threads, worktrees, handoffs, review reports, and launchers connect.
- When the human owner must make a final decision, and when agents can keep moving without interrupting the human.

In one sentence: **AI agents can do work; OpenACP keeps the work coordinated, reviewable, and recoverable.**

## Who This Is For

OpenACP is for people who have moved beyond one-off prompts and are starting to use AI agents like a small project team.

| You are | Common pain | What OpenACP gives you |
|---|---|---|
| An independent developer running several agent threads | One thread reads the spec, another edits code, another reviews, and soon nobody knows which result still counts. | Each thread gets a role, scope, authority, handoff, and status path. |
| A startup founder or engineering lead | Agents can move quickly, but merge, release, customer impact, and risk acceptance still need a clear owner. | Execution authority and final authority are kept separate. |
| A large repo maintainer | Migration, refactor, testing, docs, and release prep happen across branches, PRs, CI, and chat history. | Source packs, CARDs, authority charters, handoffs, review reports, and consume results connect the work. |
| An AI coding workflow owner | The team already uses Codex, Claude Code, Aider, OpenHands, or other tools, but handoff and review practices differ by tool. | A tool-neutral coordination layer that different agents can share. |
| A complex delivery owner | Backend, frontend, tests, security, docs, and launch work move in parallel, but only some agent output should be accepted. | A clean distinction between "an agent produced this" and "the project accepted this." |
| A team with only a PRD or rough product idea | There is no source pack, spec, scope boundary, or task card, so agents start guessing. | Bootstrap turns rough material into a minimal source pack, scope boundary, assumptions ledger, open questions, starter spec, and first CARDs. |

OpenACP does not replace tests, CI, code review, security review, legal review, release ownership, or engineering judgment. It makes those things easier for humans and agents to coordinate.

## Quick Start

Ask Codex or Claude Code:

```text
Install https://github.com/0fuk/OpenACP as a skill + workflow kit, then follow the README startup flow.
```

The startup agent should:

1. Install or load every OpenACP skill under `skills/`.
2. Install the Python workflow kit and run basic validation.
3. Produce a formal report automatically. The user should not need to ask for it separately.

After installation and validation, the agent should ask you for:

- **Working directory**: required. Launchers need a concrete project workspace where the agent is allowed to work.
- **Facts input**: a source pack, PRD, spec, design document, facts path, or uploaded project materials.
- **Preferred language**: the language that every Primary, Frontier, worker, reviewer, and discovery reply should use consistently.

If you do not have a clean facts path, upload or attach the project materials. The agent should treat them as candidate facts until it organizes and validates them. A working directory is still required.

After you provide those inputs, the startup agent should:

1. Write one full Primary prompt record to your working directory.
2. Write one short Primary launcher file beside it.
3. Return one copyable short Primary launcher in the current chat as a fenced `prompt` block.
4. Tell you, in natural language, to create a new thread from the left sidebar and paste only that short launcher there.

The full prompt body belongs on disk. Chat should contain the short launcher only. A `.short.md` link, file attachment, file list, or `Get-Content` command is not enough.

## What Happens After Startup

GitHub install startup creates **one Primary launcher only**. It does not create Frontier launchers yet.

The Primary thread starts after you paste the short Primary launcher into a new thread. Primary then reviews the real workspace and facts before deciding how much parallel coordination is useful.

Primary should:

1. Read the working directory and facts input.
2. Classify sources as `current`, `reference`, `deprecated`, or `invalid`.
3. Create or refresh the source pack, scope boundary, current manifest, sequence registry, and assumptions ledger.
4. Split the project into CARDs before dispatching Frontier lanes.
5. Decide how many Frontier lanes are useful based on project complexity, dependencies, risk, and parallel safety.
6. Write full Frontier prompt records and short Frontier launchers for selected lanes.
7. Print each selected Frontier launcher in chat as a copyable fenced `prompt` block.

Primary should default to **at least two Frontier lanes** for normal or medium-complexity projects when two safe independent CARD clusters exist. It may launch one Frontier only when the project is clearly small, only one safe lane exists, or the user explicitly asks for a single lane. Broad or medium-high-complexity projects should normally receive two to five Frontier lanes. More than five requires explicit user approval.

## Manual Primary And Frontier Startup

OpenACP is not only an install script. After the skills are installed, you can manually start a new Primary or Frontier.

Manual Primary launcher:

```prompt
Use primary-orchestrator-openacp to start OpenACP coordination for this project.

Working directory: <your project path>
Facts input: <source pack, PRD, spec, design document, facts path, or uploaded materials>
Preferred language: <English / Chinese / your choice>

First review the workspace and facts. Create or refresh the source pack, scope boundary, assumptions ledger, current manifest, sequence registry, and CARD registry. Split the project into enough CARDs to support useful parallel Frontier lanes. Then return a human-readable status report and copyable short Frontier launchers for selected lanes.
```

Manual Frontier launcher:

```prompt
Use frontier-orchestrator-openacp for this lane.

Lane objective: <what this lane should close>
Authority: B2 lane-local unless explicitly narrowed
Working directory: <project path>
Facts/source pack: <path or artifact>
Assigned CARDs: <CARD ids or task cards>
Preferred language: <same as Primary>

Continue B0/B1/B2 lane-local closure. Dispatch worker, reviewer, discovery, or validation subagents when safe. Do not return to the human unless the next action truly needs final authority or missing user facts.
```

If a full prompt record already exists, use a short launcher. The short launcher tells the new thread which prompt record to read, which Prompt ID to execute, which language to use, and how to stop if the file cannot be read cleanly.

## How Orchestrators Communicate

OpenACP does not rely on the previous chat thread "remembering" everything. Orchestrators communicate through project artifacts.

```text
Primary
  -> writes CARDs, authority charters, and Frontier prompt records
  -> returns short Frontier launchers

Frontier
  -> reads assigned CARDs and source pack
  -> runs B0/B1/B2 lane-local closure
  -> dispatches worker/reviewer/discovery subagents when safe
  -> consumes child handoffs
  -> writes lane status, child ledger, and Primary-ready packet

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
| `CARD` | A project-level work slice large enough for lane planning. A CARD can later become several task cards. |
| `task card` | A bounded executable task with scope, acceptance, verification, and stop conditions. |
| `authority charter` | The permission contract: who can read, who can write, allowed effects, forbidden effects, and data risk. |
| `prompt record` | The full role prompt saved on disk and executed by Prompt ID. |
| `short launcher` | The copyable chat block that points a new thread to the full prompt record. |
| `handoff` | Evidence from a worker, reviewer, or discovery agent. It proves some things and leaves other things unproven. |
| `consume result` | The orchestrator decision about what a handoff actually proves. A handoff is not acceptance by itself. |
| `formal report` | Human-readable status: what changed, progress, area, goal, gaps, next action, and evidence. |
| `machine summary` | Compact locators for downstream agents and validators. |

## Role Model

| Role | What it does | What it must not do |
|---|---|---|
| `Primary` | Owns project-level coordination, CARD decomposition, lane dispatch, final consume, and final acceptance decisions. | Must not treat worker claims, reviewer recommendations, or validator pass as final acceptance by themselves. |
| `Frontier` | Owns one lane. It keeps closing B0/B1/B2-safe work by refreshing backlog, dispatching subagents, consuming child handoffs, and preparing Primary-ready packets. | Is not the default implementation worker and cannot perform B3 final authority actions. |
| `worker` | Executes one bounded task card and returns verification evidence. | Must not expand scope, invent authority, or claim final acceptance. |
| `reviewer` | Performs read-only review of scope, correctness, verification, side effects, and overclaiming. | Must not commit, merge, waive, or final accept. |
| `discovery` | Reads facts, classifies gaps, and prepares safe next actions. | Must not implement or promote reference-only material to current facts without authority. |
| `human owner` | Decides product intent, risk acceptance, release, and high-risk exceptions. | Should not be interrupted for work that agents can safely continue under B0/B1/B2. |

## B0 / B1 / B2 / B3

These levels answer one practical question: **how much authority does this agent have right now?**

| Level | Plain meaning | Typical actions |
|---|---|---|
| `B0` | Read-only discovery and review. | Source discovery, risk scan, evidence review, backlog refresh, source classification. |
| `B1` | Package preparation. | CARD shaping, task-card drafts, verification matrices, owner questions, handoff schema, dispatch-ready packets. |
| `B2` | Scoped execution under an authority charter. | Worker dispatch, worktree setup, bounded implementation, focused verification, child handoff consume. |
| `B3` | Final authority. | Final acceptance, PR/CI/merge, release, publication, final waiver, cross-lane final decisions. |

The key rule: **a B3 blocker does not stop all B0/B1/B2 work.** If agents can still discover facts, narrow scope, prepare packages, dispatch scoped workers, or add review evidence, they should keep moving.

## CARD Decomposition

Good CARDs are the difference between one overloaded Frontier and several useful lanes.

Primary should not create only five to seven backend-looking CARDs by default. For a normal product or medium-high-complexity project, Primary should usually create **10-20 project-level CARDs**, and those CARDs may later expand into dozens or hundreds of concrete task cards.

Primary should scan the facts for product domains before cutting CARDs. Examples include:

- product workflow and user journeys,
- backend/API and service contracts,
- frontend/UI surfaces when the facts mention them,
- desktop/mobile/native/Electron/Tauri surfaces when the facts mention them,
- data model, storage, migration, import/export, or analytics,
- integrations, external systems, and platform runtime,
- authentication, authorization, privacy, compliance, and data risk,
- testing, QA, accessibility, performance, observability, and CI,
- docs, release, operations, deployment, and rollback.

Do not invent a frontend, UI, Electron, mobile, or compliance lane when the project facts do not mention it. But if the PRD, spec, or source pack explicitly names Electron, UI, frontend, desktop shell, mobile, or another surface, Primary must create CARD coverage for that surface instead of treating the project as backend-only.

CARDs should then be grouped into Frontier lanes. A lane can own several related CARDs, but each lane should have a clear objective and enough independence to make parallel work useful.

## Skills

OpenACP skills are installable agent workflow instructions. They are not decorative folders; each skill maps to a real coordination role or governance action.

| Skill | When to use it | Why it matters |
|---|---|---|
| `primary-orchestrator-openacp` | Start or run project-level coordination. Use it for CARD decomposition, lane dispatch, final handoff consume, and acceptance decisions. | Keeps the project moving without mixing provisional agent output with final acceptance. |
| `frontier-orchestrator-openacp` | Run one bounded lane. Use it for lane backlog, discovery, package preparation, worker/reviewer dispatch, and child handoff consume. | Prevents Frontier from returning to the human too early when B0/B1/B2 work can still continue. |
| `worker-openacp` | Execute one narrow task under a task card and authority charter. | Keeps implementation scoped and evidence-backed. |
| `reviewer-openacp` | Review a task card, diff, branch, handoff, prompt, or status artifact. | Turns "looks okay" into an approve/amend/reject/split-follow-up recommendation with evidence. |
| `discovery-openacp` | Run read-only fact discovery when scope, source status, risk, or next safe action is unclear. | Prevents agents from treating guesses as facts. |
| `source-pack-openacp` | Create, review, or update source packs and manifests. | Keeps current, reference, deprecated, and invalid sources separate. |
| `bootstrap-openacp` | Start from a rough PRD, idea, issue list, or scattered notes. | Builds the first source pack, scope boundary, assumptions ledger, starter spec, and CARDs. |
| `handoff-consume-openacp` | Decide what a handoff proves before merge, release, follow-up dispatch, or acceptance. | Prevents "a file exists" from becoming "the project accepted it." |
| `formal-report-openacp` | Report project, lane, review, validation, or release-readiness status. | Gives humans stable, readable status without machine-log noise. |
| `human-explain-openacp` | Explain orchestration status in plain language. | Translates Prompt IDs, lanes, handoffs, and B0/B1/B2/B3 into delivery meaning. |
| `validator-openacp` | Validate artifacts before dispatch, consume, reports, launchers, or release packaging. | Checks structure, encoding, source status, authority boundary, overclaiming, and public package hygiene. |

## Language Contract

If the user chooses a preferred language, all Primary, Frontier, worker, reviewer, discovery, and formal report replies should use that language as the main language.

For example, if the preferred language is Chinese, the reply should be Chinese-first. Keep fixed technical terms in English only when they are useful as terms: `Primary`, `Frontier`, `worker`, `reviewer`, `handoff`, `validator`, `source pack`, `authority boundary`, `Prompt ID`, `Response ID`, `CARD`, `task-card`, `B0/B1/B2/B3`, `CI`, `README`, `CLI`, `JSON`, `schema`, `Electron`, or exact file names. Do not write long English paragraphs such as "Primary recommended next action..." when the user asked for Chinese.

## Core Technology

OpenACP is not "more prompts." It is a set of reusable coordination techniques.

### Source-Driven Coordination

Work starts from current facts. A PRD, old spec, screenshot, chat note, or draft does not automatically become current truth. OpenACP asks agents to classify source status:

- `current`: may drive implementation.
- `reference`: may provide background but cannot expand scope.
- `deprecated`: replaced by newer material.
- `invalid`: unreadable, contaminated, role-mismatched, stale, or untrusted.

### Authority Boundary

Worker output, reviewer recommendations, Frontier synthesis, and validator pass are all evidence. They are not final acceptance. B3 final authority remains explicit.

### Active Closure

Primary and Frontier should not only list blockers. They should ask:

- Can this gap be reduced by B0 discovery?
- Can it be turned into a B1 package?
- Can a scoped B2 worker or reviewer handle it?
- Is the remaining issue truly B3 final authority?

Only when all visible remaining gaps are final-authority-only or explicitly out should Frontier return the lane to Primary.

### Handoff Consume

A handoff is evidence, not completion. The consuming orchestrator checks scope, changed files, verification evidence, skipped checks, reviewer findings, data risk, authority limits, and overclaims.

### Human-Readable Status

OpenACP rejects machine-log replies as the main user-facing answer. A useful status says what changed, what is proven, what is provisional, what is missing, and what happens next.

## Minimum Useful Setup

The smallest useful OpenACP package contains:

```text
source pack
scope boundary
assumptions ledger
CARD registry
task card
authority charter
worker handoff
review report
consume result
formal report
```

If you do not have these yet, start with `bootstrap-openacp`. Do not ask an implementation worker to guess requirements without a task card, acceptance criteria, verification plan, and stop conditions.

## Repository Map

```text
docs/        Concepts, role model, authority model, bootstrap, coordination, validator rules.
templates/   Reusable Markdown templates for source packs, specs, prompts, reports, handoffs.
schemas/     Minimal JSON Schemas for machine-checkable coordination artifacts.
tools/       Validator and helper CLI.
skills/      Portable agent skills for using OpenACP workflows.
examples/    Strict fixtures and concept examples.
```

## Examples

- `examples/single-worker-flow/`: complete strict-validation fixture.
- `examples/prd-only-bootstrap/`: bootstrap fixture for teams starting from rough material.
- `examples/primary-two-frontier-kickoff/`: concept example for Primary-generated Frontier launchers after CARD and lane analysis.
- `examples/primary-orchestrator-flow/`: concept example for final-authority dispatch and consume.
- `examples/frontier-lane-flow/`: concept example for lane authority.
- `examples/multi-worktree-review/`: concept example for multiple workers and reviewer sidecars.

The first two are best for direct validation. The other examples show shape and vocabulary, not a complete project package.

## Local CLI

For a local trial:

```bash
git clone https://github.com/0fuk/OpenACP.git
cd OpenACP
python -m pip install -e .
openacp --version
openacp-validate --version
```

If you only have a rough PRD or scattered material, create a starter package:

```bash
openacp init ./my-openacp-package
openacp init ./my-openacp-package --write
```

`openacp init` is a dry run by default. It is a bootstrap fallback, not the normal startup flow. For real projects, install the skills first, then let Primary create project-specific prompt records and launchers from your working directory and facts input.

## Positioning

OpenACP can be used with Claude Workflow, SuperClaude, Aider, OpenHands, SWE-agent, LangGraph, CrewAI, AutoGen, the OpenAI Agents SDK, Codex, or a custom agent stack.

The difference:

- Runtime and coding-agent tools make agents run, call tools, and write code.
- OpenACP makes multi-agent work traceable, reviewable, handoff-ready, and authority-aware.

One layer executes work. The other coordinates project truth.

## Public Package Hygiene

The public repository should not contain private response logs, private source packs, local absolute paths, customer material, credentials, or production logs. Keep private run material in ignored local paths such as `.openacp-local/` or your team's private workspace.

Before release, run:

```bash
python tools/openacp_validate_selftest.py
python tools/openacp_validate.py --artifact . --ruleset public-package --strict
```

The validator checks structure, common leakage patterns, and common overclaims. It is not a full secret scanner or a semantic proof of correctness. Run a dedicated secret scanner and human review before a formal release.
