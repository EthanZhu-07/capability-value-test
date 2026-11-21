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
RESEARCH_STATES = {"completed", "blocked"}
REQUIRED_LOCALES = {"en", "zh-CN", "ja", "ko"}
SCENARIO_RECOMMENDATIONS = {"use", "avoid", "retest"}
SCENARIO_BASES = {"experiment", "research", "combined"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}
REPORT_FORMAT_VERSION = "2.0"

# This is the fixed public report contract. The renderer refuses to produce an
# artifact when a future template edit removes or reorders one of these blocks.
FIXED_SECTION_MARKERS = (
    'id="comparison-title"',
    'id="design-title"',
)
REQUIRED_EXPLANATION_MARKERS = (
    'id="comparison-note"',
    'id="design-note"',
)
REQUIRED_EXPLANATION_KEYS = (
    "comparisonNote",
    "designNote",
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
    if research.get("attempted") is not True:
        raise ValidationError("root.analysis.research.attempted must be true")
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
    if research_status == "blocked":
        require_string(research, "blocker", "root.analysis.research")
        if sources:
            raise ValidationError(
                "root.analysis.research.sources must be empty when research is blocked"
            )

    source_ids: set[str] = set()
    for index, source_value in enumerate(sources):
        source_path = f"root.analysis.research.sources[{index}]"
        source = require_mapping(source_value, source_path)
        source_id = require_string(source, "id", source_path)
        if source_id in source_ids:
            raise ValidationError(f"{source_path}.id must be unique")
        source_ids.add(source_id)
        for key in ("title", "publisher", "finding"):
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


def require_localized_arm(overlay_value: Any, base_value: Any, path: str) -> None:
    overlay = require_mapping(overlay_value, path)
    base = require_mapping(base_value, f"{path} (base)")
    for key in ("name", "version", "result_summary"):
        require_string(overlay, key, path)
    quality = require_mapping(overlay.get("quality"), f"{path}.quality")
    for key in ("label", "summary"):
        require_string(quality, key, f"{path}.quality")

    overlay_steps = overlay.get("steps")
    base_steps = base.get("steps")
    if not isinstance(overlay_steps, list) or len(overlay_steps) != len(base_steps):
        raise ValidationError(f"{path}.steps must translate every base step")
    for index, (step_value, base_step_value) in enumerate(zip(overlay_steps, base_steps)):
        step_path = f"{path}.steps[{index}]"
        step = require_mapping(step_value, step_path)
        base_step = require_mapping(base_step_value, f"{step_path} (base)")
        for key in ("title", "detail"):
            require_string(step, key, step_path)
        overlay_evidence = step.get("evidence", [])
        base_evidence = base_step.get("evidence", [])
        if not isinstance(overlay_evidence, list) or len(overlay_evidence) != len(base_evidence):
            raise ValidationError(f"{step_path}.evidence must translate every evidence label")
        for evidence_index, evidence_value in enumerate(overlay_evidence):
            evidence_path = f"{step_path}.evidence[{evidence_index}]"
            evidence = require_mapping(evidence_value, evidence_path)
            require_string(evidence, "label", evidence_path)

    overlay_evidence = overlay.get("evidence", [])
    base_evidence = base.get("evidence", [])
    if not isinstance(overlay_evidence, list) or len(overlay_evidence) != len(base_evidence):
        raise ValidationError(f"{path}.evidence must translate every evidence label")
    for index, evidence_value in enumerate(overlay_evidence):
        evidence_path = f"{path}.evidence[{index}]"
        evidence = require_mapping(evidence_value, evidence_path)
        require_string(evidence, "label", evidence_path)


def validate_complete_locale_content(content_value: Any, root: dict[str, Any], path: str) -> None:
    content = require_mapping(content_value, path)
    for key in ("title", "task", "primary_question"):
        require_string(content, key, path)

    verdict = require_mapping(content.get("verdict"), f"{path}.verdict")
    for key in ("label", "summary", "limitation"):
        require_string(verdict, key, f"{path}.verdict")

    require_localized_arm(content.get("baseline"), root["baseline"], f"{path}.baseline")
    require_localized_arm(content.get("candidate"), root["candidate"], f"{path}.candidate")

    design = require_mapping(content.get("design"), f"{path}.design")
    for key in ("basis", "fairness", "judgment_rule"):
        require_string(design, key, f"{path}.design")

    overlay_rounds = content.get("rounds")
    base_rounds = root["rounds"]
    if not isinstance(overlay_rounds, list) or len(overlay_rounds) != len(base_rounds):
        raise ValidationError(f"{path}.rounds must translate all three rounds")
    for index, (round_value, base_round_value) in enumerate(zip(overlay_rounds, base_rounds)):
        round_path = f"{path}.rounds[{index}]"
        round_data = require_mapping(round_value, round_path)
        base_round = require_mapping(base_round_value, f"{round_path} (base)")
        for key in ("title", "task"):
            require_string(round_data, key, round_path)
        require_localized_arm(
            round_data.get("baseline"), base_round["baseline"], f"{round_path}.baseline"
        )
        require_localized_arm(
            round_data.get("candidate"), base_round["candidate"], f"{round_path}.candidate"
        )

    analysis = require_mapping(content.get("analysis"), f"{path}.analysis")
    base_analysis = root["analysis"]
    for key in ("experiment_findings", "benefits", "tradeoffs"):
        values = require_string_list(analysis.get(key), f"{path}.analysis.{key}")
        if len(values) != len(base_analysis[key]):
            raise ValidationError(f"{path}.analysis.{key} must translate every item")
    require_string(analysis, "recommendation", f"{path}.analysis")

    research = require_mapping(analysis.get("research"), f"{path}.analysis.research")
    require_string(research, "summary", f"{path}.analysis.research")
    if base_analysis["research"]["status"] == "blocked":
        require_string(research, "blocker", f"{path}.analysis.research")
    overlay_sources = research.get("sources", [])
    base_sources = base_analysis["research"]["sources"]
    if not isinstance(overlay_sources, list) or len(overlay_sources) != len(base_sources):
        raise ValidationError(f"{path}.analysis.research.sources must translate every source")
    for index, source_value in enumerate(overlay_sources):
        source_path = f"{path}.analysis.research.sources[{index}]"
        source = require_mapping(source_value, source_path)
        for key in ("title", "publisher", "finding"):
            require_string(source, key, source_path)

    overlay_scenarios = analysis.get("scenarios")
    base_scenarios = base_analysis["scenarios"]
    if not isinstance(overlay_scenarios, list) or len(overlay_scenarios) != len(base_scenarios):
        raise ValidationError(f"{path}.analysis.scenarios must translate every scenario")
    for index, scenario_value in enumerate(overlay_scenarios):
        scenario_path = f"{path}.analysis.scenarios[{index}]"
        scenario = require_mapping(scenario_value, scenario_path)
        for key in ("title", "audience", "task", "environment", "reason"):
            require_string(scenario, key, scenario_path)


def validate_i18n(data: Any, root: dict[str, Any]) -> dict[str, Any]:
    i18n = require_mapping(data, "root.i18n")
    default_locale = require_string(i18n, "default_locale", "root.i18n")
    locales = require_mapping(i18n.get("locales"), "root.i18n.locales")
    missing_locales = sorted(REQUIRED_LOCALES - set(locales))
    if missing_locales:
        raise ValidationError(
            "root.i18n.locales must include en, zh-CN, ja, and ko; missing: "
            + ", ".join(missing_locales)
        )
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
        validate_complete_locale_content(content, root, f"{locale_path}.content")
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
        require_string(step, "time", step_path)
        step_evidence = step.get("evidence", [])
        if not isinstance(step_evidence, list):
            raise ValidationError(f"{step_path}.evidence must be an array")
        for evidence_index, item_value in enumerate(step_evidence):
            item_path = f"{step_path}.evidence[{evidence_index}]"
            item = require_mapping(item_value, item_path)
            require_string(item, "type", item_path)
            require_string(item, "label", item_path)
            if not item.get("content") and not item.get("path"):
                raise ValidationError(f"{item_path} needs content or path")

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

    design = require_mapping(root.get("design"), "root.design")
    for key in ("basis", "fairness", "judgment_rule"):
        require_string(design, key, "root.design")

    rounds = root.get("rounds")
    if not isinstance(rounds, list) or len(rounds) != 3:
        raise ValidationError("root.rounds must contain exactly three rounds")
    round_ids: set[str] = set()
    for index, round_value in enumerate(rounds):
        round_path = f"root.rounds[{index}]"
        round_data = require_mapping(round_value, round_path)
        round_id = require_string(round_data, "id", round_path)
        if round_id in round_ids:
            raise ValidationError(f"{round_path}.id must be unique")
        round_ids.add(round_id)
        require_string(round_data, "title", round_path)
        require_string(round_data, "task", round_path)
        validate_arm(round_data.get("baseline"), f"{round_path}.baseline")
        validate_arm(round_data.get("candidate"), f"{round_path}.candidate")

    validate_analysis(root.get("analysis"))
    validate_i18n(root.get("i18n"), root)

    return root


def enrich_evidence(data: dict[str, Any], input_path: Path) -> None:
    base = input_path.parent.resolve()
    evidence_lists: list[list[dict[str, Any]]] = []
    for arm_name in ("baseline", "candidate"):
        evidence_lists.append(data[arm_name]["evidence"])
    for round_data in data["rounds"]:
        for arm_name in ("baseline", "candidate"):
            arm = round_data[arm_name]
            evidence_lists.append(arm["evidence"])
            for step in arm["steps"]:
                evidence_lists.append(step.get("evidence", []))

    for evidence_list in evidence_lists:
        for item in evidence_list:
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
