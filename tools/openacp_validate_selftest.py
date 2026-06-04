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
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(VALIDATOR), *args], text=True, capture_output=True)


def assert_exit(name: str, proc: subprocess.CompletedProcess[str], expected: int) -> None:
    if proc.returncode != expected:
        print(f"FAIL {name}: expected {expected}, got {proc.returncode}")
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit(1)
    print(f"PASS {name}")


def fixtures(tmp: Path) -> dict[str, Path]:
    source_pack = {
        "schemaVersion": "openacp-source-pack.v1",
        "artifactType": "source-pack",
        "currentSources": [{"sourceId": "SRC-001", "title": "Current PRD", "status": "current"}],
        "referenceSources": [{"sourceId": "REF-001", "title": "Old idea", "status": "reference"}],
        "deprecatedSources": [{"sourceId": "DEP-001", "title": "Discarded plan", "status": "deprecated"}],
        "readingOrder": ["source-pack", "task-card"],
        "conflictPolicy": ["current sources win over reference sources"],
        "scopeBoundaryRef": "scope-boundary.json",
        "openQuestionsRef": "open-questions.md",
        "assumptionsRef": "assumptions.json",
    }
    task_card = {
        "schemaVersion": "openacp-task-card.v1",
        "artifactType": "task-card",
        "taskId": "TASK-001",
        "objective": "Create starter documentation",
        "inputRefs": ["SRC-001"],
        "allowedScope": {"filesOrArtifacts": ["docs/**"], "effects": ["docs-only"]},
        "forbiddenScope": {"filesOrArtifacts": ["src/**"], "effects": ["external-side-effect"], "claims": ["accepted", "merged"]},
        "acceptanceCriteria": ["Documentation explains the workflow"],
        "verificationPlan": [{"check": "scan", "method": "validator", "required": True}],
        "stopConditions": ["Implementation needed"],
        "expectedHandoff": {"artifactType": "handoff", "requiredFields": ["verificationEvidence"]},
        "authorityRequired": "B2",
        "authorityCharterRef": "authority-charter.json",
        "riskLevel": "low",
    }
    handoff = {
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
    paths = {
        "source_pack": tmp / "source-pack.json",
        "task_card": tmp / "task-card.json",
        "handoff": tmp / "handoff.json",
    }
    write_json(paths["source_pack"], source_pack)
    write_json(paths["task_card"], task_card)
    write_json(paths["handoff"], handoff)
    return paths


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        paths = fixtures(tmp)
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
        assert_exit(
            "legacy source rejected",
            run(["--artifact", str(bad_task_path), "--ruleset", "task-card", "--source-pack", str(paths["source_pack"]), "--strict"]),
            1,
        )

        bad_handoff = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        bad_handoff["claims"] = ["accepted and merged"]
        bad_handoff_path = tmp / "bad-handoff.json"
        write_json(bad_handoff_path, bad_handoff)
        assert_exit(
            "handoff overclaim rejected",
            run(["--artifact", str(bad_handoff_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
            1,
        )

        bad_final_ref = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        bad_final_ref["claims"] = ["accepted and merged"]
        bad_final_ref["finalAuthorityRef"] = "free-form"
        bad_final_ref_path = tmp / "bad-final-ref.json"
        write_json(bad_final_ref_path, bad_final_ref)
        assert_exit(
            "finalAuthorityRef does not bypass overclaim",
            run(["--artifact", str(bad_final_ref_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
            1,
        )

        bad_task_id = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        bad_task_id["taskId"] = "TASK-OTHER"
        bad_task_id_path = tmp / "bad-task-id.json"
        write_json(bad_task_id_path, bad_task_id)
        assert_exit(
            "handoff taskId mismatch rejected",
            run(["--artifact", str(bad_task_id_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
            1,
        )

        bad_actor_task = json.loads(paths["task_card"].read_text(encoding="utf-8"))
        bad_actor_task["authorityRequired"] = "B0"
        bad_actor_task_path = tmp / "bad-actor-task.json"
        write_json(bad_actor_task_path, bad_actor_task)
        assert_exit(
            "worker handoff cannot satisfy B0 task",
            run(["--artifact", str(paths["handoff"]), "--ruleset", "handoff", "--task-card", str(bad_actor_task_path), "--strict"]),
            1,
        )

        frontier_task = json.loads(paths["task_card"].read_text(encoding="utf-8"))
        frontier_task["taskId"] = "TASK-FRONTIER-001"
        frontier_task["objective"] = "Synthesize lane-local orchestration evidence"
        frontier_task["allowedScope"] = {"filesOrArtifacts": [".openacp/**"], "effects": ["orchestration-local"]}
        frontier_task["forbiddenScope"] = {"filesOrArtifacts": ["src/**", "docs/**"], "effects": ["implementation", "docs-commit"], "claims": ["accepted", "merged"]}
        frontier_task_path = tmp / "frontier-task.json"
        write_json(frontier_task_path, frontier_task)

        frontier_actor = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        frontier_actor["taskId"] = "TASK-FRONTIER-001"
        frontier_actor["actorRole"] = "frontier"
        frontier_actor["effectsPreset"] = "orchestration_local_write"
        frontier_actor["changedFiles"] = [".openacp/frontier/lane-status.md"]
        frontier_actor["changedArtifacts"] = [{"path": ".openacp/frontier/lane-status.md", "changeType": "created"}]
        frontier_actor["claims"] = ["Synthesized provisional lane evidence"]
        frontier_actor_path = tmp / "frontier-actor.json"
        write_json(frontier_actor_path, frontier_actor)
        assert_exit(
            "frontier B2 lane handoff accepted",
            run(["--artifact", str(frontier_actor_path), "--ruleset", "handoff", "--task-card", str(frontier_task_path), "--strict"]),
            0,
        )

        bad_frontier_effects = json.loads(frontier_actor_path.read_text(encoding="utf-8"))
        bad_frontier_effects["effectsPreset"] = "docs_task_card_commit"
        bad_frontier_effects_path = tmp / "bad-frontier-effects.json"
        write_json(bad_frontier_effects_path, bad_frontier_effects)
        assert_exit(
            "frontier implementation effects rejected",
            run(["--artifact", str(bad_frontier_effects_path), "--ruleset", "handoff", "--task-card", str(frontier_task_path), "--strict"]),
            1,
        )

        bad_repro = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        del bad_repro["baseCommit"]
        bad_repro_path = tmp / "bad-repro-handoff.json"
        write_json(bad_repro_path, bad_repro)
        assert_exit(
            "handoff reproducibility fields required",
            run(["--artifact", str(bad_repro_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
            1,
        )

        bad_scope = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        bad_scope["changedArtifacts"] = [{"path": "src/app.py", "changeType": "updated"}]
        bad_scope["changedFiles"] = ["src/app.py"]
        bad_scope_path = tmp / "bad-scope.json"
        write_json(bad_scope_path, bad_scope)
        assert_exit(
            "scope overrun rejected",
            run(["--artifact", str(bad_scope_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
            1,
        )

        bad_changed_files = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        bad_changed_files["changedFiles"] = ["src/app.py"]
        bad_changed_files_path = tmp / "bad-changed-files.json"
        write_json(bad_changed_files_path, bad_changed_files)
        assert_exit(
            "changedFiles scope overrun rejected",
            run(["--artifact", str(bad_changed_files_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
            1,
        )

        bad_worker_b3 = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        bad_worker_b3["authority"] = "B3"
        bad_worker_b3_path = tmp / "bad-worker-b3.json"
        write_json(bad_worker_b3_path, bad_worker_b3)
        assert_exit(
            "worker B3 handoff rejected",
            run(["--artifact", str(bad_worker_b3_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
            1,
        )

        bad_skip = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        bad_skip["stateClaim"] = "verified"
        bad_skip["verificationEvidence"] = [{"check": "scan", "method": "validator", "result": "skipped"}]
        bad_skip_path = tmp / "bad-skip.json"
        write_json(bad_skip_path, bad_skip)
        assert_exit(
            "skip reason required",
            run(["--artifact", str(bad_skip_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
            1,
        )

        bad_verification_item = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        bad_verification_item["verificationEvidence"] = [{"result": "pass"}]
        bad_verification_item_path = tmp / "bad-verification-item.json"
        write_json(bad_verification_item_path, bad_verification_item)
        assert_exit(
            "verification item required fields enforced",
            run(["--artifact", str(bad_verification_item_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
            1,
        )

        bad_plan = json.loads(paths["task_card"].read_text(encoding="utf-8"))
        bad_plan["verificationPlan"] = [{}]
        bad_plan_path = tmp / "bad-plan.json"
        write_json(bad_plan_path, bad_plan)
        assert_exit(
            "task verification plan fields enforced",
            run(["--artifact", str(bad_plan_path), "--ruleset", "task-card", "--source-pack", str(paths["source_pack"]), "--strict"]),
            1,
        )

        bad_authority_ref = json.loads(paths["task_card"].read_text(encoding="utf-8"))
        del bad_authority_ref["authorityCharterRef"]
        bad_authority_ref_path = tmp / "bad-authority-ref.json"
        write_json(bad_authority_ref_path, bad_authority_ref)
        assert_exit(
            "B2 task card requires authorityCharterRef",
            run(["--artifact", str(bad_authority_ref_path), "--ruleset", "task-card", "--source-pack", str(paths["source_pack"]), "--strict"]),
            1,
        )

        bad_forbidden_claim = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        bad_forbidden_claim["claims"] = ["Used external-side-effect during setup"]
        bad_forbidden_claim_path = tmp / "bad-forbidden-claim.json"
        write_json(bad_forbidden_claim_path, bad_forbidden_claim)
        assert_exit(
            "forbidden claim marker rejected",
            run(["--artifact", str(bad_forbidden_claim_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
            1,
        )

        current_manifest = {
            "schemaVersion": "openacp-current-manifest.v1",
            "artifactType": "current-manifest",
            "manifestId": "MAN-001",
            "preferredLanguage": "Chinese",
            "workingDirectory": str(tmp / "work"),
            "factsInput": str(paths["source_pack"]),
            "currentSourcePackRef": str(paths["source_pack"]),
            "invalidSourceRefs": [],
            "deprecatedSourceRefs": ["DEP-001"],
            "promptRegistryRef": "prompts.json",
            "responseRegistryRef": "responses.json",
            "handoffRegistryRef": "handoffs.json",
            "sequenceRegistryRef": "sequence-registry.json",
            "cardRegistryRef": "cards.json",
        }
        for ref_name in [
            "prompts.json",
            "responses.json",
            "handoffs.json",
            "sequence-registry.json",
            "cards.json",
        ]:
            (tmp / ref_name).write_text("[]\n", encoding="utf-8")
        current_manifest_path = tmp / "current-manifest.json"
        write_json(current_manifest_path, current_manifest)
        assert_exit("valid current manifest", run(["--artifact", str(current_manifest_path), "--ruleset", "current-manifest", "--strict"]), 0)

        bad_current_manifest = dict(current_manifest)
        bad_current_manifest["deprecatedSourceRefs"] = ["SRC-001"]
        bad_current_manifest_path = tmp / "bad-current-manifest.json"
        write_json(bad_current_manifest_path, bad_current_manifest)
        assert_exit("current manifest rejects deprecated current source", run(["--artifact", str(bad_current_manifest_path), "--ruleset", "current-manifest", "--strict"]), 1)

        bad_invalid_manifest = dict(current_manifest)
        bad_invalid_manifest["invalidSourceRefs"] = ["SRC-001"]
        bad_invalid_manifest_path = tmp / "bad-invalid-manifest.json"
        write_json(bad_invalid_manifest_path, bad_invalid_manifest)
        assert_exit("current manifest rejects invalid current source", run(["--artifact", str(bad_invalid_manifest_path), "--ruleset", "current-manifest", "--strict"]), 1)

        sequence_registry = {
            "schemaVersion": "openacp-sequence-registry.v1",
            "artifactType": "sequence-registry",
            "registryId": "SEQ-001",
            "currentPromptId": "PROMPT-001",
            "latestResponseId": "RESP-001",
            "prompts": [{"promptId": "PROMPT-001", "path": "prompt.md", "role": "primary", "status": "active"}],
            "responses": [{"responseId": "RESP-001", "promptId": "PROMPT-001", "path": "response.md", "status": "complete"}],
            "handoffs": [{"handoffId": "HAND-001", "taskId": "TASK-001", "path": "handoff.json", "status": "present"}],
            "cards": [{"cardId": "CARD-001", "status": "ready", "ownerRole": "primary"}],
        }
        sequence_registry_path = tmp / "sequence-registry.json"
        write_json(sequence_registry_path, sequence_registry)
        assert_exit("valid sequence registry", run(["--artifact", str(sequence_registry_path), "--ruleset", "sequence-registry", "--strict"]), 0)

        bad_sequence_registry = dict(sequence_registry)
        bad_sequence_registry["currentPromptId"] = "PROMPT-MISSING"
        bad_sequence_registry_path = tmp / "bad-sequence-registry.json"
        write_json(bad_sequence_registry_path, bad_sequence_registry)
        assert_exit("sequence registry current prompt required", run(["--artifact", str(bad_sequence_registry_path), "--ruleset", "sequence-registry", "--strict"]), 1)

        bad_response_registry = json.loads(json.dumps(sequence_registry))
        bad_response_registry["currentPromptId"] = "PROMPT-002"
        bad_response_registry["prompts"].append({"promptId": "PROMPT-002", "path": "other.md", "role": "frontier", "status": "active"})
        bad_response_registry_path = tmp / "bad-response-registry.json"
        write_json(bad_response_registry_path, bad_response_registry)
        assert_exit("sequence registry latest response prompt match required", run(["--artifact", str(bad_response_registry_path), "--ruleset", "sequence-registry", "--strict"]), 1)

        prompt_record_path = tmp / "primary.prompt.md"
        prompt_record_path.write_text(
            "\n".join(
                [
                    "Prompt ID: PROMPT-001",
                    "Role: Primary",
                    "Authority level: B3",
                    "Preferred language: Chinese",
                    "Use human-explain-openacp for every reply.",
                ]
            ),
            encoding="utf-8",
        )
        assert_exit("valid prompt record", run(["--artifact", str(prompt_record_path), "--ruleset", "prompt-record", "--strict"]), 0)

        launcher_path = tmp / "launcher.md"
        launcher_path.write_text(
            "\n".join(
                [
                    "Project - Primary Orchestrator - Startup",
                    "Purpose: start the Primary coordination thread.",
                    "",
                    "Read and execute this OpenACP prompt record:",
                    f"- Prompt Record: {prompt_record_path}",
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
        assert_exit("valid short launcher", run(["--artifact", str(launcher_path), "--ruleset", "launcher", "--strict"]), 0)

        bad_child_launcher_path = tmp / "bad-child-launcher.md"
        bad_child_launcher_path.write_text(
            "\n".join(
                [
                    "Project - Worker - Startup",
                    "Purpose: start a worker child thread.",
                    "",
                    "Read and execute this OpenACP prompt record:",
                    f"- Prompt Record: {prompt_record_path}",
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
        assert_exit("child launcher requires fallback reason", run(["--artifact", str(bad_child_launcher_path), "--ruleset", "launcher", "--strict"]), 1)

        bad_launcher_language_path = tmp / "bad-launcher-language.md"
        bad_launcher_language_path.write_text(
            launcher_path.read_text(encoding="utf-8").replace("- Preferred language: Chinese\n", ""),
            encoding="utf-8",
        )
        assert_exit("launcher preferred language required", run(["--artifact", str(bad_launcher_language_path), "--ruleset", "launcher", "--strict"]), 1)

        bad_launcher_path = tmp / "bad-launcher.md"
        bad_launcher_path.write_text(launcher_path.read_text(encoding="utf-8") + "\n\n## Active Closure Rules\nFull prompt body here.\n", encoding="utf-8")
        assert_exit("full prompt rejected from launcher", run(["--artifact", str(bad_launcher_path), "--ruleset", "launcher", "--strict"]), 1)

        formal_report_path = tmp / "formal-report.md"
        formal_report_path.write_text(
            "\n".join(
                [
                    "Response ID: RESP-001",
                    "",
                    "| Item | Content |",
                    "|---|---|",
                    "| Changed | Primary created startup artifacts. |",
                    "| Progress | 80%. Startup is ready but final acceptance is pending. |",
                    "| Gate | Startup validation passed. |",
                    "| Area | OpenACP startup. |",
                    "| Goal | Start Primary from current facts. |",
                    "| Gaps | User project execution has not started. |",
                    "| Next | Start the Primary launcher. |",
                    "",
                    "## Evidence Details",
                    "- Basis: validator selftest fixture.",
                ]
            ),
            encoding="utf-8",
        )
        assert_exit("valid formal report", run(["--artifact", str(formal_report_path), "--ruleset", "formal-report", "--strict"]), 0)

        bad_formal_report_path = tmp / "bad-formal-report.md"
        bad_formal_report_path.write_text(
            formal_report_path.read_text(encoding="utf-8").replace("| Changed |", "| What changed |"),
            encoding="utf-8",
        )
        assert_exit("legacy formal report rows rejected", run(["--artifact", str(bad_formal_report_path), "--ruleset", "formal-report", "--strict"]), 1)

        bad_report_id_path = tmp / "bad-report-id.md"
        bad_report_id_path.write_text(formal_report_path.read_text(encoding="utf-8").replace("Response ID:", "Report ID:"), encoding="utf-8")
        assert_exit("formal report requires response id", run(["--artifact", str(bad_report_id_path), "--ruleset", "formal-report", "--strict"]), 1)

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
                    "Maintain a child ledger with promptId, responseId, taskId, handoffId, role, authority, effects, subagent id, terminal status, consume status, and remaining risk.",
                    "Every reply must include a human next step.",
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

        public_pkg = tmp / "public-package"
        (public_pkg / "templates").mkdir(parents=True)
        (public_pkg / "examples").mkdir()
        (public_pkg / "templates" / "formal-report.md").write_text("Response ID: `OACP-TEMPLATE-0001`\n", encoding="utf-8")
        (public_pkg / "examples" / "formal-report-example.md").write_text("Response ID: `OACP-EXAMPLE-0001`\n", encoding="utf-8")
        assert_exit(
            "formal report templates and examples allowed",
            run(["--artifact", str(public_pkg), "--ruleset", "public-package", "--strict"]),
            0,
        )

        reports_dir = public_pkg / "reports"
        reports_dir.mkdir()
        internal_report = reports_dir / "release-report.md"
        internal_report.write_text("Response ID: `OACP-2026-0001`\nResponse log path: local response log\n", encoding="utf-8")
        assert_exit(
            "internal formal report rejected from public reports path",
            run(["--artifact", str(public_pkg), "--ruleset", "public-package", "--strict"]),
            1,
        )
        internal_report.unlink()

        local_response_path = "C:" + "\\" + "Users" + "\\" + "example" + "\\" + "OpenACP" + "\\" + "response.md"
        (public_pkg / "README.md").write_text("Response log path: " + local_response_path + "\n", encoding="utf-8")
        assert_exit(
            "local absolute response log path rejected",
            run(["--artifact", str(public_pkg), "--ruleset", "public-package", "--strict"]),
            1,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
