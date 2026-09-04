#!/usr/bin/env python3
"""Check Xiaohongshu copy for detached narration and internal production notes."""

from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path


DEFAULT_FORBIDDEN = [
    "文章里说到",
    "文章里提到",
    "文章中提到",
    "原文提到",
    "原文说到",
    "原文展示",
    "作者提到",
    "作者说到",
    "作者发现",
    "文中提到",
    "文中展示",
]


DEFAULT_PUBLIC_IMAGE_FORBIDDEN = [
    "截图来自附件",
    "图片来自附件",
    "来自附件真实案例",
    "附件没有提供",
    "附件未提供",
    "未提供独立文件",
    "原始视频未单独提供",
    "原始视频文件未单独提供",
    "真实界面证据",
    "真实节点关系",
    "本页保留作者",
    "轨迹只用于说明",
    "轨迹仅作示意",
    "轨迹示意不代表实际成片",
    "素材缺失说明",
    "来源审计",
    "制作过程说明",
]


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)

    def text(self) -> str:
        return "\n".join(self.parts)


def load_requirements(root: Path) -> dict:
    path = root / "requirements.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"COPY_VOICE_ERROR invalid requirements.json: {exc}") from exc


def visible_text(path: Path) -> str:
    content = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() != ".html":
        return content
    parser = VisibleTextParser()
    parser.feed(content)
    return parser.text()


def line_for_phrase(text: str, phrase: str) -> int:
    return text[: text.index(phrase)].count("\n") + 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    root = args.output_dir.resolve()
    requirements = load_requirements(root)
    if requirements.get("narrative_voice") != "author-first-person":
        print("COPY_VOICE_SKIP narrative_voice is not author-first-person")
        return 0

    configured = requirements.get("forbidden_narration", [])
    forbidden = list(dict.fromkeys([*DEFAULT_FORBIDDEN, *configured]))
    configured_public = requirements.get("public_image_forbidden_copy", [])
    public_forbidden = list(dict.fromkeys([*DEFAULT_PUBLIC_IMAGE_FORBIDDEN, *configured_public]))

    files: list[Path] = []
    note = root / "note.md"
    if note.exists():
        files.append(note)
    html_files: list[Path] = []
    html_dir = root / "html"
    if html_dir.exists():
        html_files = sorted(html_dir.rglob("*.html"))
        files.extend(html_files)

    failures: list[tuple[Path, int, str]] = []
    for path in files:
        text = visible_text(path)
        for phrase in forbidden:
            if phrase in text:
                failures.append((path, line_for_phrase(text, phrase), phrase))

    public_failures: list[tuple[Path, int, str]] = []
    for path in html_files:
        text = visible_text(path)
        for phrase in public_forbidden:
            if phrase in text:
                public_failures.append((path, line_for_phrase(text, phrase), phrase))

    if failures or public_failures:
        print("COPY_VOICE_FAIL")
        for path, line, phrase in failures:
            print(f"{path.relative_to(root)}:{line}: {phrase}")
        for path, line, phrase in public_failures:
            print(f"{path.relative_to(root)}:{line}: public-image-meta: {phrase}")
        return 1

    print(f"COPY_VOICE_PASS files={len(files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
