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
    "card-registry",
    "consume-result",
    "current-manifest",
    "formal-report",
    "frontier-contract",
    "handoff",
    "launcher",
    "launcher-output",
    "machine-summary",
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
    "launcher-output",
    "card-registry",
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
        "dataRiskLimit",
        "resourceUseLimit",
        "allowedInputs",
        "allowedOutputs",
        "forbiddenSideEffects",
        "stopConditions",
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
        "activeLanes",
        "supersededPromptIds",
        "cancelledPromptIds",
        "latestConsumeRefs",
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
        "consumes",
        "activeLanes",
    ],
    "consume-result": [
        "schemaVersion",
        "artifactType",
        "consumeId",
        "responseId",
        "consumerRole",
        "authorityScope",
        "targetHandoffIds",
        "targetReviewIds",
        "decision",
        "basisRefs",
        "evidenceStatus",
        "claimsAccepted",
        "claimsRejected",
        "remainingRisks",
        "authorityLimits",
        "nextActions",
    ],
    "machine-summary": [
        "schemaVersion",
        "artifactType",
        "summaryId",
        "role",
        "promptId",
        "responseId",
        "authority",
        "effectsPreset",
        "basisRefs",
        "locators",
        "status",
        "claims",
        "nextActions",
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
    "consume-result": "consume-result",
    "machine-summary": "machine-summary",
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
CONSUME_DECISIONS = {"accepted", "amend", "split-follow-up", "rejected", "blocked"}
AUTHORITY_SCOPES = {"provisional", "final"}
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
JSON_FENCE_RE = re.compile(r"```(?:json|JSON)?\s*(\{.*?\})\s*```", re.DOTALL)
PROMPT_FENCE_RE = re.compile(r"```prompt\s*(.*?)```", re.DOTALL | re.IGNORECASE)
ZH_ITEM = "\u9879"
ZH_FIELD = "\u5b57\u6bb5"
ZH_PROGRESS = "\u603b\u4f53\u8fdb\u5ea6"
ZH_EVIDENCE = "\u8bc1\u636e"
ZH_BASIS = "\u4f9d\u636e"
ZH_LEFT_SIDEBAR = "\u5de6\u4fa7"
ZH_NEW_THREAD = "\u65b0\u5efa"
ZH_PASTE = "\u7c98\u8d34"

FORMAL_ROW_SETS = [
    {"Changed", "Progress", "Gate", "Area", "Goal", "Gaps", "Next"},
    {
        "\u505a\u4e86\u4ec0\u4e48",
        "\u603b\u4f53\u8fdb\u5ea6",
        "Frontier",
        "\u76ee\u6807",
        "\u7f3a\u53e3",
        "\u4e0b\u4e00\u6b65",
    },
    {
        "\u505a\u4e86\u4ec0\u4e48",
        "\u603b\u4f53\u8fdb\u5ea6",
        "Lane",
        "\u76ee\u6807",
        "\u7f3a\u53e3",
        "\u4e0b\u4e00\u6b65",
    },
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
        if not left or left.lower() == "item" or left in {ZH_ITEM, ZH_FIELD}:
            continue
        if set(left) <= {"-"}:
            continue
        rows.append((left, right))
    return rows


def extract_json_fence_objects(text: str) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    for match in JSON_FENCE_RE.finditer(text):
        try:
            parsed = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            objects.append(parsed)
    return objects


def validate_expected_prompt_id(prompt_ids: list[str], expected_prompt_id: str | None, report: Report, check_id: str) -> None:
    if not expected_prompt_id:
        return
    unique_ids = set(prompt_ids)
    if unique_ids == {expected_prompt_id}:
        report.add(check_id, "blocking", "pass", f"Prompt ID matches expected value {expected_prompt_id}.")
    else:
        report.add(check_id, "blocking", "fail", f"Prompt ID must match expected value {expected_prompt_id}; found {sorted(unique_ids)}.")


def validate_prompt_record_text(text: str, report: Report, expected_prompt_id: str | None = None) -> None:
    prompt_ids = PROMPT_ID_RE.findall(text)
    if not prompt_ids:
        report.add("PROMPT_ID", "blocking", "fail", "Prompt record must include a stable Prompt ID line.")
    elif len(set(prompt_ids)) != 1:
        report.add("PROMPT_ID", "blocking", "fail", "Prompt record must contain exactly one stable Prompt ID.")
    else:
        report.add("PROMPT_ID", "blocking", "pass", f"Prompt ID found: {prompt_ids[0]}.")
    validate_expected_prompt_id(prompt_ids, expected_prompt_id, report, "PROMPT_ID_EXPECTED")
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
    if is_primary_prompt_record(text):
        validate_primary_prompt_contract_text(text, report)


def is_primary_prompt_record(text: str) -> bool:
    return bool(
        re.search(r"(?im)^\s*(Role|角色)\s*:\s*Primary\b", text)
        or re.search(r"(?i)\bPrimary\s+Orchestrator\b", text)
    )


def validate_primary_prompt_contract_text(text: str, report: Report) -> None:
    lowered = text.lower()
    if re.search(r"10\s*[-\u2010-\u2015]\s*20|10\s+to\s+20", text):
        report.add("PRIMARY_CARD_COUNT_RULE", "blocking", "pass", "Primary prompt requires 10-20 CARDs for normal or medium/high complexity.")
    else:
        report.add(
            "PRIMARY_CARD_COUNT_RULE",
            "blocking",
            "fail",
            "Primary prompt must require 10-20 project-level CARDs for normal or medium/high complexity, with a small-project exception.",
        )
    domain_terms = [
        "product workflow",
        "backend",
        "data",
        "frontend",
        "ui",
        "electron",
        "integrations",
        "security",
        "testing",
        "ci",
        "release",
    ]
    missing_domain_terms = [term for term in domain_terms if term not in lowered]
    if len(missing_domain_terms) <= 2:
        report.add("PRIMARY_DOMAIN_SCAN", "blocking", "pass", "Primary prompt requires broad product-domain scan before CARD finalization.")
    else:
        report.add(
            "PRIMARY_DOMAIN_SCAN",
            "blocking",
            "fail",
            "Primary prompt must scan product domains before CARD finalization; missing examples: " + ", ".join(missing_domain_terms[:5]),
        )
    if re.search(r"(?i)at\s+least\s+two\s+Frontier|2\s*[-\u2010-\u2015]\s*5\s+Frontier|two\s+to\s+five\s+Frontier", text):
        report.add("PRIMARY_FRONTIER_MIN_RULE", "blocking", "pass", "Primary prompt defaults to multiple Frontier lanes when safe.")
    else:
        report.add(
            "PRIMARY_FRONTIER_MIN_RULE",
            "blocking",
            "fail",
            "Primary prompt must default to at least two Frontier lanes when two safe independent CARD clusters exist.",
        )
    if re.search(r"(?is)one\s+Frontier.*(?:small|single|user)", text) or re.search(r"(?i)single[- ]safe[- ]lane|single safe lane", text):
        report.add("PRIMARY_SINGLE_FRONTIER_EXCEPTION", "blocking", "pass", "Primary prompt records when one Frontier is allowed.")
    else:
        report.add(
            "PRIMARY_SINGLE_FRONTIER_EXCEPTION",
            "blocking",
            "fail",
            "Primary prompt must allow one Frontier only for a small project, single safe lane, or explicit user request, with a recorded reason.",
        )


def validate_card_registry_text(text: str, report: Report) -> None:
    if re.search(r"(?im)^\s*schemaVersion\s*:\s*openacp-card-registry\.v1\s*$", text):
        report.add("CARD_REGISTRY_SCHEMA", "blocking", "pass", "CARD registry schemaVersion is present.")
    else:
        report.add("CARD_REGISTRY_SCHEMA", "blocking", "fail", "CARD registry must include schemaVersion: openacp-card-registry.v1.")
    if re.search(r"(?im)^\s*artifactType\s*:\s*card-registry\s*$", text):
        report.add("CARD_REGISTRY_TYPE", "blocking", "pass", "CARD registry artifactType is present.")
    else:
        report.add("CARD_REGISTRY_TYPE", "blocking", "fail", "CARD registry must include artifactType: card-registry.")
    required_sections = ["Domain Coverage", "CARD List", "Lane Grouping"]
    missing_sections = [section for section in required_sections if section.lower() not in text.lower()]
    if missing_sections:
        report.add("CARD_REGISTRY_SECTIONS", "blocking", "fail", "CARD registry missing sections: " + ", ".join(missing_sections))
    else:
        report.add("CARD_REGISTRY_SECTIONS", "blocking", "pass", "CARD registry has required sections.")
    card_ids = sorted(set(re.findall(r"\bCARD-\d{3,}\b", text)))
    has_small_exception = bool(
        re.search(r"(?im)^\s*-\s*(small-project-reason|single-lane-reason|explicit-user-request)\s*:\s*\S", text)
        or re.search(r"(?i)\b(small project|single safe lane|explicit user request)\b.{0,120}\bCARD", text)
    )
    if len(card_ids) >= 10:
        report.add("CARD_REGISTRY_CARD_COUNT", "blocking", "pass", f"CARD registry includes {len(card_ids)} CARD ids.")
    elif has_small_exception:
        report.add("CARD_REGISTRY_CARD_COUNT", "blocking", "pass", "CARD registry uses fewer than 10 CARDs with an explicit small/single-lane/user-request reason.")
    else:
        report.add(
            "CARD_REGISTRY_CARD_COUNT",
            "blocking",
            "fail",
            f"CARD registry has only {len(card_ids)} CARD ids; normal projects need 10-20 or an explicit small/single-lane/user-request reason.",
        )
    lowered = text.lower()
    coverage_terms = ["frontend", "ui", "electron", "backend", "api", "data", "testing", "release"]
    missing_terms = [term for term in coverage_terms if term not in lowered]
    if len(missing_terms) <= 1:
        report.add("CARD_REGISTRY_DOMAIN_SCAN", "blocking", "pass", "CARD registry records broad domain-scan coverage.")
    else:
        report.add(
            "CARD_REGISTRY_DOMAIN_SCAN",
            "blocking",
            "fail",
            "CARD registry must show domain-scan coverage before lane dispatch; missing examples: " + ", ".join(missing_terms[:4]),
        )
    if re.search(r"(?i)task[- ]card", text):
        report.add("CARD_REGISTRY_TASK_CARD_CANDIDATES", "blocking", "pass", "CARD registry links CARDs to task-card candidates.")
    else:
        report.add("CARD_REGISTRY_TASK_CARD_CANDIDATES", "blocking", "fail", "CARD registry must include task-card candidates.")
    if re.search(r"(?i)Frontier|lane candidate|candidate lane", text):
        report.add("CARD_REGISTRY_LANE_GROUPING", "blocking", "pass", "CARD registry supports Frontier lane grouping.")
    else:
        report.add("CARD_REGISTRY_LANE_GROUPING", "blocking", "fail", "CARD registry must support Frontier lane grouping.")


def validate_launcher_text(
    text: str,
    report: Report,
    prompt_record_text: str | None = None,
    expected_prompt_id: str | None = None,
) -> None:
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
    validate_expected_prompt_id(prompt_ids, expected_prompt_id, report, "LAUNCHER_PROMPT_ID_EXPECTED")
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
    if re.search(r"(?i)\b(worker|reviewer|discovery|task-card-only|task card only|validation)\b", text):
        if re.search(r"(?i)fallback launcher|fallback only", text) and re.search(r"(?i)unavailable|unsafe|explicitly requested|separately user-managed", text):
            report.add("CHILD_LAUNCHER_FALLBACK", "blocking", "pass", "Child-role launcher is explicitly marked as fallback.")
        else:
            report.add(
                "CHILD_LAUNCHER_FALLBACK",
                "blocking",
                "fail",
                "Worker, reviewer, discovery, validation, or task-card-only launchers must be fallback launchers with a direct-dispatch failure reason.",
            )
    else:
        report.add("CHILD_LAUNCHER_FALLBACK", "blocking", "pass", "Launcher is not a child worker/reviewer/discovery launcher.")
    if prompt_record_text is None:
        report.add("LAUNCHER_PROMPT_RECORD_MATCH", "warning", "pass", "No prompt record cross-check requested.")
    else:
        record_prompt_ids = PROMPT_ID_RE.findall(prompt_record_text)
        launcher_ids = set(prompt_ids)
        record_ids = set(record_prompt_ids)
        if len(record_ids) == 1 and launcher_ids == record_ids:
            report.add("LAUNCHER_PROMPT_RECORD_MATCH", "blocking", "pass", "Launcher Prompt ID matches prompt record Prompt ID.")
        elif not record_ids:
            report.add("LAUNCHER_PROMPT_RECORD_MATCH", "blocking", "fail", "Prompt record cross-check target has no Prompt ID.")
        elif len(record_ids) != 1:
            report.add("LAUNCHER_PROMPT_RECORD_MATCH", "blocking", "fail", "Prompt record cross-check target must contain exactly one Prompt ID.")
        else:
            report.add(
                "LAUNCHER_PROMPT_RECORD_MATCH",
                "blocking",
                "fail",
                f"Launcher Prompt ID {sorted(launcher_ids)} does not match prompt record Prompt ID {sorted(record_ids)}.",
            )


def validate_launcher_output_text(text: str, report: Report) -> None:
    prompt_blocks = [match.group(1).strip() for match in PROMPT_FENCE_RE.finditer(text)]
    if not prompt_blocks:
        report.add("PROMPT_FENCE", "blocking", "fail", "Launcher output must include at least one fenced ```prompt block with the copyable short launcher.")
    else:
        report.add("PROMPT_FENCE", "blocking", "pass", f"Found {len(prompt_blocks)} fenced prompt launcher block(s).")
    lower_text = text.lower()
    english_has_left_sidebar = bool(re.search(r"(?i)left\s+sidebar", text))
    english_has_new_thread = bool(re.search(r"(?i)(new\s+thread|create\s+(?:a\s+)?(?:new\s+)?thread|open\s+(?:a\s+)?(?:new\s+)?thread|start\s+(?:that\s+)?thread)", text))
    english_has_paste_action = bool(re.search(r"(?i)\b(?:paste|copy)\b.{0,80}\b(?:launcher|prompt|block)\b", text))
    has_human_instruction = (
        (english_has_left_sidebar and english_has_new_thread and english_has_paste_action)
        or (ZH_LEFT_SIDEBAR in text and ZH_NEW_THREAD in text and ZH_PASTE in text)
    )
    if has_human_instruction:
        report.add("HUMAN_THREAD_INSTRUCTION", "blocking", "pass", "Output tells the human where to paste the short launcher.")
    else:
        report.add("HUMAN_THREAD_INSTRUCTION", "blocking", "fail", "Output must tell the human to create a new left-sidebar thread and paste the short launcher there.")
    if "get-content" in lower_text and not prompt_blocks:
        report.add("GET_CONTENT_SUBSTITUTE", "blocking", "fail", "A Get-Content command is not a copyable chat launcher.")
    else:
        report.add("GET_CONTENT_SUBSTITUTE", "blocking", "pass", "No Get-Content-only launcher substitute found.")
    if re.search(r"(?i)\.short\.md", text) and not prompt_blocks:
        report.add("FILE_LINK_ONLY", "blocking", "fail", "Launcher output names short launcher files but does not include copyable prompt blocks.")
    else:
        report.add("FILE_LINK_ONLY", "blocking", "pass", "Output is not file-link-only.")
    for idx, block in enumerate(prompt_blocks):
        loc = f"promptBlock[{idx}]"
        line_count = len([line for line in block.splitlines() if line.strip()])
        if line_count > 40:
            report.add("PROMPT_BLOCK_SHORT", "blocking", "fail", "Prompt block is too long; full prompt records belong on disk.", loc)
        else:
            report.add("PROMPT_BLOCK_SHORT", "blocking", "pass", "Prompt block is short.", loc)
        if PROMPT_RECORD_RE.search(block):
            report.add("PROMPT_BLOCK_RECORD_PATH", "blocking", "pass", "Prompt block names a prompt record path.", loc)
        else:
            report.add("PROMPT_BLOCK_RECORD_PATH", "blocking", "fail", "Prompt block must name the on-disk prompt record path.", loc)
        if PROMPT_ID_RE.search(block):
            report.add("PROMPT_BLOCK_ID", "blocking", "pass", "Prompt block names a Prompt ID.", loc)
        else:
            report.add("PROMPT_BLOCK_ID", "blocking", "fail", "Prompt block must name a Prompt ID.", loc)
        if re.search(r"(?i)preferred\s*language|preferredLanguage", block):
            report.add("PROMPT_BLOCK_LANGUAGE", "blocking", "pass", "Prompt block carries preferred language.", loc)
        else:
            report.add("PROMPT_BLOCK_LANGUAGE", "blocking", "fail", "Prompt block must carry preferred language.", loc)
        if re.search(r"UTF-?8", block, re.IGNORECASE):
            report.add("PROMPT_BLOCK_UTF8", "blocking", "pass", "Prompt block requires UTF-8 reading.", loc)
        else:
            report.add("PROMPT_BLOCK_UTF8", "blocking", "fail", "Prompt block must require UTF-8 reading.", loc)
        block_lower = block.lower()
        if "stop" in block_lower and ("missing" in block_lower or "corrupt" in block_lower or "cannot be read" in block_lower):
            report.add("PROMPT_BLOCK_STOP_RULE", "blocking", "pass", "Prompt block has a read-failure stop rule.", loc)
        else:
            report.add("PROMPT_BLOCK_STOP_RULE", "blocking", "fail", "Prompt block must stop on read failure, missing Prompt ID, or corruption.", loc)


def _non_code_lines(text: str) -> list[str]:
    without_fences = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return [line.strip() for line in without_fences.splitlines() if line.strip()]


def _has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def _long_english_dominant_lines(text: str) -> list[str]:
    offenders: list[str] = []
    for line in _non_code_lines(text):
        if line.startswith("|") or re.match(r"^[-*]\s*`?[\w.-]+`?\s*:", line):
            continue
        english_words = re.findall(r"\b[A-Za-z][A-Za-z0-9_-]*\b", line)
        cjk_chars = re.findall(r"[\u4e00-\u9fff]", line)
        if len(english_words) >= 10 and len(english_words) > len(cjk_chars):
            offenders.append(line[:120])
    return offenders


def validate_formal_report_text(text: str, report: Report) -> None:
    response_ids = RESPONSE_ID_RE.findall(text)
    if not response_ids:
        report.add("RESPONSE_ID", "blocking", "fail", "Formal report must include Response ID.")
    else:
        report.add("RESPONSE_ID", "blocking", "pass", "Formal report includes Response ID.")
    if re.search(r"(?im)^\s*Response log path\s*:", text):
        report.add("RESPONSE_LOG_PATH", "blocking", "pass", "Formal report names a response log path.")
    else:
        report.add("RESPONSE_LOG_PATH", "blocking", "fail", "Formal report must include a Response log path line.")
    rows = extract_table_rows(text)
    labels = {label for label, _ in rows}
    if any(required.issubset(labels) for required in FORMAL_ROW_SETS):
        report.add("FORMAL_ROWS", "blocking", "pass", "Formal report has a known role-aware row set.")
    else:
        report.add("FORMAL_ROWS", "blocking", "fail", "Formal report rows must match a known OpenACP row set.")
    bad_labels = labels.intersection({"What changed", "Lane or area", "Next step", "Validation", "Checkpoint"})
    if bad_labels:
        report.add("LEGACY_ROW_LABELS", "blocking", "fail", "Legacy or overlong row labels found: " + ", ".join(sorted(bad_labels)))
    else:
        report.add("LEGACY_ROW_LABELS", "blocking", "pass", "No legacy long row labels found.")
    progress_cells = [right for label, right in rows if label in {"Progress", ZH_PROGRESS}]
    if progress_cells and any(re.search(r"\d+\s*%", cell) for cell in progress_cells):
        report.add("PROGRESS_PERCENT", "blocking", "pass", "Progress row includes a numeric estimate.")
    else:
        report.add("PROGRESS_PERCENT", "blocking", "fail", "Formal report progress row must include a numeric percentage.")
    if re.search(r"Evidence Details|Basis", text, re.IGNORECASE) or ZH_EVIDENCE in text or ZH_BASIS in text:
        report.add("EVIDENCE_DETAILS", "blocking", "pass", "Formal report includes evidence or basis details outside the table.")
    else:
        report.add("EVIDENCE_DETAILS", "blocking", "fail", "Formal report must include Evidence Details or basis outside the table.")
    if any(_has_cjk(label) for label in labels):
        english_offenders = _long_english_dominant_lines(text)
        if english_offenders:
            report.add(
                "PREFERRED_LANGUAGE_CONTRACT",
                "blocking",
                "fail",
                "Chinese formal reports must not contain long English-dominant prose lines: " + " | ".join(english_offenders[:3]),
            )
        else:
            report.add("PREFERRED_LANGUAGE_CONTRACT", "blocking", "pass", "Chinese formal report is not dominated by long English prose.")


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
    if "create_downstream_prompt" in text:
        report.add("FRONTIER_LEGACY_GAP_DECISION", "blocking", "fail", "Frontier contract must not use create_downstream_prompt as a gap decision; use current-thread dispatch or fallback package decisions.")
    else:
        report.add("FRONTIER_LEGACY_GAP_DECISION", "blocking", "pass", "No legacy create_downstream_prompt decision found.")
    if "worker" in lowered and "reviewer" in lowered and ("subagent" in lowered or "sub-agent" in lowered or "dispatch" in lowered):
        report.add("FRONTIER_DISPATCH", "blocking", "pass", "Frontier contract allows bounded downstream dispatch.")
    else:
        report.add("FRONTIER_DISPATCH", "blocking", "fail", "Frontier contract must allow bounded worker/reviewer/subagent dispatch.")
    if re.search(r"(?i)subagent[- ]first|sub-agent[- ]first", text):
        report.add("FRONTIER_SUBAGENT_FIRST", "blocking", "pass", "Frontier contract requires subagent-first dispatch.")
    else:
        report.add("FRONTIER_SUBAGENT_FIRST", "blocking", "fail", "Frontier contract must require subagent-first dispatch.")
    if "dispatch_current_thread_subagent" in text or re.search(r"(?i)current\s+Frontier\s+thread", text):
        report.add("FRONTIER_CURRENT_THREAD_DISPATCH", "blocking", "pass", "Frontier contract anchors child dispatch in the current Frontier thread.")
    else:
        report.add("FRONTIER_CURRENT_THREAD_DISPATCH", "blocking", "fail", "Frontier contract must require current-thread child subagent dispatch.")
    if (
        re.search(r"(?i)human.*(?:thread launcher|open .*thread|managed child launcher|child thread)", text)
        and re.search(r"(?i)fallback launcher|fallback only", text)
        and re.search(r"(?i)unavailable|unsafe|explicitly requested|separately user-managed", text)
    ):
        report.add("FRONTIER_NO_HUMAN_TRAMPOLINE", "blocking", "pass", "Frontier contract makes human-managed child launchers fallback-only.")
    else:
        report.add(
            "FRONTIER_NO_HUMAN_TRAMPOLINE",
            "blocking",
            "fail",
            "Frontier contract must say human-managed child launchers are fallback-only and explain when fallback is allowed.",
        )
    bad_child_launcher_lines = find_child_launcher_antipatterns(text)
    if bad_child_launcher_lines:
        report.add(
            "FRONTIER_CHILD_LAUNCHER_ANTIPATTERN",
            "blocking",
            "fail",
            "Child launcher anti-pattern found outside fallback context: " + " | ".join(bad_child_launcher_lines[:3]),
        )
    else:
        report.add("FRONTIER_CHILD_LAUNCHER_ANTIPATTERN", "blocking", "pass", "No non-fallback child launcher anti-pattern found.")
    if re.search(r"(?i)child ledger", text) and all(term in text for term in ["promptId", "responseId", "handoffId"]):
        report.add("FRONTIER_CHILD_LEDGER", "blocking", "pass", "Frontier contract requires child ledger identifiers.")
    else:
        report.add("FRONTIER_CHILD_LEDGER", "blocking", "fail", "Frontier contract must require a child ledger with promptId, responseId, and handoffId.")
    if re.search(r"(?i)human next step|what the human should do next", text):
        report.add("FRONTIER_HUMAN_NEXT_STEP", "blocking", "pass", "Frontier contract requires an explicit human next step.")
    else:
        report.add("FRONTIER_HUMAN_NEXT_STEP", "blocking", "fail", "Frontier contract must require an explicit human next step.")
    if re.search(r"(?i)not\s+return\s+to\s+Primary\s+merely\s+because", text) and re.search(r"(?i)provisional\s+packet|source\s+baseline|consume-result|handoff", text):
        report.add("FRONTIER_NO_PACKET_RETURN", "blocking", "pass", "Frontier contract forbids returning to Primary merely after writing intermediate lane evidence.")
    else:
        report.add(
            "FRONTIER_NO_PACKET_RETURN",
            "blocking",
            "fail",
            "Frontier contract must forbid returning to Primary merely because a provisional packet, handoff, source baseline, or consume-result was written.",
        )
    if re.search(r"(?i)`?blocked on Primary`?.*branchReturnGate", text, re.DOTALL):
        report.add("FRONTIER_BLOCKED_GATE", "blocking", "pass", "Frontier contract gates blocked-on-Primary claims behind branchReturnGate.")
    else:
        report.add("FRONTIER_BLOCKED_GATE", "blocking", "fail", "Frontier contract must gate blocked-on-Primary claims behind branchReturnGate.")
    if "human-explain-openacp" in text and "formal-report-openacp" in text:
        report.add("FRONTIER_REPORTING", "blocking", "pass", "Frontier contract requires human explanation and formal reports.")
    else:
        report.add("FRONTIER_REPORTING", "blocking", "fail", "Frontier contract must require human-explain-openacp and formal-report-openacp.")
    validate_frontier_contract_block(text, report)


def validate_frontier_contract_block(text: str, report: Report) -> None:
    blocks = extract_json_fence_objects(text)
    contracts = [
        block
        for block in blocks
        if block.get("schemaVersion") == "openacp-frontier-orchestration-contract.v1"
        or block.get("artifactType") == "frontier-orchestration-contract"
    ]
    if not contracts:
        report.add(
            "FRONTIER_CONTRACT_BLOCK",
            "blocking",
            "fail",
            "Frontier contract must include a JSON block with schemaVersion openacp-frontier-orchestration-contract.v1.",
        )
        return
    report.add("FRONTIER_CONTRACT_BLOCK", "blocking", "pass", "Frontier machine-readable contract block is present.")
    contract = contracts[0]
    required = [
        "schemaVersion",
        "artifactType",
        "authorityLevel",
        "laneObjective",
        "backlogScope",
        "operatingOrder",
        "gapDecisionMatrix",
        "branchReturnGate",
        "worktreeDecision",
        "childLedger",
        "subagentFirst",
        "defaultMode",
        "continuationPolicy",
        "seedArtifacts",
    ]
    missing = [field for field in required if field not in contract]
    if missing:
        report.add("FRONTIER_CONTRACT_REQUIRED_FIELDS", "blocking", "fail", "Contract block missing fields: " + ", ".join(missing))
    else:
        report.add("FRONTIER_CONTRACT_REQUIRED_FIELDS", "blocking", "pass", "Contract block includes required fields.")
    if contract.get("artifactType") == "frontier-orchestration-contract":
        report.add("FRONTIER_CONTRACT_TYPE", "blocking", "pass", "Contract artifactType is valid.")
    else:
        report.add("FRONTIER_CONTRACT_TYPE", "blocking", "fail", "Contract artifactType must be frontier-orchestration-contract.")
    if contract.get("authorityLevel") == "B2":
        report.add("FRONTIER_CONTRACT_AUTHORITY", "blocking", "pass", "Contract grants B2 lane-local authority.")
    else:
        report.add(
            "FRONTIER_CONTRACT_AUTHORITY",
            "blocking",
            "fail",
            "Contract block authorityLevel must be B2 unless a narrower prompt record is explicitly validated separately.",
        )
    backlog = contract.get("backlogScope", {})
    if isinstance(backlog, dict) and backlog.get("seedArtifactsPolicy") == "starting_points_not_exhaustive":
        report.add("FRONTIER_SEED_POLICY", "blocking", "pass", "Seed artifacts are marked as non-exhaustive.")
    else:
        report.add("FRONTIER_SEED_POLICY", "blocking", "fail", "backlogScope.seedArtifactsPolicy must be starting_points_not_exhaustive.")
    matrix = contract.get("gapDecisionMatrix", {})
    allowed = set(matrix.get("allowedValues", [])) if isinstance(matrix, dict) and isinstance(matrix.get("allowedValues"), list) else set()
    required_decisions = {
        "do_now",
        "dispatch_current_thread_subagent",
        "prepare_package",
        "prepare_package_only_when_dispatch_unavailable",
        "apply_conservative_default",
        "needs_final_authority",
        "explicitly_out",
    }
    missing_decisions = sorted(required_decisions - allowed)
    if missing_decisions:
        report.add("FRONTIER_GAP_DECISIONS", "blocking", "fail", "gapDecisionMatrix missing decisions: " + ", ".join(missing_decisions))
    else:
        report.add("FRONTIER_GAP_DECISIONS", "blocking", "pass", "gapDecisionMatrix has the full OpenACP decision vocabulary.")
    subagent_first = contract.get("subagentFirst")
    if subagent_first is True or (isinstance(subagent_first, dict) and subagent_first.get("enabled") is True):
        report.add("FRONTIER_CONTRACT_SUBAGENT_FIRST", "blocking", "pass", "Contract enables subagent-first dispatch.")
    else:
        report.add("FRONTIER_CONTRACT_SUBAGENT_FIRST", "blocking", "fail", "Contract must set subagentFirst true or {enabled: true}.")
    child_ledger = contract.get("childLedger", {})
    ledger_fields = set(child_ledger.get("requiredFields", [])) if isinstance(child_ledger, dict) and isinstance(child_ledger.get("requiredFields"), list) else set()
    ledger_required = {"promptId", "responseId", "handoffId", "role", "authority", "effects", "terminalStatus", "consumeStatus"}
    missing_ledger = sorted(ledger_required - ledger_fields)
    if missing_ledger:
        report.add("FRONTIER_CONTRACT_CHILD_LEDGER", "blocking", "fail", "childLedger missing fields: " + ", ".join(missing_ledger))
    else:
        report.add("FRONTIER_CONTRACT_CHILD_LEDGER", "blocking", "pass", "childLedger carries stable child identifiers and terminal status.")
    branch_gate = contract.get("branchReturnGate", {})
    branch_gate_text = json.dumps(branch_gate, ensure_ascii=False)
    if isinstance(branch_gate, dict) and "needs_final_authority" in branch_gate_text and "explicitly_out" in branch_gate_text:
        report.add("FRONTIER_CONTRACT_RETURN_GATE", "blocking", "pass", "branchReturnGate preserves final-authority-only return rule.")
    else:
        report.add(
            "FRONTIER_CONTRACT_RETURN_GATE",
            "blocking",
            "fail",
            "branchReturnGate must only allow return when remaining gaps are needs_final_authority or explicitly_out.",
        )


def find_child_launcher_antipatterns(text: str) -> list[str]:
    child_markers = [
        "downstream",
        "child",
        "worker",
        "reviewer",
        "discovery",
        "validation",
        "task-card-only",
        "task card",
    ]
    launcher_markers = [
        "short launcher",
        "chat launcher",
        "create a new thread",
        "open a new thread",
        "left sidebar",
        "paste the launcher",
        "return a launcher",
        "return only a launcher",
        "return only a short launcher",
        "return short",
    ]
    fallback_markers = [
        "fallback",
        "fallback-only",
        "unavailable",
        "unsafe",
        "explicitly requested",
        "separately user-managed",
        "do not",
        "must not",
        "not return",
        "only when",
    ]
    hits: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        lowered = line.lower()
        if not line:
            continue
        if any(child in lowered for child in child_markers) and any(marker in lowered for marker in launcher_markers):
            if not any(marker in lowered for marker in fallback_markers):
                hits.append(line[:160])
    return hits


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
    if data.get("dataRiskLimit") not in DATA_RISK_LEVELS:
        report.add("DATA_RISK_LIMIT", "blocking", "fail", "dataRiskLimit must be none, low, medium, high, or sensitive.")
    else:
        report.add("DATA_RISK_LIMIT", "blocking", "pass", "dataRiskLimit is valid.")
    for field_name in [
        "allowedActions",
        "forbiddenActions",
        "delegationRules",
        "scopeLimits",
        "resourceUseLimit",
        "allowedInputs",
        "allowedOutputs",
        "forbiddenSideEffects",
        "stopConditions",
    ]:
        require_non_empty_array(data, field_name, report)


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
    for field_name in ["activeLanes", "supersededPromptIds", "cancelledPromptIds", "latestConsumeRefs"]:
        if isinstance(data.get(field_name), list):
            report.add(f"{field_name.upper()}_ARRAY", "blocking", "pass", f"{field_name} is an array.")
        else:
            report.add(f"{field_name.upper()}_ARRAY", "blocking", "fail", f"{field_name} must be an array.")
    for idx, lane in enumerate(data.get("activeLanes", [])):
        loc = f"activeLanes[{idx}]"
        if not isinstance(lane, dict):
            report.add("ACTIVE_LANE_OBJECT", "blocking", "fail", "activeLanes entries must be objects.", loc)
            continue
        missing = [field for field in ["laneId", "role", "status", "currentPromptId", "authorityLevel"] if field not in lane]
        if missing:
            report.add("ACTIVE_LANE_FIELDS", "blocking", "fail", "active lane missing fields: " + ", ".join(missing), loc)
        else:
            report.add("ACTIVE_LANE_FIELDS", "blocking", "pass", "active lane has required fields.", loc)
        if lane.get("role") not in ROLES:
            report.add("ACTIVE_LANE_ROLE", "blocking", "fail", "active lane role must be a known OpenACP role.", loc)
        if lane.get("authorityLevel") not in AUTHORITY_LEVELS:
            report.add("ACTIVE_LANE_AUTHORITY", "blocking", "fail", "active lane authorityLevel must be B0, B1, B2, or B3.", loc)
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
    for field_name in ["prompts", "responses", "handoffs", "cards", "consumes", "activeLanes"]:
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
    known_handoff_ids = {
        str(item.get("handoffId"))
        for item in data.get("handoffs", [])
        if isinstance(item, dict) and item.get("handoffId")
    }
    known_response_ids = response_ids
    for idx, consume in enumerate(data.get("consumes", [])):
        loc = f"consumes[{idx}]"
        if not isinstance(consume, dict):
            report.add("CONSUME_OBJECT", "blocking", "fail", "consume entries must be objects.", loc)
            continue
        missing = [field for field in ["consumeId", "responseId", "targetHandoffIds", "decision", "authorityScope"] if field not in consume]
        if missing:
            report.add("CONSUME_FIELDS", "blocking", "fail", "consume entry missing fields: " + ", ".join(missing), loc)
            continue
        if consume.get("responseId") not in known_response_ids:
            report.add("CONSUME_RESPONSE_REF", "blocking", "fail", "consume responseId is not registered.", loc)
        targets = [str(item) for item in consume.get("targetHandoffIds", []) if str(item).strip()]
        unknown_targets = sorted({item for item in targets if item not in known_handoff_ids})
        if unknown_targets:
            report.add("CONSUME_HANDOFF_REFS", "blocking", "fail", "consume references unknown handoffs: " + ", ".join(unknown_targets), loc)
        if consume.get("decision") not in CONSUME_DECISIONS:
            report.add("CONSUME_DECISION", "blocking", "fail", "consume decision is not valid.", loc)
        if consume.get("authorityScope") not in AUTHORITY_SCOPES:
            report.add("CONSUME_AUTHORITY_SCOPE", "blocking", "fail", "consume authorityScope is not valid.", loc)
    for idx, lane in enumerate(data.get("activeLanes", [])):
        loc = f"activeLanes[{idx}]"
        if not isinstance(lane, dict):
            report.add("SEQ_ACTIVE_LANE_OBJECT", "blocking", "fail", "activeLanes entries must be objects.", loc)
            continue
        current_prompt = lane.get("currentPromptId")
        if current_prompt and current_prompt not in prompt_ids:
            report.add("SEQ_ACTIVE_LANE_PROMPT", "blocking", "fail", "active lane currentPromptId is not registered.", loc)


def validate_consume_result(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "consume-result":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be consume-result.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is consume-result.")
    if data.get("consumerRole") not in ROLES:
        report.add("CONSUMER_ROLE", "blocking", "fail", "consumerRole is not a known OpenACP role.")
    else:
        report.add("CONSUMER_ROLE", "blocking", "pass", "consumerRole is valid.")
    if data.get("authorityScope") not in AUTHORITY_SCOPES:
        report.add("AUTHORITY_SCOPE", "blocking", "fail", "authorityScope must be provisional or final.")
    else:
        report.add("AUTHORITY_SCOPE", "blocking", "pass", "authorityScope is valid.")
    if data.get("decision") not in CONSUME_DECISIONS:
        report.add("CONSUME_DECISION", "blocking", "fail", "decision must be accepted, amend, split-follow-up, rejected, or blocked.")
    else:
        report.add("CONSUME_DECISION", "blocking", "pass", "decision is valid.")
    if data.get("authorityScope") == "final" and data.get("consumerRole") not in {"primary", "human-owner"}:
        report.add("FINAL_CONSUME_AUTHORITY", "blocking", "fail", "Only Primary or human-owner may issue final consume results.")
    else:
        report.add("FINAL_CONSUME_AUTHORITY", "blocking", "pass", "Final consume authority is not overclaimed.")
    for field_name in [
        "targetHandoffIds",
        "basisRefs",
        "evidenceStatus",
        "claimsAccepted",
        "claimsRejected",
        "remainingRisks",
        "authorityLimits",
        "nextActions",
    ]:
        require_non_empty_array(data, field_name, report)
    if isinstance(data.get("targetReviewIds"), list):
        report.add("TARGET_REVIEW_IDS_ARRAY", "blocking", "pass", "targetReviewIds is an array.")
    else:
        report.add("TARGET_REVIEW_IDS_ARRAY", "blocking", "fail", "targetReviewIds must be an array.")


def validate_machine_summary(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "machine-summary":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be machine-summary.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is machine-summary.")
    if data.get("role") not in ROLES:
        report.add("SUMMARY_ROLE", "blocking", "fail", "role is not a known OpenACP role.")
    else:
        report.add("SUMMARY_ROLE", "blocking", "pass", "role is valid.")
    if data.get("authority") not in AUTHORITY_LEVELS:
        report.add("SUMMARY_AUTHORITY", "blocking", "fail", "authority must be B0, B1, B2, or B3.")
    else:
        report.add("SUMMARY_AUTHORITY", "blocking", "pass", "authority is valid.")
    if data.get("effectsPreset") not in EFFECTS_PRESETS:
        report.add("SUMMARY_EFFECTS_PRESET", "blocking", "fail", "effectsPreset is not a known OpenACP effects preset.")
    else:
        report.add("SUMMARY_EFFECTS_PRESET", "blocking", "pass", "effectsPreset is valid.")
    for field_name in ["promptId", "responseId", "status"]:
        require_non_empty_string(data, field_name, report)
    for field_name in ["basisRefs", "locators", "claims", "nextActions"]:
        require_non_empty_array(data, field_name, report)
    for idx, locator in enumerate(data.get("locators", [])):
        loc = f"locators[{idx}]"
        if not isinstance(locator, dict):
            report.add("LOCATOR_OBJECT", "blocking", "fail", "locator entries must be objects.", loc)
            continue
        if not str(locator.get("kind", "")).strip():
            report.add("LOCATOR_KIND", "blocking", "fail", "locator.kind is required.", loc)
        if not (str(locator.get("id", "")).strip() or str(locator.get("path", "")).strip()):
            report.add("LOCATOR_TARGET", "blocking", "fail", "locator must include id or path.", loc)


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
    if actor == "frontier":
        if data.get("effectsPreset") == "orchestration_local_write":
            report.add("FRONTIER_HANDOFF_EFFECTS", "blocking", "pass", "Frontier handoff uses orchestration-local effects.")
        else:
            report.add(
                "FRONTIER_HANDOFF_EFFECTS",
                "blocking",
                "fail",
                "Frontier handoffs must use orchestration_local_write; implementation or docs commit evidence must come from scoped workers.",
            )
    else:
        report.add("FRONTIER_HANDOFF_EFFECTS", "blocking", "pass", "Actor is not a Frontier handoff.")
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
    elif args.ruleset == "consume-result":
        validate_consume_result(data, report)
    elif args.ruleset == "machine-summary":
        validate_machine_summary(data, report)
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
        validate_prompt_record_text(text, report, args.expect_prompt_id)
    elif args.ruleset == "launcher":
        prompt_record_text = None
        if args.prompt_record:
            prompt_record_path = Path(args.prompt_record)
            prompt_record_text, prompt_record_error = read_utf8(prompt_record_path)
            if prompt_record_error:
                report.add("PROMPT_RECORD_CROSSCHECK_READ", "blocking", "fail", prompt_record_error, str(prompt_record_path))
            else:
                report.add("PROMPT_RECORD_CROSSCHECK_READ", "blocking", "pass", "Prompt record cross-check target read as UTF-8.", str(prompt_record_path))
        validate_launcher_text(text, report, prompt_record_text, args.expect_prompt_id)
    elif args.ruleset == "launcher-output":
        validate_launcher_output_text(text, report)
    elif args.ruleset == "formal-report":
        validate_formal_report_text(text, report)
    elif args.ruleset == "frontier-contract":
        validate_frontier_contract_text(text, report)
    elif args.ruleset == "card-registry":
        validate_card_registry_text(text, report)
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
        try:
            relative = path.relative_to(root)
        except ValueError:
            relative = path
        if relative == Path("README.md"):
            if _has_cjk(text):
                report.add("ROOT_README_LANGUAGE", "blocking", "fail", "Root README.md must be English. Put localized onboarding in docs or examples.", str(path))
            else:
                report.add("ROOT_README_LANGUAGE", "blocking", "pass", "Root README.md is English-only.", str(path))
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
    parser.add_argument("--prompt-record", help="Optional full prompt record for launcher Prompt ID cross-checks.")
    parser.add_argument("--expect-prompt-id", help="Expected Prompt ID for prompt-record or launcher validation.")
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
