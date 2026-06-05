#!/usr/bin/env python3
"""Self-tests for the OpenACP validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "openacp_validate.py"


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )


def assert_exit(name: str, proc: subprocess.CompletedProcess[str], expected: int) -> None:
    if proc.returncode != expected:
        print(f"FAIL {name}: expected {expected}, got {proc.returncode}")
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit(1)
    print(f"PASS {name}")


def source_pack() -> dict:
    return {
        "schemaVersion": "openacp-source-pack.v1",
        "artifactType": "source-pack",
        "currentSources": [{"sourceId": "SRC-001", "title": "Current PRD", "status": "current"}],
        "referenceSources": [{"sourceId": "REF-001", "title": "Old idea", "status": "reference"}],
        "deprecatedSources": [{"sourceId": "DEP-001", "title": "Discarded plan", "status": "deprecated"}],
        "readingOrder": ["source-pack.json", "scope-boundary.json", "card-registry.md", "task-card.json"],
        "conflictPolicy": ["Current sources win over reference sources."],
        "scopeBoundaryRef": "scope-boundary.json",
        "openQuestionsRef": "open-questions.md",
        "assumptionsRef": "assumptions.json",
    }


def task_card(authority: str = "B2") -> dict:
    return {
        "schemaVersion": "openacp-task-card.v1",
        "artifactType": "task-card",
        "taskId": "TASK-001",
        "parentCardId": "CARD-001",
        "domain": "docs/spec",
        "objective": "Create starter documentation",
        "inputRefs": ["SRC-001"],
        "sourceStatusNote": "SRC-001 is current in the accepted source pack.",
        "allowedScope": {"filesOrArtifacts": ["docs/**"], "effects": ["docs-only"]},
        "forbiddenScope": {
            "filesOrArtifacts": ["src/**"],
            "effects": ["external-side-effect"],
            "claims": ["accepted", "merged"],
        },
        "acceptanceCriteria": ["Documentation explains the workflow"],
        "verificationPlan": [{"check": "scan", "method": "validator", "required": True}],
        "stopConditions": ["Implementation needed"],
        "expectedHandoff": {"artifactType": "handoff", "requiredFields": ["verificationEvidence"]},
        "authorityRequired": authority,
        "authorityCharterRef": "authority-charter.json",
        "riskLevel": "low",
    }


def handoff() -> dict:
    return {
        "schemaVersion": "openacp-handoff.v1",
        "artifactType": "handoff",
        "handoffId": "HAND-001",
        "taskId": "TASK-001",
        "responseId": "RESP-001",
        "actorRole": "worker",
        "authority": "B2",
        "workspaceRef": "local-workspace",
        "worktree": "worktrees/docs-task-001",
        "branchRef": "docs/task-001",
        "baseCommit": "BASE-001",
        "commit": "COMMIT-001",
        "dataRisk": "low",
        "effectsPreset": "docs_task_card_commit",
        "changedFiles": ["docs/guide.md"],
        "changedArtifacts": [{"path": "docs/guide.md", "changeType": "created"}],
        "claims": ["Implemented starter documentation"],
        "verificationEvidence": [{"check": "scan", "method": "validator", "result": "pass", "exitCode": 0}],
        "deviations": [],
        "risks": [],
        "assumptionsUsed": [],
        "remainingWork": [],
        "stateClaim": "verified",
    }


def fixtures(tmp: Path) -> dict[str, Path]:
    paths = {
        "source_pack": tmp / "source-pack.json",
        "task_card": tmp / "task-card.json",
        "handoff": tmp / "handoff.json",
    }
    write_json(paths["source_pack"], source_pack())
    write_json(paths["task_card"], task_card())
    write_json(paths["handoff"], handoff())
    return paths


def valid_sequence_registry() -> dict:
    return {
        "schemaVersion": "openacp-sequence-registry.v1",
        "artifactType": "sequence-registry",
        "registryId": "SEQ-001",
        "currentPromptId": "PROMPT-001",
        "latestResponseId": "RESP-001",
        "prompts": [{"promptId": "PROMPT-001", "path": "prompt.md", "role": "primary", "status": "active"}],
        "responses": [{"responseId": "RESP-001", "promptId": "PROMPT-001", "path": "response.md", "status": "complete"}],
        "handoffs": [{"handoffId": "HAND-001", "taskId": "TASK-001", "cardId": "CARD-001", "path": "handoff.json", "status": "present"}],
        "cards": [{"cardId": "CARD-001", "status": "ready", "ownerRole": "primary"}],
        "consumes": [
            {
                "consumeId": "CONSUME-001",
                "responseId": "RESP-001",
                "targetHandoffIds": ["HAND-001"],
                "decision": "accepted",
                "authorityScope": "final",
            }
        ],
        "activeLanes": [{"laneId": "primary", "role": "primary", "status": "active", "currentPromptId": "PROMPT-001", "authorityLevel": "B3"}],
    }


def valid_runtime_boundary(tmp: Path) -> dict:
    return {
        "schemaVersion": "openacp-runtime-boundary.v1",
        "artifactType": "runtime-boundary",
        "boundaryId": "RB-001",
        "workingDirectory": str(tmp / "work"),
        "productRepoStatus": "found",
        "productRepoPath": str(tmp / "repo"),
        "baseBranch": "main",
        "sourceRoots": ["src"],
        "testEntrypoints": ["pytest"],
        "worktreePolicy": "allowed",
        "allowedWritablePaths": [".openacp/**", "worktrees/**"],
        "readOnlyPaths": ["source/**"],
        "forbiddenPaths": [".git/**"],
        "externalSideEffects": "none",
        "dataRisk": "low",
        "unresolvedOwnerInputs": [],
        "b2DispatchGate": {
            "state": "ready",
            "allowsProductWrite": True,
            "reason": "Product repo path, base branch, source roots, test entrypoints, and worktree policy are resolved.",
            "missingInputs": [],
        },
    }


def valid_lane_registry() -> dict:
    return {
        "schemaVersion": "openacp-lane-registry.v1",
        "artifactType": "lane-registry",
        "registryId": "LANES-001",
        "projectComplexity": "bootstrap",
        "frontierDispatchMode": "pre_frontier",
        "frontierDispatchReason": "Bootstrap registry before Frontier dispatch.",
        "lanes": [
            {
                "laneId": "primary",
                "objective": "Coordinate the project",
                "role": "primary",
                "status": "active",
                "currentPromptId": "PROMPT-001",
                "authorityLevel": "B3",
                "assignedCardIds": ["CARD-001"],
                "runtimeBoundaryRef": "runtime-boundary.json",
                "childLedgerRef": "child-ledger.json",
                "latestConsumeRefs": ["CONSUME-001"],
                "b2DispatchGate": {
                    "mode": "coordination_only",
                    "state": "ready",
                    "reason": "Primary coordination lane does not dispatch product-write workers.",
                },
                "returnGateStatus": {
                    "state": "not_applicable",
                    "safeWorkRemainingCount": 0,
                    "finalAuthorityGapCount": 0,
                    "explicitlyOutCount": 0,
                    "frontierClosureRef": "",
                    "latestChildLedgerRef": "child-ledger.json",
                    "latestConsumeRefs": ["CONSUME-001"],
                },
            }
        ],
    }


def valid_child_ledger() -> dict:
    return {
        "schemaVersion": "openacp-child-ledger.v1",
        "artifactType": "child-ledger",
        "ledgerId": "LEDGER-001",
        "laneId": "frontier-docs",
        "children": [
            {
                "promptId": "PROMPT-WORKER-001",
                "responseId": "RESP-WORKER-001",
                "taskId": "TASK-001",
                "handoffId": "HAND-001",
                "role": "worker",
                "authority": "B2",
                "effects": ["docs-only"],
                "subagentIdOrToolStatus": "direct-subagent",
                "expectedHandoffPath": ".openacp/handoffs/HAND-001.json",
                "dispatchStatus": "returned",
                "handoffStatus": "present",
                "consumeStatus": "consumed",
                "remainingRisk": "none",
            }
        ],
    }


def valid_source_status_registry() -> dict:
    return {
        "schemaVersion": "openacp-source-status-registry.v1",
        "artifactType": "source-status-registry",
        "registryId": "SRCSTAT-001",
        "sources": [
            {
                "sourceId": "SRC-001",
                "status": "current",
                "reason": "Accepted fact source.",
                "authority": "B3",
                "locator": "source-pack.json#SRC-001",
                "lastReviewedAt": "2026-06-05",
            },
            {
                "sourceId": "DEP-001",
                "status": "deprecated",
                "reason": "Superseded by SRC-001.",
                "authority": "B3",
                "locator": "source-pack.json#DEP-001",
                "lastReviewedAt": "2026-06-05",
            },
        ],
    }


def valid_decision_registry() -> dict:
    return {
        "schemaVersion": "openacp-decision-registry.v1",
        "artifactType": "decision-registry",
        "registryId": "DEC-REG-001",
        "decisions": [
            {
                "decisionId": "OQ-001",
                "type": "owner-question",
                "status": "open",
                "question": "Which repo branch should implementation workers use?",
                "basisRefs": ["runtime-boundary.json"],
                "blocks": ["B2 implementation dispatch"],
                "safeDefault": "Do B0/B1 packaging only.",
                "authorityRequired": "B3",
            }
        ],
    }


def valid_frontier_closure() -> dict:
    return {
        "schemaVersion": "openacp-frontier-closure.v1",
        "artifactType": "frontier-closure",
        "closureId": "FC-001",
        "laneId": "frontier-docs",
        "responseId": "RESP-FRONTIER-001",
        "authorityLevel": "B2",
        "branchState": "blocked_on_primary",
        "gapDecisionMatrix": [{"gap": "final acceptance", "decision": "needs_final_authority", "nextSafeAction": "Primary consume"}],
        "childLedgerRef": "child-ledger.json",
        "allChildrenTerminal": True,
        "allChildHandoffsConsumedOrRejected": True,
        "primaryReadyPacketRef": "primary-ready-packet.md",
        "remainingB0B1B2SafeWork": [],
        "remainingFinalAuthorityGaps": ["final acceptance"],
        "explicitlyOutGaps": [],
        "worktreeDecision": {
            "base": "main",
            "worktree": "not-required",
            "branch": "not-required",
            "allowedFiles": [".openacp/**"],
            "verification": ["validator"],
            "handoffPath": ".openacp/handoffs/frontier-docs.json",
            "dataRisk": "low",
            "resourceUse": "local only",
            "noDispatchReason": "No B2 work remains.",
        },
        "humanNextStep": "Primary should consume the ready packet.",
    }


def write_coordination_fixtures(tmp: Path, source_path: Path) -> dict[str, Path]:
    files = {
        "sequence": tmp / "sequence-registry.json",
        "runtime": tmp / "runtime-boundary.json",
        "lanes": tmp / "lane-registry.json",
        "source_status": tmp / "source-status-registry.json",
        "cards": tmp / "cards.md",
        "current": tmp / "current-manifest.json",
        "child": tmp / "child-ledger.json",
        "decision": tmp / "decision-registry.json",
        "closure": tmp / "frontier-closure.json",
        "ready_packet": tmp / "primary-ready-packet.md",
    }
    write_json(files["sequence"], valid_sequence_registry())
    write_json(files["runtime"], valid_runtime_boundary(tmp))
    write_json(files["lanes"], valid_lane_registry())
    write_json(files["source_status"], valid_source_status_registry())
    write_json(files["child"], valid_child_ledger())
    write_json(files["decision"], valid_decision_registry())
    write_json(files["closure"], valid_frontier_closure())
    files["ready_packet"].write_text("Primary-ready packet for selftest.\n", encoding="utf-8")
    files["cards"].write_text("schemaVersion: openacp-card-registry.v1\nartifactType: card-registry\n", encoding="utf-8")
    write_json(
        files["current"],
        {
            "schemaVersion": "openacp-current-manifest.v1.1",
            "artifactType": "current-manifest",
            "manifestId": "MAN-001",
            "preferredLanguage": "Chinese",
            "workingDirectory": str(tmp / "work"),
            "factsInput": str(source_path),
            "currentSourcePackRef": str(source_path),
            "invalidSourceRefs": [],
            "deprecatedSourceRefs": ["DEP-001"],
            "sequenceRegistryRef": "sequence-registry.json",
            "laneRegistryRef": "lane-registry.json",
            "runtimeBoundaryRef": "runtime-boundary.json",
            "sourceStatusRegistryRef": "source-status-registry.json",
            "cardRegistryRef": "cards.md",
            "activeLanes": [{"laneId": "primary", "role": "primary", "status": "active", "currentPromptId": "PROMPT-001", "authorityLevel": "B3"}],
            "supersededPromptIds": [],
            "cancelledPromptIds": [],
            "latestConsumeRefs": ["CONSUME-001"],
        },
    )
    return files


def assert_json_rules(tmp: Path, paths: dict[str, Path]) -> None:
    assert_exit("valid source pack", run(["--artifact", str(paths["source_pack"]), "--ruleset", "source-pack", "--strict"]), 0)
    assert_exit(
        "valid task card",
        run(["--artifact", str(paths["task_card"]), "--ruleset", "task-card", "--source-pack", str(paths["source_pack"]), "--strict"]),
        0,
    )
    assert_exit(
        "valid handoff",
        run(["--artifact", str(paths["handoff"]), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
        0,
    )

    bad_task = json.loads(paths["task_card"].read_text(encoding="utf-8"))
    bad_task["inputRefs"] = ["REF-001"]
    bad_task_path = tmp / "bad-task.json"
    write_json(bad_task_path, bad_task)
    assert_exit("legacy source rejected", run(["--artifact", str(bad_task_path), "--ruleset", "task-card", "--source-pack", str(paths["source_pack"]), "--strict"]), 1)

    bad_parent = json.loads(paths["task_card"].read_text(encoding="utf-8"))
    del bad_parent["parentCardId"]
    bad_parent_path = tmp / "bad-parent-task.json"
    write_json(bad_parent_path, bad_parent)
    assert_exit("task card requires parent card", run(["--artifact", str(bad_parent_path), "--ruleset", "task-card", "--source-pack", str(paths["source_pack"]), "--strict"]), 1)

    bad_handoff = json.loads(paths["handoff"].read_text(encoding="utf-8"))
    bad_handoff["claims"] = ["accepted and merged"]
    bad_handoff_path = tmp / "bad-handoff.json"
    write_json(bad_handoff_path, bad_handoff)
    assert_exit("handoff overclaim rejected", run(["--artifact", str(bad_handoff_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]), 1)

    bad_scope = json.loads(paths["handoff"].read_text(encoding="utf-8"))
    bad_scope["changedArtifacts"] = [{"path": "src/app.py", "changeType": "updated"}]
    bad_scope["changedFiles"] = ["src/app.py"]
    bad_scope_path = tmp / "bad-scope.json"
    write_json(bad_scope_path, bad_scope)
    assert_exit("scope overrun rejected", run(["--artifact", str(bad_scope_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]), 1)

    coordination = write_coordination_fixtures(tmp, paths["source_pack"])
    assert_exit("valid current manifest", run(["--artifact", str(coordination["current"]), "--ruleset", "current-manifest", "--strict"]), 0)
    assert_exit("valid sequence registry", run(["--artifact", str(coordination["sequence"]), "--ruleset", "sequence-registry", "--strict"]), 0)
    assert_exit("valid runtime boundary", run(["--artifact", str(coordination["runtime"]), "--ruleset", "runtime-boundary", "--strict"]), 0)
    assert_exit("valid lane registry", run(["--artifact", str(coordination["lanes"]), "--ruleset", "lane-registry", "--strict"]), 0)
    assert_exit("valid child ledger", run(["--artifact", str(coordination["child"]), "--ruleset", "child-ledger", "--strict"]), 0)
    assert_exit("valid source status registry", run(["--artifact", str(coordination["source_status"]), "--ruleset", "source-status-registry", "--strict"]), 0)
    assert_exit("valid decision registry", run(["--artifact", str(coordination["decision"]), "--ruleset", "decision-registry", "--strict"]), 0)
    assert_exit("valid frontier closure", run(["--artifact", str(coordination["closure"]), "--ruleset", "frontier-closure", "--strict"]), 0)

    bad_manifest = json.loads(coordination["current"].read_text(encoding="utf-8"))
    bad_manifest["activeLanes"][0]["role"] = "frontier"
    bad_manifest["activeLanes"][0]["authorityLevel"] = "B3"
    bad_manifest_path = tmp / "bad-current-manifest-frontier-b3.json"
    write_json(bad_manifest_path, bad_manifest)
    assert_exit("current manifest rejects Frontier B3", run(["--artifact", str(bad_manifest_path), "--ruleset", "current-manifest", "--strict"]), 1)

    bad_sequence = valid_sequence_registry()
    bad_sequence["activeLanes"][0]["role"] = "frontier"
    bad_sequence["activeLanes"][0]["authorityLevel"] = "B3"
    bad_sequence_path = tmp / "bad-sequence-frontier-b3.json"
    write_json(bad_sequence_path, bad_sequence)
    assert_exit("sequence registry rejects Frontier B3", run(["--artifact", str(bad_sequence_path), "--ruleset", "sequence-registry", "--strict"]), 1)

    bad_lane_auth = valid_lane_registry()
    bad_lane_auth["lanes"][0]["role"] = "frontier"
    bad_lane_auth["lanes"][0]["authorityLevel"] = "B3"
    bad_lane_auth_path = tmp / "bad-lane-frontier-b3.json"
    write_json(bad_lane_auth_path, bad_lane_auth)
    assert_exit("lane registry rejects Frontier B3", run(["--artifact", str(bad_lane_auth_path), "--ruleset", "lane-registry", "--strict"]), 1)

    bad_single_frontier = valid_lane_registry()
    bad_single_frontier["projectComplexity"] = "normal"
    bad_single_frontier["frontierDispatchMode"] = "single_frontier"
    bad_single_frontier["frontierDispatchReason"] = "Normal project default."
    bad_single_frontier["lanes"][0]["role"] = "frontier"
    bad_single_frontier["lanes"][0]["authorityLevel"] = "B2"
    bad_single_frontier_path = tmp / "bad-normal-single-frontier.json"
    write_json(bad_single_frontier_path, bad_single_frontier)
    assert_exit("lane registry rejects normal project single Frontier without exception", run(["--artifact", str(bad_single_frontier_path), "--ruleset", "lane-registry", "--strict"]), 1)

    bad_runtime = valid_runtime_boundary(tmp)
    bad_runtime["productRepoStatus"] = "found"
    bad_runtime["productRepoPath"] = ""
    bad_runtime_path = tmp / "bad-runtime-boundary.json"
    write_json(bad_runtime_path, bad_runtime)
    assert_exit("runtime boundary rejects missing found repo path", run(["--artifact", str(bad_runtime_path), "--ruleset", "runtime-boundary", "--strict"]), 1)

    blocked_runtime = valid_runtime_boundary(tmp)
    blocked_runtime["productRepoStatus"] = "missing"
    blocked_runtime["productRepoPath"] = ""
    blocked_runtime["baseBranch"] = ""
    blocked_runtime["sourceRoots"] = []
    blocked_runtime["testEntrypoints"] = []
    blocked_runtime["worktreePolicy"] = "unknown"
    blocked_runtime["b2DispatchGate"] = {
        "state": "coordination_only",
        "allowsProductWrite": False,
        "reason": "Product repo fields are missing.",
        "missingInputs": ["productRepoPath", "baseBranch", "sourceRoots", "testEntrypoints", "worktreePolicy"],
    }
    blocked_runtime_path = tmp / "blocked-runtime-boundary.json"
    write_json(blocked_runtime_path, blocked_runtime)
    bad_product_write_lane = valid_lane_registry()
    bad_product_write_lane["lanes"][0]["role"] = "frontier"
    bad_product_write_lane["lanes"][0]["authorityLevel"] = "B2"
    bad_product_write_lane["lanes"][0]["runtimeBoundaryRef"] = "blocked-runtime-boundary.json"
    bad_product_write_lane["lanes"][0]["b2DispatchGate"] = {
        "mode": "product_write",
        "state": "ready",
        "reason": "This incorrectly claims product-write dispatch is ready.",
    }
    bad_product_write_lane_path = tmp / "bad-product-write-lane.json"
    write_json(bad_product_write_lane_path, bad_product_write_lane)
    assert_exit("lane registry rejects B2 product write without runtime gate", run(["--artifact", str(bad_product_write_lane_path), "--ruleset", "lane-registry", "--strict"]), 1)

    bad_return_gate = valid_lane_registry()
    bad_return_gate["lanes"][0]["role"] = "frontier"
    bad_return_gate["lanes"][0]["authorityLevel"] = "B2"
    bad_return_gate["lanes"][0]["status"] = "blocked_on_primary"
    bad_return_gate["lanes"][0]["returnGateStatus"]["state"] = "not_ready"
    bad_return_gate["lanes"][0]["returnGateStatus"]["safeWorkRemainingCount"] = 1
    bad_return_gate_path = tmp / "bad-return-gate-lane.json"
    write_json(bad_return_gate_path, bad_return_gate)
    assert_exit("lane registry rejects inconsistent return gate", run(["--artifact", str(bad_return_gate_path), "--ruleset", "lane-registry", "--strict"]), 1)

    bad_child = valid_child_ledger()
    bad_child["children"][0]["authority"] = "B3"
    bad_child_path = tmp / "bad-child-ledger.json"
    write_json(bad_child_path, bad_child)
    assert_exit("child ledger rejects B3 child authority", run(["--artifact", str(bad_child_path), "--ruleset", "child-ledger", "--strict"]), 1)

    bad_source_status = valid_source_status_registry()
    bad_source_status["sources"][1]["status"] = "invalid"
    bad_source_status["sources"][1]["reason"] = ""
    bad_source_status_path = tmp / "bad-source-status.json"
    write_json(bad_source_status_path, bad_source_status)
    assert_exit("invalid source status requires reason", run(["--artifact", str(bad_source_status_path), "--ruleset", "source-status-registry", "--strict"]), 1)

    bad_closure = valid_frontier_closure()
    bad_closure["remainingB0B1B2SafeWork"] = ["Dispatch reviewer before returning."]
    bad_closure_path = tmp / "bad-frontier-closure.json"
    write_json(bad_closure_path, bad_closure)
    assert_exit("frontier closure rejects early Primary return", run(["--artifact", str(bad_closure_path), "--ruleset", "frontier-closure", "--strict"]), 1)

    bad_ready_packet = valid_frontier_closure()
    bad_ready_packet["primaryReadyPacketRef"] = "missing-primary-ready-packet.md"
    bad_ready_packet_path = tmp / "bad-frontier-closure-ready-packet.json"
    write_json(bad_ready_packet_path, bad_ready_packet)
    assert_exit("frontier closure requires existing Primary-ready packet", run(["--artifact", str(bad_ready_packet_path), "--ruleset", "frontier-closure", "--strict"]), 1)

    bad_worktree_closure = valid_frontier_closure()
    del bad_worktree_closure["worktreeDecision"]["allowedFiles"]
    bad_worktree_closure_path = tmp / "bad-frontier-closure-worktree.json"
    write_json(bad_worktree_closure_path, bad_worktree_closure)
    assert_exit("frontier closure requires worktree decision fields", run(["--artifact", str(bad_worktree_closure_path), "--ruleset", "frontier-closure", "--strict"]), 1)

    status_report_path = tmp / "status-report.json"
    write_json(
        status_report_path,
        {
            "schemaVersion": "openacp-status-report.v1",
            "artifactType": "status-report",
            "responseId": "RESP-STATUS-001",
            "basisRefs": ["handoff.json"],
            "currentState": "provisional",
            "completedWork": ["Scoped work is verified."],
            "unverifiedClaims": [],
            "blockers": [],
            "nextActions": ["Primary consume."],
            "authorityLimits": ["No final acceptance."],
        },
    )
    assert_exit("valid status report response id", run(["--artifact", str(status_report_path), "--ruleset", "status-report", "--strict"]), 0)
    bad_status = json.loads(status_report_path.read_text(encoding="utf-8"))
    bad_status["reportId"] = "OLD-ID"
    bad_status_path = tmp / "bad-status-report.json"
    write_json(bad_status_path, bad_status)
    assert_exit("status report rejects reportId", run(["--artifact", str(bad_status_path), "--ruleset", "status-report", "--strict"]), 1)


def assert_text_rules(tmp: Path) -> None:
    primary_prompt = "\n".join(
        [
            "Prompt ID: PROMPT-001",
            "Role: Primary",
            "Authority level: B3",
            "Preferred language: Chinese",
            "Use human-explain-openacp for every reply.",
            "Before Frontier dispatch, resolve working directory, facts path, preferred language, product repo path, base branch, source roots, test entrypoints, worktree policy, runtime boundary, and runtimeBoundaryRef.",
            "Create 10-20 project-level CARDs for normal or medium/high-complexity work before Frontier dispatch.",
            "Scan product workflow, backend/API, data/storage, frontend/UI, desktop/mobile/native/Electron/Tauri surfaces, integrations, security, testing, CI, release, and ops before finalizing CARDs.",
            "Default to at least two Frontier lanes when two safe independent CARD clusters exist.",
            "Use one Frontier only for a small project, a single safe lane, or an explicit user request, and record the reason.",
        ]
    )
    primary_prompt_path = tmp / "primary.prompt.md"
    primary_prompt_path.write_text(primary_prompt, encoding="utf-8")
    assert_exit("valid prompt record", run(["--artifact", str(primary_prompt_path), "--ruleset", "prompt-record", "--strict"]), 0)

    launcher_path = tmp / "primary.short.md"
    launcher_path.write_text(
        "\n".join(
            [
                "Project - Primary Orchestrator - Startup",
                "",
                "Read and execute this OpenACP prompt record:",
                f"- Prompt Record: {primary_prompt_path}",
                "- Prompt ID: PROMPT-001",
                "- Preferred language: Chinese",
                "",
                "Hard requirements:",
                "1. Read the prompt record explicitly as UTF-8.",
                "2. Execute only the named Prompt ID.",
                "3. If the file cannot be read cleanly, the Prompt ID is missing, or the text appears corrupted, stop and report launcher-read failure.",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("valid launcher", run(["--artifact", str(launcher_path), "--ruleset", "launcher", "--prompt-record", str(primary_prompt_path), "--expect-prompt-id", "PROMPT-001", "--strict"]), 0)

    card_registry_path = tmp / "card-registry.md"
    card_rows = [
        f"| CARD-{idx:03d} | domain-{idx} | B2 | frontier-{idx % 3} | ready-candidate | objective | SRC-001 | task-card candidates TASK-{idx:03d}-A/TASK-{idx:03d}-B |"
        for idx in range(1, 13)
    ]
    card_registry_path.write_text(
        "\n".join(
            [
                "schemaVersion: openacp-card-registry.v1",
                "artifactType: card-registry",
                "",
                "## Domain Coverage",
                "| Domain | Present? | Source refs | CARD coverage | Notes |",
                "|---|---|---|---|---|",
                "| Product workflow / user journey | yes | SRC-001 | CARD-001 | Product flow exists. |",
                "| Backend / API / services | yes | SRC-001 | CARD-002 | Backend exists. |",
                "| Data / storage / migration | yes | SRC-001 | CARD-003 | Data work exists. |",
                "| Frontend / UI / design system | yes | SRC-001 | CARD-004 | UI exists. |",
                "| Desktop shell / Electron / Tauri | yes | SRC-001 | CARD-005 | Electron exists. |",
                "| Integrations / external systems | yes | SRC-001 | CARD-006 | Integrations exist. |",
                "| Auth / security / privacy | yes | SRC-001 | CARD-007 | Security exists. |",
                "| Testing / QA / validation | yes | SRC-001 | CARD-008 | QA exists. |",
                "| Observability / CI / release / ops | yes | SRC-001 | CARD-009 | Release exists. |",
                "| Docs / migration guide / launch materials | yes | SRC-001 | CARD-010 | Docs exist. |",
                "",
                "## Complexity Assessment",
                "- normal project, 10-20 CARDs expected.",
                "",
                "## CARD List",
                "| CARD | Domain | Authority | Lane | Status | Objective | Source | Task-card candidates |",
                "|---|---|---|---|---|---|---|---|",
                *card_rows,
                "",
                "## Lane Grouping",
                "- Frontier lane candidates group related CARDs by risk and parallel safety.",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("valid card registry", run(["--artifact", str(card_registry_path), "--ruleset", "card-registry", "--strict"]), 0)

    placeholder_card_registry_path = tmp / "placeholder-card-registry.md"
    placeholder_card_registry_path.write_text(
        "\n".join(
            [
                "schemaVersion: openacp-card-registry.v1",
                "artifactType: card-registry",
                "",
                "## Domain Coverage",
                "| Domain | Present? | Source refs | CARD coverage | Notes |",
                "|---|---|---|---|---|",
                "| Frontend / UI / design system | yes / no / unclear | | | |",
                "",
                "## Complexity Assessment",
                "- normal project, 10-20 CARDs expected.",
                "",
                "## CARD List",
                "| CARD | Domain | Authority | Lane | Status | Objective | Source | Task-card candidates |",
                "|---|---|---|---|---|---|---|---|",
                "| CARD-001 | | B0/B1/B2 | | draft | | | |",
                "",
                "## Lane Grouping",
                "- Frontier lane candidates are still placeholders.",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("card registry rejects placeholder rows", run(["--artifact", str(placeholder_card_registry_path), "--ruleset", "card-registry", "--strict"]), 1)

    formal_report_path = tmp / "formal-report.md"
    formal_report_path.write_text(
        "\n".join(
            [
                "Response ID: RESP-001",
                "Response log path: chat reply",
                "",
                "| Item/Status | Content |",
                "|---|---|",
                "| Changed | Primary created startup artifacts. |",
                "| Progress | 80%. Startup is ready but final acceptance is pending. |",
                "| Gate | Validation passed. |",
                "| Area | OpenACP startup. |",
                "| Goal | Start Primary from current facts. |",
                "| Gaps | User project execution has not started. |",
                "| Next | Start the Primary launcher. |",
                "",
                "## Evidence and Validation",
                "- Basis: validator selftest fixture.",
                "",
                "## Recommended Next Step",
                "Create a new Primary thread and paste the short launcher.",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("valid English formal report", run(["--artifact", str(formal_report_path), "--ruleset", "formal-report", "--strict"]), 0)

    zh_frontier_report_path = tmp / "zh-frontier-formal-report.md"
    zh_frontier_report_path.write_text(
        "\n".join(
            [
                "Response ID: RESP-ZH-001",
                "Response log path: chat reply",
                "",
                "| 类型/状态 | 内容 |",
                "|---|---|",
                "| 做了什么　　 | Frontier 刷新了 lane backlog。 |",
                "| 总体进度　　 | 60%。仍有 B2 子任务未 consume。 |",
                "| Lane | docs lane。 |",
                "| 目标　　　　 | 收口当前 lane 的 B0/B1/B2 工作。 |",
                "| 缺口　　　　 | 需要继续 consume worker handoff。 |",
                "| 下一步　　　 | Frontier 继续派发 reviewer 并 consume 结果。 |",
                "",
                "## 依据与验证",
                "- 本报告来自中文 selftest 样例。",
                "",
                "## 下一步建议",
                "你现在不用新开 worker 线程；Frontier 会在当前 lane 内继续收口。",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("valid Chinese Frontier formal report", run(["--artifact", str(zh_frontier_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 0)

    bad_no_padding_report_path = tmp / "bad-no-padding-formal-report.md"
    bad_no_padding_report_path.write_text(
        zh_frontier_report_path.read_text(encoding="utf-8")
        .replace("做了什么　　", "做了什么")
        .replace("总体进度　　", "总体进度")
        .replace("目标　　　　", "目标")
        .replace("缺口　　　　", "缺口")
        .replace("下一步　　　", "下一步"),
        encoding="utf-8",
    )
    assert_exit("Chinese formal report rejects missing label padding", run(["--artifact", str(bad_no_padding_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    bad_checkpoint_report_path = tmp / "bad-checkpoint-formal-report.md"
    bad_checkpoint_report_path.write_text(
        zh_frontier_report_path.read_text(encoding="utf-8").replace("| Lane | docs lane。 |", "| Checkpoint | lane-local closure。 |\n| Lane | docs lane。 |"),
        encoding="utf-8",
    )
    assert_exit("formal report rejects checkpoint row", run(["--artifact", str(bad_checkpoint_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    bad_report_item_header_path = tmp / "bad-report-item-header-formal-report.md"
    bad_report_item_header_path.write_text(
        zh_frontier_report_path.read_text(encoding="utf-8").replace("| 类型/状态 | 内容 |", "| 报告项 | 内容 |"),
        encoding="utf-8",
    )
    assert_exit("Chinese formal report rejects report-item header", run(["--artifact", str(bad_report_item_header_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    bad_legacy_evidence_report_path = tmp / "bad-legacy-evidence-formal-report.md"
    bad_legacy_evidence_report_path.write_text(
        zh_frontier_report_path.read_text(encoding="utf-8").replace("## 依据与验证", "## Evidence Details"),
        encoding="utf-8",
    )
    assert_exit("Chinese formal report rejects English evidence heading", run(["--artifact", str(bad_legacy_evidence_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    bad_legacy_next_step_report_path = tmp / "bad-legacy-next-step-formal-report.md"
    bad_legacy_next_step_report_path.write_text(
        zh_frontier_report_path.read_text(encoding="utf-8").replace("## 下一步建议", "## 给人的下一步"),
        encoding="utf-8",
    )
    assert_exit("Chinese formal report rejects old next-step heading", run(["--artifact", str(bad_legacy_next_step_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    bad_command_report_path = tmp / "bad-command-formal-report.md"
    bad_command_report_path.write_text(zh_frontier_report_path.read_text(encoding="utf-8") + "\n```powershell\nopenacp --version\n```\n", encoding="utf-8")
    assert_exit("formal report rejects command dumps", run(["--artifact", str(bad_command_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    bad_tail_report_path = tmp / "bad-tail-formal-report.md"
    bad_tail_report_path.write_text(zh_frontier_report_path.read_text(encoding="utf-8") + "\n## Extra Section\n- This should not appear after Recommended Next Step.\n", encoding="utf-8")
    assert_exit("formal report requires trailing recommended next step", run(["--artifact", str(bad_tail_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    bad_english_report_path = tmp / "bad-english-formal-report.md"
    bad_english_report_path.write_text(
        zh_frontier_report_path.read_text(encoding="utf-8")
        + "\nSource classification summary: current sources are final specification, product requirements, platform checklist, and migration readiness notes.\n",
        encoding="utf-8",
    )
    assert_exit("Chinese formal report rejects English-dominant prose", run(["--artifact", str(bad_english_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    frontier_contract_path = tmp / "frontier-contract.md"
    frontier_contract_path.write_text(
        "\n".join(
            [
                "Prompt ID: FRONTIER-001",
                "Role: Frontier",
                "Authority level: B2",
                "Use human-explain-openacp and formal-report-openacp for every status reply.",
                "gapDecisionMatrix",
                "branchReturnGate",
                "worktreeDecision",
                "Subagent-first dispatch is required.",
                "Use dispatch_current_thread_subagent for child work in the current Frontier thread.",
                "Dispatch bounded worker, reviewer, discovery, validation, and subagent work inside the lane.",
                "Do not use the human as a thread launcher for B0/B1/B2-safe child work.",
                "Human-managed child launchers are fallback only when direct subagent dispatch is unavailable, unsafe, explicitly requested, or requires a separately user-managed session.",
                "Maintain a child ledger with promptId, taskId, role, authority, effects, subagent id, dispatchStatus, handoffStatus, consumeStatus, and remaining risk.",
                "Every Frontier reply must end with a recommended next step.",
                "Do not return to Primary merely because a provisional packet, source baseline, handoff, or consume-result was written.",
                "`blocked on Primary` is valid only when branchReturnGate is satisfied and every visible remaining gap is needs_final_authority or explicitly_out.",
                "```json",
                json.dumps(
                    {
                        "schemaVersion": "openacp-frontier-orchestration-contract.v1",
                        "artifactType": "frontier-orchestration-contract",
                        "authorityLevel": "B2",
                        "laneObjective": "Run one bounded lane to closure.",
                        "backlogScope": {"seedArtifactsPolicy": "starting_points_not_exhaustive"},
                        "operatingOrder": {"B0": "discover", "B1": "package", "B2": "dispatch"},
                        "gapDecisionMatrix": {
                            "allowedValues": [
                                "do_now",
                                "dispatch_current_thread_subagent",
                                "prepare_package",
                                "prepare_package_only_when_dispatch_unavailable",
                                "apply_conservative_default",
                                "needs_final_authority",
                                "explicitly_out",
                            ]
                        },
                        "branchReturnGate": {"rule": "remaining gaps must be needs_final_authority or explicitly_out"},
                        "coordinationRefs": {
                            "runtimeBoundaryRef": "runtime-boundary.json",
                            "laneRegistryRef": "lane-registry.json",
                            "childLedgerRef": "child-ledger.json",
                            "frontierClosureRef": "frontier-closure.json",
                        },
                        "worktreeDecision": {"requiredWhen": "creating_or_skipping_B2_worker"},
                        "childLedger": {
                            "requiredFields": [
                                "promptId",
                                "taskId",
                                "handoffId",
                                "role",
                                "authority",
                                "effects",
                                "dispatchStatus",
                                "handoffStatus",
                                "consumeStatus",
                            ]
                        },
                        "subagentFirst": {"enabled": True},
                        "defaultMode": "continue_until_lane_closure_or_true_final_authority_blocker",
                        "continuationPolicy": "dispatch, consume, reclassify, continue",
                        "seedArtifacts": [],
                    },
                    ensure_ascii=False,
                ),
                "```",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("valid frontier contract", run(["--artifact", str(frontier_contract_path), "--ruleset", "frontier-contract", "--strict"]), 0)

    bad_frontier_contract_path = tmp / "bad-frontier-contract.md"
    bad_frontier_contract_path.write_text(
        "\n".join(
            [
                "Prompt ID: FRONTIER-002",
                "Role: Frontier",
                "Authority level: B2",
                "Use human-explain-openacp and formal-report-openacp for every status reply.",
                "gapDecisionMatrix",
                "branchReturnGate",
                "worktreeDecision",
                "Dispatch bounded worker, reviewer, and subagent work inside the lane.",
                "create_downstream_prompt",
                "Return a short downstream launcher to the human.",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("frontier human trampoline rejected", run(["--artifact", str(bad_frontier_contract_path), "--ruleset", "frontier-contract", "--strict"]), 1)


def assert_public_package_rules(tmp: Path) -> None:
    public_pkg = tmp / "public-package"
    (public_pkg / "templates").mkdir(parents=True)
    (public_pkg / "examples").mkdir()
    (public_pkg / "README.md").write_text("OpenACP public package\n", encoding="utf-8")
    (public_pkg / "templates" / "formal-report.md").write_text("Response ID: `OACP-TEMPLATE-0001`\n", encoding="utf-8")
    (public_pkg / "examples" / "formal-report-example.md").write_text("Response ID: `OACP-EXAMPLE-0001`\n", encoding="utf-8")
    assert_exit("formal report templates and examples allowed", run(["--artifact", str(public_pkg), "--ruleset", "public-package", "--strict"]), 0)

    reports_dir = public_pkg / "reports"
    reports_dir.mkdir()
    internal_report = reports_dir / "release-report.md"
    internal_report.write_text("Response ID: `OACP-2026-0001`\nResponse log path: local response log\n", encoding="utf-8")
    assert_exit("internal formal report rejected from public reports path", run(["--artifact", str(public_pkg), "--ruleset", "public-package", "--strict"]), 1)
    internal_report.unlink()

    (public_pkg / "README.md").write_text("OpenACP 中文入口\n", encoding="utf-8")
    assert_exit("root README must stay English", run(["--artifact", str(public_pkg), "--ruleset", "public-package", "--strict"]), 1)

    local_response_path = "C:" + "\\" + "Users" + "\\" + "example" + "\\" + "OpenACP" + "\\" + "response.md"
    (public_pkg / "README.md").write_text("Response log path: " + local_response_path + "\n", encoding="utf-8")
    assert_exit("local absolute response log path rejected", run(["--artifact", str(public_pkg), "--ruleset", "public-package", "--strict"]), 1)


def assert_cli_entrypoints(tmp: Path) -> None:
    version_proc = subprocess.run(
        [sys.executable, "-m", "openacp", "--version"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    assert_exit("python -m openacp version", version_proc, 0)

    init_proc = subprocess.run(
        [sys.executable, "-m", "openacp", "init", str(tmp / "starter")],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    assert_exit("python -m openacp init dry run", init_proc, 0)
    required_output = [
        "coordination",
        "runtime-boundary.json",
        "lane-registry.json",
        "sequence-registry.json",
        "current-manifest.json",
    ]
    missing = [item for item in required_output if item not in init_proc.stdout]
    if missing:
        print("FAIL python -m openacp init lists coordination artifacts: missing " + ", ".join(missing))
        print(init_proc.stdout)
        raise SystemExit(1)
    print("PASS python -m openacp init lists coordination artifacts")


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        paths = fixtures(tmp)
        assert_json_rules(tmp, paths)
        assert_text_rules(tmp)
        assert_public_package_rules(tmp)
        assert_cli_entrypoints(tmp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
