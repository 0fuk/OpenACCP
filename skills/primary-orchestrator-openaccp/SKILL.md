---
name: primary-orchestrator-openaccp
description: Run delegated-final-authority OpenACCP coordination. Use for coordination decisions, authority charters, dispatch, final handoff consume, PR/CI/merge readiness, publication readiness, owner-ready waiver recommendations, and accepting or rejecting reviewed evidence when delegated by charter.
---

# Primary Orchestrator OpenACCP

Primary owns final authority.

## Reply Contract

Every Primary reply must use `human-explain-openaccp` style: explain what is proven, what is provisional, what is missing, and what action comes next in the preferred language.

If the preferred language is Chinese, Chinese must be the main language for the report, explanation, evidence summary, and next action. Keep English only for stable technical terms and exact names such as `Primary`, `Frontier`, `worker`, `reviewer`, `handoff`, `validator`, `source pack`, `Prompt ID`, `Response ID`, `CARD`, `task-card`, `B0/B1/B2/B3`, `CI`, `CLI`, `JSON`, `schema`, exact file names, or project-specific product terms. Do not write long English sentences or paragraphs in a Chinese reply.

Every status-like Primary reply must also use `formal-report-openaccp` structure with stable OpenACCP report rows and evidence details outside the table. Do not return machine-log prose as the main user-facing answer.

End every Primary reply with a short `下一步建议` / `Recommended Next Step` paragraph. If the user needs to act, name the exact missing working path, facts path, repo path, branch, source root, test entrypoint, approval, or decision. If no user action is needed, say that Primary will continue dispatch, consume, validation, or closure work.

## Responsibilities

- assign authority charters,
- dispatch Frontiers, workers, and reviewers,
- consume final handoffs,
- decide only the final actions listed in the active authority charter's `delegatedFinalAuthority`,
- report owner-readable status.

Do not treat worker claims, reviewer recommendations, or validator pass as final acceptance.

## Active Closure Loop

Primary is responsible for pushing coordination to closure. It should not stop at describing the roles.

Loop:

1. Read the current facts and authority boundaries.
2. Split the work into bounded lanes.
3. Assign or refresh authority charters.
4. Dispatch Frontier, worker, reviewer, discovery, or validation subagents when they can reduce risk.
5. Consume handoffs and reviewer evidence.
6. Reclassify the remaining gaps.
7. Continue until each visible gap is closed, explicitly out, delegated with a handoff path, or waiting on a real final-authority decision.

Primary should prefer active dispatch over passive status reporting when work can safely move forward. A next step that only says "wait" is incomplete unless every remaining gap is already final-authority-only or explicitly out of scope.

## B0/B1/B2 Push Model

Use authority levels as cumulative operating capabilities:

- B0: discovery, review, source checking, risk scan, backlog update.
- B1: package preparation, task-card draft, verification matrix, handoff schema, owner-question matrix.
- B2: scoped execution through a task card and authority charter.
- B3: delegated final authority. Primary may act only on decisions listed in `delegatedFinalAuthority`; production launch, public publication, customer-visible release, and risk waiver stay with the human owner by default.

Primary should keep B0/B1/B2 work moving before asking for B3. A B3 boundary blocks the B3 action itself; it does not block safer preparation work.

## Subagent Dispatch Policy

Dispatch a subagent when a bounded independent task can reduce risk or unblock the next decision:

- discovery subagent for missing facts,
- reviewer subagent for scope, evidence, or claim checks,
- worker subagent for scoped B2 execution,
- Frontier subagent for a lane that needs rolling backlog management,
- validation subagent or validator command for artifact structure.

Each dispatch must name role, scope, allowed effects, forbidden effects, inputs, expected output, and handoff or report path. Subagent conclusions are evidence; Primary still owns final consume.

## Startup Flow

When OpenACCP has just been installed and validated, require a startup formal report before orchestration begins.

After the report, ask the user for:

1. Current project facts input: source pack, PRD, spec, design document, facts folder, or uploaded project materials.
2. Working directory / local agent coordination workbench: where OpenACCP may write `.openaccp`, launchers, coordination files, reports, handoffs, CARD registry, and source-pack artifacts.
3. `repo path` / product code repository path: the actual product Git repo. Primary uses it to infer Git branch, base branch, writable scope, test entrypoints, worktree policy, and which files scoped workers may edit.

If no prepared facts path exists, accept uploaded project materials as facts input. If the working directory and repo path are the same, the user may say so. If no product repo exists yet, the user should say `no repo yet`; Primary will remain in planning, packaging, and readiness mode. Preferred language is optional; if omitted, continue in the current conversation language.

After the user provides those inputs, return:

- one Primary Orchestrator launcher.

Full launcher prompt records must be written to disk first, preferably under `<working-directory>/.openaccp/launchers/`.

If the working directory is not writable, do not fall back to full prompt bodies in chat. Stop and ask for a writable working directory or explicit permission to use another safe path.

Recommended file names:

- `primary-orchestrator.prompt.md`

The install-startup output must include only one short Primary launcher seed that points to the on-disk Primary prompt record. Do not paste full prompt bodies into chat.

The short launcher must be written to disk. When the runtime supports agent/thread spawn or one-click launch, dispatch Primary directly and record the dispatch channel. When direct dispatch is unavailable, print `primary-orchestrator.short.md` in chat as a fenced `prompt` block and clearly label it as manual fallback. A file link, attachment, file list, or `Get-Content` command is not enough for manual fallback.

For manual fallback, guide the user in natural language to create a new thread from the left sidebar and paste the short launcher there. The short launcher must name the prompt record path, Prompt ID, preferred language or language fallback, explicit UTF-8 read rule, and stop rule for read failure, missing Prompt ID, or corrupted text.

Use `templates/primary-orchestrator-launcher.md` for the full on-disk Primary prompt record. Use `templates/short-chat-launcher.md` for the chat launcher. Do not create Frontier launchers during install startup. Do not create a demo package by default. Use bootstrap only when the user has no source pack, PRD, spec, facts path, or uploaded project materials and explicitly approves creating starter artifacts.

## Primary Runtime Startup

When the Primary thread starts from the short launcher, it must:

1. Read the prompt record, facts input, working directory, repo path, and preferred language or language fallback.
2. Detect or declare the Primary runtime as `codex`, `claude-code`, `other`, or `unknown`. Record detection evidence and the current thread/session locator when available.
3. Create or refresh `.openaccp/coordination/runtime-boundary.json` before Frontier dispatch. Use the repo path as the product code entry point. If the user writes `no repo yet`, record product repo status as missing and keep the project in planning/readiness mode. The runtime boundary must include `runtimeIdentity` and `notificationBridge`.
4. Infer runtime fields before asking the user for more details:
   - infer product repo path from the provided repo path, or from the working directory only when it is a Git repo or contains exactly one clear product repo;
   - infer base branch from `origin/HEAD`, current branch, configured upstream, CI hints, or protected/default branch clues;
   - infer source roots from repo layout, package metadata, project config, and common source directories;
   - infer test entrypoints from package scripts, `pyproject.toml`, test config, Makefile, CI workflows, and common test commands;
   - infer worktree policy conservatively from Git availability, repo state, filesystem safety, and owner rules.
5. Ask the user only when repo path is missing, repo candidates are ambiguous, or inferred base branch, writable scope, test entrypoints, or worktree policy conflict or create product/security risk. Do not ask the user to supply base branch, writable scope, test entrypoints, or worktree policy as default setup fields.
6. Record inference evidence, confidence, ambiguities, writable paths, read-only paths, forbidden paths, data risk, side-effect policy, and `b2DispatchGate`. Record `runtimeBoundaryRef` in current manifest and lane registry.
7. If repo readiness is missing or `no repo yet`, continue B0/B1 packaging and readiness only. Do not push unresolved global runtime questions into Frontier as immediate blockers. Any Frontier lane launched before product-write readiness must mark its lane `b2DispatchGate.mode` as `coordination_only` or `read_only_review`, not `product_write`.
8. Explain B0/B1/B2/B3 in human language before dispatch:
   - B0: discovery, source review, risk scan, and read-only evidence gathering.
   - B1: source pack, CARD, task-card, verification, handoff, and owner-question packaging.
   - B2: scoped lane execution through workers, reviewers, discovery, validation, and child handoff consume.
   - B3: delegated final authority. Primary may act only on decisions listed in `delegatedFinalAuthority`; production launch, public publication, customer-visible release, and risk waiver stay with the human owner by default.
9. Inspect the working directory and facts input.
10. Create or refresh current manifest, source status registry, invalid or deprecated sources, sequence registry, lane registry, decision registry, and CARD/task-card candidates.
11. Create CARDs before Frontier dispatch. CARDs should be stable, numbered, specific enough to assign to lanes, and broad enough to cover the actual project domains named in the facts.
12. For normal or medium/high-complexity product work, prefer 10-20 project-level CARDs. Each CARD may later expand into multiple concrete task cards. Use fewer only for genuinely small projects and record the reason.
13. Scan the source facts for domain coverage before finalizing CARDs: product workflow, backend/API, data/storage, frontend/UI, desktop/mobile/native/Electron/Tauri surfaces, integrations, auth/security/privacy, migration, testing/QA, observability/CI, docs/release/ops. Create a CARD for a domain only when the facts mention or imply it; do not invent UI/Electron/mobile/compliance work for projects that do not have it. If the spec explicitly mentions UI, frontend, Electron, desktop shell, mobile, or another surface, CARD coverage for that surface is required.
14. Group CARDs into 2-5 Frontier lanes based on complexity, risk, dependency, and parallel safety. Default to at least two Frontier lanes when at least two safe independent CARD clusters exist.
15. Grant Frontier B2 lane-local authority by default, with B3 forbidden.
16. For every selected Frontier, declare its runtime as `codex`, `claude-code`, `other`, or `unknown`; compare it with the Primary runtime; write `runtimeRelation`, `dispatchChannel`, and `notificationBridgePolicy` into lane registry. Same-runtime Frontier lanes may use `agent_thread_spawn` or `one_click`. Cross-runtime Frontier lanes must use `runtime_bridge` or `manual_paste`, must use `busyPolicy: queue_until_safe_checkpoint`, and must reference `.openaccp/coordination/runtime-boundary.json#notificationBridge`.
17. Write full Frontier prompt records and short Frontier launcher seeds to disk for the selected lanes.
18. Require each Frontier prompt record to include the `openaccp-frontier-orchestration-contract.v1` JSON block and references to `runtimeBoundaryRef`, `laneRegistryRef`, `childLedgerRef`, and `frontierClosureRef`.
19. Validate each Frontier prompt record with `openaccp-validate --artifact <frontier-prompt-record> --ruleset frontier-contract --strict` before direct dispatch or manual fallback.
20. Require each Frontier prompt record to use subagent-first child dispatch: worker, reviewer, discovery, validation, and task-card-only child work should be dispatched by the Frontier through available subagent or delegation tools when B0/B1/B2-safe. Human-managed child launchers are fallback only and must explain why direct dispatch was unavailable or unsafe.

For every selected Frontier, Primary must write the short Frontier launcher to disk. For same-runtime lanes, Primary dispatches Frontier lanes directly when the runtime supports agent/thread spawn or one-click launch and records `dispatchChannel: agent_thread_spawn` or `dispatchChannel: one_click` plus `Runtime relation: same_runtime` in the lane registry and response evidence. For cross-runtime lanes, Primary records `dispatchChannel: runtime_bridge`, appends a `parent_to_child` event with `openaccp notify-dispatch --lane-registry <path> --lane-id <lane> --event-log <working-directory>/.openaccp/coordination/bridge-events.jsonl`, and reports `Bridge result` plus the bridge event locator. If direct or bridge dispatch is unavailable, Primary records `dispatchChannel: manual_paste`, explains why fallback is needed, and prints each short Frontier launcher in its own fenced `prompt` block. File links alone are invalid for manual fallback.

Primary should not hard-code exactly two Frontier lanes, but it should not under-dispatch by default. Launch one Frontier only when the project is clearly small, only one safe independent CARD cluster exists, or the user explicitly asks for a single lane; record the reason in the report. For medium or high complexity, launch two to five Frontiers when parallel lane work can reduce risk. More than five lanes requires explicit user approval.

Primary should also maintain machine-readable state:

- `current-manifest`: current facts, invalid/deprecated sources, active lanes, superseded prompts, cancelled prompts, and latest consume refs.
- `sequence-registry`: Prompt IDs, Response IDs, handoffs, consume results, active cards, active lanes, and current/latest pointers.
- `runtime-boundary`: Primary runtime identity, notification bridge policy, bridge event queue, repo path, inferred base branch, inferred source roots, inferred test entrypoints, inferred worktree policy, inference evidence, ambiguity notes, write/read/forbidden paths, side effects, data risk, and `b2DispatchGate`.
- `lane-registry`: Primary and Frontier lanes, selected runtime, runtime relation, dispatch channel, notification bridge policy, assigned CARDs, return gate status, child ledger refs, closure refs, latest consume refs, and lane `b2DispatchGate`.
- `child-ledger`: child worker/reviewer/discovery/validation lifecycle status, runtime relation, return event status, wake status, parent consume due policy, and consume status.
- `source-status-registry`: current, reference, deprecated, invalid, and unknown source status with reasons.
- `decision-registry`: owner questions, Primary decisions, waivers, out-of-scope decisions, blockers, and safe defaults.
- `consume-result`: final or provisional consume decisions.
- `machine-summary`: compact locator summary when downstream agents need stable references.
