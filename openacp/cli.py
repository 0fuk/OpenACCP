#!/usr/bin/env python3
"""OpenACP helper CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .validate import VERSION
except ImportError:  # pragma: no cover - supports direct script execution
    from validate import VERSION


def json_text(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def starter_files(target: Path) -> dict[Path, str]:
    return {
        target / "source-pack.json": json_text(
            {
                "schemaVersion": "openacp-source-pack.v1",
                "artifactType": "source-pack",
                "currentSources": [{"sourceId": "SRC-001", "title": "Current product note or PRD", "status": "current"}],
                "referenceSources": [],
                "deprecatedSources": [],
                "readingOrder": ["source-pack.json", "scope-boundary.json", "assumptions.json", "task-card.json"],
                "conflictPolicy": ["Current sources control task scope."],
                "scopeBoundaryRef": "scope-boundary.json",
                "openQuestionsRef": "open-questions.md",
                "assumptionsRef": "assumptions.json",
            }
        ),
        target / "scope-boundary.json": json_text(
            {
                "schemaVersion": "openacp-scope-boundary.v1",
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
                "schemaVersion": "openacp-assumption-ledger.v1",
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
                "schemaVersion": "openacp-authority-charter.v1",
                "artifactType": "authority-charter",
                "charterId": "CHARTER-001",
                "grantedRole": "worker",
                "authorityLevel": "B2",
                "allowedActions": ["Edit artifacts named in the task card.", "Run verification.", "Produce a handoff."],
                "forbiddenActions": ["Claim final acceptance.", "Merge or publish.", "Use credentials."],
                "delegationRules": ["Final authority cannot be delegated by the worker."],
                "finalAuthorityReservedTo": "Primary or human owner",
                "scopeLimits": ["Docs and specs only.", "No external side effects."],
                "expiresWhen": "The task is completed, rejected, amended, or revoked.",
            }
        ),
        target / "task-card.json": json_text(
            {
                "schemaVersion": "openacp-task-card.v1",
                "artifactType": "task-card",
                "taskId": "TASK-001",
                "objective": "Draft a starter spec from the current source.",
                "inputRefs": ["SRC-001"],
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
        target / "open-questions.md": "# Open Questions\n\n- What should final authority decide after the first reviewed handoff?\n",
    }


def init_command(args: argparse.Namespace) -> int:
    target = Path(args.target)
    files = starter_files(target)
    action = "create" if args.write else "would create"
    print(f"OpenACP init {'write' if args.write else 'dry run'}: {target}")
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
    parser = argparse.ArgumentParser(prog="openacp", description="OpenACP workflow helpers.")
    parser.add_argument("--version", action="version", version=f"OpenACP {VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init", help="Generate a starter OpenACP work package.")
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
