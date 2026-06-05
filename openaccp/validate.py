#!/usr/bin/env python3
"""OpenACCP artifact validator.

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
from importlib import resources
from pathlib import Path
from typing import Any

try:
    from .version import VERSION
except ImportError:  # pragma: no cover - supports direct script execution
    from version import VERSION

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError, ValidationError
except ImportError:  # pragma: no cover - fallback covers source checkouts without installed deps
    Draft202012Validator = None  # type: ignore[assignment]
    SchemaError = ValidationError = Exception  # type: ignore[assignment]

RULESETS = {
    "authority-charter",
    "assumption-ledger",
    "card-registry",
    "child-ledger",
    "consume-result",
    "current-manifest",
    "decision-registry",
    "formal-report",
    "frontier-closure",
    "frontier-contract",
    "handoff",
    "launcher",
    "launcher-output",
    "lane-registry",
    "machine-summary",
    "prompt-record",
    "review-report",
    "runtime-boundary",
    "scope-boundary",
    "sequence-registry",
    "source-pack",
    "source-status-registry",
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

JSON_SCHEMA_RULESETS = RULESETS - TEXT_RULESETS - {"public-package"}

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
        "responseId",
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
        "sequenceRegistryRef",
        "laneRegistryRef",
        "runtimeBoundaryRef",
        "sourceStatusRegistryRef",
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
    "runtime-boundary": [
        "schemaVersion",
        "artifactType",
        "boundaryId",
        "workingDirectory",
        "productRepoStatus",
        "productRepoPath",
        "baseBranch",
        "sourceRoots",
        "testEntrypoints",
        "worktreePolicy",
        "allowedWritablePaths",
        "readOnlyPaths",
        "forbiddenPaths",
        "externalSideEffects",
        "dataRisk",
        "unresolvedOwnerInputs",
        "b2DispatchGate",
    ],
    "lane-registry": [
        "schemaVersion",
        "artifactType",
        "registryId",
        "lanes",
    ],
    "child-ledger": [
        "schemaVersion",
        "artifactType",
        "ledgerId",
        "laneId",
        "children",
    ],
    "source-status-registry": [
        "schemaVersion",
        "artifactType",
        "registryId",
        "sources",
    ],
    "decision-registry": [
        "schemaVersion",
        "artifactType",
        "registryId",
        "decisions",
    ],
    "frontier-closure": [
        "schemaVersion",
        "artifactType",
        "closureId",
        "laneId",
        "responseId",
        "authorityLevel",
        "branchState",
        "gapDecisionMatrix",
        "childLedgerRef",
        "allChildrenTerminal",
        "allChildHandoffsConsumedOrRejected",
        "primaryReadyPacketRef",
        "remainingB0B1B2SafeWork",
        "remainingFinalAuthorityGaps",
        "explicitlyOutGaps",
        "worktreeDecision",
        "humanNextStep",
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
    "runtime-boundary": "runtime-boundary",
    "lane-registry": "lane-registry",
    "child-ledger": "child-ledger",
    "source-status-registry": "source-status-registry",
    "decision-registry": "decision-registry",
    "frontier-closure": "frontier-closure",
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
ROLE_MAX_AUTHORITY = {
    "primary": "B3",
    "human-owner": "B3",
    "frontier": "B2",
    "worker": "B2",
    "reviewer": "B2",
    "discovery": "B2",
    "validation": "B2",
    "task-card-only": "B1",
}
AUTHORITY_RANK = {"B0": 0, "B1": 1, "B2": 2, "B3": 3}
REVIEW_RECOMMENDATIONS = {"approve", "amend", "split-follow-up", "reject"}
CONSUME_DECISIONS = {"accepted", "amend", "split-follow-up", "rejected", "blocked"}
AUTHORITY_SCOPES = {"provisional", "final"}
VERIFY_RESULTS = {"pass", "fail", "skipped"}
SOURCE_STATUSES = {"current", "reference", "deprecated"}
SOURCE_REGISTRY_STATUSES = {"current", "reference", "deprecated", "invalid", "unknown"}
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
LAUNCHER_TITLE_RE = re.compile(
    r"^(?P<project>[^#\r\n][^-`\r\n]{1,80}?)\s+-\s+(?P<slot>Primary Orchestrator|Frontier 0[1-5]|PO\s+(?:Worker|Reviewer|Discovery|Validation|Task-Card Packager|Task-Card Worker)|F0[1-5]\s+(?:Worker|Reviewer|Discovery|Validation|Task-Card Packager|Task-Card Worker))\s+-\s+(?P<title>[^`\r\n]{3,120})$",
    re.IGNORECASE,
)
ZH_ITEM = "\u9879"
ZH_TYPE_STATUS = "\u7c7b\u578b\u548c\u72b6\u6001"
ZH_FIELD = "\u5b57\u6bb5"
ZH_PROGRESS = "\u603b\u4f53\u8fdb\u5ea6"
ZH_EVIDENCE = "\u8bc1\u636e"
ZH_BASIS = "\u4f9d\u636e"
ZH_EVIDENCE_AND_VALIDATION = "\u4f9d\u636e\u4e0e\u9a8c\u8bc1"
ZH_RECOMMENDED_NEXT_STEP = "\u4e0b\u4e00\u6b65\u5efa\u8bae"
ZH_LEFT_SIDEBAR = "\u5de6\u4fa7"
ZH_NEW_THREAD = "\u65b0\u5efa"
ZH_PASTE = "\u7c98\u8d34"
ZH_VALIDATION = "\u9a8c\u8bc1"
ZH_AREA = "\u8303\u56f4"

FORMAL_HEADERS = {("Item/Status", "Content"), (ZH_TYPE_STATUS, "\u5185\u5bb9")}
FORMAL_ROW_SEQUENCES = [
    ["Changed", "Progress", "Gate", "Area", "Goal", "Gaps", "Next"],
    [
        "\u505a\u4e86\u4ec0\u4e48",
        "\u603b\u4f53\u8fdb\u5ea6",
        "\u9a8c\u8bc1",
        "\u8303\u56f4",
        "\u76ee\u6807",
        "\u7f3a\u53e3",
        "\u4e0b\u4e00\u6b65",
    ],
    [
        "\u505a\u4e86\u4ec0\u4e48",
        "\u603b\u4f53\u8fdb\u5ea6",
        "Frontier",
        "\u76ee\u6807",
        "\u7f3a\u53e3",
        "\u4e0b\u4e00\u6b65",
    ],
    [
        "\u505a\u4e86\u4ec0\u4e48",
        "\u603b\u4f53\u8fdb\u5ea6",
        "Lane",
        "\u76ee\u6807",
        "\u7f3a\u53e3",
        "\u4e0b\u4e00\u6b65",
    ],
]

LEGACY_PROJECT_NAME = "Open" + "ACP"
LEGACY_HIDDEN_DIR = "." + "open" + "acp"
LEGACY_PROMPT_PREFIX = "open" + "acp-"

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
    re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:\\"),
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
    ".openaccp-local",
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
            "schemaVersion": "openaccp-validator-report.v1",
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


def schema_path_for_ruleset(ruleset: str) -> Path | None:
    if ruleset not in JSON_SCHEMA_RULESETS:
        return None
    package_schema = resources.files("openaccp").joinpath("schemas", f"{ruleset}.schema.json")
    if package_schema.is_file():
        return Path(str(package_schema))
    root = Path(__file__).resolve().parents[1]
    candidates = [
        root / "schemas" / f"{ruleset}.schema.json",
        Path.cwd() / "schemas" / f"{ruleset}.schema.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def resolve_schema_ref(ref: str, root_schema: dict[str, Any]) -> dict[str, Any] | None:
    if not ref.startswith("#/"):
        return None
    node: Any = root_schema
    for raw_part in ref[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, dict) else None


def json_schema_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def json_schema_errors(value: Any, schema: dict[str, Any], root_schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    ref = schema.get("$ref")
    if isinstance(ref, str):
        target = resolve_schema_ref(ref, root_schema)
        if target is None:
            return [f"{path}: unsupported or missing $ref {ref}"]
        return json_schema_errors(value, target, root_schema, path)

    if "anyOf" in schema:
        variants = schema.get("anyOf")
        if isinstance(variants, list):
            variant_errors = [json_schema_errors(value, item, root_schema, path) for item in variants if isinstance(item, dict)]
            if variant_errors and not any(not item_errors for item_errors in variant_errors):
                errors.append(f"{path}: does not match any anyOf branch")

    if "allOf" in schema and isinstance(schema.get("allOf"), list):
        for idx, sub_schema in enumerate(schema["allOf"]):
            if isinstance(sub_schema, dict):
                errors.extend(json_schema_errors(value, sub_schema, root_schema, f"{path}.allOf[{idx}]"))

    if "if" in schema and isinstance(schema.get("if"), dict):
        condition_errors = json_schema_errors(value, schema["if"], root_schema, path)
        if not condition_errors and isinstance(schema.get("then"), dict):
            errors.extend(json_schema_errors(value, schema["then"], root_schema, path))

    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not json_schema_type_matches(value, expected_type):
        errors.append(f"{path}: expected {expected_type}")
        return errors
    if isinstance(expected_type, list) and not any(json_schema_type_matches(value, item) for item in expected_type if isinstance(item, str)):
        errors.append(f"{path}: expected one of {', '.join(str(item) for item in expected_type)}")
        return errors

    if "const" in schema and value != schema.get("const"):
        errors.append(f"{path}: must equal {schema.get('const')!r}")
    if "enum" in schema and isinstance(schema.get("enum"), list) and value not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']!r}")
    if isinstance(value, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            errors.append(f"{path}: string length must be >= {min_length}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and not re.search(pattern, value):
            errors.append(f"{path}: string does not match pattern {pattern!r}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            errors.append(f"{path}: value must be >= {minimum}")
    if isinstance(value, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{path}: array length must be >= {min_items}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(value):
                errors.extend(json_schema_errors(item, item_schema, root_schema, f"{path}[{idx}]"))
    if isinstance(value, dict):
        required = schema.get("required")
        if isinstance(required, list):
            for field_name in required:
                if isinstance(field_name, str) and field_name not in value:
                    errors.append(f"{path}: missing required field {field_name}")
        properties = schema.get("properties")
        if isinstance(properties, dict):
            for field_name, field_schema in properties.items():
                if field_name in value and isinstance(field_schema, dict):
                    errors.extend(json_schema_errors(value[field_name], field_schema, root_schema, f"{path}.{field_name}"))
        if schema.get("additionalProperties") is False and isinstance(properties, dict):
            extra_fields = sorted(set(value) - set(properties))
            for field_name in extra_fields:
                errors.append(f"{path}: additional property {field_name} is not allowed")
    return errors


def validate_json_schema_contract(ruleset: str, data: dict[str, Any], report: Report) -> None:
    schema_path = schema_path_for_ruleset(ruleset)
    if schema_path is None:
        report.add("JSON_SCHEMA", "warning", "pass", "No JSON Schema is configured for this ruleset.")
        return
    if not schema_path.exists():
        report.add("JSON_SCHEMA_FILE", "blocking", "fail", "JSON Schema file is missing.", str(schema_path))
        return
    schema_report = Report(str(schema_path), "schema")
    schema = load_json(schema_path, schema_report)
    if not isinstance(schema, dict):
        report.add("JSON_SCHEMA_FILE", "blocking", "fail", "JSON Schema file could not be parsed.", str(schema_path))
        return
    if Draft202012Validator is not None:
        try:
            validator = Draft202012Validator(schema)
            errors = [
                f"{'.'.join(str(part) for part in error.absolute_path) or '$'}: {error.message}"
                for error in sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path))
            ]
        except SchemaError as exc:
            report.add("JSON_SCHEMA_FILE", "blocking", "fail", f"JSON Schema itself is invalid: {exc}", str(schema_path))
            return
    else:
        errors = json_schema_errors(data, schema, schema)
    if errors:
        report.add("JSON_SCHEMA", "blocking", "fail", "Schema validation failed: " + "; ".join(errors[:8]), str(schema_path))
    else:
        report.add("JSON_SCHEMA", "blocking", "pass", "Artifact conforms to its JSON Schema.", str(schema_path))


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


def split_table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def extract_table_groups(text: str) -> list[list[str]]:
    groups: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            current.append(stripped)
        elif current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    return groups


def parse_formal_table(text: str, report: Report) -> tuple[list[tuple[str, str]], tuple[str, str] | None]:
    groups = extract_table_groups(text)
    if len(groups) != 1:
        report.add("FORMAL_SINGLE_TABLE", "blocking", "fail", "Formal report must contain exactly one Markdown table.")
        return [], None
    report.add("FORMAL_SINGLE_TABLE", "blocking", "pass", "Formal report contains exactly one Markdown table.")
    group = groups[0]
    if len(group) < 3:
        report.add("FORMAL_TABLE_SHAPE", "blocking", "fail", "Formal report table must include header, separator, and rows.")
        return [], None
    header_cells = [normalize_table_label(cell) for cell in split_table_cells(group[0])]
    separator_cells = split_table_cells(group[1])
    if len(header_cells) != 2 or len(separator_cells) != 2:
        report.add("FORMAL_TWO_COLUMNS", "blocking", "fail", "Formal report table must have exactly two columns.")
        return [], None
    if not is_table_separator(separator_cells):
        report.add("FORMAL_TABLE_SEPARATOR", "blocking", "fail", "Formal report table separator row is invalid.")
        return [], None
    report.add("FORMAL_TWO_COLUMNS", "blocking", "pass", "Formal report table has exactly two columns.")
    header = (header_cells[0], header_cells[1])
    rows: list[tuple[str, str]] = []
    for idx, line in enumerate(group[2:], start=3):
        cells = split_table_cells(line)
        if len(cells) != 2:
            report.add("FORMAL_ROW_COLUMNS", "blocking", "fail", "Formal report data rows must have exactly two columns.", f"row {idx}")
            continue
        left = normalize_table_label(cells[0])
        right = cells[1].strip()
        rows.append((left, right))
    if all(len(split_table_cells(line)) == 2 for line in group[2:]):
        report.add("FORMAL_ROW_COLUMNS", "blocking", "pass", "Formal report data rows have exactly two columns.")
    return rows, header


PLACEHOLDER_CELL_VALUES = {
    "",
    "-",
    "--",
    "n/a",
    "na",
    "none",
    "todo",
    "tbd",
    "unknown",
    "unclear",
    "yes / no / unclear",
    "safe / risky / unclear",
    "<lane-id>",
    "<card-id>",
    "<task-id>",
}


def is_meaningful_cell(value: Any) -> bool:
    text = str(value or "").strip()
    lowered = text.lower()
    if lowered in PLACEHOLDER_CELL_VALUES:
        return False
    if re.fullmatch(r"<[^>]+>", text):
        return False
    return bool(text)


def find_table_by_headers(text: str, required_headers: list[str]) -> tuple[list[str], list[list[str]]] | None:
    required = [header.lower() for header in required_headers]
    for group in extract_table_groups(text):
        if len(group) < 3:
            continue
        headers = [normalize_table_label(cell).lower() for cell in split_table_cells(group[0])]
        if all(any(required_header in header for header in headers) for required_header in required):
            rows: list[list[str]] = []
            for line in group[2:]:
                cells = split_table_cells(line)
                if len(cells) == len(headers):
                    rows.append(cells)
            return headers, rows
    return None


def table_index(headers: list[str], candidates: list[str]) -> int | None:
    lowered_candidates = [candidate.lower() for candidate in candidates]
    for idx, header in enumerate(headers):
        if any(candidate in header for candidate in lowered_candidates):
            return idx
    return None


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


def has_valid_formal_header(text: str) -> bool:
    rows, header = parse_formal_table(text, Report("<inline>", "formal-report"))
    return bool(rows) and header in FORMAL_HEADERS


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
    if "human-explain-openaccp" in text:
        report.add("HUMAN_EXPLAIN_REQUIRED", "blocking", "pass", "Prompt record requires human-explain-openaccp.")
    else:
        report.add("HUMAN_EXPLAIN_REQUIRED", "blocking", "fail", "Prompt record must require human-explain-openaccp for replies.")
    if is_primary_prompt_record(text):
        validate_primary_prompt_contract_text(text, report)


def is_primary_prompt_record(text: str) -> bool:
    return bool(
        re.search(r"(?im)^\s*(Role|角色)\s*:\s*Primary\b", text)
        or re.search(r"(?i)\bPrimary\s+Orchestrator\b", text)
    )


def validate_primary_prompt_contract_text(text: str, report: Report) -> None:
    lowered = text.lower()
    runtime_terms = [
        "runtime boundary",
        "product repo path",
        "base branch",
        "source roots",
        "test entrypoints",
        "worktree policy",
        "runtimeboundaryref",
    ]
    missing_runtime_terms = [term for term in runtime_terms if term not in lowered.replace("-", " ")]
    if len(missing_runtime_terms) <= 1 and re.search(r"(?i)(before|prior to).{0,80}Frontier|Frontier.{0,80}(before|prior to)", text):
        report.add("PRIMARY_RUNTIME_BOUNDARY_GATE", "blocking", "pass", "Primary prompt gates Frontier dispatch on runtime boundary.")
    else:
        report.add(
            "PRIMARY_RUNTIME_BOUNDARY_GATE",
            "blocking",
            "fail",
            "Primary prompt must resolve runtime boundary before Frontier dispatch: product repo path, base branch, source roots, test entrypoints, worktree policy, and runtimeBoundaryRef.",
        )
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
    if re.search(r"(?im)^\s*schemaVersion\s*:\s*openaccp-card-registry\.v1\s*$", text):
        report.add("CARD_REGISTRY_SCHEMA", "blocking", "pass", "CARD registry schemaVersion is present.")
    else:
        report.add("CARD_REGISTRY_SCHEMA", "blocking", "fail", "CARD registry must include schemaVersion: openaccp-card-registry.v1.")
    if re.search(r"(?im)^\s*artifactType\s*:\s*card-registry\s*$", text):
        report.add("CARD_REGISTRY_TYPE", "blocking", "pass", "CARD registry artifactType is present.")
    else:
        report.add("CARD_REGISTRY_TYPE", "blocking", "fail", "CARD registry must include artifactType: card-registry.")
    required_sections = ["Domain Coverage", "Complexity Assessment", "CARD List", "Lane Grouping"]
    missing_sections = [section for section in required_sections if section.lower() not in text.lower()]
    if missing_sections:
        report.add("CARD_REGISTRY_SECTIONS", "blocking", "fail", "CARD registry missing sections: " + ", ".join(missing_sections))
    else:
        report.add("CARD_REGISTRY_SECTIONS", "blocking", "pass", "CARD registry has required sections.")
    card_table = find_table_by_headers(text, ["card", "domain", "authority", "status", "objective", "task-card"])
    card_ids: list[str] = []
    invalid_card_rows: list[str] = []
    if card_table is None:
        report.add("CARD_REGISTRY_CARD_TABLE", "blocking", "fail", "CARD registry must include a CARD List table with CARD, domain, authority, lane, status, objective, source refs, and task-card candidates.")
    else:
        headers, rows = card_table
        card_idx = table_index(headers, ["card"])
        domain_idx = table_index(headers, ["domain"])
        authority_idx = table_index(headers, ["authority"])
        lane_idx = table_index(headers, ["candidate lane", "lane"])
        status_idx = table_index(headers, ["status"])
        objective_idx = table_index(headers, ["objective"])
        source_idx = table_index(headers, ["source refs", "source"])
        task_idx = table_index(headers, ["task-card candidates", "task-card"])
        required_indices = {
            "CARD": card_idx,
            "Domain": domain_idx,
            "Authority": authority_idx,
            "Lane": lane_idx,
            "Status": status_idx,
            "Objective": objective_idx,
            "Source": source_idx,
            "Task-card candidates": task_idx,
        }
        missing_columns = [name for name, idx in required_indices.items() if idx is None]
        if missing_columns:
            report.add("CARD_REGISTRY_CARD_TABLE_COLUMNS", "blocking", "fail", "CARD List table missing columns: " + ", ".join(missing_columns))
        else:
            for row_number, row in enumerate(rows, start=1):
                card_cell = row[card_idx]  # type: ignore[index]
                if not re.fullmatch(r"CARD-\d{3,}", card_cell.strip()):
                    invalid_card_rows.append(f"row {row_number}: invalid CARD id")
                    continue
                required_cells = {
                    "domain": row[domain_idx],  # type: ignore[index]
                    "authority": row[authority_idx],  # type: ignore[index]
                    "lane": row[lane_idx],  # type: ignore[index]
                    "status": row[status_idx],  # type: ignore[index]
                    "objective": row[objective_idx],  # type: ignore[index]
                    "source refs": row[source_idx],  # type: ignore[index]
                    "task-card candidates": row[task_idx],  # type: ignore[index]
                }
                missing_values = [name for name, value in required_cells.items() if not is_meaningful_cell(value)]
                if missing_values:
                    invalid_card_rows.append(f"{card_cell}: missing " + ", ".join(missing_values))
                    continue
                card_ids.append(card_cell.strip())
            if invalid_card_rows:
                report.add("CARD_REGISTRY_CARD_ROWS", "blocking", "fail", "CARD rows must be real dispatch candidates, not placeholders: " + "; ".join(invalid_card_rows[:5]))
            else:
                report.add("CARD_REGISTRY_CARD_ROWS", "blocking", "pass", "CARD List rows have real dispatch fields.")
            duplicate_card_ids = sorted({card_id for card_id in card_ids if card_ids.count(card_id) > 1})
            if duplicate_card_ids:
                report.add("CARD_REGISTRY_CARD_IDS_UNIQUE", "blocking", "fail", "CARD ids must be unique: " + ", ".join(duplicate_card_ids[:5]))
            elif card_ids:
                report.add("CARD_REGISTRY_CARD_IDS_UNIQUE", "blocking", "pass", "CARD ids are unique.")
    has_small_exception = bool(
        re.search(r"(?im)^\s*-\s*(starter[- ]package[- ]reason|small[- ]project[- ]reason|single[- ]lane[- ]reason|explicit[- ]user[- ]request)\s*:\s*\S", text)
        or re.search(r"(?i)\b(starter package|small project|single safe lane|explicit user request)\b.{0,160}\bCARD", text)
    )
    has_count_reason = bool(re.search(r"(?im)^\s*-\s*cardCountReason\s*:\s*\S", text) or "card count reason" in text.lower())
    if 10 <= len(card_ids) <= 20:
        report.add("CARD_REGISTRY_CARD_COUNT", "blocking", "pass", f"CARD registry includes {len(card_ids)} CARD ids.")
    elif len(card_ids) > 20 and has_count_reason:
        report.add("CARD_REGISTRY_CARD_COUNT", "warning", "pass", "CARD registry has more than 20 CARDs with a split or approval reason.")
    elif len(card_ids) > 20:
        report.add("CARD_REGISTRY_CARD_COUNT", "warning", "fail", "CARD registry has more than 20 CARDs; record a split reason or human approval.")
    elif has_small_exception:
        report.add("CARD_REGISTRY_CARD_COUNT", "blocking", "pass", "CARD registry uses fewer than 10 CARDs with an explicit small/single-lane/user-request reason.")
    else:
        report.add(
            "CARD_REGISTRY_CARD_COUNT",
            "blocking",
            "fail",
            f"CARD registry has only {len(card_ids)} CARD ids; normal projects need 10-20 or an explicit small/single-lane/user-request reason.",
        )
    validate_card_domain_coverage(text, report)
    if re.search(r"(?i)task[- ]card", text):
        report.add("CARD_REGISTRY_TASK_CARD_CANDIDATES", "blocking", "pass", "CARD registry links CARDs to task-card candidates.")
    else:
        report.add("CARD_REGISTRY_TASK_CARD_CANDIDATES", "blocking", "fail", "CARD registry must include task-card candidates.")
    if re.search(r"(?i)Frontier|lane candidate|candidate lane", text):
        report.add("CARD_REGISTRY_LANE_GROUPING", "blocking", "pass", "CARD registry supports Frontier lane grouping.")
    else:
        report.add("CARD_REGISTRY_LANE_GROUPING", "blocking", "fail", "CARD registry must support Frontier lane grouping.")


def validate_card_domain_coverage(text: str, report: Report) -> None:
    domain_table = find_table_by_headers(text, ["domain", "present", "card coverage"])
    if domain_table is None:
        report.add("CARD_REGISTRY_DOMAIN_SCAN", "blocking", "fail", "CARD registry must include a Domain Coverage table with present/coverage decisions.")
        return
    headers, rows = domain_table
    domain_idx = table_index(headers, ["domain"])
    present_idx = table_index(headers, ["present"])
    source_idx = table_index(headers, ["source refs", "source"])
    coverage_idx = table_index(headers, ["card coverage"])
    if domain_idx is None or present_idx is None or coverage_idx is None:
        report.add("CARD_REGISTRY_DOMAIN_SCAN", "blocking", "fail", "Domain Coverage table must include Domain, Present?, and CARD coverage columns.")
        return
    if not rows:
        report.add("CARD_REGISTRY_DOMAIN_SCAN", "blocking", "fail", "Domain Coverage table must include domain rows.")
        return
    invalid_rows: list[str] = []
    known_rows = 0
    present_domains = 0
    placeholder_values = {"yes / no / unclear", "yes/no/unclear", "safe / risky / unclear"}
    positive_values = {"yes", "present", "current", "true", "needed", "in-scope", "in scope"}
    neutral_values = {"no", "absent", "false", "out", "out-of-scope", "out of scope", "unclear", "unknown", "n/a", "na"}
    for row_number, row in enumerate(rows, start=1):
        domain = row[domain_idx].strip()
        present_value = row[present_idx].strip().lower()
        coverage = row[coverage_idx].strip()
        source = row[source_idx].strip() if source_idx is not None and source_idx < len(row) else ""
        if not is_meaningful_cell(domain):
            invalid_rows.append(f"row {row_number}: missing domain")
            continue
        if present_value in placeholder_values or not is_meaningful_cell(present_value):
            invalid_rows.append(f"{domain}: Present? is still a placeholder")
            continue
        if present_value not in positive_values and present_value not in neutral_values:
            invalid_rows.append(f"{domain}: Present? must be yes/no/unclear-style, not `{present_value}`")
            continue
        known_rows += 1
        if present_value in positive_values:
            present_domains += 1
            if not is_meaningful_cell(source):
                invalid_rows.append(f"{domain}: present domain needs source refs")
            if not is_meaningful_cell(coverage) or not re.search(r"\bCARD-\d{3,}\b", coverage):
                invalid_rows.append(f"{domain}: present domain needs CARD coverage")
    if invalid_rows:
        report.add("CARD_REGISTRY_DOMAIN_SCAN", "blocking", "fail", "Domain Coverage rows must be resolved before Frontier dispatch: " + "; ".join(invalid_rows[:5]))
    elif known_rows:
        report.add("CARD_REGISTRY_DOMAIN_SCAN", "blocking", "pass", f"Domain Coverage table has {known_rows} resolved rows and {present_domains} present domains with CARD coverage.")
    else:
        report.add("CARD_REGISTRY_DOMAIN_SCAN", "blocking", "fail", "Domain Coverage table has no resolved rows.")


def launcher_non_empty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def is_child_launcher_slot(slot: str | None) -> bool:
    if not slot:
        return False
    return bool(re.match(r"(?i)^(?:F0[1-5]|PO)\s+", slot.strip()))


def validate_launcher_contract_text(text: str, report: Report, location: str = "") -> re.Match[str] | None:
    lines = launcher_non_empty_lines(text)
    first_line = lines[0] if lines else ""
    title_match = LAUNCHER_TITLE_RE.match(first_line)
    if not first_line:
        report.add("LAUNCHER_TITLE", "blocking", "fail", "Launcher must start with a title line.", location)
    elif first_line.startswith("#"):
        report.add("LAUNCHER_TITLE", "blocking", "fail", "Launcher title must be plain text, not a Markdown heading.", location)
    elif title_match:
        report.add("LAUNCHER_TITLE", "blocking", "pass", "Launcher title follows the OpenACCP slot contract.", location)
    else:
        report.add(
            "LAUNCHER_TITLE",
            "blocking",
            "fail",
            "Launcher title must be `<Project> - Primary Orchestrator - <Title>`, `<Project> - Frontier 01..05 - <Title>`, `F01..F05 Worker/Reviewer/Discovery/Validation/Task-Card Worker - <Title>`, or `PO Worker/Reviewer/Discovery/Validation/Task-Card Worker - <Title>`.",
            location,
        )
    legacy_hits: list[str] = []
    if re.search(r"(?<!C)" + re.escape(LEGACY_PROJECT_NAME) + r"(?!C)", text):
        legacy_hits.append(LEGACY_PROJECT_NAME)
    if re.search(re.escape(LEGACY_HIDDEN_DIR) + r"(?!p)", text, re.IGNORECASE):
        legacy_hits.append(LEGACY_HIDDEN_DIR)
    if re.search(r"\b" + re.escape(LEGACY_PROMPT_PREFIX), text, re.IGNORECASE):
        legacy_hits.append(LEGACY_PROMPT_PREFIX)
    if legacy_hits:
        report.add("LAUNCHER_NAMESPACE", "blocking", "fail", "Legacy pre-ACCP namespace found: " + ", ".join(sorted(set(legacy_hits))), location)
    else:
        report.add("LAUNCHER_NAMESPACE", "blocking", "pass", "Launcher uses OpenACCP namespace.", location)
    if re.search(r"(?m)^Read and execute this OpenACCP prompt record:\s*$", text):
        report.add("LAUNCHER_PROMPT_RECORD_PHRASE", "blocking", "pass", "Launcher uses the standard prompt-record instruction.", location)
    else:
        report.add("LAUNCHER_PROMPT_RECORD_PHRASE", "blocking", "fail", "Launcher must include `Read and execute this OpenACCP prompt record:`.", location)
    return title_match


def validate_launcher_text(
    text: str,
    report: Report,
    prompt_record_text: str | None = None,
    expected_prompt_id: str | None = None,
) -> None:
    title_match = validate_launcher_contract_text(text, report)
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
    slot = title_match.group("slot") if title_match else ""
    if is_child_launcher_slot(slot):
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
        block_title_match = validate_launcher_contract_text(block, report, loc)
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
        slot = block_title_match.group("slot") if block_title_match else ""
        if is_child_launcher_slot(slot):
            if re.search(r"(?i)fallback launcher|fallback only", block) and re.search(r"(?i)unavailable|unsafe|explicitly requested|separately user-managed", block):
                report.add("PROMPT_BLOCK_CHILD_FALLBACK", "blocking", "pass", "Child-role prompt block is explicitly marked as fallback.", loc)
            else:
                report.add(
                    "PROMPT_BLOCK_CHILD_FALLBACK",
                    "blocking",
                    "fail",
                    "Child worker/reviewer/discovery/validation prompt blocks must be fallback launchers with a direct-dispatch failure reason.",
                    loc,
                )


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


def _trailing_report_section_heading(text: str, pattern: str) -> str | None:
    headings = list(re.finditer(rf"(?im)^\s{{0,3}}#{{1,6}}\s*({pattern})\s*$", text))
    if not headings:
        return None
    last = headings[-1]
    after = text[last.end() :].strip()
    if not after:
        return None
    if re.search(r"(?im)^\s{0,3}#{1,6}\s+\S", after):
        return None
    return last.group(1).strip()


def _trailing_recommended_next_step_heading(text: str) -> str | None:
    return _trailing_report_section_heading(text, r"Recommended Next Step|\u4e0b\u4e00\u6b65\u5efa\u8bae")


def _has_heading(text: str, pattern: str) -> bool:
    return bool(re.search(rf"(?im)^\s{{0,3}}#{{1,6}}\s*(?:{pattern})\s*$", text))


def validate_formal_report_text(text: str, report: Report, preferred_language: str | None = None) -> None:
    response_ids = RESPONSE_ID_RE.findall(text)
    if not response_ids:
        report.add("RESPONSE_ID", "blocking", "fail", "Formal report must include Response ID.")
    else:
        report.add("RESPONSE_ID", "blocking", "pass", "Formal report includes Response ID.")
    if re.search(r"(?im)^\s*Response log path\s*:", text):
        report.add("RESPONSE_LOG_PATH", "blocking", "pass", "Formal report names a response log path.")
    else:
        report.add("RESPONSE_LOG_PATH", "blocking", "fail", "Formal report must include a Response log path line.")
    rows, header = parse_formal_table(text, report)
    preferred = (preferred_language or "").strip().lower()
    wants_chinese = preferred in {"chinese", "zh", "zh-cn", "\u4e2d\u6587"} or (header and header[0] == ZH_TYPE_STATUS)

    if header in FORMAL_HEADERS:
        report.add("FORMAL_HEADER", "blocking", "pass", "Formal report uses the standard Item/Status or 类型和状态 header.")
    else:
        report.add("FORMAL_HEADER", "blocking", "fail", "Formal report must use `| Item/Status | Content |` or `| 类型和状态 | 内容 |`.")
    labels = [label for label, _ in rows]
    if any(labels == required for required in FORMAL_ROW_SEQUENCES):
        report.add("FORMAL_ROWS", "blocking", "pass", "Formal report has an exact role-aware row set in the required order.")
    else:
        report.add("FORMAL_ROWS", "blocking", "fail", "Formal report rows must exactly match a known OpenACCP row set in order, with no extra rows.")
    bad_labels = set(labels).intersection({"What changed", "Lane or area", "Next step", "Validation", "Checkpoint", "Skill", "CLI", "\u5b89\u88c5", ZH_ITEM, ZH_FIELD})
    if bad_labels:
        report.add("LEGACY_ROW_LABELS", "blocking", "fail", "Legacy or overlong row labels found: " + ", ".join(sorted(bad_labels)))
    else:
        report.add("LEGACY_ROW_LABELS", "blocking", "pass", "No legacy long row labels found.")
    progress_cells = [right for label, right in rows if label in {"Progress", ZH_PROGRESS}]
    if progress_cells and any(re.search(r"\d+\s*%", cell) for cell in progress_cells):
        report.add("PROGRESS_PERCENT", "blocking", "pass", "Progress row includes a numeric estimate.")
    else:
        report.add("PROGRESS_PERCENT", "blocking", "fail", "Formal report progress row must include a numeric percentage.")
    has_english_evidence = _has_heading(text, r"Evidence and Validation|Basis")
    has_chinese_evidence = _has_heading(text, rf"{ZH_EVIDENCE_AND_VALIDATION}")
    has_legacy_english_evidence = _has_heading(text, r"Evidence Details")
    if wants_chinese and has_legacy_english_evidence:
        report.add("EVIDENCE_DETAILS", "blocking", "fail", "Chinese formal reports must use `依据与验证`, not `Evidence Details`.")
    elif wants_chinese and has_chinese_evidence:
        report.add("EVIDENCE_DETAILS", "blocking", "pass", "Chinese formal report includes `依据与验证` outside the table.")
    elif wants_chinese:
        report.add("EVIDENCE_DETAILS", "blocking", "fail", "Chinese formal reports must include `依据与验证` outside the table.")
    elif has_english_evidence:
        report.add("EVIDENCE_DETAILS", "blocking", "pass", "Formal report includes evidence or basis details outside the table.")
    else:
        report.add("EVIDENCE_DETAILS", "blocking", "fail", "Formal report must include Evidence and Validation or basis outside the table.")
    trailing_next_step = _trailing_recommended_next_step_heading(text)
    has_legacy_next_step = _has_heading(text, r"Human Next Step|\u7ed9\u4eba\u7684\u4e0b\u4e00\u6b65")
    if wants_chinese and trailing_next_step == ZH_RECOMMENDED_NEXT_STEP:
        report.add("HUMAN_NEXT_STEP_SUMMARY", "blocking", "pass", "Formal report ends with a human-readable next-step section.")
    elif wants_chinese and has_legacy_next_step:
        report.add("HUMAN_NEXT_STEP_SUMMARY", "blocking", "fail", "Chinese formal reports must use `下一步建议`, not `给人的下一步`.")
    elif wants_chinese and trailing_next_step:
        report.add("HUMAN_NEXT_STEP_SUMMARY", "blocking", "fail", "Chinese formal reports must end with `下一步建议`.")
    elif wants_chinese:
        report.add("HUMAN_NEXT_STEP_SUMMARY", "blocking", "fail", "Chinese formal reports must end with a `下一步建议` section.")
    elif trailing_next_step == "Recommended Next Step":
        report.add("HUMAN_NEXT_STEP_SUMMARY", "blocking", "pass", "Formal report ends with a human-readable next-step section.")
    elif re.search(r"(?i)Recommended Next Step|recommended next step|what happens next|Human Next Step|human next step", text):
        report.add("HUMAN_NEXT_STEP_SUMMARY", "blocking", "fail", "Recommended Next Step must be the final report section.")
    else:
        report.add("HUMAN_NEXT_STEP_SUMMARY", "blocking", "fail", "Formal reports must end with a human-readable next-step section.")
    if (
        re.search(r"```(?:powershell|pwsh|bash|sh|shell|cmd)\b", text, re.IGNORECASE)
        or re.search(r"(?i)\bPowerShell\b|\bcommands?\s+(?:include|passed)\b|\u9a8c\u8bc1\u901a\u8fc7\u7684\u547d\u4ee4", text)
        or re.search(r"(?im)^\s*(?:[-*]\s*)?(?:python|openaccp|openaccp-validate|pip|git)\s+[-A-Za-z0-9_.\\/]", text)
        or re.search(r"`\s*(?:python|openaccp|openaccp-validate|pip|git)\b[^`]*`", text, re.IGNORECASE)
        or re.search(r"(?im)^\s*(?:[-*]\s*)?(?:validation|verify|check|run|command|commands|validated)\s*:\s*`?(?:python|openaccp|openaccp-validate|pip|git)\b", text)
    ):
        report.add("FORMAL_REPORT_NO_COMMAND_DUMP", "blocking", "fail", "Formal reports must not include shell command blocks or command dumps; summarize validation status instead.")
    else:
        report.add("FORMAL_REPORT_NO_COMMAND_DUMP", "blocking", "pass", "No shell command dump found in formal report.")
    if wants_chinese and header and header[0] != ZH_TYPE_STATUS:
        report.add("PREFERRED_LANGUAGE_HEADER", "blocking", "fail", "Chinese reports must use the Chinese formal-report header.")
    elif wants_chinese:
        report.add("PREFERRED_LANGUAGE_HEADER", "blocking", "pass", "Chinese report uses the Chinese formal-report header.")
    if re.search(r"</?\s*nobr\b", text, re.IGNORECASE):
        report.add("FORMAL_REPORT_NO_HTML_NOWRAP", "blocking", "fail", "Formal reports must not use <nobr> or HTML no-wrap wrappers.")
    else:
        report.add("FORMAL_REPORT_NO_HTML_NOWRAP", "blocking", "pass", "Formal report does not use HTML no-wrap wrappers.")
    if wants_chinese or any(_has_cjk(label) for label in labels):
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
    required_terms = [
        "gapDecisionMatrix",
        "branchReturnGate",
        "worktreeDecision",
        "runtimeBoundaryRef",
        "laneRegistryRef",
        "childLedgerRef",
        "frontierClosureRef",
    ]
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
    early_return_lines = find_frontier_early_return_antipatterns(text)
    if early_return_lines:
        report.add(
            "FRONTIER_EARLY_RETURN_ANTIPATTERN",
            "blocking",
            "fail",
            "Frontier early-return anti-pattern found: " + " | ".join(early_return_lines[:3]),
        )
    else:
        report.add("FRONTIER_EARLY_RETURN_ANTIPATTERN", "blocking", "pass", "No Frontier early-return anti-pattern found.")
    if re.search(r"(?i)child ledger", text) and all(term in text for term in ["promptId", "taskId", "dispatchStatus", "handoffStatus"]):
        report.add("FRONTIER_CHILD_LEDGER", "blocking", "pass", "Frontier contract requires child ledger identifiers and lifecycle status.")
    else:
        report.add("FRONTIER_CHILD_LEDGER", "blocking", "fail", "Frontier contract must require a child ledger with promptId, taskId, dispatchStatus, and handoffStatus.")
    if re.search(r"(?is)(?:every|all)\s+Frontier\s+repl(?:y|ies).{0,160}(?:end|finish).{0,160}(?:recommended\s+next\s+step|\u4e0b\u4e00\u6b65\u5efa\u8bae)", text) or re.search(
        r"(?is)(?:end|finish).{0,160}(?:every|all)\s+Frontier\s+repl(?:y|ies).{0,160}(?:recommended\s+next\s+step|\u4e0b\u4e00\u6b65\u5efa\u8bae)",
        text,
    ):
        report.add("FRONTIER_HUMAN_NEXT_STEP", "blocking", "pass", "Frontier contract requires every Frontier reply to end with a recommended next-step paragraph.")
    else:
        report.add("FRONTIER_HUMAN_NEXT_STEP", "blocking", "fail", "Frontier contract must require every Frontier reply to end with a recommended next-step paragraph.")
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
    if "human-explain-openaccp" in text and "formal-report-openaccp" in text:
        report.add("FRONTIER_REPORTING", "blocking", "pass", "Frontier contract requires human explanation and formal reports.")
    else:
        report.add("FRONTIER_REPORTING", "blocking", "fail", "Frontier contract must require human-explain-openaccp and formal-report-openaccp.")
    validate_frontier_contract_block(text, report)


def validate_frontier_contract_block(text: str, report: Report) -> None:
    blocks = extract_json_fence_objects(text)
    contracts = [
        block
        for block in blocks
        if block.get("schemaVersion") == "openaccp-frontier-orchestration-contract.v1"
        or block.get("artifactType") == "frontier-orchestration-contract"
    ]
    if not contracts:
        report.add(
            "FRONTIER_CONTRACT_BLOCK",
            "blocking",
            "fail",
            "Frontier contract must include a JSON block with schemaVersion openaccp-frontier-orchestration-contract.v1.",
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
        "coordinationRefs",
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
    coordination_refs = contract.get("coordinationRefs")
    if not isinstance(coordination_refs, dict):
        report.add("FRONTIER_CONTRACT_COORDINATION_REFS", "blocking", "fail", "coordinationRefs must be an object.")
    else:
        missing_refs = [
            field
            for field in ["runtimeBoundaryRef", "laneRegistryRef", "childLedgerRef", "frontierClosureRef"]
            if not str(coordination_refs.get(field, "")).strip()
        ]
        if missing_refs:
            report.add("FRONTIER_CONTRACT_COORDINATION_REFS", "blocking", "fail", "coordinationRefs missing refs: " + ", ".join(missing_refs))
        else:
            report.add("FRONTIER_CONTRACT_COORDINATION_REFS", "blocking", "pass", "coordinationRefs names runtime, lane, child-ledger, and closure refs.")
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
        report.add("FRONTIER_GAP_DECISIONS", "blocking", "pass", "gapDecisionMatrix has the full OpenACCP decision vocabulary.")
    subagent_first = contract.get("subagentFirst")
    if subagent_first is True or (isinstance(subagent_first, dict) and subagent_first.get("enabled") is True):
        report.add("FRONTIER_CONTRACT_SUBAGENT_FIRST", "blocking", "pass", "Contract enables subagent-first dispatch.")
    else:
        report.add("FRONTIER_CONTRACT_SUBAGENT_FIRST", "blocking", "fail", "Contract must set subagentFirst true or {enabled: true}.")
    child_ledger = contract.get("childLedger", {})
    ledger_fields = set(child_ledger.get("requiredFields", [])) if isinstance(child_ledger, dict) and isinstance(child_ledger.get("requiredFields"), list) else set()
    ledger_required = {"promptId", "taskId", "role", "authority", "effects", "dispatchStatus", "handoffStatus", "consumeStatus"}
    missing_ledger = sorted(ledger_required - ledger_fields)
    if missing_ledger:
        report.add("FRONTIER_CONTRACT_CHILD_LEDGER", "blocking", "fail", "childLedger missing fields: " + ", ".join(missing_ledger))
    else:
        report.add("FRONTIER_CONTRACT_CHILD_LEDGER", "blocking", "pass", "childLedger carries stable child identifiers and lifecycle status.")
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


def find_frontier_early_return_antipatterns(text: str) -> list[str]:
    hits: list[str] = []
    early_return_patterns = [
        r"(?i)(?:after|once)\s+(?:writing|creating|preparing|finishing).{0,80}(?:packet|prompt|handoff|baseline|matrix).{0,80}(?:return|hand\s*back|send).{0,40}Primary",
        r"(?i)(?:return|hand\s*back|send).{0,40}Primary.{0,80}(?:after|once).{0,80}(?:packet|prompt|handoff|baseline|matrix)",
        r"(?i)Frontier-safe work exhausted",
        r"(?i)(?:blocked on Primary|blocked_on_primary).{0,140}(?:do_now|dispatch_current_thread_subagent|prepare_package|apply_conservative_default)",
    ]
    safe_context = re.compile(
        r"(?i)(?:do\s+not|must\s+not|only\s+when|valid\s+only|return\s+gate|branchReturnGate|remaining\s+gaps)",
    )
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or safe_context.search(line):
            continue
        if any(re.search(pattern, line) for pattern in early_return_patterns):
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
    if str(data.get("parentCardId", "")).strip() or isinstance(data.get("cardRefs"), list):
        report.add("TASK_CARD_PARENT_CARD", "blocking", "pass", "Task card links back to a parent CARD.")
    else:
        report.add("TASK_CARD_PARENT_CARD", "blocking", "fail", "Task card must include parentCardId or cardRefs.")
    if str(data.get("domain", "")).strip():
        report.add("TASK_CARD_DOMAIN", "blocking", "pass", "Task card names its product or coordination domain.")
    else:
        report.add("TASK_CARD_DOMAIN", "blocking", "fail", "Task card must include a domain for CARD traceability.")
    if str(data.get("sourceStatusNote", "")).strip():
        report.add("TASK_CARD_SOURCE_STATUS_NOTE", "blocking", "pass", "Task card includes a source status note.")
    else:
        report.add("TASK_CARD_SOURCE_STATUS_NOTE", "warning", "fail", "Task card should include sourceStatusNote for source traceability.")
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


def validate_role_authority(role: Any, authority: Any, report: Report, check_name: str, location: str) -> None:
    if role not in ROLE_MAX_AUTHORITY or authority not in AUTHORITY_RANK:
        return
    max_authority = ROLE_MAX_AUTHORITY[str(role)]
    if AUTHORITY_RANK[str(authority)] > AUTHORITY_RANK[max_authority]:
        report.add(check_name, "blocking", "fail", f"{role} authority must not exceed {max_authority}.", location)
    else:
        report.add(check_name, "blocking", "pass", f"{role} authority is within {max_authority}.", location)


def validate_authority_charter(data: dict[str, Any], report: Report) -> None:
    if data.get("grantedRole") not in ROLES:
        report.add("GRANTED_ROLE", "blocking", "fail", "grantedRole is not a known OpenACCP role.")
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
    validate_role_authority(data.get("grantedRole"), data.get("authorityLevel"), report, "ROLE_AUTHORITY_MATRIX", "authority-charter")
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
        "sequenceRegistryRef",
        "laneRegistryRef",
        "runtimeBoundaryRef",
        "sourceStatusRegistryRef",
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
            report.add("ACTIVE_LANE_ROLE", "blocking", "fail", "active lane role must be a known OpenACCP role.", loc)
        if lane.get("authorityLevel") not in AUTHORITY_LEVELS:
            report.add("ACTIVE_LANE_AUTHORITY", "blocking", "fail", "active lane authorityLevel must be B0, B1, B2, or B3.", loc)
        validate_role_authority(lane.get("role"), lane.get("authorityLevel"), report, "ACTIVE_LANE_ROLE_AUTHORITY", loc)
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
        "sequenceRegistryRef",
        "laneRegistryRef",
        "runtimeBoundaryRef",
        "sourceStatusRegistryRef",
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
    lifecycle_statuses = {"created", "startup_provided", "dispatched", "returned", "consumed", "superseded", "cancelled", "invalid", "active", "complete", "present"}
    for collection_name, id_field in [("prompts", "promptId"), ("responses", "responseId"), ("handoffs", "handoffId")]:
        for idx, item in enumerate(data.get(collection_name, [])):
            loc = f"{collection_name}[{idx}]"
            if not isinstance(item, dict):
                continue
            required_item_fields = {
                "prompts": ["promptId", "path", "role", "status"],
                "responses": ["responseId", "promptId", "path", "status"],
                "handoffs": ["handoffId", "taskId", "path", "status"],
            }[collection_name]
            missing_item_fields = [field for field in required_item_fields if field not in item or not str(item.get(field, "")).strip()]
            if missing_item_fields:
                report.add("SEQUENCE_LOCATOR_FIELDS", "blocking", "fail", f"{collection_name} entry missing locator fields: " + ", ".join(missing_item_fields), loc)
            status = item.get("status")
            if status not in lifecycle_statuses:
                report.add("SEQUENCE_LIFECYCLE_STATUS", "blocking", "fail", f"{collection_name} status is invalid.", loc)
            if status == "superseded" and not str(item.get("supersededBy", "")).strip():
                report.add("SEQUENCE_SUPERSEDED_BY", "blocking", "fail", f"{collection_name} superseded entries require supersededBy.", loc)
            if status == "invalid" and not str(item.get("invalidReason", "")).strip():
                report.add("SEQUENCE_INVALID_REASON", "blocking", "fail", f"{collection_name} invalid entries require invalidReason.", loc)
            if id_field not in item:
                report.add("SEQUENCE_ID_FIELD", "blocking", "fail", f"{collection_name} entry missing {id_field}.", loc)
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
        missing_lane_fields = [field for field in ["laneId", "role", "status", "currentPromptId", "authorityLevel"] if field not in lane]
        if missing_lane_fields:
            report.add("SEQ_ACTIVE_LANE_FIELDS", "blocking", "fail", "active lane missing fields: " + ", ".join(missing_lane_fields), loc)
        if lane.get("role") not in ROLES:
            report.add("SEQ_ACTIVE_LANE_ROLE", "blocking", "fail", "active lane role must be a known OpenACCP role.", loc)
        if lane.get("authorityLevel") not in AUTHORITY_LEVELS:
            report.add("SEQ_ACTIVE_LANE_AUTHORITY", "blocking", "fail", "active lane authorityLevel must be B0, B1, B2, or B3.", loc)
        validate_role_authority(lane.get("role"), lane.get("authorityLevel"), report, "SEQ_ACTIVE_LANE_ROLE_AUTHORITY", loc)
        current_prompt = lane.get("currentPromptId")
        if current_prompt and current_prompt not in prompt_ids:
            report.add("SEQ_ACTIVE_LANE_PROMPT", "blocking", "fail", "active lane currentPromptId is not registered.", loc)


def validate_consume_result(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "consume-result":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be consume-result.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is consume-result.")
    if data.get("consumerRole") not in ROLES:
        report.add("CONSUMER_ROLE", "blocking", "fail", "consumerRole is not a known OpenACCP role.")
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
        report.add("SUMMARY_ROLE", "blocking", "fail", "role is not a known OpenACCP role.")
    else:
        report.add("SUMMARY_ROLE", "blocking", "pass", "role is valid.")
    if data.get("authority") not in AUTHORITY_LEVELS:
        report.add("SUMMARY_AUTHORITY", "blocking", "fail", "authority must be B0, B1, B2, or B3.")
    else:
        report.add("SUMMARY_AUTHORITY", "blocking", "pass", "authority is valid.")
    validate_role_authority(data.get("role"), data.get("authority"), report, "SUMMARY_ROLE_AUTHORITY", "machine-summary")
    if data.get("effectsPreset") not in EFFECTS_PRESETS:
        report.add("SUMMARY_EFFECTS_PRESET", "blocking", "fail", "effectsPreset is not a known OpenACCP effects preset.")
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


def validate_runtime_boundary(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "runtime-boundary":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be runtime-boundary.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is runtime-boundary.")
    product_statuses = {"found", "provided", "missing", "not_applicable"}
    if data.get("productRepoStatus") not in product_statuses:
        report.add("PRODUCT_REPO_STATUS", "blocking", "fail", "productRepoStatus must be found, provided, missing, or not_applicable.")
    else:
        report.add("PRODUCT_REPO_STATUS", "blocking", "pass", "productRepoStatus is valid.")
    if data.get("productRepoStatus") in {"found", "provided"} and not str(data.get("productRepoPath", "")).strip():
        report.add("PRODUCT_REPO_PATH", "blocking", "fail", "found/provided product repos require productRepoPath.")
    else:
        report.add("PRODUCT_REPO_PATH", "blocking", "pass", "productRepoPath is compatible with productRepoStatus.")
    if data.get("worktreePolicy") not in {"allowed", "forbidden", "unknown"}:
        report.add("WORKTREE_POLICY", "blocking", "fail", "worktreePolicy must be allowed, forbidden, or unknown.")
    else:
        report.add("WORKTREE_POLICY", "blocking", "pass", "worktreePolicy is valid.")
    if data.get("externalSideEffects") not in {"none", "local_only", "requires_approval"}:
        report.add("EXTERNAL_SIDE_EFFECTS", "blocking", "fail", "externalSideEffects must be none, local_only, or requires_approval.")
    else:
        report.add("EXTERNAL_SIDE_EFFECTS", "blocking", "pass", "externalSideEffects is valid.")
    if data.get("dataRisk") not in DATA_RISK_LEVELS:
        report.add("DATA_RISK", "blocking", "fail", "dataRisk must be none, low, medium, high, or sensitive.")
    else:
        report.add("DATA_RISK", "blocking", "pass", "dataRisk is valid.")
    for field_name in ["sourceRoots", "testEntrypoints", "allowedWritablePaths", "readOnlyPaths", "forbiddenPaths", "unresolvedOwnerInputs"]:
        if isinstance(data.get(field_name), list):
            report.add(f"{field_name.upper()}_ARRAY", "blocking", "pass", f"{field_name} is an array.")
        else:
            report.add(f"{field_name.upper()}_ARRAY", "blocking", "fail", f"{field_name} must be an array.")
    gate = data.get("b2DispatchGate")
    if not isinstance(gate, dict):
        report.add("B2_DISPATCH_GATE_OBJECT", "blocking", "fail", "b2DispatchGate must be an object.")
        return
    report.add("B2_DISPATCH_GATE_OBJECT", "blocking", "pass", "b2DispatchGate is an object.")
    required_gate = ["state", "allowsProductWrite", "reason", "missingInputs"]
    missing_gate = [field for field in required_gate if field not in gate]
    if missing_gate:
        report.add("B2_DISPATCH_GATE_FIELDS", "blocking", "fail", "b2DispatchGate missing fields: " + ", ".join(missing_gate))
    else:
        report.add("B2_DISPATCH_GATE_FIELDS", "blocking", "pass", "b2DispatchGate has required fields.")
    if gate.get("state") not in {"ready", "coordination_only", "blocked", "not_applicable"}:
        report.add("B2_DISPATCH_GATE_STATE", "blocking", "fail", "b2DispatchGate.state must be ready, coordination_only, blocked, or not_applicable.")
    if not isinstance(gate.get("allowsProductWrite"), bool):
        report.add("B2_DISPATCH_GATE_PRODUCT_WRITE", "blocking", "fail", "b2DispatchGate.allowsProductWrite must be boolean.")
    if not str(gate.get("reason", "")).strip():
        report.add("B2_DISPATCH_GATE_REASON", "blocking", "fail", "b2DispatchGate.reason must explain the gate state.")
    if not isinstance(gate.get("missingInputs"), list):
        report.add("B2_DISPATCH_GATE_MISSING_INPUTS", "blocking", "fail", "b2DispatchGate.missingInputs must be an array.")
    ready_for_product_write = gate.get("state") == "ready" or gate.get("allowsProductWrite") is True
    missing_runtime = []
    if data.get("productRepoStatus") not in {"found", "provided"}:
        missing_runtime.append("productRepoStatus")
    if not str(data.get("productRepoPath", "")).strip():
        missing_runtime.append("productRepoPath")
    if not str(data.get("baseBranch", "")).strip():
        missing_runtime.append("baseBranch")
    if not data.get("sourceRoots"):
        missing_runtime.append("sourceRoots")
    if not data.get("testEntrypoints"):
        missing_runtime.append("testEntrypoints")
    if data.get("worktreePolicy") == "unknown":
        missing_runtime.append("worktreePolicy")
    if ready_for_product_write and missing_runtime:
        report.add("B2_PRODUCT_WRITE_RUNTIME_READY", "blocking", "fail", "B2 product-write dispatch requires runtime fields: " + ", ".join(missing_runtime))
    elif ready_for_product_write:
        report.add("B2_PRODUCT_WRITE_RUNTIME_READY", "blocking", "pass", "B2 product-write runtime fields are ready.")
    else:
        report.add("B2_PRODUCT_WRITE_RUNTIME_READY", "blocking", "pass", "B2 product-write is not allowed by this runtime boundary.")


def validate_lane_registry(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "lane-registry":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be lane-registry.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is lane-registry.")
    lanes = data.get("lanes")
    if not isinstance(lanes, list) or not lanes:
        report.add("LANES_NON_EMPTY", "blocking", "fail", "lanes must be a non-empty array.")
        return
    report.add("LANES_NON_EMPTY", "blocking", "pass", "lanes is non-empty.")
    validate_lane_registry_dispatch_policy(data, lanes, report)
    statuses = {"prepared", "active", "open", "closed", "blocked_on_primary", "blocked_on_human", "cancelled"}
    for idx, lane in enumerate(lanes):
        loc = f"lanes[{idx}]"
        if not isinstance(lane, dict):
            report.add("LANE_OBJECT", "blocking", "fail", "lane must be an object.", loc)
            continue
        required = [
            "laneId",
            "objective",
            "role",
            "status",
            "currentPromptId",
            "authorityLevel",
            "assignedCardIds",
            "runtimeBoundaryRef",
            "childLedgerRef",
            "latestConsumeRefs",
            "returnGateStatus",
            "b2DispatchGate",
        ]
        missing = [field for field in required if field not in lane]
        if missing:
            report.add("LANE_REQUIRED_FIELDS", "blocking", "fail", "lane missing fields: " + ", ".join(missing), loc)
        else:
            report.add("LANE_REQUIRED_FIELDS", "blocking", "pass", "lane has required fields.", loc)
        if lane.get("role") not in {"primary", "frontier"}:
            report.add("LANE_ROLE", "blocking", "fail", "lane role must be primary or frontier.", loc)
        if lane.get("authorityLevel") not in AUTHORITY_LEVELS:
            report.add("LANE_AUTHORITY", "blocking", "fail", "lane authorityLevel must be B0, B1, B2, or B3.", loc)
        validate_role_authority(lane.get("role"), lane.get("authorityLevel"), report, "LANE_ROLE_AUTHORITY", loc)
        if lane.get("status") not in statuses:
            report.add("LANE_STATUS", "blocking", "fail", "lane status is not a known OpenACCP lane status.", loc)
        if not isinstance(lane.get("assignedCardIds"), list) or not lane.get("assignedCardIds"):
            report.add("LANE_ASSIGNED_CARDS", "blocking", "fail", "lane assignedCardIds must be non-empty.", loc)
        validate_lane_b2_dispatch_gate(lane, report, loc)
        return_gate = lane.get("returnGateStatus")
        if not isinstance(return_gate, dict):
            report.add("LANE_RETURN_GATE_OBJECT", "blocking", "fail", "lane returnGateStatus must be an object.", loc)
            continue
        required_gate = [
            "state",
            "safeWorkRemainingCount",
            "finalAuthorityGapCount",
            "explicitlyOutCount",
            "frontierClosureRef",
            "latestChildLedgerRef",
            "latestConsumeRefs",
        ]
        missing_gate = [field for field in required_gate if field not in return_gate]
        if missing_gate:
            report.add("LANE_RETURN_GATE_FIELDS", "blocking", "fail", "returnGateStatus missing fields: " + ", ".join(missing_gate), loc)
        else:
            report.add("LANE_RETURN_GATE_FIELDS", "blocking", "pass", "returnGateStatus has required fields.", loc)
        if return_gate.get("state") not in {"not_applicable", "not_ready", "ready_for_primary", "closed", "blocked_on_human"}:
            report.add("LANE_RETURN_GATE_STATE", "blocking", "fail", "returnGateStatus.state is invalid.", loc)
        for count_field in ["safeWorkRemainingCount", "finalAuthorityGapCount", "explicitlyOutCount"]:
            count_value = return_gate.get(count_field)
            if not isinstance(count_value, int) or count_value < 0:
                report.add("LANE_RETURN_GATE_COUNTS", "blocking", "fail", f"{count_field} must be a non-negative integer.", loc)
        if not isinstance(return_gate.get("latestConsumeRefs"), list):
            report.add("LANE_RETURN_GATE_CONSUMES", "blocking", "fail", "returnGateStatus.latestConsumeRefs must be an array.", loc)
        validate_lane_return_gate_consistency(lane, return_gate, report, loc)


def validate_lane_registry_dispatch_policy(data: dict[str, Any], lanes: list[Any], report: Report) -> None:
    complexity = str(data.get("projectComplexity", "")).strip().lower()
    mode = str(data.get("frontierDispatchMode", "")).strip().lower()
    reason = str(data.get("frontierDispatchReason", "")).strip()
    valid_complexities = {"bootstrap", "small", "normal", "medium", "medium-high", "high", "unknown"}
    valid_modes = {"pre_frontier", "single_frontier", "multi_frontier"}
    if complexity not in valid_complexities:
        report.add("LANE_DISPATCH_POLICY_COMPLEXITY", "blocking", "fail", "projectComplexity must be bootstrap, small, normal, medium, medium-high, high, or unknown.")
    else:
        report.add("LANE_DISPATCH_POLICY_COMPLEXITY", "blocking", "pass", "projectComplexity is recorded.")
    if mode not in valid_modes:
        report.add("LANE_DISPATCH_POLICY_MODE", "blocking", "fail", "frontierDispatchMode must be pre_frontier, single_frontier, or multi_frontier.")
        return
    if not reason:
        report.add("LANE_DISPATCH_POLICY_REASON", "blocking", "fail", "frontierDispatchReason must explain the lane count decision.")
    else:
        report.add("LANE_DISPATCH_POLICY_REASON", "blocking", "pass", "frontierDispatchReason is recorded.")
    frontier_count = sum(1 for lane in lanes if isinstance(lane, dict) and lane.get("role") == "frontier" and lane.get("status") != "cancelled")
    if mode == "pre_frontier":
        if frontier_count != 0:
            report.add("LANE_DISPATCH_POLICY_COUNT", "blocking", "fail", "pre_frontier lane registry should not contain active Frontier lanes.")
        else:
            report.add("LANE_DISPATCH_POLICY_COUNT", "blocking", "pass", "pre_frontier registry has no Frontier lanes yet.")
        return
    if mode == "single_frontier":
        single_reason_ok = bool(re.search(r"(?i)\b(small|single[- ]safe[- ]lane|single safe lane|explicit user request|user requested one)\b", reason))
        if frontier_count != 1:
            report.add("LANE_DISPATCH_POLICY_COUNT", "blocking", "fail", "single_frontier mode requires exactly one Frontier lane.")
        elif complexity not in {"small", "unknown"} and not single_reason_ok:
            report.add("LANE_DISPATCH_POLICY_COUNT", "blocking", "fail", "single Frontier for non-small projects requires a single-safe-lane or explicit-user-request reason.")
        elif not single_reason_ok:
            report.add("LANE_DISPATCH_POLICY_COUNT", "blocking", "fail", "single_frontier mode requires a small-project, single-safe-lane, or explicit-user-request reason.")
        else:
            report.add("LANE_DISPATCH_POLICY_COUNT", "blocking", "pass", "single Frontier mode has an explicit exception reason.")
        return
    if mode == "multi_frontier":
        if 2 <= frontier_count <= 5:
            report.add("LANE_DISPATCH_POLICY_COUNT", "blocking", "pass", f"multi_frontier mode has {frontier_count} Frontier lanes.")
        else:
            report.add("LANE_DISPATCH_POLICY_COUNT", "blocking", "fail", f"multi_frontier mode requires 2-5 Frontier lanes; found {frontier_count}.")


def validate_lane_b2_dispatch_gate(lane: dict[str, Any], report: Report, loc: str) -> None:
    gate = lane.get("b2DispatchGate")
    if not isinstance(gate, dict):
        report.add("LANE_B2_DISPATCH_GATE", "blocking", "fail", "lane b2DispatchGate must be an object.", loc)
        return
    required = ["mode", "state", "reason"]
    missing = [field for field in required if field not in gate or not str(gate.get(field, "")).strip()]
    if missing:
        report.add("LANE_B2_DISPATCH_GATE_FIELDS", "blocking", "fail", "b2DispatchGate missing fields: " + ", ".join(missing), loc)
    else:
        report.add("LANE_B2_DISPATCH_GATE_FIELDS", "blocking", "pass", "b2DispatchGate has required fields.", loc)
    mode = gate.get("mode")
    state = gate.get("state")
    if mode not in {"coordination_only", "read_only_review", "product_write"}:
        report.add("LANE_B2_DISPATCH_GATE_MODE", "blocking", "fail", "b2DispatchGate.mode must be coordination_only, read_only_review, or product_write.", loc)
    if state not in {"ready", "not_ready", "not_applicable"}:
        report.add("LANE_B2_DISPATCH_GATE_STATE", "blocking", "fail", "b2DispatchGate.state must be ready, not_ready, or not_applicable.", loc)
    if lane.get("authorityLevel") == "B2" and mode == "product_write":
        if state != "ready":
            report.add("LANE_B2_PRODUCT_WRITE_GATE", "blocking", "fail", "B2 product_write lanes require b2DispatchGate.state ready.", loc)
            return
        runtime_ref = lane.get("runtimeBoundaryRef")
        runtime_path = resolve_ref(Path(report.artifact).parent, str(runtime_ref))
        runtime_report = Report(str(runtime_path), "runtime-boundary")
        runtime_data = load_json(runtime_path, runtime_report) if runtime_path.exists() else None
        if not isinstance(runtime_data, dict):
            report.add("LANE_B2_PRODUCT_WRITE_RUNTIME_REF", "blocking", "fail", "B2 product_write lane requires a readable runtimeBoundaryRef.", str(runtime_path))
            return
        runtime_gate = runtime_data.get("b2DispatchGate")
        if not isinstance(runtime_gate, dict) or runtime_gate.get("state") != "ready" or runtime_gate.get("allowsProductWrite") is not True:
            report.add("LANE_B2_PRODUCT_WRITE_RUNTIME_GATE", "blocking", "fail", "B2 product_write lane requires runtime b2DispatchGate ready with allowsProductWrite true.", str(runtime_path))
        else:
            report.add("LANE_B2_PRODUCT_WRITE_RUNTIME_GATE", "blocking", "pass", "B2 product_write lane is backed by a ready runtime boundary.", str(runtime_path))
    elif lane.get("authorityLevel") == "B2":
        report.add("LANE_B2_PRODUCT_WRITE_GATE", "blocking", "pass", "B2 lane is not allowed to write product code by this lane gate.", loc)


def validate_lane_return_gate_consistency(lane: dict[str, Any], return_gate: dict[str, Any], report: Report, loc: str) -> None:
    status = lane.get("status")
    state = return_gate.get("state")
    safe_count = return_gate.get("safeWorkRemainingCount")
    final_count = return_gate.get("finalAuthorityGapCount")
    closure_ref = str(return_gate.get("frontierClosureRef", "")).strip()
    if status == "blocked_on_primary":
        if state != "ready_for_primary":
            report.add("LANE_RETURN_GATE_CONSISTENCY", "blocking", "fail", "blocked_on_primary lanes require returnGateStatus.state ready_for_primary.", loc)
        elif safe_count != 0:
            report.add("LANE_RETURN_GATE_CONSISTENCY", "blocking", "fail", "blocked_on_primary lanes cannot have safeWorkRemainingCount > 0.", loc)
        elif not closure_ref:
            report.add("LANE_RETURN_GATE_CONSISTENCY", "blocking", "fail", "blocked_on_primary lanes require frontierClosureRef.", loc)
        else:
            report.add("LANE_RETURN_GATE_CONSISTENCY", "blocking", "pass", "blocked_on_primary lane has a consistent return gate.", loc)
    elif status == "closed":
        if state != "closed" or safe_count != 0 or final_count != 0:
            report.add("LANE_RETURN_GATE_CONSISTENCY", "blocking", "fail", "closed lanes require state closed with no safe or final-authority gaps.", loc)
        else:
            report.add("LANE_RETURN_GATE_CONSISTENCY", "blocking", "pass", "closed lane has a consistent return gate.", loc)
    elif status == "blocked_on_human":
        if state != "blocked_on_human" or safe_count != 0:
            report.add("LANE_RETURN_GATE_CONSISTENCY", "blocking", "fail", "blocked_on_human lanes require state blocked_on_human and no remaining safe work.", loc)
        else:
            report.add("LANE_RETURN_GATE_CONSISTENCY", "blocking", "pass", "blocked_on_human lane has a consistent return gate.", loc)
    elif state in {"ready_for_primary", "closed", "blocked_on_human"} and status in {"prepared", "active", "open"}:
        report.add("LANE_RETURN_GATE_CONSISTENCY", "warning", "fail", "open/prepared lanes should not carry terminal returnGateStatus.state.", loc)


def validate_child_ledger(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "child-ledger":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be child-ledger.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is child-ledger.")
    children = data.get("children")
    if not isinstance(children, list):
        report.add("CHILDREN_ARRAY", "blocking", "fail", "children must be an array.")
        return
    report.add("CHILDREN_ARRAY", "blocking", "pass", "children is an array.")
    dispatch_statuses = {"not_started", "startup_provided", "dispatched", "running", "returned", "failed", "cancelled"}
    handoff_statuses = {"not_expected", "not_started", "expected", "present", "missing", "invalid"}
    consume_statuses = {"not_applicable", "not_consumed", "consumed", "rejected"}
    for idx, child in enumerate(children):
        loc = f"children[{idx}]"
        if not isinstance(child, dict):
            report.add("CHILD_OBJECT", "blocking", "fail", "child must be an object.", loc)
            continue
        required = [
            "promptId",
            "taskId",
            "role",
            "authority",
            "effects",
            "subagentIdOrToolStatus",
            "expectedHandoffPath",
            "dispatchStatus",
            "handoffStatus",
            "consumeStatus",
            "remainingRisk",
        ]
        missing = [field for field in required if field not in child]
        if missing:
            report.add("CHILD_REQUIRED_FIELDS", "blocking", "fail", "child missing fields: " + ", ".join(missing), loc)
        else:
            report.add("CHILD_REQUIRED_FIELDS", "blocking", "pass", "child has required fields.", loc)
        if child.get("role") not in {"worker", "reviewer", "discovery", "validation", "task-card-only"}:
            report.add("CHILD_ROLE", "blocking", "fail", "child role is not a supported downstream role.", loc)
        if child.get("authority") not in AUTHORITY_LEVELS:
            report.add("CHILD_AUTHORITY", "blocking", "fail", "child authority must be B0, B1, B2, or B3.", loc)
        if child.get("authority") == "B3":
            report.add("CHILD_B3_FORBIDDEN", "blocking", "fail", "Frontier child work must not use B3 authority.", loc)
        if child.get("dispatchStatus") not in dispatch_statuses:
            report.add("CHILD_DISPATCH_STATUS", "blocking", "fail", "child dispatchStatus is invalid.", loc)
        if child.get("handoffStatus") not in handoff_statuses:
            report.add("CHILD_HANDOFF_STATUS", "blocking", "fail", "child handoffStatus is invalid.", loc)
        if child.get("consumeStatus") not in consume_statuses:
            report.add("CHILD_CONSUME_STATUS", "blocking", "fail", "child consumeStatus is invalid.", loc)
        if child.get("dispatchStatus") in {"returned", "failed", "cancelled"} and not str(child.get("responseId", "")).strip():
            report.add("CHILD_RESPONSE_ID_LIFECYCLE", "blocking", "fail", "returned, failed, or cancelled child entries must include responseId.", loc)
        if child.get("handoffStatus") == "present" and not str(child.get("handoffId", "")).strip():
            report.add("CHILD_HANDOFF_ID_LIFECYCLE", "blocking", "fail", "child entries with handoffStatus present must include handoffId.", loc)
        if child.get("handoffStatus") == "present" and child.get("consumeStatus") == "not_applicable":
            report.add("CHILD_CONSUME_LIFECYCLE", "blocking", "fail", "present handoffs must be consumed, rejected, or marked not_consumed.", loc)
        if child.get("fallbackLauncherReason") and child.get("dispatchStatus") not in {"not_started", "startup_provided"}:
            report.add("CHILD_FALLBACK_REASON", "blocking", "fail", "fallbackLauncherReason should only be used before direct dispatch succeeds.", loc)


def validate_source_status_registry(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "source-status-registry":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be source-status-registry.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is source-status-registry.")
    sources = data.get("sources")
    if not isinstance(sources, list):
        report.add("SOURCES_ARRAY", "blocking", "fail", "sources must be an array.")
        return
    report.add("SOURCES_ARRAY", "blocking", "pass", "sources is an array.")
    for idx, source in enumerate(sources):
        loc = f"sources[{idx}]"
        if not isinstance(source, dict):
            report.add("SOURCE_STATUS_OBJECT", "blocking", "fail", "source status entry must be an object.", loc)
            continue
        required = ["sourceId", "status", "reason", "authority", "locator", "lastReviewedAt"]
        missing = [field for field in required if field not in source]
        if missing:
            report.add("SOURCE_STATUS_FIELDS", "blocking", "fail", "source status missing fields: " + ", ".join(missing), loc)
        if source.get("status") not in SOURCE_REGISTRY_STATUSES:
            report.add("SOURCE_REGISTRY_STATUS", "blocking", "fail", "source status must be current, reference, deprecated, invalid, or unknown.", loc)
        if source.get("status") in {"deprecated", "invalid", "unknown"} and not str(source.get("reason", "")).strip():
            report.add("SOURCE_STATUS_REASON", "blocking", "fail", "deprecated, invalid, and unknown sources require a reason.", loc)


def validate_decision_registry(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "decision-registry":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be decision-registry.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is decision-registry.")
    decisions = data.get("decisions")
    if not isinstance(decisions, list):
        report.add("DECISIONS_ARRAY", "blocking", "fail", "decisions must be an array.")
        return
    report.add("DECISIONS_ARRAY", "blocking", "pass", "decisions is an array.")
    types = {"owner-question", "primary-decision", "waiver", "out-of-scope"}
    statuses = {"open", "answered", "superseded", "rejected"}
    for idx, decision in enumerate(decisions):
        loc = f"decisions[{idx}]"
        if not isinstance(decision, dict):
            report.add("DECISION_OBJECT", "blocking", "fail", "decision must be an object.", loc)
            continue
        required = ["decisionId", "type", "status", "question", "basisRefs", "blocks", "safeDefault", "authorityRequired"]
        missing = [field for field in required if field not in decision]
        if missing:
            report.add("DECISION_FIELDS", "blocking", "fail", "decision missing fields: " + ", ".join(missing), loc)
        if decision.get("type") not in types:
            report.add("DECISION_TYPE", "blocking", "fail", "decision type is invalid.", loc)
        if decision.get("status") not in statuses:
            report.add("DECISION_STATUS", "blocking", "fail", "decision status is invalid.", loc)
        if decision.get("authorityRequired") not in AUTHORITY_LEVELS:
            report.add("DECISION_AUTHORITY", "blocking", "fail", "decision authorityRequired must be B0, B1, B2, or B3.", loc)
        for field_name in ["basisRefs", "blocks"]:
            if not isinstance(decision.get(field_name), list):
                report.add("DECISION_ARRAY_FIELDS", "blocking", "fail", f"{field_name} must be an array.", loc)


def validate_frontier_closure(data: dict[str, Any], report: Report) -> None:
    if data.get("artifactType") != "frontier-closure":
        report.add("ARTIFACT_TYPE", "blocking", "fail", "artifactType must be frontier-closure.")
    else:
        report.add("ARTIFACT_TYPE", "blocking", "pass", "artifactType is frontier-closure.")
    if data.get("authorityLevel") != "B2":
        report.add("FRONTIER_CLOSURE_AUTHORITY", "blocking", "fail", "frontier-closure should record B2 lane-local authority.")
    else:
        report.add("FRONTIER_CLOSURE_AUTHORITY", "blocking", "pass", "frontier-closure records B2 lane-local authority.")
    states = {"open", "closed", "blocked_on_primary", "blocked_on_human"}
    if data.get("branchState") not in states:
        report.add("BRANCH_STATE", "blocking", "fail", "branchState must be open, closed, blocked_on_primary, or blocked_on_human.")
    else:
        report.add("BRANCH_STATE", "blocking", "pass", "branchState is valid.")
    gaps = data.get("gapDecisionMatrix")
    safe_decisions = {
        "do_now",
        "dispatch_current_thread_subagent",
        "prepare_package",
        "prepare_package_only_when_dispatch_unavailable",
        "apply_conservative_default",
    }
    remaining_safe_decisions: list[str] = []
    if not isinstance(gaps, list) or not gaps:
        report.add("GAP_DECISION_MATRIX", "blocking", "fail", "gapDecisionMatrix must be non-empty.")
    else:
        report.add("GAP_DECISION_MATRIX", "blocking", "pass", "gapDecisionMatrix is non-empty.")
        allowed = {
            "do_now",
            "dispatch_current_thread_subagent",
            "prepare_package",
            "prepare_package_only_when_dispatch_unavailable",
            "apply_conservative_default",
            "needs_final_authority",
            "explicitly_out",
        }
        for idx, item in enumerate(gaps):
            loc = f"gapDecisionMatrix[{idx}]"
            if not isinstance(item, dict):
                report.add("GAP_DECISION_OBJECT", "blocking", "fail", "gap decision must be an object.", loc)
                continue
            missing = [field for field in ["gap", "decision", "nextSafeAction"] if field not in item]
            if missing:
                report.add("GAP_DECISION_FIELDS", "blocking", "fail", "gap decision missing fields: " + ", ".join(missing), loc)
            if item.get("decision") not in allowed:
                report.add("GAP_DECISION_VALUE", "blocking", "fail", "gap decision is not valid.", loc)
            elif item.get("decision") in safe_decisions:
                remaining_safe_decisions.append(f"{loc}:{item.get('decision')}")
    for field_name in ["remainingB0B1B2SafeWork", "remainingFinalAuthorityGaps", "explicitlyOutGaps"]:
        if isinstance(data.get(field_name), list):
            report.add(f"{field_name.upper()}_ARRAY", "blocking", "pass", f"{field_name} is an array.")
        else:
            report.add(f"{field_name.upper()}_ARRAY", "blocking", "fail", f"{field_name} must be an array.")
    branch_state = data.get("branchState")
    if branch_state in {"closed", "blocked_on_primary", "blocked_on_human"} and remaining_safe_decisions:
        report.add(
            "FRONTIER_RETURN_GATE_SAFE_DECISIONS",
            "blocking",
            "fail",
            "closed or blocked Frontier closure cannot leave safe gap decisions unresolved: " + ", ".join(remaining_safe_decisions[:5]),
        )
    elif branch_state in {"closed", "blocked_on_primary", "blocked_on_human"}:
        report.add("FRONTIER_RETURN_GATE_SAFE_DECISIONS", "blocking", "pass", "No B0/B1/B2-safe gap decisions remain.")
    if branch_state == "blocked_on_primary":
        if data.get("remainingB0B1B2SafeWork"):
            report.add("FRONTIER_RETURN_GATE", "blocking", "fail", "blocked_on_primary is invalid while B0/B1/B2-safe work remains.")
        elif not str(data.get("primaryReadyPacketRef", "")).strip():
            report.add("FRONTIER_RETURN_GATE", "blocking", "fail", "blocked_on_primary requires primaryReadyPacketRef.")
        elif data.get("allChildrenTerminal") is not True or data.get("allChildHandoffsConsumedOrRejected") is not True:
            report.add("FRONTIER_RETURN_GATE", "blocking", "fail", "blocked_on_primary requires child work to be terminal and consumed or rejected.")
        else:
            report.add("FRONTIER_RETURN_GATE", "blocking", "pass", "blocked_on_primary satisfies Frontier return gate.")
    elif branch_state == "closed":
        if data.get("remainingB0B1B2SafeWork"):
            report.add("FRONTIER_RETURN_GATE", "blocking", "fail", "closed is invalid while B0/B1/B2-safe work remains.")
        elif data.get("remainingFinalAuthorityGaps"):
            report.add("FRONTIER_RETURN_GATE", "blocking", "fail", "closed is invalid while final-authority gaps remain.")
        elif data.get("allChildrenTerminal") is not True or data.get("allChildHandoffsConsumedOrRejected") is not True:
            report.add("FRONTIER_RETURN_GATE", "blocking", "fail", "closed requires child work to be terminal and consumed or rejected.")
        else:
            report.add("FRONTIER_RETURN_GATE", "blocking", "pass", "closed satisfies Frontier return gate.")
    elif branch_state == "blocked_on_human":
        if data.get("remainingB0B1B2SafeWork"):
            report.add("FRONTIER_RETURN_GATE", "blocking", "fail", "blocked_on_human is invalid while B0/B1/B2-safe work remains.")
        elif not str(data.get("blockedOnHumanReason", "")).strip():
            report.add("FRONTIER_RETURN_GATE", "blocking", "fail", "blocked_on_human requires blockedOnHumanReason.")
        else:
            report.add("FRONTIER_RETURN_GATE", "blocking", "pass", "blocked_on_human names a true human blocker.")
    else:
        report.add("FRONTIER_RETURN_GATE", "blocking", "pass", "branchState is not blocked_on_primary.")
    validate_frontier_primary_ready_packet(data, report)
    validate_frontier_closure_worktree_decision(data.get("worktreeDecision"), report)
    validate_frontier_closure_child_ledger(data, report)
    if not str(data.get("humanNextStep", "")).strip():
        report.add("FRONTIER_HUMAN_NEXT_STEP", "blocking", "fail", "frontier-closure must include humanNextStep.")
    else:
        report.add("FRONTIER_HUMAN_NEXT_STEP", "blocking", "pass", "frontier-closure includes humanNextStep.")


def validate_frontier_primary_ready_packet(data: dict[str, Any], report: Report) -> None:
    if data.get("branchState") != "blocked_on_primary":
        return
    ref = str(data.get("primaryReadyPacketRef", "")).strip()
    if not ref:
        return
    packet_path = resolve_ref(Path(report.artifact).parent, ref)
    if not packet_path.exists():
        report.add("FRONTIER_PRIMARY_READY_PACKET_REF", "blocking", "fail", "primaryReadyPacketRef must point to an existing Primary-ready packet.", str(packet_path))
        return
    if not packet_path.is_file():
        report.add("FRONTIER_PRIMARY_READY_PACKET_REF", "blocking", "fail", "primaryReadyPacketRef must point to a file.", str(packet_path))
        return
    try:
        packet_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        report.add("FRONTIER_PRIMARY_READY_PACKET_UTF8", "blocking", "fail", "primaryReadyPacketRef must read as UTF-8.", str(packet_path))
        return
    report.add("FRONTIER_PRIMARY_READY_PACKET_REF", "blocking", "pass", "primaryReadyPacketRef exists and is UTF-8.", str(packet_path))


def validate_frontier_closure_worktree_decision(worktree: Any, report: Report) -> None:
    if not isinstance(worktree, dict):
        report.add("FRONTIER_WORKTREE_DECISION", "blocking", "fail", "worktreeDecision must be an object.")
        return
    report.add("FRONTIER_WORKTREE_DECISION", "blocking", "pass", "worktreeDecision is an object.")
    required = ["base", "worktree", "branch", "allowedFiles", "verification", "handoffPath", "dataRisk", "resourceUse", "noDispatchReason"]
    missing = [field for field in required if field not in worktree]
    if missing:
        report.add("FRONTIER_WORKTREE_DECISION_FIELDS", "blocking", "fail", "worktreeDecision missing fields: " + ", ".join(missing))
    else:
        report.add("FRONTIER_WORKTREE_DECISION_FIELDS", "blocking", "pass", "worktreeDecision has required fields.")
    for field_name in ["base", "worktree", "branch", "handoffPath", "resourceUse"]:
        if field_name in worktree and not str(worktree.get(field_name, "")).strip():
            report.add("FRONTIER_WORKTREE_DECISION_STRINGS", "blocking", "fail", f"worktreeDecision.{field_name} must be non-empty.")
    for field_name in ["allowedFiles", "verification"]:
        if field_name in worktree and (not isinstance(worktree.get(field_name), list) or not worktree.get(field_name)):
            report.add("FRONTIER_WORKTREE_DECISION_ARRAYS", "blocking", "fail", f"worktreeDecision.{field_name} must be a non-empty array.")
    if worktree.get("dataRisk") not in DATA_RISK_LEVELS:
        report.add("FRONTIER_WORKTREE_DECISION_DATA_RISK", "blocking", "fail", "worktreeDecision.dataRisk must be none, low, medium, high, or sensitive.")
    skipped_markers = {"not_applicable", "not_required", "none", "skipped"}
    skipped_b2 = any(str(worktree.get(field, "")).strip().lower() in skipped_markers for field in ["base", "worktree", "branch"])
    if skipped_b2 and not str(worktree.get("noDispatchReason", "")).strip():
        report.add("FRONTIER_WORKTREE_NO_DISPATCH_REASON", "blocking", "fail", "Skipped B2 dispatch requires noDispatchReason.")
    elif skipped_b2:
        report.add("FRONTIER_WORKTREE_NO_DISPATCH_REASON", "blocking", "pass", "Skipped B2 dispatch names noDispatchReason.")


def validate_frontier_closure_child_ledger(data: dict[str, Any], report: Report) -> None:
    ref = data.get("childLedgerRef")
    if not isinstance(ref, str) or not ref.strip():
        return
    ledger_path = resolve_ref(Path(report.artifact).parent, ref)
    if not ledger_path.exists():
        report.add("FRONTIER_CLOSURE_CHILD_LEDGER_REF", "warning", "fail", "childLedgerRef was not found for lifecycle cross-check.", str(ledger_path))
        return
    ledger_report = Report(str(ledger_path), "child-ledger")
    ledger = load_json(ledger_path, ledger_report)
    if not isinstance(ledger, dict):
        report.add("FRONTIER_CLOSURE_CHILD_LEDGER_LOAD", "blocking", "fail", "childLedgerRef could not be loaded as JSON.", str(ledger_path))
        return
    children = ledger.get("children")
    if not isinstance(children, list):
        report.add("FRONTIER_CLOSURE_CHILD_LEDGER_CHILDREN", "blocking", "fail", "childLedgerRef children must be an array.", str(ledger_path))
        return
    non_terminal = []
    unconsumed = []
    for idx, child in enumerate(children):
        if not isinstance(child, dict):
            continue
        loc = f"children[{idx}]"
        if child.get("dispatchStatus") not in {"returned", "failed", "cancelled"}:
            non_terminal.append(loc)
        if child.get("handoffStatus") == "present" and child.get("consumeStatus") not in {"consumed", "rejected"}:
            unconsumed.append(loc)
    if data.get("branchState") in {"closed", "blocked_on_primary"} and non_terminal:
        report.add("FRONTIER_CLOSURE_CHILD_TERMINAL", "blocking", "fail", "child ledger has non-terminal children: " + ", ".join(non_terminal[:5]), str(ledger_path))
    elif data.get("branchState") in {"closed", "blocked_on_primary"}:
        report.add("FRONTIER_CLOSURE_CHILD_TERMINAL", "blocking", "pass", "child ledger dispatch lifecycle matches closure state.", str(ledger_path))
    if data.get("branchState") in {"closed", "blocked_on_primary"} and unconsumed:
        report.add("FRONTIER_CLOSURE_CHILD_CONSUME", "blocking", "fail", "child ledger has present handoffs not consumed or rejected: " + ", ".join(unconsumed[:5]), str(ledger_path))
    elif data.get("branchState") in {"closed", "blocked_on_primary"}:
        report.add("FRONTIER_CLOSURE_CHILD_CONSUME", "blocking", "pass", "child handoffs are consumed or rejected for closure.", str(ledger_path))


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
        report.add("EFFECTS_PRESET", "blocking", "fail", "effectsPreset is not a known OpenACCP effects preset.")
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
    require_non_empty_string(data, "responseId", report)
    if "reportId" in data:
        report.add("REPORT_ID_DEPRECATED", "warning", "fail", "reportId is deprecated; use responseId for status artifacts.")
    else:
        report.add("REPORT_ID_DEPRECATED", "warning", "pass", "No deprecated reportId field found.")
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
    validate_json_schema_contract(args.ruleset, data, report)
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
    elif args.ruleset == "runtime-boundary":
        validate_runtime_boundary(data, report)
    elif args.ruleset == "lane-registry":
        validate_lane_registry(data, report)
    elif args.ruleset == "child-ledger":
        validate_child_ledger(data, report)
    elif args.ruleset == "source-status-registry":
        validate_source_status_registry(data, report)
    elif args.ruleset == "decision-registry":
        validate_decision_registry(data, report)
    elif args.ruleset == "frontier-closure":
        validate_frontier_closure(data, report)
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
        validate_formal_report_text(text, report, args.preferred_language)
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
    print(f"OpenACCP validator {VERSION}")
    print(f"status: {data['status']}")
    print(f"artifact: {report.artifact}")
    print(f"ruleset: {report.ruleset}")
    for check in report.checks:
        loc = f" [{check.location}]" if check.location else ""
        print(f"- {check.status.upper()} {check.severity} {check.check_id}{loc}: {check.message}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate OpenACCP artifacts.")
    parser.add_argument("--version", action="version", version=f"OpenACCP validator {VERSION}")
    parser.add_argument("--artifact", help="Artifact path to validate.")
    parser.add_argument("--ruleset", choices=sorted(RULESETS), required=True)
    parser.add_argument("--source-pack", help="Optional source pack JSON for task-card cross-checks.")
    parser.add_argument("--task-card", help="Optional task card JSON for handoff scope cross-checks.")
    parser.add_argument("--prompt-record", help="Optional full prompt record for launcher Prompt ID cross-checks.")
    parser.add_argument("--expect-prompt-id", help="Expected Prompt ID for prompt-record or launcher validation.")
    parser.add_argument("--preferred-language", help="Preferred language for formal-report validation.")
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
