# Primary Plus Two Frontier Kickoff

This example shows the expected output shape after a Primary thread has inspected the project facts, coordination workbench, product repo path, created CARDs, and decided that two Frontier lanes are useful.

GitHub install startup returns one short Primary launcher. Frontier launchers are created later by Primary after CARD and lane analysis.

## Required Primary Inputs

Primary should already have:

- facts input: source pack, PRD, spec, design document, facts folder, or uploaded project materials,
- working directory: the local agent coordination workbench where OpenACCP may write `.openaccp`, launchers, coordination files, reports, handoffs, CARD registry, and source-pack artifacts,
- repo path: the actual product Git repository path, or `no repo yet`,
- preferred language or current conversation language fallback,
- current manifest or manifest draft,
- runtime boundary with Primary-inferred Git branch, base branch, source roots, writable scope, test entrypoints, worktree policy, and worker-editable files,
- CARD/task-card candidates.

If no facts path exists yet, the user can upload project materials instead. If the working directory and repo path are the same, the user can say so. If no product repo exists yet, the user can say `no repo yet`; Primary then keeps product-write B2 closed and continues planning, packaging, and readiness work.

Optional but useful:

- read-only reference paths,
- forbidden paths or side effects,
- known lanes or priorities.

## Output Shape

After Primary decides that two Frontier lanes are useful, return:

1. One `Frontier 01` launcher.
2. One `Frontier 02` launcher.

Write the full launcher prompt records to disk first, preferably under:

```text
<working-directory>/.openaccp/launchers/
```

Then return short copyable launchers in chat. Do not paste the full prompt bodies into chat.

The short launcher files may also be written to disk, but the chat response must include the exact short launcher text in fenced `prompt` blocks. Do not give only file links, attachments, file lists, or `Get-Content` commands.

Before each short launcher block, tell the user where to use it:

```text
Create a new thread from the left sidebar, paste the short Frontier launcher below, and start that thread.
```

Then print the short launcher in a fenced `prompt` block. Repeat the same pattern for `Frontier 01` and `Frontier 02`.

Example short chat launcher:

```prompt
<Project> - Frontier 01 - Source Pack Lane
Purpose: start the source-pack and scope-baseline lane.

Read and execute this OpenACCP prompt record:
- Prompt Record: <working-directory>/.openaccp/launchers/frontier-01.prompt.md
- Prompt ID: openaccp-frontier-01-source-pack
- Preferred language: <user-preferred-or-current-language>

Hard requirements:
1. Read the prompt record explicitly as UTF-8.
2. Execute only the named Prompt ID.
3. If the file cannot be read cleanly, the Prompt ID is missing, or the text appears corrupted, stop and report launcher-read failure.
```

Use:

- `templates/primary-orchestrator-launcher.md`
- `templates/frontier-orchestrator-launcher.md`

The launchers should include active closure and subagent dispatch rules. Each Frontier should run a B0/B1/B2 lane loop under B2 lane-local authority and return only when the lane has closure proof or a true final-authority blocker.

## Example Primary Decision Summary

```text
Role: Primary Orchestrator
Authority: B3 final authority
Working directory: <user-provided path>
Facts input: <user-provided source pack, PRD, spec, facts path, or uploaded materials>
Repo path: <actual product Git repo path, or no repo yet>
Preferred language: <user-provided language>
Runtime boundary: <Primary-inferred base branch, source roots, writable scope, test entrypoints, and worktree policy>
CARDs: <CARD list created by Primary>
Goal: decide source status, authority boundaries, and lane split.
Next action: dispatch the selected B2 Frontier lanes and consume their provisional evidence.
```

## Example Frontier 01 Launcher Summary

```text
Role: Frontier Orchestrator
Authority: B2 lane-local
Lane: <lane 01 objective>
Working directory: <user-provided path>
Facts input: <user-provided source pack, PRD, spec, facts path, or uploaded materials>
Repo path: <actual product Git repo path, or no repo yet>
Runtime boundary: <Primary-inferred fields and b2DispatchGate>
Assigned CARDs: <CARD ids>
Goal: discover gaps, prepare task cards, and identify safe worker packages for lane 01.
```

## Example Frontier 02 Launcher Summary

```text
Role: Frontier Orchestrator
Authority: B2 lane-local
Lane: <lane 02 objective>
Working directory: <user-provided path>
Facts input: <user-provided source pack, PRD, spec, facts path, or uploaded materials>
Repo path: <actual product Git repo path, or no repo yet>
Runtime boundary: <Primary-inferred fields and b2DispatchGate>
Assigned CARDs: <CARD ids>
Goal: discover gaps, prepare task cards, and identify safe worker packages for lane 02.
```

If the facts input is not enough to define two lanes, the Primary launcher should say so and ask for the missing decision instead of inventing lanes.
