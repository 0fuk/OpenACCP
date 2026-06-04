#!/usr/bin/env python3
"""OpenACP artifact validator.

This validator is a structural and hygiene gate. It does not replace
semantic review, CI, security review, or final owner acceptance.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from .version import VERSION
except ImportError:  # pragma: no cover - supports direct script execution
    from version import VERSION

RULESETS = {
    "authority-charter",
    "assumption-ledger",
    "current-manifest",
    "formal-report",
    "frontier-contract",
    "handoff",
    "launcher",
    "prompt-record",
    "review-report",
    "scope-boundary",
    "sequence-registry",
    "source-pack",
    "status-report",
    "task-card",
    "public-package",
}

TEXT_RULESETS = {
    "prompt-record",
    "launcher",
    "formal-report",
    "frontier-contract",
}

REQUIRED_FIELDS: dict[str, list[str]] = {
    "source-pack": [
        "schemaVersion",
        "artifactType",
        "currentSources",
        "referenceSources",
        "deprecatedSources",
        "readingOrder",
        "conflictPolicy",
        "scopeBoundaryRef",
        "openQuestionsRef",
        "assumptionsRef",
    ],
    "scope-boundary": [
        "schemaVersion",
        "artifactType",
        "inScope",
        "outOfScope",
        "deferred",
        "requiresHumanApproval",
        "forbiddenActions",
        "stopConditions",
        "scopeLeakExamples",
    ],
    "task-card": [
        "schemaVersion",
        "artifactType",
        "taskId",
        "objective",
        "inputRefs",
        "allowedScope",
        "forbiddenScope",
        "acceptanceCriteria",
        "verificationPlan",
        "stopConditions",
        "expectedHandoff",
        "authorityRequired",
        "riskLevel",
    ],
    "authority-charter": [
        "schemaVersion",
        "artifactType",
        "charterId",
        "grantedRole",
        "authorityLevel",
        "allowedActions",
        "forbiddenActions",
        "delegationRules",
        "finalAuthorityReservedTo",
        "scopeLimits",
        "expiresWhen",
    ],
    "handoff": [
        "schemaVersion",
        "artifactType",
        "handoffId",
        "taskId",
        "responseId",
        "actorRole",
        "authority",
        "workspaceRef",
        "worktree",
        "branchRef",
        "baseCommit",
        "commit",
        "dataRisk",
        "effectsPreset",
        "changedFiles",
        "changedArtifacts",
        "claims",
        "verificationEvidence",
        "deviations",
        "risks",
        "assumptionsUsed",
        "remainingWork",
        "stateClaim",
    ],
    "review-report": [
        "schemaVersion",
        "artifactType",
        "reviewId",
        "targetHandoffId",
        "reviewedArtifacts",
        "scopeAssessment",
        "testAssessment",
        "claimAssessment",
        "findings",
        "recommendation",
        "residualRisk",
    ],
    "status-report": [
        "schemaVersion",
        "artifactType",
        "reportId",
        "basisRefs",
        "currentState",
        "completedWork",
        "unverifiedClaims",
        "blockers",
        "nextActions",
        "authorityLimits",
    ],
    "assumption-ledger": [
        "schemaVersion",
        "artifactType",
        "assumptions",
    ],
    "current-manifest": [
        "schemaVersion",
        "artifactType",
        "manifestId",
        "preferredLanguage",
        "workingDirectory",
        "factsInput",
        "currentSourcePackRef",
        "invalidSourceRefs",
        "deprecatedSourceRefs",
        "promptRegistryRef",
        "responseRegistryRef",
        "handoffRegistryRef",
        "sequenceRegistryRef",
        "cardRegistryRef",
    ],
    "sequence-registry": [
        "schemaVersion",
        "artifactType",
        "registryId",
        "currentPromptId",
        "latestResponseId",
        "prompts",
        "responses",
        "handoffs",
        "cards",
    ],
}

ARTIFACT_TYPE_BY_RULESET = {
    "source-pack": "source-pack",
    "scope-boundary": "scope-boundary",
    "task-card": "task-card",
    "authority-charter": "authority-charter",
    "handoff": "handoff",
    "review-report": "review-report",
    "assumption-ledger": "assumption-ledger",
    "current-manifest": "current-manifest",
    "sequence-registry": "sequence-registry",
}

FINAL_STATE_CLAIMS = {
    "accepted",
    "merged",
    "released",
    "launched",
    "complete",
    "final",
    "waived",
}

NON_FINAL_HANDOFF_STATES = {
    "proposed",
    "implemented",
    "verified",
    "reviewed",
}

AUTHORITY_LEVELS = {"B0", "B1", "B2", "B3"}
RISK_LEVELS = {"low", "medium", "high"}
ROLES = {"primary", "frontier", "worker", "reviewer", "discovery", "human-owner"}
REVIEW_RECOMMENDATIONS = {"approve", "amend", "split-follow-up", "reject"}
VERIFY_RESULTS = {"pass", "fail", "skipped"}
SOURCE_STATUSES = {"current", "reference", "deprecated"}
DATA_RISK_LEVELS = {"none", "low", "medium", "high", "sensitive"}
EFFECTS_PRESETS = {
    "read_only_handoff",
    "review_handoff",
    "orchestration_local_write",
    "docs_task_card_commit",
    "implementation_local_commit",
    "primary_only",
    "custom_expanded",
}
PROMPT_ID_RE = re.compile(r"(?im)^\s*(?:-\s*)?Prompt ID\s*:\s*`?([A-Za-z0-9][A-Za-z0-9_.:-]*)`?\s*$")
RESPONSE_ID_RE = re.compile(r"(?im)^\s*(?:-\s*)?Response ID\s*:\s*`?([A-Za-z0-9][A-Za-z0-9_.:-]*)`?\s*$")
PROMPT_RECORD_RE = re.compile(r"(?im)^\s*-\s*Prompt Record\s*:\s*(.+?)\s*$")

FORMAL_ROW_SETS = [
    {"Changed", "Progress", "Gate", "Area", "Goal", "Gaps", "Next"},
]

FULL_PROMPT_MARKERS = [
    "## Active Closure Rules",
    "## B0/B1/B2 Closure Loop",
    "## Project Inputs",
    "## Startup Work",
    "# Primary Orchestrator Prompt Record",
    "# Frontier Orchestrator Prompt Record",
]

MOJIBAKE_MARKERS = [
    chr(0xFFFD),
    chr(0x00C3),
    chr(0x00C2),
    chr(0x00E2) + chr(0x20AC),
    chr(0x00E5) + chr(0x00AD) + chr(0x2014),
    chr(0x00E5) + chr(0x2020) + chr(0x00B7),
]

PRIVATE_LEAK_PATTERNS = [
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"/(?:Users|home|var|tmp)/[^\s]+"),
    re.compile(r"\b[A-Z][A-Za-z0-9_-]+_(?:Prompt|Response|Coordination|Handoff|Log|Registry)s?\b"),
    re.compile(r"\b(?:internal|private|customer|production)[_-](?:log|handoff|registry|prompt|record)\b", re.IGNORECASE),
]

SECRET_MARKER_PATTERNS = [
    re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][A-Za-z0-9_\-./+=]{12,}['\"]"),
    re.compile(r"(?i)\b(?:bearer)\s+[A-Za-z0-9_\-./+=]{20,}"),
]

PUBLIC_SCAN_SKIP_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".openacp-local",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}

INTERNAL_FORMAL_REPORT_MARKERS = [
    "Response ID",
    "Response log path",
    "internal release review",
    "owner release review",
]


@dataclass
class Check:
    check_id: str
    severity: str
    status: str
    message: str
    location: str = ""


@dataclass
class Report:
    artifact: str
    ruleset: str
    checks: list[Check] = field(default_factory=list)

    def add(self, check_id: str, severity: str, status: str, message: str, location: str = "") -> None:
        self.checks.append(Check(check_id, severity, status, message, location))

    def status(self, strict: bool) -> str:
        for check in self.checks:
            if check.status == "fail" and check.severity == "blocking":
                return "fail"
        if strict:
            for check in self.checks:
                if check.status == "fail" and check.severity == "warning":
                    return "fail"
        return "pass"

    def to_dict(self, strict: bool) -> dict[str, Any]:
        return {
            "schemaVersion": "openacp-validator-report.v1",
            "validatorVersion": VERSION,
            "status": self.status(strict),
            "artifact": self.artifact,
            "ruleset": self.ruleset,
            "checks": [check.__dict__ for check in self.checks],
        }


def read_utf8(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError as exc:
        return None, f"UTF-8 decode failed: {exc}"
    except OSError as exc:
        return None, f"read failed: {exc}"


def load_json(path: Path, report: Report) -> Any | None:
    text, error = read_utf8(path)
    if error:
        report.add("UTF8_READ", "blocking", "fail", error)
        return None
    assert text is not None
    report.add("UTF8_READ", "blocking", "pass", "Artifact read as UTF-8.")
    scan_mojibake(text, report, str(path))
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        report.add("JSON_PARSE", "blocking", "fail", f"JSON parse failed: {exc}", str(path))
        return None
    report.add("JSON_PARSE", "blocking", "pass", "JSON parsed.")
    return data


def scan_mojibake(text: str, report: Report, location: str) -> None:
    hits = [marker for marker in MOJIBAKE_MARKERS if marker in text]
    if hits:
        report.add("MOJIBAKE", "blocking", "fail", f"Common mojibake markers found: {', '.join(hits)}", location)
    else:
        report.add("MOJIBAKE", "blocking", "pass", "No configured mojibake markers found.", location)


def scan_private_leaks(text: str, report: Report, location: str) -> None:
    hits: list[str] = []
    for pattern in PRIVATE_LEAK_PATTERNS:
        match = pattern.search(text)
        if match:
            hits.append(match.group(0))
    if hits:
        report.add("PRIVATE_LEAK_SCAN", "blocking", "fail", f"Private path or internal identifier marker found: {', '.join(sorted(set(hits)))}", location)
    else:
        report.add("PRIVATE_LEAK_SCAN", "blocking", "pass", "No configured private path or internal identifier markers found.", location)


def scan_secret_markers(text: str, report: Report, location: str) -> None:
    hits: list[str] = []
    for pattern in SECRET_MARKER_PATTERNS:
        match = pattern.search(text)
        if match:
            hits.append(match.group(0)[:64])
    if hits:
        report.add("SECRET_MARKER_SCAN", "blocking", "fail", f"Potential secret marker found: {', '.join(hits)}", location)
    else:
        report.add("SECRET_MARKER_SCAN", "blocking", "pass", "No configured secret markers found.", location)


def require_fields(data: Any, required: list[str], report: Report) -> bool:
    if not isinstance(data, dict):
        report.add("ROOT_OBJECT", "blocking", "fail", "Artifact root must be a JSON object.")
        return False
    missing = [field for field in required if field not in data]
    if missing:
        report.add("REQUIRED_FIELDS", "blocking", "fail", f"Missing required fields: {', '.join(missing)}")
        return False
    report.add("REQUIRED_FIELDS", "blocking", "pass", "All required fields are present.")
    return True


def require_non_empty_array(data: dict[str, Any], field: str, report: Report) -> None:
    value = data.get(field)
    if not isinstance(value, list) or not value:
        report.add(f"{field.upper()}_NON_EMPTY", "blocking", "fail", f"{field} must be a non-empty array.")
    else:
        report.add(f"{field.upper()}_NON_EMPTY", "blocking", "pass", f"{field} is non-empty.")


def require_non_empty_string(data: dict[str, Any], field: str, report: Report) -> None:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        report.add(f"{field.upper()}_NON_EMPTY", "blocking", "fail", f"{field} must be a non-empty string.")
    else:
        report.add(f"{field.upper()}_NON_EMPTY", "blocking", "pass", f"{field} is present.")


def normalize_table_label(raw: str) -> str:
    cleaned = raw.strip().strip("`")
    cleaned = cleaned.replace("\u3000", "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_table_rows(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        left = normalize_table_label(cells[0])
        right = cells[1].strip()
        if not left or left.lower() in {"item", "项", "字段"}:
            continue
        if set(left) <= {"-"}:
            continue
        rows.append((left, right))
    return rows


def validate_prompt_record_text(text: str, report: Report) -> None:
    prompt_ids = PROMPT_ID_RE.findall(text)
    if not prompt_ids:
        report.add("PROMPT_ID", "blocking", "fail", "Prompt record must include a stable Prompt ID line.")
    elif len(set(prompt_ids)) != 1:
        report.add("PROMPT_ID", "blocking", "fail", "Prompt record must contain exactly one stable Prompt ID.")
    else:
        report.add("PROMPT_ID", "blocking", "pass", f"Prompt ID found: {prompt_ids[0]}.")
    if re.search(r"(?im)^\s*(Role|角色)\s*:", text):
        report.add("PROMPT_ROLE", "blocking", "pass", "Prompt record names a role.")
    else:
        report.add("PROMPT_ROLE", "blocking", "fail", "Prompt record must name a role.")
    if re.search(r"(?im)^\s*(Authority|权限|Authority level)\s*:", text):
        report.add("PROMPT_AUTHORITY", "blocking", "pass", "Prompt record names authority.")
    else:
        report.add("PROMPT_AUTHORITY", "blocking", "fail", "Prompt record must name authority.")
    if re.search(r"(?i)preferred\s*language|preferredLanguage|首选语言|语言", text):
        report.add("PREFERRED_LANGUAGE", "blocking", "pass", "Prompt record carries language preference.")
    else:
        report.add("PREFERRED_LANGUAGE", "blocking", "fail", "Prompt record must carry preferred language.")
    if "human-explain-openacp" in text:
        report.add("HUMAN_EXPLAIN_REQUIRED", "blocking", "pass", "Prompt record requires human-explain-openacp.")
    else:
        report.add("HUMAN_EXPLAIN_REQUIRED", "blocking", "fail", "Prompt record must require human-explain-openacp for replies.")


def validate_launcher_text(text: str, report: Report) -> None:
    line_count = len([line for line in text.splitlines() if line.strip()])
    if line_count > 40:
        report.add("SHORT_LAUNCHER_LENGTH", "blocking", "fail", "Launcher must be short; full prompt records belong on disk.")
    else:
        report.add("SHORT_LAUNCHER_LENGTH", "blocking", "pass", "Launcher is short.")
    prompt_ids = PROMPT_ID_RE.findall(text)
    if not prompt_ids:
        report.add("PROMPT_ID", "blocking", "fail", "Launcher must name a Prompt ID.")
    else:
        report.add("PROMPT_ID", "blocking", "pass", "Launcher names a Prompt ID.")
    if PROMPT_RECORD_RE.search(text):
        report.add("PROMPT_RECORD_PATH", "blocking", "pass", "Launcher names a prompt record path.")
    else:
        report.add("PROMPT_RECORD_PATH", "blocking", "fail", "Launcher must name the on-disk prompt record path.")
    if re.search(r"UTF-?8", text, re.IGNORECASE):
        report.add("UTF8_REQUIREMENT", "blocking", "pass", "Launcher requires explicit UTF-8 read.")
    else:
        report.add("UTF8_REQUIREMENT", "blocking", "fail", "Launcher must require explicit UTF-8 read.")
    if re.search(r"(?i)preferred\s*language|preferredLanguage", text):
        report.add("PREFERRED_LANGUAGE", "blocking", "pass", "Launcher carries preferred language.")
    else:
        report.add("PREFERRED_LANGUAGE", "blocking", "fail", "Launcher must carry the preferred language or language fallback.")
    lowered = text.lower()
    if "stop" in lowered and ("missing" in lowered or "corrupt" in lowered or "cannot be read" in lowered):
        report.add("READ_FAILURE_STOP", "blocking", "pass", "Launcher has a read-failure stop rule.")
    else:
        report.add("READ_FAILURE_STOP", "blocking", "fail", "Launcher must stop on read failure, missing Prompt ID, or corruption.")
    full_hits = [marker for marker in FULL_PROMPT_MARKERS if marker in text]
    if full_hits:
        report.add("FULL_PROMPT_IN_LAUNCHER", "blocking", "fail", "Launcher appears to contain a full prompt body: " + ", ".join(full_hits))
    else:
        report.add("FULL_PROMPT_IN_LAUNCHER", "blocking", "pass", "Launcher does not include configured full-prompt markers.")


def validate_formal_report_text(text: str, report: Report) -> None:
    response_ids = RESPONSE_ID_RE.findall(text)
    if not response_ids:
        report.add("RESPONSE_ID", "blocking", "fail", "Formal report must include Response ID.")
    else:
        report.add("RESPONSE_ID", "blocking", "pass", "Formal report includes Response ID.")
    rows = extract_table_rows(text)
    labels = {label for label, _ in rows}
    if any(required.issubset(labels) for required in FORMAL_ROW_SETS):
        report.add("FORMAL_ROWS", "blocking", "pass", "Formal report has a known role-aware row set.")
    else:
        report.add("FORMAL_ROWS", "blocking", "fail", "Formal report rows must match a known OpenACP row set.")
    bad_labels = labels.intersection({"What changed", "Checkpoint", "Lane or area", "Next step", "Validation"})
    if bad_labels:
        report.add("LEGACY_ROW_LABELS", "blocking", "fail", "Legacy or overlong row labels found: " + ", ".join(sorted(bad_labels)))
    else:
        report.add("LEGACY_ROW_LABELS", "blocking", "pass", "No legacy long row labels found.")
    progress_cells = [right for label, right in rows if label in {"Progress", "总体进度"}]
    if progress_cells and any(re.search(r"\d+\s*%", cell) for cell in progress_cells):
        report.add("PROGRESS_PERCENT", "blocking", "pass", "Progress row includes a numeric estimate.")
    else:
        report.add("PROGRESS_PERCENT", "blocking", "fail", "Formal report progress row must include a numeric percentage.")
    if re.search(r"Evidence Details|证据|依据|Basis", text, re.IGNORECASE):
        report.add("EVIDENCE_DETAILS", "blocking", "pass", "Formal report includes evidence or basis details outside the table.")
    else:
        report.add("EVIDENCE_DETAILS", "blocking", "fail", "Formal report must include Evidence Details or basis outside the table.")


def validate_frontier_contract_text(text: str, report: Report) -> None:
    if re.search(r"(?i)authority(?:Level| level)?\s*[:：]\s*B2|Authority\s+B2|权限.*B2", text):
        report.add("FRONTIER_B2_AUTHORITY", "blocking", "pass", "Frontier contract grants B2 lane authority.")
    else:
        report.add("FRONTIER_B2_AUTHORITY", "blocking", "fail", "Frontier contract must grant B2 lane authority by default.")
    required_terms = ["gapDecisionMatrix", "branchReturnGate", "worktreeDecision"]
    missing = [term for term in required_terms if term not in text]
    if missing:
        report.add("FRONTIER_CLOSURE_FIELDS", "blocking", "fail", "Frontier contract missing closure fields: " + ", ".join(missing))
    else:
        report.add("FRONTIER_CLOSURE_FIELDS", "blocking", "pass", "Frontier closure fields are present.")
    lowered = text.lower()
    if "worker" in lowered and "reviewer" in lowered and ("subagent" in lowered or "sub-agent" in lowered or "dispatch" in lowered):
        report.add("FRONTIER_DISPATCH", "blocking", "pass", "Frontier contract allows bounded downstream dispatch.")
    else:
        report.add("FRONTIER_DISPATCH", "blocking", "fail", "Frontier contract must allow bounded worker/reviewer/subagent dispatch.")
    if "human-explain-openacp" in text and "formal-report-openacp" in text:
        report.add("FRONTIER_REPORTING", "blocking", "pass", "Frontier contract requires human explanation and formal reports.")
    else:
        report.add("FRONTIER_REPORTING", "blocking", "fail", "Frontier contract must require human-explain-openacp and formal-report-openacp.")


def validate_source_pack(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "source-pack":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be source-pack.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is source-pack.")
    require_non_empty_array(data, "currentSources", report)
    for group_name in ["currentSources", "referenceSources", "deprecatedSources"]:
        sources = data.get(group_name, [])
        if not isinstance(sources, list):
            report.add(f"{group_name.upper()}_TYPE", "blocking", "fail", f"{group_name} must be an array.")
            continue
        for idx, source in enumerate(sources):
            loc = f"{group_name}[{idx}]"
            if not isinstance(source, dict):
                report.add("SOURCE_OBJECT", "blocking", "fail", "Source entry must be an object.", loc)
                continue
            status = source.get("status")
            if status not in SOURCE_STATUSES:
                report.add("SOURCE_STATUS", "blocking", "fail", "Source status must be current, reference, or deprecated.", loc)
            elif group_name == "currentSources" and status != "current":
                report.add("CURRENT_SOURCE_STATUS", "blocking", "fail", "currentSources entries must have status current.", loc)
            elif group_name == "referenceSources" and status != "reference":
                report.add("REFERENCE_SOURCE_STATUS", "blocking", "fail", "referenceSources entries must have status reference.", loc)
            elif group_name == "deprecatedSources" and status != "deprecated":
                report.add("DEPRECATED_SOURCE_STATUS", "blocking", "fail", "deprecatedSources entries must have status deprecated.", loc)
    report.add("SOURCE_STATUS_GROUPS", "blocking", "pass", "Source status groups checked.")


def validate_scope_boundary(data: dict[str, Any], report: Report) -> None:
    for field_name in [
        "inScope",
        "outOfScope",
        "requiresHumanApproval",
        "forbiddenActions",
        "stopConditions",
        "scopeLeakExamples",
    ]:
        require_non_empty_array(data, field_name, report)


def validate_task_card(data: dict[str, Any], report: Report, source_pack: dict[str, Any] | None) -> None:
    if data.get("artifactType") != "task-card":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be task-card.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is task-card.")
    if data.get("authorityRequired") not in AUTHORITY_LEVELS:
        report.add("AUTHORITY_REQUIRED", "blocking", "fail", "authorityRequired must be B0, B1, B2, or B3.")
    else:
        report.add("AUTHORITY_REQUIRED", "blocking", "pass", "authorityRequired is valid.")
    if data.get("authorityRequired") in {"B2", "B3"} and not str(data.get("authorityCharterRef", "")).strip():
        report.add("AUTHORITY_CHARTER_REF", "blocking", "fail", "B2/B3 task cards must include authorityCharterRef.")
    elif data.get("authorityRequired") in {"B2", "B3"}:
        report.add("AUTHORITY_CHARTER_REF", "blocking", "pass", "B2/B3 task card includes authorityCharterRef.")
    else:
        report.add("AUTHORITY_CHARTER_REF", "blocking", "pass", "authorityCharterRef is not required for B0/B1 task cards.")
    if data.get("riskLevel") not in RISK_LEVELS:
        report.add("RISK_LEVEL", "blocking", "fail", "riskLevel must be low, medium, or high.")
    else:
        report.add("RISK_LEVEL", "blocking", "pass", "riskLevel is valid.")
    for field_name in ["inputRefs", "acceptanceCriteria", "verificationPlan", "stopConditions"]:
        require_non_empty_array(data, field_name, report)
    validate_task_verification_plan(data, report)
    for scope_name in ["allowedScope", "forbiddenScope"]:
        scope = data.get(scope_name)
        if not isinstance(scope, dict):
            report.add(f"{scope_name.upper()}_OBJECT", "blocking", "fail", f"{scope_name} must be an object.")
            continue
        for subfield in ["filesOrArtifacts", "effects"]:
            if subfield not in scope or not isinstance(scope[subfield], list) or not scope[subfield]:
                report.add(f"{scope_name.upper()}_{subfield.upper()}", "blocking", "fail", f"{scope_name}.{subfield} must be non-empty.")
        if scope_name == "forbiddenScope" and (not isinstance(scope.get("claims"), list) or not scope.get("claims")):
            report.add("FORBIDDEN_SCOPE_CLAIMS", "blocking", "fail", "forbiddenScope.claims must be non-empty.")
    check_task_card_source_refs(data, source_pack, report)


def validate_task_verification_plan(data: dict[str, Any], report: Report) -> None:
    plan = data.get("verificationPlan", [])
    if not isinstance(plan, list):
        return
    failures = []
    for idx, item in enumerate(plan):
        loc = f"verificationPlan[{idx}]"
        if not isinstance(item, dict):
            failures.append(f"{loc}: not an object")
            continue
        for field_name in ["check", "method", "required"]:
            if field_name not in item:
                failures.append(f"{loc}: missing {field_name}")
            elif field_name in {"check", "method"} and not str(item.get(field_name, "")).strip():
                failures.append(f"{loc}: empty {field_name}")
        if "required" in item and item.get("required") not in {True, False}:
            failures.append(f"{loc}: required must be boolean")
    if failures:
        report.add("VERIFICATION_PLAN_ITEMS", "blocking", "fail", "Invalid verificationPlan items: " + "; ".join(failures))
    else:
        report.add("VERIFICATION_PLAN_ITEMS", "blocking", "pass", "verificationPlan items have required fields.")


def source_id_statuses(source_pack: dict[str, Any]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for group in ["currentSources", "referenceSources", "deprecatedSources"]:
        for source in source_pack.get(group, []):
            if isinstance(source, dict) and "sourceId" in source and "status" in source:
                statuses[str(source["sourceId"])] = str(source["status"])
    return statuses


def check_task_card_source_refs(data: dict[str, Any], source_pack: dict[str, Any] | None, report: Report) -> None:
    input_refs = data.get("inputRefs", [])
    if not source_pack:
        report.add("SOURCE_PACK_CROSSCHECK", "warning", "fail", "No --source-pack provided; inputRefs were not checked against current/reference/deprecated status.")
        return
    statuses = source_id_statuses(source_pack)
    bad: list[str] = []
    unknown: list[str] = []
    for ref in input_refs:
        ref_text = str(ref)
        status = statuses.get(ref_text)
        if status in {"reference", "deprecated"}:
            bad.append(f"{ref_text}:{status}")
        elif status is None:
            unknown.append(ref_text)
    if bad:
        report.add("TASK_INPUT_REFS_CURRENT", "blocking", "fail", f"Task card inputRefs include non-current sources: {', '.join(bad)}")
    elif unknown:
        report.add("TASK_INPUT_REFS_KNOWN", "warning", "fail", f"Task card inputRefs not found in source pack: {', '.join(unknown)}")
    else:
        report.add("TASK_INPUT_REFS_CURRENT", "blocking", "pass", "Task card inputRefs are current sources.")


def validate_authority_charter(data: dict[str, Any], report: Report) -> None:
    if data.get("grantedRole") not in ROLES:
        report.add("GRANTED_ROLE", "blocking", "fail", "grantedRole is not a known OpenACP role.")
    else:
        report.add("GRANTED_ROLE", "blocking", "pass", "grantedRole is valid.")
    if data.get("authorityLevel") not in AUTHORITY_LEVELS:
        report.add("AUTHORITY_LEVEL", "blocking", "fail", "authorityLevel must be B0, B1, B2, or B3.")
    else:
        report.add("AUTHORITY_LEVEL", "blocking", "pass", "authorityLevel is valid.")
    if data.get("grantedRole") in {"frontier", "worker", "reviewer", "discovery"} and data.get("authorityLevel") == "B3":
        report.add("B3_NON_PRIMARY", "blocking", "fail", "B3 final authority should not be granted to non-final roles by default.")
    elif data.get("grantedRole") == "frontier" and data.get("authorityLevel") == "B2":
        report.add("FRONTIER_B2_DEFAULT", "blocking", "pass", "Frontier is granted B2 lane authority.")


def validate_current_manifest(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "current-manifest":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be current-manifest.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is current-manifest.")
    for field_name in [
        "manifestId",
        "preferredLanguage",
        "workingDirectory",
        "currentSourcePackRef",
        "promptRegistryRef",
        "responseRegistryRef",
        "handoffRegistryRef",
        "sequenceRegistryRef",
        "cardRegistryRef",
    ]:
        require_non_empty_string(data, field_name, report)
    facts_input = data.get("factsInput")
    if isinstance(facts_input, (str, list, dict)) and facts_input:
        report.add("FACTS_INPUT", "blocking", "pass", "factsInput is present.")
    else:
        report.add("FACTS_INPUT", "blocking", "fail", "factsInput must name the current fact input path or uploaded materials.")
    if isinstance(data.get("invalidSourceRefs"), list):
        report.add("INVALID_SOURCE_REFS", "blocking", "pass", "invalidSourceRefs is an array.")
    else:
        report.add("INVALID_SOURCE_REFS", "blocking", "fail", "invalidSourceRefs must be an array.")
    if isinstance(data.get("deprecatedSourceRefs"), list):
        report.add("DEPRECATED_SOURCE_REFS", "blocking", "pass", "deprecatedSourceRefs is an array.")
    else:
        report.add("DEPRECATED_SOURCE_REFS", "blocking", "fail", "deprecatedSourceRefs must be an array.")
    validate_manifest_refs_exist(data, report)


def resolve_ref(base: Path, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return base / path


def validate_manifest_refs_exist(data: dict[str, Any], report: Report) -> None:
    artifact_base = Path(report.artifact).parent
    for field_name in [
        "currentSourcePackRef",
        "promptRegistryRef",
        "responseRegistryRef",
        "handoffRegistryRef",
        "sequenceRegistryRef",
        "cardRegistryRef",
    ]:
        value = data.get(field_name)
        if not isinstance(value, str) or not value.strip():
            continue
        target = resolve_ref(artifact_base, value)
        if target.exists():
            report.add(f"{field_name.upper()}_EXISTS", "blocking", "pass", f"{field_name} exists.", str(target))
        else:
            report.add(f"{field_name.upper()}_EXISTS", "blocking", "fail", f"{field_name} does not exist.", str(target))
    source_ref = data.get("currentSourcePackRef")
    if isinstance(source_ref, str) and source_ref.strip():
        source_path = resolve_ref(artifact_base, source_ref)
        source_report = Report(str(source_path), "source-pack")
        source_pack = load_json(source_path, source_report) if source_path.exists() else None
        if isinstance(source_pack, dict):
            current_ids = {
                str(source.get("sourceId"))
                for source in source_pack.get("currentSources", [])
                if isinstance(source, dict) and source.get("sourceId")
            }
            deprecated_refs = {str(ref) for ref in data.get("deprecatedSourceRefs", [])}
            invalid_refs = {str(ref) for ref in data.get("invalidSourceRefs", [])}
            conflicts = sorted(current_ids.intersection(deprecated_refs.union(invalid_refs)))
            if conflicts:
                report.add("CURRENT_SOURCE_STATUS_CONFLICT", "blocking", "fail", "Source ids cannot be both current and deprecated or invalid: " + ", ".join(conflicts))
            else:
                report.add("CURRENT_SOURCE_STATUS_CONFLICT", "blocking", "pass", "No current/deprecated or current/invalid source id conflict.")


def validate_sequence_registry(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "sequence-registry":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be sequence-registry.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is sequence-registry.")
    for field_name in ["registryId", "currentPromptId", "latestResponseId"]:
        require_non_empty_string(data, field_name, report)
    for field_name in ["prompts", "responses", "handoffs", "cards"]:
        value = data.get(field_name)
        if not isinstance(value, list):
            report.add(f"{field_name.upper()}_ARRAY", "blocking", "fail", f"{field_name} must be an array.")
        else:
            report.add(f"{field_name.upper()}_ARRAY", "blocking", "pass", f"{field_name} is an array.")
    prompt_ids = {
        str(item.get("promptId"))
        for item in data.get("prompts", [])
        if isinstance(item, dict) and item.get("promptId")
    }
    if data.get("currentPromptId") in prompt_ids:
        report.add("CURRENT_PROMPT_REGISTERED", "blocking", "pass", "currentPromptId is registered.")
    else:
        report.add("CURRENT_PROMPT_REGISTERED", "blocking", "fail", "currentPromptId must appear in prompts[].promptId.")
    response_ids = {
        str(item.get("responseId"))
        for item in data.get("responses", [])
        if isinstance(item, dict) and item.get("responseId")
    }
    if data.get("latestResponseId") in response_ids:
        report.add("LATEST_RESPONSE_REGISTERED", "blocking", "pass", "latestResponseId is registered.")
    else:
        report.add("LATEST_RESPONSE_REGISTERED", "blocking", "fail", "latestResponseId must appear in responses[].responseId.")
    prompt_status = {
        str(item.get("promptId")): str(item.get("status", ""))
        for item in data.get("prompts", [])
        if isinstance(item, dict) and item.get("promptId")
    }
    if prompt_status.get(str(data.get("currentPromptId"))) in {"deprecated", "invalid", "rejected"}:
        report.add("CURRENT_PROMPT_STATUS", "blocking", "fail", "currentPromptId must not point to deprecated, invalid, or rejected prompt status.")
    else:
        report.add("CURRENT_PROMPT_STATUS", "blocking", "pass", "currentPromptId status is usable.")
    response_prompt_by_id = {
        str(item.get("responseId")): str(item.get("promptId"))
        for item in data.get("responses", [])
        if isinstance(item, dict) and item.get("responseId")
    }
    if response_prompt_by_id.get(str(data.get("latestResponseId"))) == str(data.get("currentPromptId")):
        report.add("LATEST_RESPONSE_PROMPT_MATCH", "blocking", "pass", "latestResponseId belongs to currentPromptId.")
    else:
        report.add("LATEST_RESPONSE_PROMPT_MATCH", "blocking", "fail", "latestResponseId must belong to currentPromptId.")
    known_card_ids = {
        str(item.get("cardId"))
        for item in data.get("cards", [])
        if isinstance(item, dict) and item.get("cardId")
    }
    handoff_card_refs = [
        str(item.get("cardId"))
        for item in data.get("handoffs", [])
        if isinstance(item, dict) and item.get("cardId")
    ]
    unknown_handoff_cards = sorted({card_id for card_id in handoff_card_refs if card_id and card_id not in known_card_ids})
    if unknown_handoff_cards:
        report.add("HANDOFF_CARD_REFS", "blocking", "fail", "Handoff entries reference unknown cards: " + ", ".join(unknown_handoff_cards))
    else:
        report.add("HANDOFF_CARD_REFS", "blocking", "pass", "Handoff card references are known or omitted.")


def validate_handoff(data: dict[str, Any], report: Report, task_card: dict[str, Any] | None) -> None:
    if data.get("artifactType") != "handoff":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be handoff.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is handoff.")
    if data.get("authority") not in AUTHORITY_LEVELS:
        report.add("HANDOFF_AUTHORITY", "blocking", "fail", "handoff authority must be B0, B1, B2, or B3.")
    else:
        report.add("HANDOFF_AUTHORITY", "blocking", "pass", "handoff authority is valid.")
    if data.get("dataRisk") not in DATA_RISK_LEVELS:
        report.add("DATA_RISK", "blocking", "fail", "dataRisk must be none, low, medium, high, or sensitive.")
    else:
        report.add("DATA_RISK", "blocking", "pass", "dataRisk is valid.")
    if data.get("effectsPreset") not in EFFECTS_PRESETS:
        report.add("EFFECTS_PRESET", "blocking", "fail", "effectsPreset is not a known OpenACP effects preset.")
    else:
        report.add("EFFECTS_PRESET", "blocking", "pass", "effectsPreset is valid.")
    for field_name in ["responseId", "worktree", "baseCommit", "commit"]:
        require_non_empty_string(data, field_name, report)
    require_non_empty_array(data, "changedFiles", report)
    state = str(data.get("stateClaim", ""))
    if state not in NON_FINAL_HANDOFF_STATES:
        report.add("HANDOFF_STATE_CLAIM", "blocking", "fail", "handoff stateClaim must be proposed, implemented, verified, or reviewed.")
    else:
        report.add("HANDOFF_STATE_CLAIM", "blocking", "pass", "handoff stateClaim is non-final.")
    claims_text = " ".join(str(x).lower() for x in data.get("claims", []))
    leaked_claims = sorted(term for term in FINAL_STATE_CLAIMS if re.search(rf"\b{re.escape(term)}\b", claims_text))
    if leaked_claims:
        report.add("FINAL_STATE_OVERCLAIM", "blocking", "fail", f"Handoff claims final state; final authority consume must be a separate artifact: {', '.join(leaked_claims)}")
    else:
        report.add("FINAL_STATE_OVERCLAIM", "blocking", "pass", "No unsupported final-state claim found.")
    if data.get("finalAuthorityRef"):
        report.add("HANDOFF_FINAL_AUTHORITY_REF", "warning", "fail", "handoff contains finalAuthorityRef; use a status or consume artifact for final-authority decisions.")
    verify = data.get("verificationEvidence", [])
    if not isinstance(verify, list) or not verify:
        report.add("VERIFICATION_EVIDENCE", "blocking", "fail", "verificationEvidence must be non-empty.")
    else:
        report.add("VERIFICATION_EVIDENCE", "blocking", "pass", "verificationEvidence is present.")
        non_pass: list[str] = []
        for idx, item in enumerate(verify):
            loc = f"verificationEvidence[{idx}]"
            if not isinstance(item, dict):
                report.add("VERIFICATION_ITEM", "blocking", "fail", "verification item must be an object.", loc)
                continue
            for field_name in ["check", "method", "result"]:
                if field_name not in item:
                    report.add("VERIFICATION_ITEM_REQUIRED_FIELDS", "blocking", "fail", f"verification item missing {field_name}.", loc)
                elif field_name in {"check", "method"} and not str(item.get(field_name, "")).strip():
                    report.add("VERIFICATION_ITEM_REQUIRED_FIELDS", "blocking", "fail", f"verification item has empty {field_name}.", loc)
            result = item.get("result")
            if result not in VERIFY_RESULTS:
                report.add("VERIFICATION_RESULT", "blocking", "fail", "verification result must be pass, fail, or skipped.", loc)
            if result == "skipped" and not item.get("skipReason"):
                report.add("SKIPPED_VERIFICATION_REASON", "blocking", "fail", "Skipped verification requires skipReason.", loc)
            if result != "pass":
                non_pass.append(loc)
        if state == "verified" and non_pass:
            report.add("VERIFIED_WITH_NON_PASS_CHECK", "blocking", "fail", f"stateClaim verified cannot include non-pass checks: {', '.join(non_pass)}")
    check_handoff_scope(data, task_card, report)


def check_handoff_scope(data: dict[str, Any], task_card: dict[str, Any] | None, report: Report) -> None:
    if not task_card:
        report.add("TASK_CARD_CROSSCHECK", "warning", "fail", "No --task-card provided; changedArtifacts were not checked against allowedScope.")
        return
    if data.get("taskId") != task_card.get("taskId"):
        report.add("HANDOFF_TASK_ID_MATCH", "blocking", "fail", "handoff.taskId does not match taskCard.taskId.")
    else:
        report.add("HANDOFF_TASK_ID_MATCH", "blocking", "pass", "handoff.taskId matches taskCard.taskId.")
    validate_handoff_actor_authority(data, task_card, report)
    allowed = task_card.get("allowedScope", {}).get("filesOrArtifacts", [])
    if not isinstance(allowed, list) or not allowed:
        report.add("TASK_CARD_ALLOWED_SCOPE", "blocking", "fail", "Task card allowedScope.filesOrArtifacts is missing.")
        return
    bad: list[str] = []
    forbidden_patterns = task_card.get("forbiddenScope", {}).get("filesOrArtifacts", [])
    forbidden_hits: list[str] = []
    changed_artifact_paths = [
        str(artifact.get("path", ""))
        for artifact in data.get("changedArtifacts", [])
        if isinstance(artifact, dict) and artifact.get("path")
    ]
    changed_files = [str(path) for path in data.get("changedFiles", []) if str(path).strip()]
    for path in sorted(set(changed_artifact_paths + changed_files)):
        if not any(fnmatch.fnmatch(path, str(pattern)) or path == str(pattern) for pattern in allowed):
            bad.append(path)
        if any(fnmatch.fnmatch(path, str(pattern)) or path == str(pattern) for pattern in forbidden_patterns):
            forbidden_hits.append(path)
    if bad:
        report.add("CHANGED_ARTIFACTS_SCOPE", "blocking", "fail", f"Changed artifacts exceed allowed scope: {', '.join(bad)}")
    else:
        report.add("CHANGED_ARTIFACTS_SCOPE", "blocking", "pass", "Changed artifacts fit task card allowed scope.")
    if forbidden_hits:
        report.add("FORBIDDEN_ARTIFACTS_TOUCHED", "blocking", "fail", f"Changed artifacts match forbidden scope: {', '.join(forbidden_hits)}")
    else:
        report.add("FORBIDDEN_ARTIFACTS_TOUCHED", "blocking", "pass", "No changed artifacts match forbidden file scope.")
    artifact_set = set(changed_artifact_paths)
    file_set = set(changed_files)
    if artifact_set != file_set:
        missing_from_files = sorted(artifact_set - file_set)
        missing_from_artifacts = sorted(file_set - artifact_set)
        parts = []
        if missing_from_files:
            parts.append("missing from changedFiles: " + ", ".join(missing_from_files))
        if missing_from_artifacts:
            parts.append("missing from changedArtifacts: " + ", ".join(missing_from_artifacts))
        report.add("CHANGED_FILES_ARTIFACTS_MATCH", "blocking", "fail", "; ".join(parts))
    else:
        report.add("CHANGED_FILES_ARTIFACTS_MATCH", "blocking", "pass", "changedFiles and changedArtifacts paths match.")
    check_forbidden_handoff_claims(data, task_card, report)


def validate_handoff_actor_authority(data: dict[str, Any], task_card: dict[str, Any], report: Report) -> None:
    actor = data.get("actorRole")
    task_level = task_card.get("authorityRequired")
    handoff_level = data.get("authority")
    allowed_by_actor = {
        "discovery": {"B0"},
        "reviewer": {"B0"},
        "frontier": {"B0", "B1", "B2"},
        "worker": {"B2"},
    }
    allowed_levels = allowed_by_actor.get(str(actor), set())
    if handoff_level not in allowed_levels:
        report.add("HANDOFF_ACTOR_AUTHORITY", "blocking", "fail", f"actorRole {actor} is not compatible with handoff authority {handoff_level}.")
    else:
        report.add("HANDOFF_ACTOR_AUTHORITY", "blocking", "pass", "actorRole is compatible with handoff authority.")
    if task_level != handoff_level:
        report.add("HANDOFF_TASK_AUTHORITY_MATCH", "blocking", "fail", f"handoff authority {handoff_level} must match task authorityRequired {task_level}.")
    else:
        report.add("HANDOFF_TASK_AUTHORITY_MATCH", "blocking", "pass", "handoff authority matches task authorityRequired.")


def check_forbidden_handoff_claims(data: dict[str, Any], task_card: dict[str, Any], report: Report) -> None:
    claims_text = " ".join(str(x).lower() for x in data.get("claims", []))
    forbidden_claims = [str(x).lower() for x in task_card.get("forbiddenScope", {}).get("claims", [])]
    forbidden_effects = [str(x).lower() for x in task_card.get("forbiddenScope", {}).get("effects", [])]
    hits = []
    for phrase in forbidden_claims + forbidden_effects:
        if phrase and phrase in claims_text:
            hits.append(phrase)
    effects = data.get("effects", [])
    if isinstance(effects, list):
        effect_text = " ".join(str(x).lower() for x in effects)
        for phrase in forbidden_effects:
            if phrase and phrase in effect_text:
                hits.append(phrase)
    if hits:
        report.add("FORBIDDEN_CLAIMS_OR_EFFECTS", "blocking", "fail", f"Handoff claims or effects include forbidden scope: {', '.join(sorted(set(hits)))}")
    else:
        report.add("FORBIDDEN_CLAIMS_OR_EFFECTS", "blocking", "pass", "Handoff claims and effects do not include forbidden scope markers.")


def validate_review_report(data: dict[str, Any], report: Report) -> None:
    if data.get("recommendation") not in REVIEW_RECOMMENDATIONS:
        report.add("REVIEW_RECOMMENDATION", "blocking", "fail", "recommendation must be approve, amend, split-follow-up, or reject.")
    else:
        report.add("REVIEW_RECOMMENDATION", "blocking", "pass", "recommendation is valid.")
    for field_name in ["reviewedArtifacts"]:
        require_non_empty_array(data, field_name, report)


def validate_status_report(data: dict[str, Any], report: Report) -> None:
    for field_name in ["basisRefs", "nextActions", "authorityLimits"]:
        require_non_empty_array(data, field_name, report)
    text = json.dumps(data, ensure_ascii=False).lower()
    if "provisional" in text and re.search(r"\baccepted\b|\bmerged\b|\breleased\b", text):
        report.add("STATUS_PROVISIONAL_OVERCLAIM", "warning", "fail", "Status report mentions provisional evidence and final outcome; verify final-authority evidence is explicit.")
    else:
        report.add("STATUS_PROVISIONAL_OVERCLAIM", "warning", "pass", "No obvious provisional/final overclaim pattern found.")


def validate_assumption_ledger(data: dict[str, Any], report: Report) -> None:
    assumptions = data.get("assumptions")
    if not isinstance(assumptions, list) or not assumptions:
        report.add("ASSUMPTIONS_NON_EMPTY", "blocking", "fail", "assumptions must be non-empty.")
        return
    required = [
        "assumptionId",
        "statement",
        "evidence",
        "riskIfWrong",
        "canProceed",
        "needsHumanConfirmation",
        "expiresWhen",
    ]
    for idx, item in enumerate(assumptions):
        loc = f"assumptions[{idx}]"
        if not isinstance(item, dict):
            report.add("ASSUMPTION_OBJECT", "blocking", "fail", "assumption must be an object.", loc)
            continue
        missing = [field_name for field_name in required if field_name not in item]
        if missing:
            report.add("ASSUMPTION_REQUIRED_FIELDS", "blocking", "fail", f"Missing assumption fields: {', '.join(missing)}", loc)
        if item.get("canProceed") not in {True, False} or item.get("needsHumanConfirmation") not in {True, False}:
            report.add("ASSUMPTION_BOOLEAN_FIELDS", "blocking", "fail", "canProceed and needsHumanConfirmation must be boolean.", loc)
    report.add("ASSUMPTIONS_CHECKED", "blocking", "pass", "Assumption entries checked.")


def scan_internal_report_markers(text: str, report: Report, path: Path, root: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError:
        relative = path
    if not relative.parts or relative.parts[0] != "reports":
        return
    hits = [marker for marker in INTERNAL_FORMAL_REPORT_MARKERS if marker.lower() in text.lower()]
    if hits:
        report.add(
            "INTERNAL_FORMAL_REPORT_IN_PUBLIC_PATH",
            "blocking",
            "fail",
            "Internal formal report markers found under reports/: " + ", ".join(hits),
            str(path),
        )
    else:
        report.add("INTERNAL_FORMAL_REPORT_IN_PUBLIC_PATH", "blocking", "pass", "No internal formal report markers found.", str(path))


def load_cross_json(path_text: str | None, label: str, report: Report) -> dict[str, Any] | None:
    if not path_text:
        return None
    path = Path(path_text)
    data = load_json(path, report)
    if isinstance(data, dict):
        return data
    report.add(f"{label.upper()}_LOAD", "blocking", "fail", f"{label} could not be loaded as JSON.", str(path))
    return None


def validate_json_artifact(args: argparse.Namespace) -> Report:
    artifact_path = Path(args.artifact)
    report = Report(str(artifact_path), args.ruleset)
    if not artifact_path.exists():
        report.add("ARTIFACT_EXISTS", "blocking", "fail", "Artifact path does not exist.", str(artifact_path))
        return report
    report.add("ARTIFACT_EXISTS", "blocking", "pass", "Artifact path exists.", str(artifact_path))
    text, read_error = read_utf8(artifact_path)
    if read_error:
        report.add("UTF8_READ", "blocking", "fail", read_error, str(artifact_path))
        return report
    assert text is not None
    scan_secret_markers(text, report, str(artifact_path))
    data = load_json(artifact_path, report)
    if not isinstance(data, dict):
        return report
    if not require_fields(data, REQUIRED_FIELDS[args.ruleset], report):
        return report
    expected_type = ARTIFACT_TYPE_BY_RULESET.get(args.ruleset)
    if expected_type and data.get("artifactType") != expected_type:
        report.add("ARTIFACT_TYPE_MATCH", "blocking", "fail", f"artifactType must be {expected_type}.")
    elif expected_type:
        report.add("ARTIFACT_TYPE_MATCH", "blocking", "pass", "artifactType matches ruleset.")

    source_pack = load_cross_json(args.source_pack, "source-pack", report)
    task_card = load_cross_json(args.task_card, "task-card", report)

    if args.ruleset == "source-pack":
        validate_source_pack(data, report)
    elif args.ruleset == "scope-boundary":
        validate_scope_boundary(data, report)
    elif args.ruleset == "task-card":
        validate_task_card(data, report, source_pack)
    elif args.ruleset == "authority-charter":
        validate_authority_charter(data, report)
    elif args.ruleset == "handoff":
        validate_handoff(data, report, task_card)
    elif args.ruleset == "review-report":
        validate_review_report(data, report)
    elif args.ruleset == "status-report":
        validate_status_report(data, report)
    elif args.ruleset == "assumption-ledger":
        validate_assumption_ledger(data, report)
    elif args.ruleset == "current-manifest":
        validate_current_manifest(data, report)
    elif args.ruleset == "sequence-registry":
        validate_sequence_registry(data, report)
    return report


def validate_text_artifact(args: argparse.Namespace) -> Report:
    artifact_path = Path(args.artifact)
    report = Report(str(artifact_path), args.ruleset)
    if not artifact_path.exists():
        report.add("ARTIFACT_EXISTS", "blocking", "fail", "Artifact path does not exist.", str(artifact_path))
        return report
    report.add("ARTIFACT_EXISTS", "blocking", "pass", "Artifact path exists.", str(artifact_path))
    text, read_error = read_utf8(artifact_path)
    if read_error:
        report.add("UTF8_READ", "blocking", "fail", read_error, str(artifact_path))
        return report
    assert text is not None
    report.add("UTF8_READ", "blocking", "pass", "Artifact read as UTF-8.")
    scan_mojibake(text, report, str(artifact_path))
    scan_secret_markers(text, report, str(artifact_path))
    if args.ruleset == "prompt-record":
        validate_prompt_record_text(text, report)
    elif args.ruleset == "launcher":
        validate_launcher_text(text, report)
    elif args.ruleset == "formal-report":
        validate_formal_report_text(text, report)
    elif args.ruleset == "frontier-contract":
        validate_frontier_contract_text(text, report)
    return report


def scan_public_package(root: Path) -> Report:
    report = Report(str(root), "public-package")
    if not root.exists():
        report.add("PACKAGE_ROOT", "blocking", "fail", "Package root does not exist.", str(root))
        return report
    report.add("PACKAGE_ROOT", "blocking", "pass", "Package root exists.", str(root))
    suffixes = {".md", ".json", ".py", ".toml", ".yaml", ".yml", ".txt"}
    extensionless_names = {"LICENSE", "NOTICE", "COPYING"}
    scanned = 0
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in PUBLIC_SCAN_SKIP_DIRS or part.endswith(".egg-info") for part in path.parts):
            continue
        if path.suffix.lower() not in suffixes and path.name not in extensionless_names:
            continue
        text, error = read_utf8(path)
        if error:
            report.add("PUBLIC_UTF8_READ", "blocking", "fail", error, str(path))
            continue
        assert text is not None
        scanned += 1
        scan_mojibake(text, report, str(path))
        scan_private_leaks(text, report, str(path))
        scan_secret_markers(text, report, str(path))
        scan_internal_report_markers(text, report, path, root)
    report.add("PUBLIC_FILES_SCANNED", "blocking", "pass", f"Scanned {scanned} public text artifacts.")
    return report


def emit_report(report: Report, strict: bool, as_json: bool) -> None:
    data = report.to_dict(strict)
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    print(f"OpenACP validator {VERSION}")
    print(f"status: {data['status']}")
    print(f"artifact: {report.artifact}")
    print(f"ruleset: {report.ruleset}")
    for check in report.checks:
        loc = f" [{check.location}]" if check.location else ""
        print(f"- {check.status.upper()} {check.severity} {check.check_id}{loc}: {check.message}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate OpenACP artifacts.")
    parser.add_argument("--version", action="version", version=f"OpenACP validator {VERSION}")
    parser.add_argument("--artifact", help="Artifact path to validate.")
    parser.add_argument("--ruleset", choices=sorted(RULESETS), required=True)
    parser.add_argument("--source-pack", help="Optional source pack JSON for task-card cross-checks.")
    parser.add_argument("--task-card", help="Optional task card JSON for handoff scope cross-checks.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args(argv or sys.argv[1:])
    if args.ruleset == "public-package":
        if not args.artifact:
            print("--artifact is required for public-package scan", file=sys.stderr)
            return 2
        report = scan_public_package(Path(args.artifact))
    elif args.ruleset in TEXT_RULESETS:
        if not args.artifact:
            print("--artifact is required", file=sys.stderr)
            return 2
        report = validate_text_artifact(args)
    else:
        if not args.artifact:
            print("--artifact is required", file=sys.stderr)
            return 2
        report = validate_json_artifact(args)
    emit_report(report, args.strict, args.json)
    return 0 if report.status(args.strict) == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
