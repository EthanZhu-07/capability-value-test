#!/usr/bin/env python3
"""Render a standalone capability A/B test report from JSON."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
from pathlib import Path
from typing import Any


VERDICTS = {"adopt", "conditional", "do_not_adopt", "inconclusive"}
QUALITY_STATES = {"met", "partial", "failed"}


class ValidationError(ValueError):
    pass


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

    analysis = require_mapping(root.get("analysis"), "root.analysis")
    for key in ("benefits", "tradeoffs", "use_when", "avoid_when"):
        validate_string_list(analysis.get(key), f"root.analysis.{key}")
    require_string(analysis, "recommendation", "root.analysis")

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
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    if "__EXPERIMENT_JSON__" not in template:
        raise ValidationError("Report template is missing the data marker")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        template.replace("__EXPERIMENT_JSON__", payload), encoding="utf-8"
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
