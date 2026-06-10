# Authority Boundary

OpenACCP uses B0/B1/B2/B3 to separate preparation, execution, and final authority.

## B0

Read-only discovery, source review, risk scan, reviewer dispatch, backlog classification, and status synthesis.

## B1

Package preparation: worker prompt drafts, reviewer prompt drafts, task-card-only planning, verification matrices, handoff schema drafts, and owner question packets.

B1 task cards may be delivered by a worker with a B1 handoff when the effect is limited to documentation, package preparation, read-only evidence, or review evidence. B1 worker handoffs do not authorize product-code implementation effects.

## B2

Scoped execution under a visible charter. A Primary-launched Frontier should default to B2 lane-local authority unless Primary explicitly narrows it. B2 requires assigned CARDs or task cards, allowed actions, forbidden actions, allowed files or effects, workspace or branch boundary, verification, handoff path, data-risk limits, resource-use limits, and stop conditions.

## B3

Final authority covers final acceptance, internal merge decisions, production launch, public publication, risk waiver, final coordination gates, cross-lane final decisions, unrestricted real resource use, broad dependency authorization, or destructive cleanup.

By default, production launch, public publication, customer-visible release, legal or risk waiver, credential approval, production data approval, and destructive cleanup are reserved to the `human-owner`.

Primary may exercise B3 only for decisions explicitly listed in an authority charter's machine-readable `delegatedFinalAuthority` array. Typical delegated Primary decisions are final consume of reviewed evidence, accept/amend/reject coordination evidence, internal merge-readiness decisions, or owner-ready recommendations. If a gap is not listed in `delegatedFinalAuthority`, it is `blocked_on_human`, not `blocked_on_primary`.

Use `blocked_on_primary` only when the required B3 decision is inside the Primary charter's `delegatedFinalAuthority` list. Use `blocked_on_human` when the decision is reserved to the human owner or needs business, legal, production, credential, customer-impact, or risk-waiver authority.

## Gap Decision Matrix

Classify each gap as:

- `do_now`
- `dispatch_current_thread_subagent`
- `prepare_package`
- `prepare_package_only_when_dispatch_unavailable`
- `apply_conservative_default`
- `needs_final_authority`
- `explicitly_out`

Return to final authority only when all visible gaps are `needs_final_authority` or `explicitly_out`.
