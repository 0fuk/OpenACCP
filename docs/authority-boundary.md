# Authority Boundary

OpenACP uses B0/B1/B2/B3 to separate preparation, execution, and final authority.

## B0

Read-only discovery, source review, risk scan, reviewer dispatch, backlog classification, and status synthesis.

## B1

Package preparation: worker prompt drafts, reviewer prompt drafts, task-card-only planning, verification matrices, handoff schema drafts, and owner question packets.

## B2

Scoped execution under a visible charter. A Primary-launched Frontier should default to B2 lane-local authority unless Primary explicitly narrows it. B2 requires assigned CARDs or task cards, allowed actions, forbidden actions, allowed files or effects, workspace or branch boundary, verification, handoff path, data-risk limits, resource-use limits, and stop conditions.

## B3

Final authority: merge, release, final acceptance, waiver, checkpoint, publication, cross-lane final decisions, unrestricted real resource use, broad dependency authorization, or destructive cleanup.

## Gap Decision Matrix

Classify each gap as:

- `do_now`
- `create_downstream_prompt`
- `prepare_package`
- `apply_conservative_default`
- `needs_final_authority`
- `explicitly_out`

Return to final authority only when all visible gaps are `needs_final_authority` or `explicitly_out`.
