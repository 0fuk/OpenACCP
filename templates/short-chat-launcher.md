# Short Chat Launcher

Use this template for the copyable chat launcher shown to the user after the full prompt record has been written to disk.

Do not include the full prompt body in chat. The short launcher only points the new thread to the local prompt record.

```text
<Project> - <Role/Slot> - <Short Task>
Purpose: <one short sentence>

Read and execute this OpenACP prompt record:
- Prompt Record: <absolute-or-user-visible-path>
- Prompt ID: <prompt-id>

Hard requirements:
1. Read the prompt record explicitly as UTF-8.
2. Execute only the named Prompt ID.
3. If the file cannot be read cleanly, the Prompt ID is missing, or the text appears corrupted, stop and report launcher-read failure.
```

For Windows PowerShell, the short launcher may include:

```text
Get-Content -Encoding UTF8 -LiteralPath '<prompt-record-path>'
```
