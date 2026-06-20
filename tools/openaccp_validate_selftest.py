#!/usr/bin/env python3
"""Self-tests for the OpenACCP validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "openaccp_validate.py"


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
        "schemaVersion": "openaccp-source-pack.v1",
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
        "schemaVersion": "openaccp-task-card.v1",
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
        "schemaVersion": "openaccp-handoff.v1",
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


def read_only_handoff() -> dict:
    return {
        "schemaVersion": "openaccp-handoff.v1",
        "artifactType": "handoff",
        "handoffId": "HAND-REVIEW-001",
        "taskId": "TASK-001",
        "responseId": "RESP-REVIEW-001",
        "actorRole": "reviewer",
        "authority": "B0",
        "workspaceRef": "local-workspace",
        "worktree": "none",
        "branchRef": "none",
        "baseCommit": "none",
        "commit": "none",
        "dataRisk": "low",
        "effectsPreset": "review_handoff",
        "changedFiles": [],
        "changedArtifacts": [],
        "claims": ["Reviewed scope and evidence without modifying files."],
        "verificationEvidence": [{"check": "read-only review", "method": "manual review", "result": "pass"}],
        "deviations": [],
        "risks": [],
        "assumptionsUsed": [],
        "remainingWork": [],
        "stateClaim": "reviewed",
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
        "schemaVersion": "openaccp-sequence-registry.v1",
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


def valid_consume_result() -> dict:
    return {
        "schemaVersion": "openaccp-consume-result.v1",
        "artifactType": "consume-result",
        "consumeId": "CONSUME-001",
        "responseId": "RESP-001",
        "consumerRole": "primary",
        "authorityScope": "final",
        "targetHandoffIds": ["HAND-001"],
        "targetReviewIds": ["REV-001"],
        "decision": "accepted",
        "basisRefs": ["handoff.json", "review-report.json"],
        "evidenceStatus": ["Handoff was reviewed."],
        "claimsAccepted": ["Scoped claim accepted."],
        "claimsRejected": ["No release claim accepted."],
        "remainingRisks": ["Owner release review still pending."],
        "authorityLimits": ["Final consume covers evidence only."],
        "nextActions": ["Record the consume result."],
    }


def valid_frontier_consume_result() -> dict:
    data = valid_consume_result()
    data["targetHandoffIds"] = ["HAND-FRONTIER-DOCS-001"]
    data["targetReviewIds"] = []
    data["basisRefs"] = ["FC-001", "frontier-docs", "frontier-closures/frontier-docs.json"]
    data["evidenceStatus"] = ["Frontier closure proof was reviewed."]
    data["claimsAccepted"] = ["Frontier return evidence is accepted within Primary authority."]
    data["claimsRejected"] = ["No release, merge, publication, or waiver claim is accepted."]
    return data


def valid_machine_summary() -> dict:
    return {
        "schemaVersion": "openaccp-machine-summary.v1",
        "artifactType": "machine-summary",
        "summaryId": "MSUM-001",
        "role": "worker",
        "promptId": "PROMPT-001",
        "responseId": "RESP-001",
        "authority": "B2",
        "effectsPreset": "docs_task_card_commit",
        "basisRefs": ["source-pack.json", "task-card.json"],
        "locators": [
            {"kind": "task-card", "id": "TASK-001", "path": "task-card.json"},
            {"kind": "handoff", "id": "HAND-001", "path": "handoff.json"},
        ],
        "status": "verified-provisional",
        "claims": ["Scoped docs work completed."],
        "nextActions": ["Primary consume."],
    }


def valid_authority_charter() -> dict:
    return {
        "schemaVersion": "openaccp-authority-charter.v1",
        "artifactType": "authority-charter",
        "charterId": "CHARTER-001",
        "grantedRole": "primary",
        "authorityLevel": "B3",
        "allowedActions": ["Consume reviewed evidence."],
        "forbiddenActions": ["Claim production launch."],
        "delegationRules": ["Delegated final decisions must be listed explicitly."],
        "finalAuthorityReservedTo": "human-owner",
        "delegatedFinalAuthority": [
            {
                "decisionId": "DFA-001",
                "delegatedTo": "primary",
                "decision": "Accept or reject reviewed evidence.",
                "scope": "Coordination evidence only.",
                "owner": "human-owner",
            }
        ],
        "scopeLimits": ["No production launch."],
        "dataRiskLimit": "low",
        "resourceUseLimit": ["Local coordination only."],
        "allowedInputs": ["handoff.json", "review-report.json"],
        "allowedOutputs": ["consume-result.json"],
        "forbiddenSideEffects": ["Credential use."],
        "stopConditions": ["Owner-reserved decision is required."],
        "expiresWhen": "The consume decision is recorded.",
    }


def return_wake_contract(owner_role: str = "frontier") -> dict:
    return {
        "required": True,
        "protocol": "openaccp-return-wake-owner.v1",
        "returnOwnerRole": owner_role,
        "returnOwnerThreadId": "THREAD-OWNER-001",
        "primaryThreadId": "THREAD-PRIMARY-001",
        "primaryMirrorWake": False,
        "wakeChannel": "direct_thread_message",
        "wakeCapability": "available",
        "wakeOn": ["handoff_ready", "review_ready", "amendment_needed", "blocked", "failed"],
        "expectedWakePath": ".openaccp/coordination/wake-pending/WAKE-001.json",
    }


def valid_return_wake() -> dict:
    return {
        "schemaVersion": "openaccp-return-wake.v1",
        "artifactType": "return-wake",
        "protocol": "openaccp-return-wake-owner.v1",
        "wakeId": "project:thread:RESP-FRONTIER-001:frontier-docs",
        "dedupeKey": "project:RESP-FRONTIER-001:frontier-docs",
        "projectId": "project",
        "sourceThreadId": "THREAD-FRONTIER-001",
        "role": "frontier",
        "laneId": "frontier-docs",
        "taskCardId": "",
        "promptId": "PROMPT-FRONTIER-001",
        "responseId": "RESP-FRONTIER-001",
        "returnClass": "primary_ready",
        "returnOwner": {"role": "primary", "threadId": "THREAD-PRIMARY-001", "laneId": "primary"},
        "primaryMirrorWake": False,
        "primaryThreadId": "THREAD-PRIMARY-001",
        "wakeChannel": "direct_thread_message",
        "wakeCapability": "available",
        "artifactRefs": {
            "handoffPath": ".openaccp/handoffs/HAND-FRONTIER-DOCS-001.json",
            "closurePath": ".openaccp/coordination/frontier-closures/frontier-docs.json",
            "consumeResultPath": "",
            "reportPath": "",
            "blockerPath": "",
            "wakePendingPath": "",
        },
        "branchReturnGate": "satisfied",
        "safeWorkRemainingCount": 0,
        "validation": {"status": "pass", "evidence": "frontier-closure strict pass"},
        "ownerActionNeeded": "consume",
        "summary": "Frontier docs lane is ready for Primary consume.",
        "blockers": [],
        "createdChildThreads": [],
    }


def valid_execution_boundary(tmp: Path) -> dict:
    return {
        "schemaVersion": "openaccp-execution-boundary.v1",
        "artifactType": "execution-boundary",
        "boundaryId": "RB-001",
        "workingDirectory": str(tmp / "work"),
        "productRepoStatus": "found",
        "productRepoPath": str(tmp / "repo"),
        "baseBranch": "main",
        "sourceRoots": ["src"],
        "testEntrypoints": ["pytest"],
        "worktreePolicy": "allowed",
        "inferenceStatus": "inferred",
        "inferredFrom": ["repo path", "pyproject.toml", "git metadata"],
        "confidence": "high",
        "ambiguities": [],
        "allowedWritablePaths": [".openaccp/**", "worktrees/**"],
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
        "schemaVersion": "openaccp-lane-registry.v1",
        "artifactType": "lane-registry",
        "registryId": "LANES-001",
        "projectComplexity": "bootstrap",
        "frontierDispatchMode": "pre_frontier",
        "dispatchChannel": "agent_thread_spawn",
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
                "executionBoundaryRef": "execution-boundary.json",
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
        "schemaVersion": "openaccp-child-ledger.v1",
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
                "expectedHandoffPath": ".openaccp/handoffs/HAND-001.json",
                "returnWake": return_wake_contract("frontier"),
                "dispatchStatus": "returned",
                "handoffStatus": "present",
                "wakeStatus": "sent",
                "wakeRef": ".openaccp/coordination/wake-pending/WAKE-001.json",
                "consumeStatus": "consumed",
                "remainingRisk": "none",
            }
        ],
    }


def valid_source_status_registry() -> dict:
    return {
        "schemaVersion": "openaccp-source-status-registry.v1",
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
        "schemaVersion": "openaccp-decision-registry.v1",
        "artifactType": "decision-registry",
        "registryId": "DEC-REG-001",
        "decisions": [
            {
                "decisionId": "OQ-001",
                "type": "owner-question",
                "status": "open",
                "question": "Which repo path should Primary inspect if the provided repo path is ambiguous?",
                "basisRefs": ["execution-boundary.json"],
                "blocks": ["B2 implementation dispatch"],
                "safeDefault": "Do B0/B1 packaging only.",
                "authorityRequired": "B3",
            }
        ],
    }


def valid_frontier_closure() -> dict:
    return {
        "schemaVersion": "openaccp-frontier-closure.v1",
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
        "branchReturnGate": {
            "state": "ready_for_primary",
            "safeWorkRemainingCount": 0,
            "finalAuthorityGapCount": 1,
            "explicitlyOutCount": 0,
            "primaryReadyPacketExists": True,
            "reason": "Only final acceptance remains.",
        },
        "laneProgressPacketRef": "",
        "primaryReadyPacketRef": "primary-ready-packet.md",
        "remainingB0B1B2SafeWork": [],
        "remainingFinalAuthorityGaps": ["final acceptance"],
        "explicitlyOutGaps": [],
        "worktreeDecision": {
            "base": "main",
            "worktree": "not-required",
            "branch": "not-required",
            "allowedFiles": [".openaccp/**"],
            "verification": ["validator"],
            "handoffPath": ".openaccp/handoffs/frontier-docs.json",
            "dataRisk": "low",
            "resourceUse": "local only",
            "noDispatchReason": "No B2 work remains.",
        },
        "humanNextStep": "Primary should consume the ready packet.",
    }


def valid_frontier_progress_closure() -> dict:
    closure = valid_frontier_closure()
    closure["branchState"] = "open"
    closure["gapDecisionMatrix"] = [
        {
            "gap": "execution product write is not ready",
            "decision": "prepare_package",
            "nextSafeAction": "Frontier continues B1 readiness packaging.",
        }
    ]
    closure["allChildrenTerminal"] = False
    closure["allChildHandoffsConsumedOrRejected"] = False
    closure["branchReturnGate"] = {
        "state": "not_ready",
        "safeWorkRemainingCount": 1,
        "finalAuthorityGapCount": 0,
        "explicitlyOutCount": 0,
        "primaryReadyPacketExists": False,
        "reason": "Lane-local B0/B1/B2-safe work remains.",
    }
    closure["laneProgressPacketRef"] = "lane-progress-packet.md"
    closure["primaryReadyPacketRef"] = ""
    closure["remainingB0B1B2SafeWork"] = ["Prepare repo-readiness checklist."]
    closure["remainingFinalAuthorityGaps"] = []
    closure["worktreeDecision"]["base"] = "unresolved"
    closure["worktreeDecision"]["worktree"] = "not-created"
    closure["worktreeDecision"]["branch"] = "not-created"
    closure["worktreeDecision"]["noDispatchReason"] = "Product-write execution boundary is not ready; Frontier continues B0/B1 readiness work."
    closure["humanNextStep"] = "No human action is needed; Frontier will continue lane-local B0/B1/B2 readiness work."
    return closure


def valid_frontier_closed_closure() -> dict:
    closure = valid_frontier_closure()
    closure["branchState"] = "closed"
    closure["gapDecisionMatrix"] = [{"gap": "lane-local evidence", "decision": "explicitly_out", "nextSafeAction": "No lane-local work remains."}]
    closure["branchReturnGate"] = {
        "state": "closed",
        "safeWorkRemainingCount": 0,
        "finalAuthorityGapCount": 0,
        "explicitlyOutCount": 1,
        "primaryReadyPacketExists": False,
        "reason": "Lane-local work is closed with no final-authority gap.",
    }
    closure["primaryReadyPacketRef"] = ""
    closure["remainingFinalAuthorityGaps"] = []
    closure["explicitlyOutGaps"] = ["No additional lane-local work remains."]
    closure["humanNextStep"] = "No human action is needed; lane-local closure is recorded."
    return closure


def write_coordination_fixtures(tmp: Path, source_path: Path) -> dict[str, Path]:
    files = {
        "sequence": tmp / "sequence-registry.json",
        "execution": tmp / "execution-boundary.json",
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
    write_json(files["execution"], valid_execution_boundary(tmp))
    write_json(files["lanes"], valid_lane_registry())
    write_json(files["source_status"], valid_source_status_registry())
    write_json(files["child"], valid_child_ledger())
    write_json(files["decision"], valid_decision_registry())
    write_json(files["closure"], valid_frontier_closure())
    files["ready_packet"].write_text("Primary-ready packet for selftest.\n", encoding="utf-8")
    files["cards"].write_text("schemaVersion: openaccp-card-registry.v1\nartifactType: card-registry\n", encoding="utf-8")
    write_json(
        files["current"],
        {
            "schemaVersion": "openaccp-current-manifest.v1.1",
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
            "executionBoundaryRef": "execution-boundary.json",
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

    bad_schema_source = json.loads(paths["source_pack"].read_text(encoding="utf-8"))
    bad_schema_source["schemaVersion"] = "wrong-version"
    bad_schema_source["currentSources"] = [{"status": "current"}]
    bad_schema_source_path = tmp / "bad-source-pack-schema.json"
    write_json(bad_schema_source_path, bad_schema_source)
    assert_exit("source pack JSON Schema rejects wrong version and missing source fields", run(["--artifact", str(bad_schema_source_path), "--ruleset", "source-pack", "--strict"]), 1)

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
    read_only_task_path = tmp / "read-only-task-card.json"
    write_json(read_only_task_path, task_card("B0"))
    read_only_handoff_path = tmp / "read-only-handoff.json"
    write_json(read_only_handoff_path, read_only_handoff())
    assert_exit(
        "valid read-only reviewer handoff",
        run(["--artifact", str(read_only_handoff_path), "--ruleset", "handoff", "--task-card", str(read_only_task_path), "--strict"]),
        0,
    )
    read_only_worker = read_only_handoff()
    read_only_worker["actorRole"] = "worker"
    read_only_worker["effectsPreset"] = "read_only_handoff"
    read_only_worker_path = tmp / "read-only-worker-handoff.json"
    write_json(read_only_worker_path, read_only_worker)
    assert_exit(
        "valid B0 worker read-only handoff",
        run(["--artifact", str(read_only_worker_path), "--ruleset", "handoff", "--task-card", str(read_only_task_path), "--strict"]),
        0,
    )
    bad_b0_worker_effect = read_only_worker.copy()
    bad_b0_worker_effect["worktree"] = "worktrees/docs-task-001"
    bad_b0_worker_effect["branchRef"] = "docs/task-001"
    bad_b0_worker_effect["baseCommit"] = "BASE-001"
    bad_b0_worker_effect["commit"] = "COMMIT-001"
    bad_b0_worker_effect["effectsPreset"] = "docs_task_card_commit"
    bad_b0_worker_effect["changedFiles"] = ["docs/guide.md"]
    bad_b0_worker_effect["changedArtifacts"] = [{"path": "docs/guide.md", "changeType": "created"}]
    bad_b0_worker_effect_path = tmp / "bad-b0-worker-effect.json"
    write_json(bad_b0_worker_effect_path, bad_b0_worker_effect)
    assert_exit(
        "B0 worker docs commit rejected",
        run(["--artifact", str(bad_b0_worker_effect_path), "--ruleset", "handoff", "--task-card", str(read_only_task_path), "--strict"]),
        1,
    )
    bad_read_only_claim = read_only_handoff()
    bad_read_only_claim["claims"] = ["final acceptance approved"]
    bad_read_only_claim_path = tmp / "bad-read-only-handoff-overclaim.json"
    write_json(bad_read_only_claim_path, bad_read_only_claim)
    assert_exit(
        "read-only handoff overclaim rejected",
        run(["--artifact", str(bad_read_only_claim_path), "--ruleset", "handoff", "--task-card", str(read_only_task_path), "--strict"]),
        1,
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

    bad_b3_handoff = json.loads(paths["handoff"].read_text(encoding="utf-8"))
    bad_b3_handoff["authority"] = "B3"
    bad_b3_handoff_path = tmp / "bad-b3-handoff.json"
    write_json(bad_b3_handoff_path, bad_b3_handoff)
    assert_exit("handoff rejects B3 authority", run(["--artifact", str(bad_b3_handoff_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]), 1)

    b1_task_path = tmp / "b1-task-card.json"
    write_json(b1_task_path, task_card("B1"))
    b1_handoff = json.loads(paths["handoff"].read_text(encoding="utf-8"))
    b1_handoff["authority"] = "B1"
    b1_handoff_path = tmp / "b1-docs-handoff.json"
    write_json(b1_handoff_path, b1_handoff)
    assert_exit("valid B1 worker docs handoff", run(["--artifact", str(b1_handoff_path), "--ruleset", "handoff", "--task-card", str(b1_task_path), "--strict"]), 0)

    bad_b1_mismatch = json.loads(paths["handoff"].read_text(encoding="utf-8"))
    bad_b1_mismatch_path = tmp / "bad-b1-task-b2-handoff.json"
    write_json(bad_b1_mismatch_path, bad_b1_mismatch)
    assert_exit("B1 task rejects B2 handoff", run(["--artifact", str(bad_b1_mismatch_path), "--ruleset", "handoff", "--task-card", str(b1_task_path), "--strict"]), 1)

    bad_b1_product = b1_handoff.copy()
    bad_b1_product["effectsPreset"] = "implementation_local_commit"
    bad_b1_product_path = tmp / "bad-b1-product-handoff.json"
    write_json(bad_b1_product_path, bad_b1_product)
    assert_exit("B1 worker product-write effect rejected", run(["--artifact", str(bad_b1_product_path), "--ruleset", "handoff", "--task-card", str(b1_task_path), "--strict"]), 1)

    bad_empty_write_handoff = json.loads(paths["handoff"].read_text(encoding="utf-8"))
    bad_empty_write_handoff["changedFiles"] = []
    bad_empty_write_handoff["changedArtifacts"] = []
    bad_empty_write_handoff_path = tmp / "bad-empty-write-handoff.json"
    write_json(bad_empty_write_handoff_path, bad_empty_write_handoff)
    assert_exit("write handoff rejects empty changed artifacts", run(["--artifact", str(bad_empty_write_handoff_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]), 1)

    bad_scope = json.loads(paths["handoff"].read_text(encoding="utf-8"))
    bad_scope["changedArtifacts"] = [{"path": "src/app.py", "changeType": "updated"}]
    bad_scope["changedFiles"] = ["src/app.py"]
    bad_scope_path = tmp / "bad-scope.json"
    write_json(bad_scope_path, bad_scope)
    assert_exit("scope overrun rejected", run(["--artifact", str(bad_scope_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]), 1)

    slash_scope_task = task_card()
    slash_scope_task["allowedScope"]["filesOrArtifacts"] = ["docs/*"]
    slash_scope_task_path = tmp / "slash-scope-task.json"
    write_json(slash_scope_task_path, slash_scope_task)
    backslash_handoff = json.loads(paths["handoff"].read_text(encoding="utf-8"))
    backslash_handoff["changedFiles"] = ["docs\\guide.md"]
    backslash_handoff["changedArtifacts"] = [{"path": "docs\\guide.md", "changeType": "created"}]
    backslash_handoff_path = tmp / "backslash-handoff.json"
    write_json(backslash_handoff_path, backslash_handoff)
    assert_exit("scope matcher normalizes backslashes", run(["--artifact", str(backslash_handoff_path), "--ruleset", "handoff", "--task-card", str(slash_scope_task_path), "--strict"]), 0)

    case_handoff = json.loads(paths["handoff"].read_text(encoding="utf-8"))
    case_handoff["changedFiles"] = ["DOCS/guide.md"]
    case_handoff["changedArtifacts"] = [{"path": "DOCS/guide.md", "changeType": "created"}]
    case_handoff_path = tmp / "case-sensitive-handoff.json"
    write_json(case_handoff_path, case_handoff)
    assert_exit("scope matcher is case-sensitive", run(["--artifact", str(case_handoff_path), "--ruleset", "handoff", "--task-card", str(slash_scope_task_path), "--strict"]), 1)


    coordination = write_coordination_fixtures(tmp, paths["source_pack"])
    assert_exit("valid current manifest", run(["--artifact", str(coordination["current"]), "--ruleset", "current-manifest", "--strict"]), 0)
    assert_exit("valid sequence registry", run(["--artifact", str(coordination["sequence"]), "--ruleset", "sequence-registry", "--strict"]), 0)
    bom_sequence_path = tmp / "bom-sequence-registry.json"
    bom_sequence_path.write_bytes(b"\xef\xbb\xbf" + coordination["sequence"].read_bytes())
    assert_exit("sequence registry accepts UTF-8 BOM", run(["--artifact", str(bom_sequence_path), "--ruleset", "sequence-registry", "--strict"]), 0)
    assert_exit("valid execution boundary", run(["--artifact", str(coordination["execution"]), "--ruleset", "execution-boundary", "--strict"]), 0)
    assert_exit("valid lane registry", run(["--artifact", str(coordination["lanes"]), "--ruleset", "lane-registry", "--strict"]), 0)
    assert_exit("valid child ledger", run(["--artifact", str(coordination["child"]), "--ruleset", "child-ledger", "--strict"]), 0)
    assert_exit("valid source status registry", run(["--artifact", str(coordination["source_status"]), "--ruleset", "source-status-registry", "--strict"]), 0)
    assert_exit("valid decision registry", run(["--artifact", str(coordination["decision"]), "--ruleset", "decision-registry", "--strict"]), 0)
    assert_exit("valid frontier closure", run(["--artifact", str(coordination["closure"]), "--ruleset", "frontier-closure", "--strict"]), 0)
    consume_result_path = tmp / "consume-result.json"
    write_json(consume_result_path, valid_consume_result())
    assert_exit("valid consume result", run(["--artifact", str(consume_result_path), "--ruleset", "consume-result", "--strict"]), 0)
    frontier_consume_result_path = tmp / "frontier-consume-result.json"
    write_json(frontier_consume_result_path, valid_frontier_consume_result())
    assert_exit(
        "valid consume result accepts ready Frontier closure cross-check",
        run(["--artifact", str(frontier_consume_result_path), "--ruleset", "consume-result", "--frontier-closure", str(coordination["closure"]), "--strict"]),
        0,
    )

    mismatched_consume = valid_consume_result()
    mismatched_consume["basisRefs"] = ["FC-OTHER", "frontier-other"]
    mismatched_consume_path = tmp / "mismatched-frontier-consume-result.json"
    write_json(mismatched_consume_path, mismatched_consume)
    assert_exit(
        "consume result rejects unmatched Frontier closure cross-check",
        run(["--artifact", str(mismatched_consume_path), "--ruleset", "consume-result", "--frontier-closure", str(coordination["closure"]), "--strict"]),
        1,
    )

    warning_closure = valid_frontier_closure()
    warning_closure["childLedgerRef"] = "missing-child-ledger.json"
    warning_closure_path = tmp / "warning-frontier-closure.json"
    write_json(warning_closure_path, warning_closure)
    assert_exit(
        "consume result strict rejects Frontier closure warning failures",
        run(["--artifact", str(frontier_consume_result_path), "--ruleset", "consume-result", "--frontier-closure", str(warning_closure_path), "--strict"]),
        1,
    )

    open_closure_path = tmp / "open-frontier-closure.json"
    write_json(open_closure_path, valid_frontier_progress_closure())
    assert_exit(
        "consume result rejects final accept of open Frontier closure",
        run(["--artifact", str(frontier_consume_result_path), "--ruleset", "consume-result", "--frontier-closure", str(open_closure_path), "--strict"]),
        1,
    )

    unsafe_ready_closure = valid_frontier_closure()
    unsafe_ready_closure["branchReturnGate"]["safeWorkRemainingCount"] = 1
    unsafe_ready_closure_path = tmp / "unsafe-ready-frontier-closure.json"
    write_json(unsafe_ready_closure_path, unsafe_ready_closure)
    assert_exit(
        "consume result rejects final accept of Frontier closure with safe work",
        run(["--artifact", str(frontier_consume_result_path), "--ruleset", "consume-result", "--frontier-closure", str(unsafe_ready_closure_path), "--strict"]),
        1,
    )

    closed_closure_path = tmp / "closed-frontier-closure.json"
    write_json(closed_closure_path, valid_frontier_closed_closure())
    assert_exit(
        "valid consume result accepts closed Frontier closure cross-check",
        run(["--artifact", str(frontier_consume_result_path), "--ruleset", "consume-result", "--frontier-closure", str(closed_closure_path), "--strict"]),
        0,
    )

    blocked_consume = valid_consume_result()
    blocked_consume["decision"] = "blocked"
    blocked_consume_path = tmp / "blocked-consume-result.json"
    write_json(blocked_consume_path, blocked_consume)
    assert_exit(
        "consume result allows blocked decision against open Frontier closure",
        run(["--artifact", str(blocked_consume_path), "--ruleset", "consume-result", "--frontier-closure", str(open_closure_path), "--strict"]),
        0,
    )

    machine_summary_path = tmp / "machine-summary.json"
    write_json(machine_summary_path, valid_machine_summary())
    assert_exit("valid machine summary", run(["--artifact", str(machine_summary_path), "--ruleset", "machine-summary", "--strict"]), 0)

    return_wake_path = tmp / "return-wake.json"
    write_json(return_wake_path, valid_return_wake())
    assert_exit("valid return wake", run(["--artifact", str(return_wake_path), "--ruleset", "return-wake", "--strict"]), 0)

    bad_return_wake = valid_return_wake()
    bad_return_wake["returnClass"] = "primary_ready"
    bad_return_wake["safeWorkRemainingCount"] = 1
    bad_return_wake_path = tmp / "bad-return-wake-safe-work.json"
    write_json(bad_return_wake_path, bad_return_wake)
    assert_exit("return wake rejects primary_ready with safe work", run(["--artifact", str(bad_return_wake_path), "--ruleset", "return-wake", "--strict"]), 1)

    bad_consume = valid_consume_result()
    bad_consume["consumerRole"] = "worker"
    bad_consume_path = tmp / "bad-final-consume-worker.json"
    write_json(bad_consume_path, bad_consume)
    assert_exit("consume result rejects worker final consume", run(["--artifact", str(bad_consume_path), "--ruleset", "consume-result", "--strict"]), 1)

    bad_summary = valid_machine_summary()
    bad_summary["role"] = "worker"
    bad_summary["authority"] = "B3"
    bad_summary_path = tmp / "bad-machine-summary-worker-b3.json"
    write_json(bad_summary_path, bad_summary)
    assert_exit("machine summary rejects worker B3", run(["--artifact", str(bad_summary_path), "--ruleset", "machine-summary", "--strict"]), 1)

    authority_charter_path = tmp / "authority-charter-primary.json"
    write_json(authority_charter_path, valid_authority_charter())
    assert_exit("valid authority charter", run(["--artifact", str(authority_charter_path), "--ruleset", "authority-charter", "--strict"]), 0)

    bad_ambiguous_authority = valid_authority_charter()
    bad_ambiguous_authority["finalAuthorityReservedTo"] = "Primary or human owner"
    bad_ambiguous_authority_path = tmp / "bad-authority-ambiguous-final-owner.json"
    write_json(bad_ambiguous_authority_path, bad_ambiguous_authority)
    assert_exit("authority charter rejects ambiguous final owner", run(["--artifact", str(bad_ambiguous_authority_path), "--ruleset", "authority-charter", "--strict"]), 1)

    bad_reserved_delegation = valid_authority_charter()
    bad_reserved_delegation["delegatedFinalAuthority"][0]["decision"] = "Approve production launch"
    bad_reserved_delegation_path = tmp / "bad-authority-reserved-delegation.json"
    write_json(bad_reserved_delegation_path, bad_reserved_delegation)
    assert_exit("authority charter rejects reserved Primary delegation", run(["--artifact", str(bad_reserved_delegation_path), "--ruleset", "authority-charter", "--strict"]), 1)

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

    bad_current_superseded = valid_sequence_registry()
    bad_current_superseded["prompts"][0]["status"] = "superseded"
    bad_current_superseded["prompts"][0]["supersededBy"] = "PROMPT-002"
    bad_current_superseded_path = tmp / "bad-current-prompt-superseded.json"
    write_json(bad_current_superseded_path, bad_current_superseded)
    assert_exit("sequence registry rejects superseded current prompt", run(["--artifact", str(bad_current_superseded_path), "--ruleset", "sequence-registry", "--strict"]), 1)

    bad_current_cancelled = valid_sequence_registry()
    bad_current_cancelled["prompts"][0]["status"] = "cancelled"
    bad_current_cancelled_path = tmp / "bad-current-prompt-cancelled.json"
    write_json(bad_current_cancelled_path, bad_current_cancelled)
    assert_exit("sequence registry rejects cancelled current prompt", run(["--artifact", str(bad_current_cancelled_path), "--ruleset", "sequence-registry", "--strict"]), 1)

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

    frontier_lane_template = json.loads(json.dumps(valid_lane_registry()["lanes"][0]))
    frontier_lane_template["role"] = "frontier"
    frontier_lane_template["authorityLevel"] = "B2"
    frontier_lane_template["returnGateStatus"]["state"] = "not_ready"
    ten_frontier_registry = valid_lane_registry()
    ten_frontier_registry["projectComplexity"] = "high"
    ten_frontier_registry["frontierDispatchMode"] = "multi_frontier"
    ten_frontier_registry["frontierDispatchReason"] = "High-complexity project with ten safe independent Frontier lanes."
    ten_frontier_registry["lanes"] = []
    for lane_number in range(1, 11):
        lane = json.loads(json.dumps(frontier_lane_template))
        lane["laneId"] = f"frontier-{lane_number:02d}"
        lane["objective"] = f"Coordinate lane {lane_number:02d}"
        lane["currentPromptId"] = f"PROMPT-F{lane_number:02d}"
        lane["assignedCardIds"] = [f"CARD-{lane_number:03d}"]
        ten_frontier_registry["lanes"].append(lane)
    ten_frontier_path = tmp / "valid-ten-frontier-lanes.json"
    write_json(ten_frontier_path, ten_frontier_registry)
    assert_exit("lane registry accepts ten Frontier lanes", run(["--artifact", str(ten_frontier_path), "--ruleset", "lane-registry", "--strict"]), 0)

    eleven_frontier_registry = json.loads(json.dumps(ten_frontier_registry))
    lane = json.loads(json.dumps(frontier_lane_template))
    lane["laneId"] = "frontier-11"
    lane["objective"] = "Coordinate lane 11"
    lane["currentPromptId"] = "PROMPT-F11"
    lane["assignedCardIds"] = ["CARD-011"]
    eleven_frontier_registry["lanes"].append(lane)
    eleven_frontier_path = tmp / "bad-eleven-frontier-lanes.json"
    write_json(eleven_frontier_path, eleven_frontier_registry)
    assert_exit("lane registry rejects eleven Frontier lanes", run(["--artifact", str(eleven_frontier_path), "--ruleset", "lane-registry", "--strict"]), 1)

    bad_execution = valid_execution_boundary(tmp)
    bad_execution["productRepoStatus"] = "found"
    bad_execution["productRepoPath"] = ""
    bad_execution_path = tmp / "bad-execution-boundary.json"
    write_json(bad_execution_path, bad_execution)
    assert_exit("execution boundary rejects missing found repo path", run(["--artifact", str(bad_execution_path), "--ruleset", "execution-boundary", "--strict"]), 1)

    blocked_execution = valid_execution_boundary(tmp)
    blocked_execution["productRepoStatus"] = "missing"
    blocked_execution["productRepoPath"] = ""
    blocked_execution["baseBranch"] = ""
    blocked_execution["sourceRoots"] = []
    blocked_execution["testEntrypoints"] = []
    blocked_execution["worktreePolicy"] = "unknown"
    blocked_execution["b2DispatchGate"] = {
        "state": "coordination_only",
        "allowsProductWrite": False,
        "reason": "Product repo fields are missing.",
        "missingInputs": ["productRepoPath", "baseBranch", "sourceRoots", "testEntrypoints", "worktreePolicy"],
    }
    blocked_execution_path = tmp / "blocked-execution-boundary.json"
    write_json(blocked_execution_path, blocked_execution)
    bad_product_write_lane = valid_lane_registry()
    bad_product_write_lane["lanes"][0]["role"] = "frontier"
    bad_product_write_lane["lanes"][0]["authorityLevel"] = "B2"
    bad_product_write_lane["lanes"][0]["executionBoundaryRef"] = "blocked-execution-boundary.json"
    bad_product_write_lane["lanes"][0]["b2DispatchGate"] = {
        "mode": "product_write",
        "state": "ready",
        "reason": "This incorrectly claims product-write dispatch is ready.",
    }
    bad_product_write_lane_path = tmp / "bad-product-write-lane.json"
    write_json(bad_product_write_lane_path, bad_product_write_lane)
    assert_exit("lane registry rejects B2 product write without execution gate", run(["--artifact", str(bad_product_write_lane_path), "--ruleset", "lane-registry", "--strict"]), 1)

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

    missing_wake_child = valid_child_ledger()
    del missing_wake_child["children"][0]["returnWake"]
    missing_wake_child_path = tmp / "bad-child-ledger-missing-return-wake.json"
    write_json(missing_wake_child_path, missing_wake_child)
    assert_exit("child ledger requires returnWake", run(["--artifact", str(missing_wake_child_path), "--ruleset", "child-ledger", "--strict"]), 1)

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

    progress_closure = valid_frontier_progress_closure()
    progress_closure_path = tmp / "frontier-progress-closure.json"
    write_json(progress_closure_path, progress_closure)
    assert_exit("frontier progress closure uses lane-progress packet", run(["--artifact", str(progress_closure_path), "--ruleset", "frontier-closure", "--strict"]), 0)

    bad_progress_ready = valid_frontier_progress_closure()
    bad_progress_ready["primaryReadyPacketRef"] = "primary-ready-packet.md"
    bad_progress_ready_path = tmp / "bad-progress-primary-ready.json"
    write_json(bad_progress_ready_path, bad_progress_ready)
    assert_exit("frontier progress rejects Primary-ready packet", run(["--artifact", str(bad_progress_ready_path), "--ruleset", "frontier-closure", "--strict"]), 1)

    bad_progress_consume = valid_frontier_progress_closure()
    bad_progress_consume["humanNextStep"] = "Primary should consume the stage packet."
    bad_progress_consume_path = tmp / "bad-progress-consume-text.json"
    write_json(bad_progress_consume_path, bad_progress_consume)
    assert_exit("frontier progress rejects Primary consume next step", run(["--artifact", str(bad_progress_consume_path), "--ruleset", "frontier-closure", "--strict"]), 1)

    cross_coord = tmp / "cross-coordination"
    cross_closures = cross_coord / "frontier-closures"
    cross_closures.mkdir(parents=True)
    cross_lane = valid_lane_registry()
    cross_lane["projectComplexity"] = "small"
    cross_lane["frontierDispatchMode"] = "single_frontier"
    cross_lane["frontierDispatchReason"] = "small project"
    cross_lane["lanes"][0]["laneId"] = "frontier-docs"
    cross_lane["lanes"][0]["role"] = "frontier"
    cross_lane["lanes"][0]["status"] = "prepared"
    cross_lane["lanes"][0]["authorityLevel"] = "B2"
    cross_lane["lanes"][0]["returnGateStatus"]["state"] = "not_ready"
    cross_lane["lanes"][0]["returnGateStatus"]["safeWorkRemainingCount"] = 1
    cross_lane["lanes"][0]["returnGateStatus"]["frontierClosureRef"] = "frontier-closures/frontier-docs.json"
    write_json(cross_coord / "lane-registry.json", cross_lane)
    cross_bad_closure = valid_frontier_closure()
    write_json(cross_closures / "frontier-docs.json", cross_bad_closure)
    (cross_closures / "primary-ready-packet.md").write_text("Primary-ready packet for cross-check.\n", encoding="utf-8")
    assert_exit("frontier closure rejects lane-registry not_ready conflict", run(["--artifact", str(cross_closures / "frontier-docs.json"), "--ruleset", "frontier-closure", "--strict"]), 1)

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
            "schemaVersion": "openaccp-status-report.v1",
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
            "Use human-explain-openaccp for every reply.",
            "Before Frontier dispatch, read facts input, working directory, preferred language, and repo path as the actual product code repository path.",
            "Resolve execution boundary and executionBoundaryRef before Frontier dispatch. Infer base branch, source roots, test entrypoints, worktree policy, and writable scope from the repo before asking follow-up questions.",
            "Ask only when execution inference is ambiguous, risky, or impossible.",
            "Create 10-20 project-level CARDs for normal or medium/high-complexity work before Frontier dispatch.",
            "Scan product workflow, backend/API, data/storage, frontend/UI, desktop/mobile/native/Electron/Tauri surfaces, integrations, security, testing, CI, release, and ops before finalizing CARDs.",
            "Default to at least two Frontier lanes when two safe independent CARD clusters exist.",
            "Use one Frontier only for a small project, a single safe lane, or an explicit user request, and record the reason.",
            "Every delegated Frontier, worker, reviewer, discovery, validation, and task-card-only prompt must include structured returnWake using openaccp-return-wake-owner.v1 with returnOwnerRole, returnOwnerThreadId, wakeChannel, wakeCapability, wakeOn, and expectedWakePath.",
        ]
    )
    primary_prompt_path = tmp / "primary.prompt.md"
    primary_prompt_path.write_text(primary_prompt, encoding="utf-8")
    assert_exit("valid prompt record", run(["--artifact", str(primary_prompt_path), "--ruleset", "prompt-record", "--strict"]), 0)

    prose_only_worker_prompt = "\n".join(
        [
            "Prompt ID: PROMPT-WORKER-PROSE-ONLY",
            "Role: worker",
            "Authority level: B1",
            "Preferred language: Chinese",
            "Use human-explain-openaccp for every reply.",
            "This worker will use returnWake with protocol openaccp-return-wake-owner.v1 when it is done.",
        ]
    )
    prose_only_worker_prompt_path = tmp / "bad-worker-return-wake-prose-only.prompt.md"
    prose_only_worker_prompt_path.write_text(prose_only_worker_prompt, encoding="utf-8")
    assert_exit("prompt record rejects prose-only returnWake", run(["--artifact", str(prose_only_worker_prompt_path), "--ruleset", "prompt-record", "--strict"]), 1)

    launcher_path = tmp / "primary.short.md"
    launcher_path.write_text(
        "\n".join(
            [
                "Project - Primary Orchestrator - Startup",
                "",
                "Read and execute this OpenACCP prompt record:",
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

    def write_launcher(path: Path, title: str, prompt_id: str, extra_lines: list[str] | None = None) -> None:
        path.write_text(
            "\n".join(
                [
                    title,
                    "Purpose: start a bounded OpenACCP thread.",
                    "",
                    "Read and execute this OpenACCP prompt record:",
                    f"- Prompt Record: {tmp / '.openaccp' / 'launchers' / (prompt_id + '.prompt.md')}",
                    f"- Prompt ID: {prompt_id}",
                    "- Preferred language: Chinese",
                    "",
                    *(extra_lines or []),
                    "",
                    "Hard requirements:",
                    "1. Read the prompt record explicitly as UTF-8.",
                    "2. Execute only the named Prompt ID.",
                    "3. If the file cannot be read cleanly, the Prompt ID is missing, or the text appears corrupted, stop and report launcher-read failure.",
                ]
            ),
            encoding="utf-8",
        )

    frontier_01_launcher = tmp / "frontier-01.short.md"
    write_launcher(frontier_01_launcher, "Project - Frontier 01 - Source Pack Lane", "openaccp-frontier-01")
    assert_exit("valid Frontier 01 launcher", run(["--artifact", str(frontier_01_launcher), "--ruleset", "launcher", "--strict"]), 0)

    frontier_10_launcher = tmp / "frontier-10.short.md"
    write_launcher(frontier_10_launcher, "Project - Frontier 10 - Release Lane", "openaccp-frontier-10")
    assert_exit("valid Frontier 10 launcher", run(["--artifact", str(frontier_10_launcher), "--ruleset", "launcher", "--strict"]), 0)

    f01_worker_launcher = tmp / "f01-worker.short.md"
    write_launcher(
        f01_worker_launcher,
        "Project - F01 Worker - Scoped Fix",
        "openaccp-f01-worker",
        ["Fallback launcher: direct subagent dispatch is unavailable."],
    )
    assert_exit("valid F01 worker fallback launcher", run(["--artifact", str(f01_worker_launcher), "--ruleset", "launcher", "--strict"]), 0)

    f10_worker_launcher = tmp / "f10-worker.short.md"
    write_launcher(
        f10_worker_launcher,
        "Project - F10 Worker - Scoped Fix",
        "openaccp-f10-worker",
        ["Fallback launcher: direct subagent dispatch is unavailable."],
    )
    assert_exit("valid F10 worker fallback launcher", run(["--artifact", str(f10_worker_launcher), "--ruleset", "launcher", "--strict"]), 0)

    po_reviewer_launcher = tmp / "po-reviewer.short.md"
    write_launcher(
        po_reviewer_launcher,
        "Project - PO Reviewer - Scope Review",
        "openaccp-po-reviewer",
        ["Fallback launcher: direct subagent dispatch is explicitly requested to be separately user-managed."],
    )
    assert_exit("valid PO reviewer fallback launcher", run(["--artifact", str(po_reviewer_launcher), "--ruleset", "launcher", "--strict"]), 0)

    invalid_launcher_cases = {
        "reject markdown heading launcher": "# Frontier Launcher",
        "reject generic Frontier launcher": "Project - Frontier Launcher - Source Pack Lane",
        "reject Frontier A launcher": "Project - Frontier A - Source Pack Lane",
        "reject Frontier 1 launcher": "Project - Frontier 1 - Source Pack Lane",
        "reject Frontier 11 launcher": "Project - Frontier 11 - Source Pack Lane",
        "reject F1 child launcher": "Project - F1 Worker - Scoped Fix",
        "reject F11 child launcher": "Project - F11 Worker - Scoped Fix",
    }
    for case_name, title in invalid_launcher_cases.items():
        bad_launcher = tmp / (case_name.replace(" ", "-") + ".short.md")
        write_launcher(bad_launcher, title, "openaccp-bad-launcher")
        assert_exit(case_name, run(["--artifact", str(bad_launcher), "--ruleset", "launcher", "--strict"]), 1)

    legacy_project = "Open" + "ACP"
    legacy_dir = "." + "open" + "acp"
    legacy_prompt_prefix = "open" + "acp-"
    legacy_namespace_launcher = tmp / "legacy-namespace.short.md"
    legacy_namespace_launcher.write_text(
        "\n".join(
            [
                "Project - Frontier 02 - Data Lane",
                "",
                f"Read and execute this {legacy_project} prompt record:",
                f"- Prompt Record: {tmp / legacy_dir / 'launchers' / 'frontier-lane-02.prompt.md'}",
                f"- Prompt ID: {legacy_prompt_prefix}frontier-demo-lane-02",
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
    assert_exit("launcher rejects legacy namespace", run(["--artifact", str(legacy_namespace_launcher), "--ruleset", "launcher", "--strict"]), 1)

    launcher_output_path = tmp / "launcher-output.md"
    launcher_output_path.write_text(
        "\n".join(
            [
                "Create a new thread from the left sidebar, paste each short launcher below, and start that thread.",
                "",
                "```prompt",
                frontier_01_launcher.read_text(encoding="utf-8"),
                "```",
                "",
                "```prompt",
                frontier_10_launcher.read_text(encoding="utf-8"),
                "```",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("valid launcher output blocks", run(["--artifact", str(launcher_output_path), "--ruleset", "launcher-output", "--strict"]), 0)

    auto_launcher_output_path = tmp / "auto-launcher-output.md"
    auto_launcher_output_path.write_text(
        "\n".join(
            [
                "Dispatch channel: agent_thread_spawn",
                "Primary directly spawned Frontier 01 from the on-disk prompt record.",
                "Prompt ID: openaccp-frontier-demo-lane-01",
                "Spawn result: dispatched.",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("launcher output allows auto dispatch without paste block", run(["--artifact", str(auto_launcher_output_path), "--ruleset", "launcher-output", "--strict"]), 0)

    one_click_launcher_output_path = tmp / "one-click-launcher-output.md"
    one_click_launcher_output_path.write_text(
        "\n".join(
            [
                "Dispatch channel: one_click",
                "Primary opened Frontier 01 from the saved short launcher seed.",
                "Prompt ID: openaccp-frontier-demo-lane-01",
                "Launch result: started.",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("launcher output allows one-click dispatch without paste block", run(["--artifact", str(one_click_launcher_output_path), "--ruleset", "launcher-output", "--strict"]), 0)

    attempted_failed_bare_dispatch_path = tmp / "attempted-failed-bare-dispatch.md"
    attempted_failed_bare_dispatch_path.write_text(
        "\n".join(
            [
                "agent_thread_spawn was attempted and failed.",
                "frontier-01.short.md",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("launcher output rejects bare failed direct dispatch keyword", run(["--artifact", str(attempted_failed_bare_dispatch_path), "--ruleset", "launcher-output", "--strict"]), 1)

    failed_explicit_dispatch_path = tmp / "failed-explicit-dispatch.md"
    failed_explicit_dispatch_path.write_text(
        "\n".join(
            [
                "Dispatch channel: agent_thread_spawn",
                "Primary attempted to spawn Frontier 01 from the on-disk prompt record.",
                "Prompt ID: openaccp-frontier-demo-lane-01",
                "Spawn result: failed.",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("launcher output rejects failed explicit direct dispatch", run(["--artifact", str(failed_explicit_dispatch_path), "--ruleset", "launcher-output", "--strict"]), 1)

    missing_prompt_manual_output_path = tmp / "missing-prompt-manual-launcher-output.md"
    missing_prompt_manual_output_path.write_text(
        "\n".join(
            [
                "Dispatch channel: manual_paste",
                "Create a new thread from the left sidebar and paste the short launcher there.",
                "frontier-01.short.md",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("manual launcher output rejects file-only fallback", run(["--artifact", str(missing_prompt_manual_output_path), "--ruleset", "launcher-output", "--strict"]), 1)

    direct_unavailable_file_only_path = tmp / "direct-unavailable-file-only-launcher-output.md"
    direct_unavailable_file_only_path.write_text(
        "\n".join(
            [
                "Direct dispatch is unavailable here.",
                "frontier-01.short.md",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("launcher output rejects direct-dispatch-unavailable file-only fallback", run(["--artifact", str(direct_unavailable_file_only_path), "--ruleset", "launcher-output", "--strict"]), 1)

    missing_thread_manual_output_path = tmp / "missing-thread-manual-launcher-output.md"
    missing_thread_manual_output_path.write_text(
        "\n".join(
            [
                "Dispatch channel: manual_paste",
                "",
                "```prompt",
                frontier_01_launcher.read_text(encoding="utf-8"),
                "```",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("manual launcher output rejects missing paste guidance", run(["--artifact", str(missing_thread_manual_output_path), "--ruleset", "launcher-output", "--strict"]), 1)

    bad_launcher_output_path = tmp / "bad-launcher-output.md"
    bad_launcher_output_path.write_text(
        "\n".join(
            [
                "Create a new thread from the left sidebar, paste the short launcher below, and start that thread.",
                "",
                "```prompt",
                (tmp / "reject-Frontier-A-launcher.short.md").read_text(encoding="utf-8"),
                "```",
            ]
        ),
        encoding="utf-8",
    )
    assert_exit("launcher output rejects invalid prompt block title", run(["--artifact", str(bad_launcher_output_path), "--ruleset", "launcher-output", "--strict"]), 1)

    card_registry_path = tmp / "card-registry.md"
    card_rows = [
        f"| CARD-{idx:03d} | domain-{idx} | B2 | frontier-{idx % 3} | ready-candidate | objective | SRC-001 | task-card candidates TASK-{idx:03d}-A/TASK-{idx:03d}-B |"
        for idx in range(1, 13)
    ]
    card_registry_path.write_text(
        "\n".join(
            [
                "schemaVersion: openaccp-card-registry.v1",
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
                "schemaVersion: openaccp-card-registry.v1",
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
                "| Area | OpenACCP startup. |",
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

    human_next_step_report_path = tmp / "human-next-step-formal-report.md"
    human_next_step_report_path.write_text(
        formal_report_path.read_text(encoding="utf-8").replace("## Recommended Next Step", "## Human Next Step"),
        encoding="utf-8",
    )
    assert_exit("English formal report accepts Human Next Step", run(["--artifact", str(human_next_step_report_path), "--ruleset", "formal-report", "--strict"]), 0)

    zh_frontier_report_path = tmp / "zh-frontier-formal-report.md"
    zh_frontier_report_path.write_text(
        "\n".join(
            [
                "Response ID: RESP-ZH-001",
                "Response log path: chat reply",
                "",
                "| 类型和状态 | 内容 |",
                "|---|---|",
                "| 做了什么 | Frontier 刷新了 lane backlog。 |",
                "| 总体进度 | 60%。仍有 B2 子任务未 consume。 |",
                "| Lane | docs lane。 |",
                "| 目标 | 收口当前 lane 的 B0/B1/B2 工作。 |",
                "| 缺口 | 需要继续 consume worker handoff。 |",
                "| 下一步 | Frontier 继续派发 reviewer 并 consume 结果。 |",
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

    bad_slash_header_report_path = tmp / "bad-slash-header-formal-report.md"
    bad_slash_header_report_path.write_text(
        zh_frontier_report_path.read_text(encoding="utf-8").replace("| 类型和状态 | 内容 |", "| 类型/状态 | 内容 |"),
        encoding="utf-8",
    )
    assert_exit("Chinese formal report rejects old slash header", run(["--artifact", str(bad_slash_header_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    bad_nobr_report_path = tmp / "bad-nobr-formal-report.md"
    bad_nobr_report_path.write_text(
        zh_frontier_report_path.read_text(encoding="utf-8").replace("| 类型和状态 | 内容 |", "| <nobr>类型和状态</nobr> | 内容 |"),
        encoding="utf-8",
    )
    assert_exit("formal report rejects nobr", run(["--artifact", str(bad_nobr_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    bad_checkpoint_report_path = tmp / "bad-checkpoint-formal-report.md"
    bad_checkpoint_report_path.write_text(
        zh_frontier_report_path.read_text(encoding="utf-8").replace("| Lane | docs lane。 |", "| Checkpoint | lane-local closure。 |\n| Lane | docs lane。 |"),
        encoding="utf-8",
    )
    assert_exit("formal report rejects checkpoint row", run(["--artifact", str(bad_checkpoint_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    bad_report_item_header_path = tmp / "bad-report-item-header-formal-report.md"
    bad_report_item_header_path.write_text(
        zh_frontier_report_path.read_text(encoding="utf-8").replace("| 类型和状态 | 内容 |", "| 报告项 | 内容 |"),
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
    bad_command_report_path.write_text(zh_frontier_report_path.read_text(encoding="utf-8") + "\n```powershell\nopenaccp --version\n```\n", encoding="utf-8")
    assert_exit("formal report rejects command dumps", run(["--artifact", str(bad_command_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    bad_tail_report_path = tmp / "bad-tail-formal-report.md"
    bad_tail_report_path.write_text(zh_frontier_report_path.read_text(encoding="utf-8") + "\n## Extra Section\n- This should not appear after Recommended Next Step.\n", encoding="utf-8")
    assert_exit("formal report requires trailing recommended next step", run(["--artifact", str(bad_tail_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 1)

    english_dominant_zh_report_path = tmp / "english-dominant-zh-formal-report.md"
    english_dominant_zh_report_path.write_text(
        zh_frontier_report_path.read_text(encoding="utf-8")
        + "\nSource classification summary: current sources are final specification, product requirements, platform checklist, and migration readiness notes.\n",
        encoding="utf-8",
    )
    assert_exit("Chinese formal report does not structurally reject English prose", run(["--artifact", str(english_dominant_zh_report_path), "--ruleset", "formal-report", "--preferred-language", "Chinese", "--strict"]), 0)

    frontier_contract_path = tmp / "frontier-contract.md"
    frontier_contract_path.write_text(
        "\n".join(
            [
                "Prompt ID: FRONTIER-001",
                "Role: Frontier",
                "Authority level: B2",
                "Use human-explain-openaccp and formal-report-openaccp for every status reply.",
                "gapDecisionMatrix",
                "branchReturnGate",
                "worktreeDecision",
                "Subagent-first dispatch is required.",
                "Use dispatch_current_thread_subagent for child work in the current Frontier thread.",
                "Dispatch bounded worker, reviewer, discovery, validation, and subagent work inside the lane.",
                "Do not use the human as a thread launcher for B0/B1/B2-safe child work.",
                "Human-managed child launchers are fallback only when direct subagent dispatch is unavailable, unsafe, explicitly requested, or requires a separately user-managed session.",
                "Maintain a child ledger with promptId, taskId, role, authority, effects, subagent id, returnWake, dispatchStatus, handoffStatus, consumeStatus, and remaining risk.",
                "Return wake owner routing is required: use returnWake with openaccp-return-wake-owner.v1; child work wakes the owning Frontier, and this Frontier will wake Primary when the branchReturnGate is ready.",
                "Every Frontier reply must end with a recommended next step.",
                "Do not return to Primary merely because a provisional packet, source baseline, handoff, or consume-result was written.",
                "`blocked on Primary` is valid only when branchReturnGate is satisfied and every visible remaining gap is needs_final_authority or explicitly_out.",
                "```json",
                json.dumps(
                    {
                        "schemaVersion": "openaccp-frontier-orchestration-contract.v1",
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
                            "executionBoundaryRef": "execution-boundary.json",
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
                                "returnWake",
                                "dispatchStatus",
                                "handoffStatus",
                                "consumeStatus",
                            ]
                        },
                        "returnWake": {
                            "required": True,
                            "protocol": "openaccp-return-wake-owner.v1",
                            "returnOwnerRole": "primary",
                            "returnOwnerThreadId": "THREAD-PRIMARY-001",
                            "primaryThreadId": "THREAD-PRIMARY-001",
                            "primaryMirrorWake": False,
                            "wakeChannel": "direct_thread_message",
                            "wakeCapability": "available",
                            "wakeOn": ["primary_ready", "early_return_risk", "blocked", "failed"],
                            "expectedWakePath": ".openaccp/coordination/wake-pending/WAKE-001.json",
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
                "Use human-explain-openaccp and formal-report-openaccp for every status reply.",
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
    (public_pkg / "README.md").write_text("OpenACCP public package\n", encoding="utf-8")
    (public_pkg / "templates" / "formal-report.md").write_text("Response ID: `OACCP-TEMPLATE-0001`\n", encoding="utf-8")
    (public_pkg / "examples" / "formal-report-example.md").write_text("Response ID: `OACCP-EXAMPLE-0001`\n", encoding="utf-8")
    assert_exit("formal report templates and examples allowed", run(["--artifact", str(public_pkg), "--ruleset", "public-package", "--strict"]), 0)

    reports_dir = public_pkg / "reports"
    reports_dir.mkdir()
    internal_report = reports_dir / "release-report.md"
    internal_report.write_text("Response ID: `OACCP-2026-0001`\nResponse log path: local response log\n", encoding="utf-8")
    assert_exit("internal formal report rejected from public reports path", run(["--artifact", str(public_pkg), "--ruleset", "public-package", "--strict"]), 1)
    internal_report.unlink()

    (public_pkg / "README.md").write_text("OpenACCP 中文入口\n", encoding="utf-8")
    assert_exit("root README must stay English", run(["--artifact", str(public_pkg), "--ruleset", "public-package", "--strict"]), 1)

    local_response_path = "C:" + "\\" + "Users" + "\\" + "example" + "\\" + "OpenACCP" + "\\" + "response.md"
    (public_pkg / "README.md").write_text("Response log path: " + local_response_path + "\n", encoding="utf-8")
    assert_exit("local absolute response log path rejected", run(["--artifact", str(public_pkg), "--ruleset", "public-package", "--strict"]), 1)


def assert_cli_entrypoints(tmp: Path) -> None:
    version_proc = subprocess.run(
        [sys.executable, "-m", "openaccp", "--version"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    assert_exit("python -m openaccp version", version_proc, 0)

    init_proc = subprocess.run(
        [sys.executable, "-m", "openaccp", "init", str(tmp / "starter")],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    assert_exit("python -m openaccp init dry run", init_proc, 0)
    required_output = [
        "coordination",
        "execution-boundary.json",
        "lane-registry.json",
        "sequence-registry.json",
        "current-manifest.json",
    ]
    missing = [item for item in required_output if item not in init_proc.stdout]
    if missing:
        print("FAIL python -m openaccp init lists coordination artifacts: missing " + ", ".join(missing))
        print(init_proc.stdout)
        raise SystemExit(1)
    print("PASS python -m openaccp init lists coordination artifacts")

    write_target = tmp / "starter-write"
    write_proc = subprocess.run(
        [sys.executable, "-m", "openaccp", "init", str(write_target), "--write"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    assert_exit("python -m openaccp init write", write_proc, 0)
    init_artifacts = [
        ("source-pack.json", "source-pack", []),
        ("scope-boundary.json", "scope-boundary", []),
        ("assumptions.json", "assumption-ledger", []),
        ("authority-charter.json", "authority-charter", []),
        ("task-card.json", "task-card", ["--source-pack", str(write_target / "source-pack.json")]),
        ("card-registry.md", "card-registry", []),
        ("coordination/execution-boundary.json", "execution-boundary", []),
        ("coordination/source-status-registry.json", "source-status-registry", []),
        ("coordination/sequence-registry.json", "sequence-registry", []),
        ("coordination/lane-registry.json", "lane-registry", []),
        ("coordination/child-ledgers/primary.json", "child-ledger", []),
        ("coordination/decision-registry.json", "decision-registry", []),
        ("coordination/current-manifest.json", "current-manifest", []),
    ]
    for rel_path, ruleset, extra_args in init_artifacts:
        assert_exit(
            f"init write artifact validates: {rel_path}",
            run(["--artifact", str(write_target / rel_path), "--ruleset", ruleset, *extra_args, "--strict"]),
            0,
        )
    overwrite_proc = subprocess.run(
        [sys.executable, "-m", "openaccp", "init", str(write_target), "--write"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    assert_exit("python -m openaccp init refuses overwrite", overwrite_proc, 1)


def assert_required_fields_cover_schema() -> None:
    sys.path.insert(0, str(ROOT))
    from openaccp.validate import JSON_SCHEMA_RULESETS, REQUIRED_FIELDS

    missing_by_ruleset: list[str] = []
    for ruleset in sorted(JSON_SCHEMA_RULESETS):
        schema_path = ROOT / "openaccp" / "schemas" / f"{ruleset}.schema.json"
        if not schema_path.exists() or ruleset not in REQUIRED_FIELDS:
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema_required = set(schema.get("required", []))
        validator_required = set(REQUIRED_FIELDS.get(ruleset, []))
        missing = sorted(schema_required - validator_required)
        if missing:
            missing_by_ruleset.append(f"{ruleset}: {', '.join(missing)}")
    if missing_by_ruleset:
        print("FAIL required fields missing schema fields: " + " | ".join(missing_by_ruleset))
        raise SystemExit(1)
    print("PASS validator required fields cover schema required fields")


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        paths = fixtures(tmp)
        assert_json_rules(tmp, paths)
        assert_text_rules(tmp)
        assert_public_package_rules(tmp)
        assert_cli_entrypoints(tmp)
        assert_required_fields_cover_schema()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
