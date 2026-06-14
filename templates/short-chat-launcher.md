# Short Chat Launcher

Use this template for the short launcher seed written after the full prompt record has been written to disk. It can seed direct agent/thread spawn, one-click launch, or manual fallback.

Do not include the full prompt body in chat. The short launcher only points the new thread to the local prompt record.

The short launcher must be written to disk. When the runtime supports direct dispatch, use the saved launcher as the dispatch seed and record `dispatchChannel: agent_thread_spawn` or `dispatchChannel: one_click`. When direct dispatch is unavailable, print the short launcher in chat as a fenced `prompt` block and record `dispatchChannel: manual_paste`. A saved `.short.md` file is required for audit, but a file link, attachment, file list, or `Get-Content` command is not a substitute for the manual fallback chat block.

The first non-empty line is always the launcher title. It is plain text, not a Markdown heading. Use these slots:

- `<Project> - Primary Orchestrator - <Short Task>`
- `<Project> - Frontier 01 - <Short Task>` through `<Project> - Frontier 05 - <Short Task>`
- `<Project> - F01 Worker - <Short Task>` through `<Project> - F05 Worker - <Short Task>` for child fallback launchers owned by a Frontier lane
- `<Project> - PO Worker - <Short Task>` for child fallback launchers owned by Primary

The same pattern applies to Reviewer, Discovery, Validation, Task-Card Packager, and Task-Card Worker child fallback launchers. Do not use generic titles such as `Frontier Launcher`, `Frontier A`, or `Frontier B`.

```prompt
<Project> - Primary Orchestrator - <Short Task>
Purpose: <one short sentence>

Read and execute this OpenACCP prompt record:
- Prompt Record: <absolute-or-user-visible-path>
- Prompt ID: <prompt-id>
- Preferred language: <preferred-language-or-current-conversation-language>

Hard requirements:
1. Read the prompt record explicitly as UTF-8.
2. Execute only the named Prompt ID.
3. If the file cannot be read cleanly, the Prompt ID is missing, or the text appears corrupted, stop and report launcher-read failure.
```
