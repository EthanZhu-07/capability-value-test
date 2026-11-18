#!/usr/bin/env python3
"""Render a standalone capability A/B test report from JSON."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


VERDICTS = {"adopt", "do_not_adopt", "inconclusive"}
QUALITY_STATES = {"met", "partial", "failed"}
RESEARCH_STATES = {"completed", "unavailable"}
SCENARIO_RECOMMENDATIONS = {"use", "avoid", "retest"}
SCENARIO_BASES = {"experiment", "research", "combined"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}
REPORT_FORMAT_VERSION = "1.0"

# This is the fixed public report contract. The renderer refuses to produce an
# artifact when a future template edit removes or reorders one of these blocks.
FIXED_SECTION_MARKERS = (
    'id="comparison-title"',
    'id="process-title"',
    'id="experiment-findings-title"',
    'id="research-title"',
    'id="analysis-title"',
    'id="audit-title"',
)
REQUIRED_EXPLANATION_MARKERS = (
    'id="comparison-note"',
    'id="process-note"',
    'id="experiment-findings-note"',
    'id="research-note"',
    'id="analysis-note"',
    'id="audit-note"',
)
REQUIRED_EXPLANATION_KEYS = (
    "comparisonNote",
    "processNote",
    "experimentFindingsNote",
    "researchNote",
    "analysisNote",
    "auditNote",
)


class ValidationError(ValueError):
    pass


def validate_template_contract(template: str) -> None:
    """Protect the fixed report layout and its reader-facing explanations."""
    if "__REPORT_FORMAT_VERSION__" not in template:
        raise ValidationError("Report template is missing the format-version marker")

    previous_position = -1
    for marker in FIXED_SECTION_MARKERS:
        if template.count(marker) != 1:
            raise ValidationError(
                f"Report template must contain exactly one fixed section marker: {marker}"
            )
        position = template.index(marker)
        if position <= previous_position:
            raise ValidationError("Report template fixed sections are out of order")
        previous_position = position

    for marker in REQUIRED_EXPLANATION_MARKERS:
        if template.count(marker) != 1:
            raise ValidationError(
                f"Report template must contain exactly one explanation field: {marker}"
            )

    for key in REQUIRED_EXPLANATION_KEYS:
        localized_values = re.findall(
            rf"\b{re.escape(key)}\s*:\s*\"([^\"]+)\"", template
        )
        if len(localized_values) < 4 or any(not value.strip() for value in localized_values):
            raise ValidationError(
                f"Report template must explain every fixed section in each core locale: {key}"
            )


def require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must be an object")
    return value


def require_string(obj: dict[str, Any], key: str, path: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{path}.{key} must be a non-empty string")
    return value.strip()


def optional_number(obj: dict[str, Any], key: str, path: str) -> float | int | None:
    value = obj.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{path}.{key} must be a number or null")
    if value < 0:
        raise ValidationError(f"{path}.{key} cannot be negative")
    return value


def validate_string_list(value: Any, path: str) -> None:
    if value is None:
        return
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValidationError(f"{path} must be an array of strings")


def require_string_list(value: Any, path: str) -> list[str]:
    validate_string_list(value, path)
    if not value:
        raise ValidationError(f"{path} must be a non-empty array of strings")
    if any(not item.strip() for item in value):
        raise ValidationError(f"{path} cannot contain empty strings")
    return value


def require_public_url(obj: dict[str, Any], key: str, path: str) -> str:
    value = require_string(obj, key, path)
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValidationError(f"{path}.{key} must be an http(s) URL")
    return value


def validate_analysis(data: Any) -> dict[str, Any]:
    analysis = require_mapping(data, "root.analysis")
    require_string_list(analysis.get("experiment_findings"), "root.analysis.experiment_findings")
    require_string_list(analysis.get("benefits"), "root.analysis.benefits")
    require_string_list(analysis.get("tradeoffs"), "root.analysis.tradeoffs")
    require_string(analysis, "recommendation", "root.analysis")

    research = require_mapping(analysis.get("research"), "root.analysis.research")
    research_status = require_string(research, "status", "root.analysis.research")
    if research_status not in RESEARCH_STATES:
        raise ValidationError(
            "root.analysis.research.status must be one of: "
            + ", ".join(sorted(RESEARCH_STATES))
        )
    require_string(research, "summary", "root.analysis.research")
    sources = research.get("sources")
    if not isinstance(sources, list):
        raise ValidationError("root.analysis.research.sources must be an array")
    if research_status == "completed" and not sources:
        raise ValidationError(
            "root.analysis.research.sources must not be empty when research completed"
        )

    source_ids: set[str] = set()
    for index, source_value in enumerate(sources):
        source_path = f"root.analysis.research.sources[{index}]"
        source = require_mapping(source_value, source_path)
        source_id = require_string(source, "id", source_path)
        if source_id in source_ids:
            raise ValidationError(f"{source_path}.id must be unique")
        source_ids.add(source_id)
        for key in ("title", "publisher", "retrieved_at", "finding"):
            require_string(source, key, source_path)
        require_public_url(source, "url", source_path)

    scenarios = analysis.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValidationError("root.analysis.scenarios must be a non-empty array")
    for index, scenario_value in enumerate(scenarios):
        scenario_path = f"root.analysis.scenarios[{index}]"
        scenario = require_mapping(scenario_value, scenario_path)
        for key in ("title", "audience", "task", "environment", "reason"):
            require_string(scenario, key, scenario_path)
        recommendation = require_string(scenario, "recommendation", scenario_path)
        if recommendation not in SCENARIO_RECOMMENDATIONS:
            raise ValidationError(
                f"{scenario_path}.recommendation must be one of: "
                + ", ".join(sorted(SCENARIO_RECOMMENDATIONS))
            )
        basis = require_string(scenario, "basis", scenario_path)
        if basis not in SCENARIO_BASES:
            raise ValidationError(
                f"{scenario_path}.basis must be one of: "
                + ", ".join(sorted(SCENARIO_BASES))
            )
        confidence = require_string(scenario, "confidence", scenario_path)
        if confidence not in CONFIDENCE_LEVELS:
            raise ValidationError(
                f"{scenario_path}.confidence must be one of: "
                + ", ".join(sorted(CONFIDENCE_LEVELS))
            )
        source_refs = scenario.get("source_refs", [])
        validate_string_list(source_refs, f"{scenario_path}.source_refs")
        unknown_refs = [ref for ref in source_refs if ref not in source_ids]
        if unknown_refs:
            raise ValidationError(
                f"{scenario_path}.source_refs contains unknown ids: {', '.join(unknown_refs)}"
            )
        if basis in {"research", "combined"} and not source_refs:
            raise ValidationError(
                f"{scenario_path}.source_refs is required for {basis} scenarios"
            )

    return analysis


def validate_i18n(data: Any) -> dict[str, Any]:
    i18n = require_mapping(data, "root.i18n")
    default_locale = require_string(i18n, "default_locale", "root.i18n")
    locales = require_mapping(i18n.get("locales"), "root.i18n.locales")
    if len(locales) < 2:
        raise ValidationError("root.i18n.locales must contain at least two languages")
    if default_locale not in locales:
        raise ValidationError("root.i18n.default_locale must exist in root.i18n.locales")
    for code, locale_value in locales.items():
        locale_path = f"root.i18n.locales.{code}"
        locale = require_mapping(locale_value, locale_path)
        require_string(locale, "label", locale_path)
        direction = locale.get("direction", "ltr")
        if direction not in {"ltr", "rtl"}:
            raise ValidationError(f"{locale_path}.direction must be ltr or rtl")
        content = locale.get("content", {})
        require_mapping(content, f"{locale_path}.content")
    return i18n


def validate_arm(data: Any, path: str) -> dict[str, Any]:
    arm = require_mapping(data, path)
    require_string(arm, "name", path)

    if "verified" not in arm or not isinstance(arm["verified"], bool):
        raise ValidationError(f"{path}.verified must be true or false")

    elapsed = optional_number(arm, "elapsed_seconds", path)
    if elapsed is None:
        raise ValidationError(f"{path}.elapsed_seconds is required")

    optional_number(arm, "tokens", path)
    optional_number(arm, "cost", path)
    require_string(arm, "result_summary", path)

    quality = require_mapping(arm.get("quality"), f"{path}.quality")
    status = require_string(quality, "status", f"{path}.quality")
    if status not in QUALITY_STATES:
        raise ValidationError(
            f"{path}.quality.status must be one of: {', '.join(sorted(QUALITY_STATES))}"
        )
    require_string(quality, "label", f"{path}.quality")
    require_string(quality, "summary", f"{path}.quality")

    steps = arm.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValidationError(f"{path}.steps must be a non-empty array")
    for index, step_value in enumerate(steps):
        step_path = f"{path}.steps[{index}]"
        step = require_mapping(step_value, step_path)
        require_string(step, "title", step_path)
        require_string(step, "detail", step_path)

    evidence = arm.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValidationError(f"{path}.evidence must be a non-empty array")
    for index, item_value in enumerate(evidence):
        item_path = f"{path}.evidence[{index}]"
        item = require_mapping(item_value, item_path)
        require_string(item, "type", item_path)
        require_string(item, "label", item_path)
        if not item.get("content") and not item.get("path"):
            raise ValidationError(f"{item_path} needs content or path")

    return arm


def validate(data: Any) -> dict[str, Any]:
    root = require_mapping(data, "root")
    for key in ("title", "tested_at", "task", "primary_question"):
        require_string(root, key, "root")

    verdict = require_mapping(root.get("verdict"), "root.verdict")
    status = require_string(verdict, "status", "root.verdict")
    if status not in VERDICTS:
        raise ValidationError(
            f"root.verdict.status must be one of: {', '.join(sorted(VERDICTS))}"
        )
    for key in ("label", "summary", "limitation"):
        require_string(verdict, key, "root.verdict")

    validate_arm(root.get("baseline"), "root.baseline")
    validate_arm(root.get("candidate"), "root.candidate")

    validate_analysis(root.get("analysis"))
    validate_i18n(root.get("i18n"))

    return root


def enrich_evidence(data: dict[str, Any], input_path: Path) -> None:
    base = input_path.parent.resolve()
    for arm_name in ("baseline", "candidate"):
        for item in data[arm_name]["evidence"]:
            raw_path = item.get("path")
            if not raw_path:
                continue
            relative = Path(raw_path)
            if relative.is_absolute() or ".." in relative.parts:
                item["attachment_error"] = "Only relative evidence paths are allowed"
                continue
            resolved = (base / relative).resolve()
            if base not in resolved.parents and resolved != base:
                item["attachment_error"] = "Evidence path leaves the experiment directory"
                continue
            if not resolved.is_file():
                item["attachment_error"] = "Evidence file was not found"
                continue
            item["resolved_name"] = resolved.name
            mime, _ = mimetypes.guess_type(resolved.name)
            if mime and mime.startswith("image/"):
                if resolved.stat().st_size > 5 * 1024 * 1024:
                    item["attachment_error"] = "Image exceeds the 5 MB embed limit"
                    continue
                encoded = base64.b64encode(resolved.read_bytes()).decode("ascii")
                item["data_url"] = f"data:{mime};base64,{encoded}"


def add_computed_metrics(data: dict[str, Any]) -> None:
    baseline = data["baseline"]
    candidate = data["candidate"]
    baseline_time = float(baseline["elapsed_seconds"])
    candidate_time = float(candidate["elapsed_seconds"])

    computed: dict[str, Any] = {
        "time_delta_seconds": candidate_time - baseline_time,
        "time_improvement_percent": None,
        "token_delta": None,
        "token_improvement_percent": None,
        "cost_delta": None,
        "cost_improvement_percent": None,
    }
    if baseline_time > 0:
        computed["time_improvement_percent"] = (
            (baseline_time - candidate_time) / baseline_time * 100
        )

    for metric, delta_key, percent_key in (
        ("tokens", "token_delta", "token_improvement_percent"),
        ("cost", "cost_delta", "cost_improvement_percent"),
    ):
        base_value = baseline.get(metric)
        candidate_value = candidate.get(metric)
        if isinstance(base_value, (int, float)) and isinstance(candidate_value, (int, float)):
            computed[delta_key] = candidate_value - base_value
            if base_value > 0:
                computed[percent_key] = (
                    (base_value - candidate_value) / base_value * 100
                )

    data["computed"] = computed


def render(input_path: Path, output_path: Path) -> None:
    try:
        raw = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"Input file not found: {input_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON: {exc}") from exc

    data = validate(raw)
    enrich_evidence(data, input_path)
    add_computed_metrics(data)

    template_path = Path(__file__).resolve().parent.parent / "assets" / "report-template.html"
    if not template_path.is_file():
        raise ValidationError(f"Report template not found: {template_path}")

    template = template_path.read_text(encoding="utf-8")
    validate_template_contract(template)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    if "__EXPERIMENT_JSON__" not in template:
        raise ValidationError("Report template is missing the data marker")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        template.replace("__REPORT_FORMAT_VERSION__", REPORT_FORMAT_VERSION).replace(
            "__EXPERIMENT_JSON__", payload
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render a standalone capability value A/B test report"
    )
    parser.add_argument("input", type=Path, help="Path to experiment.json")
    parser.add_argument(
        "--output", "-o", type=Path, required=True, help="Path to report.html"
    )
    args = parser.parse_args()

    try:
        render(args.input.resolve(), args.output.resolve())
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
