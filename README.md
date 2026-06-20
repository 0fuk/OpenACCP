# OpenACCP - Coordination Layer for AI Coding Agents

**Agentic Continuous Coordination Protocol**

**Stop babysitting agents. Start coordinating them.**

OpenACCP is an open workflow protocol for coordinating multi-agent software work.

It gives Codex, Claude Code, Aider, OpenHands, SWE-agent, LangGraph, CrewAI, AutoGen, and the OpenAI Agents SDK a shared way to move from project facts to accepted work: `source pack`, `CARD`, `task-card`, `authority boundary`, `handoff`, review evidence, validator gates, worktrees, return wake, and final acceptance.

One agent can keep a small task moving with a good prompt or a loop. Real projects get harder: the PRD is fuzzy, specs drift, several agents work in parallel, reviewers return partial evidence, CI only proves part of the story, and the human quietly becomes the event bus. OpenACCP gives that work a coordination layer so the team knows which facts count, which agent owns which lane, what came back, and what is actually accepted.

## The Moment OpenACCP Is For

Use OpenACCP when your AI coding workflow has grown past "paste a prompt and hope":

- A vague ticket, PRD, or design note needs to become agent-ready work.
- Several agents need to work at the same time without mixing scope.
- A returned handoff needs consume, review, or follow-up dispatch.
- Reviewers need evidence instead of a cheerful summary.
- A Frontier lane can keep closing B0/B1/B2 work without bouncing every question to the human.
- Specs, decisions, and code need one recoverable source of truth.
- CI passes, but final acceptance still needs a clear owner.

## Why Teams Use OpenACCP

- **Start from source facts.** Classify project material as current, reference-only, deprecated, invalid, or unknown before agents act on it.
- **Give every agent a job.** Primary, Frontier, worker, reviewer, discovery, and validator roles each get a clear lane and authority boundary.
- **Keep Frontier lanes moving.** Frontiers continue B0/B1/B2-safe closure, dispatch subagents when useful, and return to Primary only when the lane is truly ready.
- **Turn output into evidence.** Handoffs, review reports, consume results, and machine summaries show what is proven, provisional, rejected, or still missing.
- **Separate doing from accepting.** Worker output, reviewer recommendations, validator passes, Primary consume, and human final authority stay distinct.
- **Recover from long-running work.** Prompt records, Response IDs, CARD registries, manifests, and coordination files make agent work restartable after thread or context loss.

## What You Get

| Need | OpenACCP gives you |
|---|---|
| Several agents working at once | Primary/Frontier lanes, CARDs, task cards, child ledgers, return wake, and handoffs. |
| A rough PRD or scattered notes | Bootstrap flow for source packs, assumptions, open questions, starter specs, and first CARDs. |
| Real code changes | Authority charters, worktree policy, scoped worker dispatch, verification evidence, and reviewer loops. |
| Clear acceptance | Consume results that say what evidence proves before final acceptance or release decisions. |
| Tool-neutral workflow | A protocol layer that can sit beside Codex, Claude Code, Aider, OpenHands, SWE-agent, LangGraph, CrewAI, AutoGen, or your own agent stack. |

## Who This Is For

OpenACCP is for people who already see the ceiling of one-off prompts and want AI agents to behave more like a small delivery team.

| You are | Common pain | What OpenACCP gives you |
|---|---|---|
| An independent developer running several agent threads | One thread reads the spec, another edits code, another reviews, and soon nobody knows which result still counts. | Each thread gets a role, scope, authority, handoff, and status path. |
| A startup founder or engineering lead | Agents can move quickly, but merge, release, customer impact, and risk acceptance still need a clear owner. | Execution authority and final authority are kept separate. |
| A large repo maintainer | Migration, refactor, testing, docs, and release prep happen across branches, PRs, CI, and chat history. | Source packs, CARDs, authority charters, handoffs, review reports, and consume results connect the work. |
| An AI coding workflow owner | The team already uses Codex, Claude Code, Aider, OpenHands, or other tools, but handoff and review practices differ by tool. | A tool-neutral coordination layer that different agents can share. |
| A complex delivery owner | Backend, frontend, tests, security, docs, and launch work move in parallel, but only some agent output should be accepted. | A clean distinction between "an agent produced this" and "the project accepted this." |
| A team with only a PRD or rough product idea | The starting material needs structure before agents can execute safely. | Bootstrap turns rough material into a minimal source pack, scope boundary, assumptions ledger, open questions, starter spec, and first CARDs. |

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

For manual skill installation details, see [docs/skill-install.md](docs/skill-install.md).

The post-install formal report stays short and human-readable. It summarizes validation in words and keeps command output, executable paths, local install paths, and temporary directories out of chat.

After installation and validation, the agent asks for these setup inputs in three clear lines:

1. **Facts input / project facts**: a source pack, PRD, spec, design document, facts folder, or uploaded project materials.
2. **Working directory / local agent coordination workbench**: the place where OpenACCP may write `.openaccp`, `launchers`, `coordination`, `reports`, `handoffs`, the CARD registry, and the source pack. This is the coordination workbench.
3. **Repo path / product code repository path**: the real product Git repository. Primary uses it to infer the current Git branch, base branch, writable scope, test entrypoints, worktree policy, and which files scoped workers may edit. This is the code workspace.

If the working directory and repo path are the same directory, say so. If there is no product repo yet, say `no repo yet`; Primary will stay in planning, packaging, and readiness mode until a repo is available. The agent uses the current conversation language unless you provide a preferred language.

After you provide those inputs:

1. Startup writes one full Primary prompt record to your working directory.
2. Startup writes one short Primary launcher file beside it.
3. Startup dispatches the Primary thread directly when the agent tool supports agent/thread spawn.
4. If direct dispatch is unavailable, Startup returns one copyable short Primary launcher in chat as a fenced `prompt` block and clearly labels it as the manual fallback.

The full prompt body belongs on disk. Chat carries only the short launcher seed when manual fallback is needed, with file links or attachments used only as supporting references.

## Pre-1.0 Compatibility

Before v1.0, breaking artifact schema changes bump that artifact's `schemaVersion` suffix. After upgrading, re-run the validator on stored artifacts and check `CHANGELOG.md` for the migration note.

## What Happens After Startup

GitHub install startup creates **one Primary prompt record first**. Primary creates and dispatches Frontier lanes later after workspace review, CARD creation, and lane analysis.

The Primary thread starts directly when the agent tool supports agent/thread spawn. If manual fallback is the only available channel, paste the short Primary launcher into a new thread. Primary then reviews the real workspace and facts before deciding how much parallel coordination is useful.

Primary does the coordination work:

1. Read the facts input, working directory, repo path, and preferred language or language fallback.
2. Classify sources as `current`, `reference`, `deprecated`, or `invalid`.
3. Create or refresh the source pack, scope boundary, assumptions ledger, execution boundary, current manifest, source status registry, lane registry, decision registry, sequence registry, and CARD registry.
4. Resolve the execution boundary before B2 Frontier dispatch. Primary takes the repo path as the product code entry point, then infers base branch, source roots, test entrypoints, worktree policy, writable/read-only/forbidden paths, side effects, and data risk from Git metadata, repo files, CI files, package metadata, and common project layouts. Primary asks follow-up questions only when inference is ambiguous, risky, or impossible.
5. Split the project into CARDs before dispatching Frontier lanes.
6. Decide how many Frontier lanes are useful based on project complexity, dependencies, risk, and parallel safety.
7. Write full Frontier prompt records and short Frontier launchers for selected lanes.
8. Dispatch selected Frontier lanes directly when the agent tool supports it; otherwise print fallback Frontier launchers as copyable fenced `prompt` blocks.

Primary defaults to **at least two Frontier lanes** for normal or medium-complexity projects when two safe independent CARD clusters exist. It launches one Frontier only when the project is clearly small, only one safe lane exists, or the user explicitly asks for a single lane. Broad or medium-high-complexity projects normally receive two to five Frontier lanes. More than five requires explicit user approval.

## Manual Primary And Frontier Startup

After the skills are installed, you can also manually start a new Primary or Frontier.

Manual Primary launcher:

```prompt
Use primary-orchestrator-openaccp to start OpenACCP coordination for this project.

Facts input: <source pack, PRD, spec, design document, facts folder, or uploaded materials>
Working directory: <where OpenACCP may write .openaccp coordination files>
Repo path: <actual product Git repository path, or "no repo yet">
Preferred language: <English / Chinese / your choice>

First review the facts, coordination workbench, and product repo path. Create or refresh the source pack, scope boundary, assumptions ledger, execution boundary, current manifest, source status registry, lane registry, decision registry, sequence registry, and CARD registry. Infer base branch, source roots, test entrypoints, and worktree policy from the repo before B2 Frontier dispatch; ask only for ambiguous or risky execution choices. Split the project into enough CARDs to support useful parallel Frontier lanes. Then return a human-readable status report, dispatch selected Frontier lanes directly when possible, and provide manual fallback launchers only when direct dispatch is unavailable.
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

OpenACCP uses classified project facts as the coordination anchor. Artifacts are the audit trail and control surface that keep those facts, authority boundaries, handoffs, and decisions visible across orchestrators.

```text
Primary
  -> writes CARDs, authority charters, and Frontier prompt records
  -> dispatches Frontier lanes or records fallback launchers

Frontier
  -> reads assigned CARDs and source pack
  -> runs B0/B1/B2 lane-local closure
  -> dispatches worker/reviewer/discovery subagents when safe
  -> consumes child handoffs
  -> writes lane status, child ledger, lane-progress packet, and frontier closure proof

worker / reviewer / discovery
  -> returns handoff, review report, machine summary, or evidence summary
  -> wakes the owning orchestrator after writing the return artifact

Primary
  -> consumes handoffs and reviewer evidence
  -> cross-checks Frontier closure proof before final accepted consume of a Frontier return
  -> accepts, rejects, amends, splits follow-up, or asks for a B3 human decision
```

OpenACCP uses a return wake owner rule. A child return should not depend on a human noticing it in the sidebar. A returning Frontier wakes Primary. A worker or reviewer wakes the orchestrator that spawned it: Primary if Primary spawned it, or Frontier if Frontier spawned it. The wake is short and points to the written artifact; it is not acceptance. The owner still has to consume the evidence.

When direct thread messaging exists, the child sends a short wake to the owner. When it does not, the child writes `.openaccp/coordination/wake-pending/<wakeId>.json` so the pending consume is visible in the coordination workbench. Heartbeat polling can still be used as a temporary safety net, but it is not the normal return path.

Important artifacts:

| Artifact | Plain meaning |
|---|---|
| `source pack` | The current fact list. It tells agents what may drive implementation and what is only background. |
| `scope boundary` | The line between allowed work and forbidden work. |
| `assumptions ledger` | Explicit assumptions that are not fully proven yet. |
| `execution boundary` | Repo path, inferred base branch, source roots, test entrypoints, worktree policy, writable/read-only/forbidden paths, side effects, data risk, and the `b2DispatchGate` that says whether product-write B2 work is ready, blocked, or coordination-only. |
| `current manifest` | The current coordination anchor: source pack, execution boundary, source status registry, lane registry, CARD registry, and active lanes. |
| `sequence registry` | Prompt IDs, Response IDs, handoffs, consumes, cards, active lanes, lifecycle states, and current/latest pointers. |
| `source status registry` | Current, reference, deprecated, invalid, and unknown sources with reasons and locators. |
| `lane registry` | Primary and Frontier lanes, project complexity, Frontier dispatch mode, lane-count reason, assigned CARDs, authority, child ledger refs, consume refs, closure refs, return-gate state, and per-lane B2 dispatch mode. |
| `child ledger` | Worker, reviewer, discovery, validation, or task-card-only child lifecycle, return wake contract, handoff status, wake status, consume status, and remaining risk. |
| `decision registry` | Owner questions, Primary decisions, waivers, out-of-scope decisions, blockers, and safe defaults. |
| `CARD` | A project-level work slice large enough for lane planning. A CARD can later become several task cards. |
| `task card` | A bounded executable task with scope, acceptance, verification, and stop conditions. |
| `authority charter` | The permission contract: who can read, who can write, allowed effects, forbidden effects, and data risk. |
| `prompt record` | The full role prompt saved on disk and executed by Prompt ID. |
| `short launcher` | A compact seed that points a thread to the full prompt record. It is printed in chat only when manual fallback is needed. |
| `handoff` | Evidence from a worker, reviewer, or discovery agent. It proves some things and leaves other things unproven. |
| `return wake` | A concise packet that tells the owning orchestrator a child has returned and which artifact needs consume or inspection. |
| `consume result` | The orchestrator decision about what a handoff actually proves before acceptance. For Frontier returns, a final accepted consume should cite the `closureId`, `laneId`, or closure path in `basisRefs` and validate against that `frontier closure`. |
| `lane-progress packet` | A stage packet showing useful Frontier progress. It stays inside the lane by default and becomes Primary evidence only when closure is ready. |
| `frontier closure` | The gate proof for whether a Frontier can keep working, close, or return to Primary. A Primary-ready packet is valid only when this proof shows that all visible remaining gaps are final-authority-only or explicitly out. |
| `formal report` | Human-readable status: what changed, progress, area, goal, gaps, next action, and evidence. |
| `machine summary` | Compact locators for downstream agents and validators. |

## Role Model

| Role | What it does | Authority boundary |
|---|---|---|
| `Primary` | Owns project-level coordination, CARD decomposition, lane dispatch, final consume, and final acceptance decisions. | Keeps final acceptance separate from worker claims, reviewer recommendations, and validator pass. |
| `Frontier` | Owns one lane. It keeps closing B0/B1/B2-safe work by refreshing backlog, dispatching subagents, consuming child handoffs, and writing lane-progress packets. It prepares a Primary-ready packet only when the return gate proves no lane-local safe work remains. | Runs lane orchestration and reserves B3 final authority for Primary or the human owner. |
| `worker` | Executes one bounded task card and returns verification evidence. | Stays inside the assigned task card, authority charter, and stop conditions. |
| `reviewer` | Performs read-only review of scope, correctness, verification, side effects, and overclaiming. | Stays read-only and returns recommendations as evidence. |
| `discovery` | Reads facts, classifies gaps, and prepares safe next actions. | Keeps source promotion under explicit authority. |
| `human owner` | Decides product intent, risk acceptance, customer-visible release, public publication, production launch, and high-risk exceptions. | Receives questions only when the next useful step needs owner facts or owner-reserved final authority. |

## B0 / B1 / B2 / B3

These levels answer one practical question: **how much authority does this agent have right now?**

| Level | Plain meaning | Typical actions |
|---|---|---|
| `B0` | Read-only discovery and review. | Source discovery, risk scan, evidence review, backlog refresh, source classification. |
| `B1` | Package preparation. | CARD shaping, task-card drafts, verification matrices, owner questions, handoff schema, dispatch-ready packets. |
| `B2` | Scoped execution under an authority charter. | Worker dispatch, worktree setup, bounded implementation, focused verification, child handoff consume. |
| `B3` | Final authority. | Primary may act only on decisions listed in `delegatedFinalAuthority`; production launch, public publication, customer-visible release, and risk waiver stay with the human owner by default. |

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
- integrations, external systems, and platform behavior,
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
| `frontier-orchestrator-openaccp` | Run one bounded lane. Use it for lane backlog, discovery, package preparation, worker/reviewer dispatch, and child handoff consume. | Helps avoid early Frontier return when B0/B1/B2 work can still continue. |
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

When Primary final-accepts a Frontier return or Primary-ready packet, the consume result cites the closure proof in `basisRefs` and is checked against that `frontier closure`. That cross-check keeps a stage-progress packet from being treated as final lane acceptance.

### Human-Readable Status

OpenACCP rejects machine-log replies as the main user-facing answer. A useful status says what changed, what is proven, what is provisional, what is missing, and what happens next.

Every Primary, Frontier, worker, reviewer, discovery, bootstrap, and validation reply uses `human-explain-openaccp` style. Status-like replies end with a practical recommended next step. If the agent can continue, the answer names the next Primary-owned or Frontier-owned action. If human input is needed, it names the exact path, fact, repo boundary, branch, source root, test entrypoint, approval, or decision.

## Minimum Useful Setup

The smallest useful OpenACCP package is the single-worker flow. It matches `examples/single-worker-flow/` and contains nine artifacts:

```text
source pack
task card
authority charter
worker handoff
review report
consume result
status report
machine summary
formal report
```

Multi-lane coordination adds these artifacts when Primary needs Frontier lanes, execution boundaries, and shared state:

```text
scope boundary
assumptions ledger
CARD registry
execution boundary
current manifest
sequence registry
lane registry
child ledger
source status registry
decision registry
frontier closure
```

When the minimum package inputs are missing, start with `bootstrap-openaccp` so implementation begins from task cards, acceptance criteria, verification plans, and stop conditions.

## Repository Map

```text
docs/        Concepts, role model, authority model, bootstrap, coordination, validator rules.
templates/   Reusable Markdown templates for source packs, specs, prompts, reports, handoffs.
openaccp/    Python package, CLI, validator, and packaged JSON Schemas under openaccp/schemas/.
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
- `examples/multi-frontier-closure/`: strict fixture for execution boundary, lane registry, child ledger, source status, decision registry, and Frontier closure.
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

`openaccp init` is a dry run by default. It is a bootstrap fallback. For real projects, install the skills first, then let Primary create project-specific prompt records and launchers from your facts input, working directory, and repo path.

## How It Compares

OpenACCP sits around the tools that run agents.

A prompt tells one agent what to try next. A loop keeps one agent moving until a check passes. A spec tells agents what the product should become. OpenACCP coordinates the project around all of that.

Loops help an agent finish a task. OpenACCP helps a team of agents finish a project.

- **Codex, Claude Code, Aider, OpenHands, and SWE-agent** are strong places to run coding work. OpenACCP gives that work a shared source pack, CARDs, authority boundaries, handoffs, return wake, reviews, and consume decisions.
- **LangGraph, CrewAI, AutoGen, and the OpenAI Agents SDK** help teams build agent frameworks, flows, graphs, tools, and application-level agent behavior. OpenACCP adds the project delivery layer: which facts count, who can act, what evidence came back, which returns need consume, and who can accept the result.
- **Agent loops** keep one lane of work alive. OpenACCP keeps multiple lanes aligned, especially when a returned handoff, reviewer result, or Frontier closure needs the right owner to consume it.
- **Spec-driven workflows** make intent clearer. OpenACCP carries that intent into execution, review, handoff, and final acceptance so the source facts remain visible after agents start changing files.

The practical difference is simple: OpenACCP lets you keep your current agent tool while adding a shared coordination protocol for source facts, roles, authority, evidence, and acceptance.

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

Author: Ocean Liu / Liu HanYang
