#!/usr/bin/env python3
"""OpenACCP helper CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .version import VERSION
except ImportError:  # pragma: no cover - supports direct script execution
    from version import VERSION


def json_text(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def starter_files(target: Path) -> dict[Path, str]:
    return {
        target / "source-pack.json": json_text(
            {
                "schemaVersion": "openaccp-source-pack.v1",
                "artifactType": "source-pack",
                "currentSources": [{"sourceId": "SRC-001", "title": "Current product note or PRD", "status": "current"}],
                "referenceSources": [],
                "deprecatedSources": [],
                "readingOrder": ["source-pack.json", "scope-boundary.json", "assumptions.json", "card-registry.md", "task-card.json"],
                "conflictPolicy": ["Current sources control task scope."],
                "scopeBoundaryRef": "scope-boundary.json",
                "openQuestionsRef": "open-questions.md",
                "assumptionsRef": "assumptions.json",
            }
        ),
        target / "scope-boundary.json": json_text(
            {
                "schemaVersion": "openaccp-scope-boundary.v1",
                "artifactType": "scope-boundary",
                "inScope": ["Draft docs or specs from the current source."],
                "outOfScope": ["Runtime code changes.", "External side effects."],
                "deferred": ["Production integration."],
                "requiresHumanApproval": ["Credentials.", "Publication.", "Dependency changes."],
                "forbiddenActions": ["Use reference-only material as current scope.", "Claim final acceptance."],
                "stopConditions": ["A real side effect is needed.", "The current source is contradicted."],
                "scopeLeakExamples": ["Changing runtime behavior.", "Calling an external service."],
            }
        ),
        target / "assumptions.json": json_text(
            {
                "schemaVersion": "openaccp-assumption-ledger.v1",
                "artifactType": "assumption-ledger",
                "assumptions": [
                    {
                        "assumptionId": "ASM-001",
                        "statement": "The first slice can be docs-only.",
                        "evidence": "No implementation authority has been granted.",
                        "riskIfWrong": "The task may need a different authority charter.",
                        "canProceed": True,
                        "needsHumanConfirmation": False,
                        "expiresWhen": "The first executable task card is approved.",
                    }
                ],
            }
        ),
        target / "authority-charter.json": json_text(
            {
                "schemaVersion": "openaccp-authority-charter.v1",
                "artifactType": "authority-charter",
                "charterId": "CHARTER-001",
                "grantedRole": "worker",
                "authorityLevel": "B2",
                "allowedActions": ["Edit artifacts named in the task card.", "Run verification.", "Produce a handoff."],
                "forbiddenActions": ["Claim final acceptance.", "Merge or publish.", "Use credentials."],
                "delegationRules": ["Final authority cannot be delegated by the worker."],
                "finalAuthorityReservedTo": "human-owner",
                "delegatedFinalAuthority": [],
                "scopeLimits": ["Docs and specs only.", "No external side effects."],
                "dataRiskLimit": "low",
                "resourceUseLimit": ["Local filesystem and local verification only."],
                "allowedInputs": ["Current source pack, scope boundary, task card, and authority charter."],
                "allowedOutputs": ["Changed docs/spec artifacts, handoff, and machine summary."],
                "forbiddenSideEffects": ["Network calls.", "Credential use.", "External publication."],
                "stopConditions": ["Scope expands beyond docs/spec artifacts.", "Data risk exceeds low."],
                "expiresWhen": "The task is completed, rejected, amended, or revoked.",
            }
        ),
        target / "task-card.json": json_text(
            {
                "schemaVersion": "openaccp-task-card.v1",
                "artifactType": "task-card",
                "taskId": "TASK-001",
                "parentCardId": "CARD-001",
                "domain": "starter-spec",
                "objective": "Draft a starter spec from the current source.",
                "inputRefs": ["SRC-001"],
                "sourceStatusNote": "SRC-001 is current in source-pack.json.",
                "allowedScope": {"filesOrArtifacts": ["docs/**", "spec/**"], "effects": ["docs-only"]},
                "forbiddenScope": {
                    "filesOrArtifacts": ["src/**", "package-lock.json"],
                    "effects": ["dependency-change", "external-side-effect"],
                    "claims": ["accepted", "merged", "released"],
                },
                "acceptanceCriteria": ["The draft names the current source, assumptions, and open questions."],
                "verificationPlan": [{"check": "artifact review", "method": "read against task card", "required": True}],
                "stopConditions": ["Runtime implementation is required.", "A dependency change is required."],
                "expectedHandoff": {"artifactType": "handoff", "requiredFields": ["changedArtifacts", "verificationEvidence", "stateClaim"]},
                "authorityRequired": "B2",
                "authorityCharterRef": "authority-charter.json",
                "riskLevel": "low",
            }
        ),
        target / "card-registry.md": "\n".join(
            [
                "# CARD Registry",
                "",
                "schemaVersion: openaccp-card-registry.v1",
                "artifactType: card-registry",
                "",
                "## Domain Coverage",
                "",
                "| Domain | Present? | Source refs | CARD coverage | Notes |",
                "|---|---|---|---|---|",
                "| Product workflow / user journey | yes | SRC-001 | CARD-001 | Starter source describes the first product note or PRD. |",
                "| Backend / API / services | no | SRC-001 | none | No current fact supports this domain yet. |",
                "| Data / storage / migration | no | SRC-001 | none | No current fact supports this domain yet. |",
                "| Frontend / UI / design system | no | SRC-001 | none | No current fact supports this domain yet. |",
                "| Desktop shell / Electron / Tauri | no | SRC-001 | none | No current fact supports this domain yet. |",
                "| Mobile / native surfaces | no | SRC-001 | none | No current fact supports this domain yet. |",
                "| Integrations / external systems | no | SRC-001 | none | No current fact supports this domain yet. |",
                "| Auth / security / privacy | no | SRC-001 | none | No current fact supports this domain yet. |",
                "| Testing / QA / validation | no | SRC-001 | none | No current fact supports this domain yet. |",
                "| Observability / CI / release / ops | no | SRC-001 | none | No current fact supports this domain yet. |",
                "",
                "## Complexity Assessment",
                "",
                "- starter-package-reason: one CARD is enough only because this is a generated bootstrap skeleton.",
                "- small-project-reason: replace this line if the real project truly needs fewer than 10 CARDs.",
                "",
                "## CARD List",
                "",
                "| CARD | Domain | Authority | Lane | Status | Objective | Source | Task-card candidates |",
                "|---|---|---|---|---|---|---|---|",
                "| CARD-001 | starter-spec | B1/B2 | primary | ready-candidate | Build the first source-driven starter spec. | SRC-001 | TASK-001 |",
                "",
                "## Lane Grouping",
                "",
                "- primary: CARD-001 stays with Primary until real source facts justify Frontier lane dispatch.",
                "",
            ]
        ),
        target / "coordination" / "runtime-boundary.json": json_text(
            {
                "schemaVersion": "openaccp-runtime-boundary.v1",
                "artifactType": "runtime-boundary",
                "boundaryId": "RB-001",
                "workingDirectory": str(target),
                "productRepoStatus": "missing",
                "productRepoPath": "",
                "baseBranch": "",
                "sourceRoots": [],
                "testEntrypoints": [],
                "worktreePolicy": "unknown",
                "inferenceStatus": "not_attempted",
                "inferredFrom": [],
                "confidence": "unknown",
                "ambiguities": [],
                "allowedWritablePaths": [".openaccp/**", "docs/**", "spec/**"],
                "readOnlyPaths": [],
                "forbiddenPaths": [".git/**"],
                "externalSideEffects": "none",
                "dataRisk": "low",
                "unresolvedOwnerInputs": ["productRepoPath"],
                "b2DispatchGate": {
                    "state": "coordination_only",
                    "allowsProductWrite": False,
                    "reason": "Product repo fields are not resolved yet; continue B0/B1 packaging and coordination-only B2 work.",
                    "missingInputs": ["productRepoPath", "baseBranch", "sourceRoots", "testEntrypoints", "worktreePolicy"],
                },
            }
        ),
        target / "coordination" / "source-status-registry.json": json_text(
            {
                "schemaVersion": "openaccp-source-status-registry.v1",
                "artifactType": "source-status-registry",
                "registryId": "SRCSTAT-001",
                "sources": [
                    {
                        "sourceId": "SRC-001",
                        "status": "current",
                        "reason": "Bootstrap current source.",
                        "authority": "B3",
                        "locator": "source-pack.json#SRC-001",
                        "lastReviewedAt": "not_reviewed",
                    }
                ],
            }
        ),
        target / "coordination" / "sequence-registry.json": json_text(
            {
                "schemaVersion": "openaccp-sequence-registry.v1",
                "artifactType": "sequence-registry",
                "registryId": "SEQ-001",
                "currentPromptId": "PROMPT-BOOTSTRAP-001",
                "latestResponseId": "RESP-BOOTSTRAP-001",
                "prompts": [{"promptId": "PROMPT-BOOTSTRAP-001", "path": "bootstrap", "role": "primary", "status": "created"}],
                "responses": [{"responseId": "RESP-BOOTSTRAP-001", "promptId": "PROMPT-BOOTSTRAP-001", "path": "bootstrap", "status": "created"}],
                "handoffs": [],
                "cards": [{"cardId": "CARD-001", "status": "ready-candidate", "ownerRole": "primary"}],
                "consumes": [],
                "activeLanes": [{"laneId": "primary", "role": "primary", "status": "active", "currentPromptId": "PROMPT-BOOTSTRAP-001", "authorityLevel": "B3"}],
            }
        ),
        target / "coordination" / "lane-registry.json": json_text(
            {
                "schemaVersion": "openaccp-lane-registry.v1",
                "artifactType": "lane-registry",
                "registryId": "LANES-001",
                "projectComplexity": "bootstrap",
                "frontierDispatchMode": "pre_frontier",
                "dispatchChannel": "agent_thread_spawn",
                "frontierDispatchReason": "Generated bootstrap starter; Primary has not reviewed real project facts or dispatched Frontier lanes yet.",
                "lanes": [
                    {
                        "laneId": "primary",
                        "objective": "Bootstrap source-driven coordination.",
                        "role": "primary",
                        "status": "active",
                        "currentPromptId": "PROMPT-BOOTSTRAP-001",
                        "authorityLevel": "B3",
                        "assignedCardIds": ["CARD-001"],
                        "runtimeBoundaryRef": "runtime-boundary.json",
                        "childLedgerRef": "child-ledgers/primary.json",
                        "latestConsumeRefs": [],
                        "b2DispatchGate": {
                            "mode": "coordination_only",
                            "state": "ready",
                            "reason": "Bootstrap lane may write OpenACCP coordination artifacts only; no product repo writes are allowed.",
                        },
                        "returnGateStatus": {
                            "state": "not_applicable",
                            "safeWorkRemainingCount": 0,
                            "finalAuthorityGapCount": 0,
                            "explicitlyOutCount": 0,
                            "frontierClosureRef": "",
                            "latestChildLedgerRef": "child-ledgers/primary.json",
                            "latestConsumeRefs": [],
                        },
                    }
                ],
            }
        ),
        target / "coordination" / "child-ledgers" / "primary.json": json_text(
            {
                "schemaVersion": "openaccp-child-ledger.v1",
                "artifactType": "child-ledger",
                "ledgerId": "LEDGER-PRIMARY-001",
                "laneId": "primary",
                "children": [],
            }
        ),
        target / "coordination" / "decision-registry.json": json_text(
            {
                "schemaVersion": "openaccp-decision-registry.v1",
                "artifactType": "decision-registry",
                "registryId": "DEC-REG-001",
                "decisions": [
                    {
                        "decisionId": "OQ-001",
                        "type": "owner-question",
                        "status": "open",
                        "question": "What product repo path should Primary inspect? If there is no product repo yet, answer no repo yet. Primary will infer base branch, writable scope, test entrypoints, and worktree policy from the repo when available.",
                        "basisRefs": ["coordination/runtime-boundary.json"],
                        "blocks": ["B2 implementation dispatch"],
                        "safeDefault": "Continue B0/B1 source packaging only.",
                        "authorityRequired": "B3",
                    }
                ],
            }
        ),
        target / "coordination" / "current-manifest.json": json_text(
            {
                "schemaVersion": "openaccp-current-manifest.v1.1",
                "artifactType": "current-manifest",
                "manifestId": "MAN-001",
                "preferredLanguage": "unspecified",
                "workingDirectory": str(target),
                "factsInput": "source-pack.json",
                "currentSourcePackRef": "../source-pack.json",
                "invalidSourceRefs": [],
                "deprecatedSourceRefs": [],
                "sequenceRegistryRef": "sequence-registry.json",
                "laneRegistryRef": "lane-registry.json",
                "runtimeBoundaryRef": "runtime-boundary.json",
                "sourceStatusRegistryRef": "source-status-registry.json",
                "cardRegistryRef": "../card-registry.md",
                "activeLanes": [{"laneId": "primary", "role": "primary", "status": "active", "currentPromptId": "PROMPT-BOOTSTRAP-001", "authorityLevel": "B3"}],
                "supersededPromptIds": [],
                "cancelledPromptIds": [],
                "latestConsumeRefs": [],
            }
        ),
        target / "open-questions.md": "# Open Questions\n\n- What should final authority decide after the first reviewed handoff?\n",
    }


def init_command(args: argparse.Namespace) -> int:
    target = Path(args.target)
    files = starter_files(target)
    action = "create" if args.write else "would create"
    print(f"OpenACCP init {'write' if args.write else 'dry run'}: {target}")
    for path in files:
        print(f"- {action}: {path}")
    if not args.write:
        print("\nDry run only. Re-run with --write to create these files.")
        return 0
    existing = [path for path in files if path.exists()]
    if existing:
        print("Refusing to overwrite existing files:", file=sys.stderr)
        for path in existing:
            print(f"- {path}", file=sys.stderr)
        return 1
    target.mkdir(parents=True, exist_ok=True)
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="openaccp", description="OpenACCP workflow helpers.")
    parser.add_argument("--version", action="version", version=f"OpenACCP {VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init", help="Generate a starter OpenACCP work package.")
    init_parser.add_argument("target", help="Target directory for starter artifacts.")
    init_parser.add_argument("--write", action="store_true", help="Create files. Without this flag, init is a dry run.")
    init_parser.set_defaults(func=init_command)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args(argv or sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
