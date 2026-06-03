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
        "actorRole": "worker",
        "workspaceRef": "local-workspace",
        "branchRef": "docs/task-001",
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

        bad_frontier_actor = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        bad_frontier_actor["actorRole"] = "frontier"
        bad_frontier_actor_path = tmp / "bad-frontier-actor.json"
        write_json(bad_frontier_actor_path, bad_frontier_actor)
        assert_exit(
            "frontier handoff cannot satisfy B2 implementation task",
            run(["--artifact", str(bad_frontier_actor_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
            1,
        )

        bad_scope = json.loads(paths["handoff"].read_text(encoding="utf-8"))
        bad_scope["changedArtifacts"] = [{"path": "src/app.py", "changeType": "updated"}]
        bad_scope_path = tmp / "bad-scope.json"
        write_json(bad_scope_path, bad_scope)
        assert_exit(
            "scope overrun rejected",
            run(["--artifact", str(bad_scope_path), "--ruleset", "handoff", "--task-card", str(paths["task_card"]), "--strict"]),
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
