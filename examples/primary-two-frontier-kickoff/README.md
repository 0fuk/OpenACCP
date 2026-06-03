# Primary Plus Two Frontier Kickoff

This example shows the expected post-install startup output shape after a user provides a real working directory and a source pack, PRD, spec, facts path, or uploaded project materials.

It is not a demo package. It is a launcher pattern for starting real work.

## Required User Inputs

The agent should ask for:

- working directory, which is required,
- current source pack, PRD, spec, or facts path.

If no facts path exists yet, the user can upload project materials instead. The working directory is still required.

Optional but useful:

- writable paths,
- read-only reference paths,
- forbidden paths or side effects,
- known lanes or priorities.

## Output Shape

After the user provides project inputs, return:

1. One Primary Orchestrator launcher.
2. Two Frontier Orchestrator launchers.

Return the launchers as copyable prompt blocks in chat. Do not only write launcher files to disk. If files are written, still print the full prompt blocks.

Before each block, tell the user where to use it:

```text
Create a new thread from the left sidebar, paste the full Primary Orchestrator launcher below, and start that thread.
```

Then print the full launcher in a fenced `prompt` block. Repeat the same pattern for Frontier A and Frontier B.

Use:

- `templates/primary-orchestrator-launcher.md`
- `templates/frontier-orchestrator-launcher.md`

The launchers should include active closure and subagent dispatch rules. Primary should push the project toward closure by dispatching bounded agents and consuming evidence. Each Frontier should run a B0/B1/B2 lane loop and return only when the lane has closure proof or a true final-authority blocker.

## Example Primary Launcher Summary

```text
Role: Primary Orchestrator
Authority: B3 final authority
Working directory: <user-provided path>
Facts input: <user-provided source pack, PRD, spec, facts path, or uploaded materials>
Goal: decide source status, authority boundaries, and lane split.
Next action: read the facts input, issue a startup formal report, then dispatch two bounded Frontier lanes.
```

## Example Frontier A Launcher Summary

```text
Role: Frontier Orchestrator
Authority: B0/B1 by default, B2 only if explicitly chartered
Lane: <lane A objective>
Working directory: <user-provided path>
Facts input: <user-provided source pack, PRD, spec, facts path, or uploaded materials>
Goal: discover gaps, prepare task cards, and identify safe worker packages for lane A.
```

## Example Frontier B Launcher Summary

```text
Role: Frontier Orchestrator
Authority: B0/B1 by default, B2 only if explicitly chartered
Lane: <lane B objective>
Working directory: <user-provided path>
Facts input: <user-provided source pack, PRD, spec, facts path, or uploaded materials>
Goal: discover gaps, prepare task cards, and identify safe worker packages for lane B.
```

If the facts input is not enough to define two lanes, the Primary launcher should say so and ask for the missing decision instead of inventing lanes.
