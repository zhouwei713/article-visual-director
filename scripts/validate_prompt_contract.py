#!/usr/bin/env python3
"""Validate compiled article-cover prompts against a requirements contract.

This is a structural guard. It cannot prove that a model rendered a good image.
It blocks common prompt regressions before an image-generation call.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


CONFLICT_TERMS = (
    "textless",
    "reserved-title-zone",
    "无字成图",
    "画面不出现任何可见文字",
    "画面不出现文字",
)
FORBIDDEN_HIGH_CONCEPT_STYLES = {
    "product-hero",
    "dark-system-pulse",
    "warm-workbench-map",
    "system-landscape",
    "single-hero",
}
REQUIRED_XHS_AI_COVER_FIELDS = (
    "impact_mechanism",
    "visual_anchor",
    "click_hook",
    "hero_subject",
    "decisive_action",
    "depth_relation",
    "title_subject_interlock",
    "safe_crop_zone",
    "thumbnail_readability",
)
XHS_IMPACT_MECHANISMS = {
    "giant-type-perspective",
    "type-subject-interlock",
    "foreground-thrust",
    "decisive-action",
    "scale-tension",
    "single-metaphor",
}


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def contract_for_prompt(contract: dict, path: Path) -> dict:
    """Merge a shared contract with the asset-specific entry, when present."""
    assets = contract.get("assets")
    if not assets:
        return contract
    merged = {key: value for key, value in contract.items() if key != "assets"}
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        names = {str(asset.get("prompt", "")), str(asset.get("output", ""))}
        if path.name in names or path.as_posix() in names:
            merged.update(asset)
            return merged
    raise ValueError(f"no asset contract matches {path}")


def validate_prompt(contract: dict, path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    meta = parse_frontmatter(text)

    for key in ("mode", "style", "aspect_ratio", "visible_text", "text_policy"):
        if key not in meta:
            fail(errors, f"{path.name}: missing frontmatter field {key}")

    ratio = str(contract.get("aspect_ratio", "")).strip()
    if ratio and ratio not in text:
        fail(errors, f"{path.name}: aspect ratio {ratio!r} is absent from prompt")
    if ratio and meta.get("aspect_ratio", "") != ratio:
        fail(errors, f"{path.name}: metadata aspect_ratio does not match contract")

    expected_style = str(contract.get("style", "")).strip()
    if expected_style and meta.get("style", "") != expected_style:
        fail(errors, f"{path.name}: metadata style does not match contract")

    mode = str(contract.get("mode", "")).strip()
    if mode and meta.get("mode", "") != mode:
        fail(errors, f"{path.name}: metadata mode does not match contract")

    expected_render_method = str(contract.get("render_method", "")).strip()
    if expected_render_method and meta.get("render_method", "") != expected_render_method:
        fail(errors, f"{path.name}: metadata render_method does not match contract")

    asset_type = meta.get("asset_type", "")
    if asset_type == "xiaohongshu-cover" and expected_render_method == "imagegen":
        for key in REQUIRED_XHS_AI_COVER_FIELDS:
            if not meta.get(key, "").strip():
                fail(errors, f"{path.name}: AI Xiaohongshu cover is missing {key}")
        expected_impact = str(contract.get("impact_mechanism", "")).strip()
        if expected_impact and meta.get("impact_mechanism", "") != expected_impact:
            fail(errors, f"{path.name}: metadata impact_mechanism does not match contract")
        if meta.get("impact_mechanism", "") not in XHS_IMPACT_MECHANISMS:
            fail(errors, f"{path.name}: unsupported Xiaohongshu impact_mechanism")

    visible_text = bool(contract.get("visible_text", False))
    expected_policy = str(contract.get("text_policy", "")).strip()
    if expected_policy and meta.get("text_policy", "") != expected_policy:
        fail(errors, f"{path.name}: metadata text_policy does not match contract")

    exact_text = str(contract.get("exact_text", ""))
    if visible_text:
        if not exact_text:
            fail(errors, f"{path.name}: visible_text requires non-empty exact_text")
        elif exact_text not in text:
            fail(errors, f"{path.name}: exact_text is absent from prompt")
        if meta.get("visible_text", "").lower() not in {"true", "yes", "1"}:
            fail(errors, f"{path.name}: metadata visible_text is not true")
        if expected_policy in {"textless", "reserved-title-zone"}:
            fail(errors, f"{path.name}: visible text cannot use {expected_policy}")
        if not bool(contract.get("allow_textless_fallback", False)):
            for term in CONFLICT_TERMS:
                if term.lower() in lower:
                    fail(errors, f"{path.name}: forbidden text fallback term {term!r}")

        allowed_text = contract.get("allowed_text", [])
        if isinstance(allowed_text, str):
            allowed_text = [allowed_text]
        if expected_policy == "editorial-hierarchy":
            if not str(contract.get("visual_mode", "")).strip():
                fail(errors, f"{path.name}: editorial-hierarchy requires visual_mode")
            if "一级主标题" not in text and "一级核心主文字" not in text:
                fail(errors, f"{path.name}: editorial-hierarchy is missing primary title hierarchy")
            if "二级" not in text or "三级" not in text:
                fail(errors, f"{path.name}: editorial-hierarchy is missing secondary hierarchy guidance")
        for phrase in allowed_text:
            phrase = str(phrase).strip()
            if phrase and phrase not in text:
                fail(errors, f"{path.name}: allowed_text phrase is absent from prompt: {phrase!r}")
    else:
        if meta.get("visible_text", "").lower() in {"true", "yes", "1"}:
            fail(errors, f"{path.name}: metadata visible_text is true but contract is false")

    if expected_style == "high-concept-poster":
        if meta.get("style", "") in FORBIDDEN_HIGH_CONCEPT_STYLES:
            fail(errors, f"{path.name}: high-concept-poster was replaced by {meta['style']}")
        if "high-concept-poster" not in lower and "高级概念海报" not in text:
            fail(errors, f"{path.name}: high-concept-poster instruction is absent")

    if mode == "prompt-led-cover" and not bool(contract.get("user_prompt_locked", False)):
        fail(errors, "contract: prompt-led-cover requires user_prompt_locked=true")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--prompt", required=True, type=Path, nargs="+")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    errors: list[str] = []
    for prompt in args.prompt:
        if not prompt.exists():
            errors.append(f"missing prompt file: {prompt}")
            continue
        try:
            effective_contract = contract_for_prompt(contract, prompt)
        except ValueError as error:
            errors.append(str(error))
            continue
        errors.extend(validate_prompt(effective_contract, prompt))

    if errors:
        print("CONTRACT_FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"CONTRACT_PASS prompts={len(args.prompt)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
