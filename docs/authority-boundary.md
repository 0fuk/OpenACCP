# Authority Boundary

OpenACP uses B0/B1/B2/B3 to separate preparation, execution, and final authority.

## B0

Read-only discovery, source review, risk scan, reviewer dispatch, backlog classification, and status synthesis.

## B1

Package preparation: worker prompt drafts, reviewer prompt drafts, task-card-only planning, verification matrices, handoff schema drafts, and owner question packets.

## B2

Scoped execution under an explicit charter. B2 requires allowed actions, forbidden actions, allowed files or effects, workspace or branch boundary, verification, handoff path, and stop conditions.

## B3

Final authority: merge, release, final acceptance, waiver, checkpoint, publication, cross-lane final decisions, unrestricted real resource use, or destructive cleanup.

## Gap Decision Matrix

Classify each gap as:

- `do_now`
- `create_downstream_prompt`
- `prepare_package`
- `apply_conservative_default`
- `needs_final_authority`
- `explicitly_out`

Return to final authority only when all visible gaps are `needs_final_authority` or `explicitly_out`.
