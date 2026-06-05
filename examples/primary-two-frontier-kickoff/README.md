# Primary Plus Two Frontier Kickoff

This example shows the expected output shape after a Primary thread has inspected a real working directory, reviewed the facts input, created CARDs, and decided that two Frontier lanes are useful.

GitHub install startup returns one short Primary launcher. Frontier launchers are created later by Primary after CARD and lane analysis.

## Required Primary Inputs

Primary should already have:

- working directory, which is required,
- current source pack, PRD, spec, or facts path,
- preferred language,
- current manifest or manifest draft,
- CARD/task-card candidates.

If no facts path exists yet, the user can upload project materials instead. The working directory is still required.

Optional but useful:

- writable paths,
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
Preferred language: <user-provided language>
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
Assigned CARDs: <CARD ids>
Goal: discover gaps, prepare task cards, and identify safe worker packages for lane 02.
```

If the facts input is not enough to define two lanes, the Primary launcher should say so and ask for the missing decision instead of inventing lanes.
