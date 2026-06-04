# Getting Started

OpenACP has two adoption paths. Pick the shortest one that matches your current material.

For Codex or Claude Code startup, begin with `docs/codex-install-and-start.md`. The default path is to install skills, install the workflow kit, validate, produce a formal report automatically, then ask for the required working directory, a source pack, PRD, spec, facts path or uploaded project materials, and the user's preferred language. After those inputs arrive, startup returns one short Primary launcher only; Primary later reviews the workspace, creates CARDs, and decides whether to launch 1-5 Frontier lanes.

## Path A: I Only Have A PRD

Use ACP Bootstrap when the project starts from a rough PRD, product note, or vague design.

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

Use ACP Coordination when the project already has enough facts to dispatch agents.

1. Confirm the current source pack.
2. Define roles and authority boundaries.
3. Split backlog into lanes and task cards.
4. Dispatch scoped workers in separate workspaces or branches.
5. Require structured handoffs.
6. Run sidecar review.
7. Let Primary or the human owner consume reviewed evidence.

## Minimum Safe Flow

```text
source pack -> scope boundary -> task card -> authority charter -> worker -> handoff -> reviewer -> final consume
```

If a step is missing, use discovery or bootstrap before implementation.
