# Getting Started

OpenACCP has two adoption paths. Pick the shortest one that matches your current material.

For Codex or Claude Code startup, begin with `docs/codex-install-and-start.md`. The default path is to install skills, install the workflow kit, validate, produce a formal report automatically, then ask for three setup inputs: facts input, working directory, and repo path. The facts input can be a source pack, PRD, spec, facts folder, design document, or uploaded project materials. The working directory is the OpenACCP coordination workbench. The repo path is the actual product Git repository; Primary uses it to infer base branch, writable scope, test entrypoints, and worktree policy. Preferred language is optional and defaults to the current conversation language. After those inputs arrive, startup writes one short Primary launcher seed and starts Primary directly when the agent tool supports agent/thread spawn or one-click launch. If direct dispatch is unavailable, startup prints the short launcher in chat as manual fallback. Primary later reviews the workspace, creates CARDs, and decides whether to launch Frontier lanes.

For normal or medium-complexity projects, Primary should usually create enough CARDs to support useful parallelism and then launch at least two Frontier lanes when two safe independent CARD clusters exist. One Frontier is only for a clearly small project, a single safe lane, or an explicit user request, and Primary must state that reason. Medium-high projects usually need two to five Frontiers; more than five requires explicit user approval.

## Path A: I Only Have A PRD

Use OpenACCP Bootstrap when the project starts from a rough PRD, product note, or vague design.

1. Fill `templates/prd-intake.md`.
2. Create `source-pack.json` from the current note or PRD.
3. Create `scope-boundary.json` to name what is in, out, deferred, and approval-gated.
4. Record assumptions in `assumptions.json`.
5. Draft starter specs from `templates/spec-starter/`.
6. Create the first `task-card.json`.
7. Add `authority-charter.json` if the task requires B2 execution.
8. Validate the task card with the source pack.

The Bootstrap path prevents agents from inventing a spec or treating old brainstorming as current truth.

## Path B: I Already Have A Work Package

Use OpenACCP Coordination when the project already has enough facts to dispatch agents.

1. Confirm the current source pack.
2. Define roles and authority boundaries.
3. Split backlog into lanes and task cards.
4. Dispatch scoped workers in separate workspaces or branches.
5. Require structured handoffs.
6. Run sidecar review.
7. Let Primary or the human owner consume reviewed evidence.

## Minimum Safe Flow

The minimum package is the single-worker flow shown in `examples/single-worker-flow/`. It contains the nine artifacts needed to validate one bounded task from source facts through review and consume:

```text
source pack -> task card -> authority charter -> worker handoff -> review report -> consume result -> status report -> machine summary -> formal report
```

Use the Bootstrap path when the source pack or task card is missing. Use the Coordination path when the project needs the larger multi-lane package: scope boundary, assumptions ledger, CARD registry, execution boundary, current manifest, sequence registry, lane registry, child ledger, source status registry, decision registry, and Frontier closure.
