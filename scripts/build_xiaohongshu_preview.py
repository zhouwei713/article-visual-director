#!/usr/bin/env python3
"""Build a local delivery dashboard for a Xiaohongshu visual package."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig")


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"PREVIEW_ERROR invalid {path.name}: {exc}") from exc


def parse_brief_values(markdown: str) -> dict[str, str]:
    values: dict[str, list[str]] = {}
    current = ""
    for line in markdown.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current = heading.group(1).strip()
            values.setdefault(current, [])
            continue
        if current and line.strip() and not line.lstrip().startswith("#"):
            values[current].append(line.strip())
    return {key: " ".join(lines).strip() for key, lines in values.items()}


def sample_image_tone(root: Path, pages: list[dict[str, Path | str | None]]) -> tuple[float, tuple[int, int, int]] | None:
    """Return average brightness and RGB for available images when Pillow exists."""
    try:
        from PIL import Image
    except ImportError:
        return None

    pixels: list[tuple[int, int, int]] = []
    for page in pages:
        image_path = page.get("image")
        if not isinstance(image_path, Path) or not image_path.is_file():
            continue
        try:
            with Image.open(image_path) as image:
                thumb = image.convert("RGB")
                thumb.thumbnail((24, 24))
                pixels.extend(thumb.getdata())
        except (OSError, ValueError):
            continue
    if not pixels:
        return None
    count = len(pixels)
    rgb = tuple(round(sum(pixel[index] for pixel in pixels) / count) for index in range(3))
    brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
    return brightness, rgb


def infer_theme(requirements: dict, brief_values: dict[str, str], pages: list[dict[str, Path | str | None]], root: Path) -> dict[str, str]:
    style_text = " ".join(
        str(requirements.get(key, "")) for key in ("style", "palette_policy", "text_policy")
    )
    content_text = " ".join(brief_values.values())
    signals = f"{style_text} {content_text}".lower()
    image_tone = sample_image_tone(root, pages)
    image_brightness = image_tone[0] if image_tone else None

    dark_words = ("深色", "深海", "蓝黑", "dark", "terminal", "workbench", "开发者", "插件")
    light_words = ("浅色", "纸张", "暖白", "生活方式", "portrait", "editorial")
    dark = any(word.lower() in signals for word in dark_words)
    if any(word.lower() in signals for word in light_words) and not any(word.lower() in signals for word in dark_words):
        dark = False
    if image_brightness is not None and image_brightness < 118:
        dark = True

    if any(word in signals for word in ("青蓝", "cyan", "蓝")):
        accent = "#3ecbff"
        accent_soft = "rgba(62,203,255,.14)"
    elif any(word in signals for word in ("紫", "violet", "purple")):
        accent = "#a78bfa"
        accent_soft = "rgba(167,139,250,.15)"
    elif any(word in signals for word in ("橙", "orange", "红")):
        accent = "#ff8a5b"
        accent_soft = "rgba(255,138,91,.15)"
    else:
        accent = "#315efb"
        accent_soft = "rgba(49,94,251,.12)"

    if dark:
        return {
            "label": "深色工程主题",
            "ink": "#eef7ff",
            "muted": "#8ea9bf",
            "paper": "#06111d",
            "card": "#0b1d2c",
            "line": "rgba(105,201,255,.24)",
            "accent": accent,
            "accent_soft": accent_soft,
            "positive": "#70f0c0",
            "warning": "#ff7b85",
            "body_background": "radial-gradient(circle at 82% 2%, rgba(62,203,255,.16), transparent 30%), linear-gradient(145deg, #06111d 0%, #071724 55%, #081c2d 100%)",
        }
    return {
        "label": "浅色编辑主题",
        "ink": "#14213d",
        "muted": "#667085",
        "paper": "#f5f7fb",
        "card": "#fffdf8",
        "line": "#dbe2ea",
        "accent": accent,
        "accent_soft": accent_soft,
        "positive": "#4caf78",
        "warning": "#e77b35",
        "body_background": "linear-gradient(135deg, #f7f9fc, #edf2ff)",
    }


def render_theme_css(theme: dict[str, str]) -> str:
    dark = theme["paper"].startswith("#0") or theme["paper"].startswith("#06")
    panel = "rgba(7,24,39,.84)" if dark else "rgba(255,255,255,.92)"
    copy_text = "#c5d5e2" if dark else "#344054"
    grid = "background-image:linear-gradient(rgba(105,201,255,.08) 1px, transparent 1px),linear-gradient(90deg, rgba(105,201,255,.08) 1px, transparent 1px);background-size:44px 44px;" if dark else ""
    return f"""
  <style id="preview-theme">
    :root {{ color-scheme:{'dark' if dark else 'light'}; --ink:{theme['ink']}; --muted:{theme['muted']}; --paper:{theme['paper']}; --card:{theme['card']}; --line:{theme['line']}; --blue:{theme['accent']}; --accent-soft:{theme['accent_soft']}; --positive:{theme['positive']}; --warning:{theme['warning']}; }}
    html, body {{ background:{theme['body_background']}; }}
    body {{ color:var(--ink); {grid} }}
    body:after {{ background:radial-gradient(circle at 50% 12%, transparent, rgba(0,0,0,{' .24' if dark else ' .03'})); }}
    a {{ color:var(--blue); }}
    .hero {{ background:linear-gradient(135deg, {theme['paper']}, {theme['card']}); border-color:var(--line); box-shadow:0 24px 70px rgba(0,0,0,{' .26' if dark else ' .08'}); }}
    .hero h1, .panel h2, .section-title h2 {{ color:var(--ink); }}
    .hero .summary span, .badge {{ border:1px solid var(--line); background:var(--accent-soft); color:var(--ink); }}
    .panel, .page-card, details {{ border-color:var(--line); background:{panel}; box-shadow:0 14px 45px rgba(0,0,0,{' .18' if dark else ' .08'}); }}
    .copy-block, .stat, pre {{ border-color:var(--line); background:{theme['card']}; }}
    .copy-text, .page-meta p, pre {{ color:{copy_text}; }}
    .page-number {{ color:{theme['paper']}; background:var(--blue); }}
    .status {{ color:{theme['positive']}; background:{'rgba(112,240,192,.10)' if dark else '#eaf8f0'}; }}
    .warnings {{ color:{theme['warning']}; background:{'rgba(255,123,133,.10)' if dark else '#fff6e8'}; }}
    .page-preview {{ background:{theme['paper']}; }}
    button[data-copy] {{ border:1px solid var(--blue); color:var(--blue); background:var(--accent-soft); }}
    button[data-copy]:hover {{ color:{theme['paper']}; background:var(--blue); }}
    dialog {{ background:{theme['paper']}; border:1px solid var(--line); }}
    .hero-context {{ max-width:820px; margin-top:20px; padding:12px 14px; border-left:3px solid var(--positive); color:{copy_text}; background:var(--accent-soft); line-height:1.7; }}
    .hero-context strong {{ margin-right:8px; color:var(--positive); }}
  </style>
"""


def split_note(markdown: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = "概览"
    sections[current] = []
    for line in markdown.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            current = match.group(1).strip()
            sections.setdefault(current, [])
            continue
        if line.startswith("# ") and current == "概览":
            continue
        sections[current].append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def parse_plan_table(markdown: str) -> list[dict[str, str]]:
    rows = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2 or all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        return []
    headers = rows[0]
    return [dict(zip(headers, row)) for row in rows[1:] if len(row) == len(headers)]


def natural_key(value: str) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


def relative_url(path: Path, root: Path) -> str:
    relative = path.relative_to(root).as_posix()
    return "/".join(quote(part) for part in relative.split("/"))


def find_pages(root: Path) -> list[dict[str, Path | str | None]]:
    html_dir = root / "html"
    image_dir = root / "images"
    html_files = {
        path.stem: path
        for path in html_dir.glob("*.html")
        if path.name.lower() != "index.html"
    } if html_dir.exists() else {}
    image_files = {
        path.stem: path
        for path in image_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    } if image_dir.exists() else {}
    stems = sorted(set(html_files) | set(image_files), key=natural_key)
    return [
        {"stem": stem, "html": html_files.get(stem), "image": image_files.get(stem)}
        for stem in stems
    ]


def first_value(data: dict, keys: list[str], fallback: str = "") -> str:
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return str(value)
    return fallback


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_copy_block(label: str, value: str, copy_id: str) -> str:
    if not value:
        return ""
    return f"""
      <section class="copy-block">
        <div class="section-heading"><h3>{esc(label)}</h3><button data-copy="{copy_id}">复制</button></div>
        <div class="copy-text" id="{copy_id}">{esc(value)}</div>
      </section>"""


def render_page_card(
    page: dict,
    index: int,
    plan: dict[str, str],
    root: Path,
    canvas_width: int,
    canvas_height: int,
) -> str:
    stem = str(page["stem"])
    html_path = page["html"]
    image_path = page["image"]
    page_number = first_value(plan, ["页码", "page", "Page"], f"{index:02d}")
    task = first_value(plan, ["页面任务", "页面职责", "任务", "page_role"], stem)
    source = first_value(plan, ["原始素材", "素材", "evidence"], "")
    layout = first_value(plan, ["版式策略", "版式", "layout"], "")
    if image_path:
        media_url = relative_url(image_path, root)
        media = (
            f'<button class="image-button" data-full="{media_url}" data-name="{esc(stem)}">'
            f'<img src="{media_url}" alt="{esc(task)}" loading="eager"></button>'
        )
        status = '<span class="badge final">已导出 PNG</span>'
    else:
        media_url = relative_url(html_path, root)
        media = (
            f'<iframe class="source-frame" src="{media_url}" title="{esc(task)}" loading="eager" scrolling="no" '
            f'data-width="{canvas_width}" data-height="{canvas_height}"></iframe>'
        )
        status = '<span class="badge draft">HTML 待导出</span>'
    links = []
    if html_path:
        links.append(f'<a href="{relative_url(html_path, root)}" target="_blank">打开 HTML</a>')
    if image_path:
        links.append(f'<a href="{relative_url(image_path, root)}" download>下载图片</a>')
    metadata = "".join(
        f'<p><strong>{esc(label)}</strong>{esc(value)}</p>'
        for label, value in (("素材", source), ("版式", layout)) if value
    )
    return f"""
      <article class="page-card">
        <header><span class="page-number">{esc(page_number)}</span><div><h3>{esc(task)}</h3>{status}</div></header>
        <div class="page-preview" style="aspect-ratio:{canvas_width}/{canvas_height}">{media}</div>
        <div class="page-meta">{metadata}<nav>{''.join(links)}</nav></div>
      </article>"""


def render_asset_rows(manifest, root: Path) -> str:
    if isinstance(manifest, dict):
        assets = manifest.get("assets", [])
    elif isinstance(manifest, list):
        assets = manifest
    else:
        assets = []
    rows = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        asset_id = first_value(asset, ["asset_id", "id"], "未编号")
        file_value = first_value(asset, ["file", "path"], "")
        target = first_value(asset, ["target_page", "page"], "未指定")
        role = first_value(asset, ["content_role", "role", "adjacent_explanation"], "未填写")
        size = first_value(asset, ["original_size"], "")
        if not size and asset.get("width") and asset.get("height"):
            size = f'{asset["width"]}×{asset["height"]}'
        file_label = file_value
        file_path = root / file_value if file_value and not Path(file_value).is_absolute() else Path(file_value) if file_value else None
        if file_path and file_path.exists() and file_path.is_file():
            try:
                file_url = relative_url(file_path, root)
            except ValueError:
                file_label = esc(file_path.name)
            else:
                file_label = f'<a href="{file_url}" target="_blank">{esc(file_value)}</a>'
        else:
            file_label = esc(file_value or "未记录")
        rows.append(
            f"<tr><td>{esc(asset_id)}</td><td>{file_label}</td><td>{esc(size or '未记录')}</td>"
            f"<td>{esc(target)}</td><td>{esc(role)}</td></tr>"
        )
    return "".join(rows)


def build_html(root: Path, output: Path, require_images: bool) -> tuple[str, list[str]]:
    note_path = root / "note.md"
    note = read_text(note_path)
    if not note:
        raise SystemExit("PREVIEW_ERROR note.md is required")
    note_sections = split_note(note)
    requirements = load_json(root / "requirements.json", {})
    manifest = load_json(root / "asset_manifest.json", [])
    brief_values = parse_brief_values(read_text(root / "brief.md"))
    plan_rows = parse_plan_table(read_text(root / "plan.md"))
    pages = find_pages(root)
    if not pages:
        raise SystemExit("PREVIEW_ERROR no HTML pages or exported images found")

    warnings = []
    html_count = sum(bool(page["html"]) for page in pages)
    image_count = sum(bool(page["image"]) for page in pages)
    if plan_rows and len(plan_rows) != len(pages):
        warnings.append(f"页面计划 {len(plan_rows)} 项，实际发现 {len(pages)} 页")
    if require_images and image_count != len(pages):
        warnings.append(f"要求最终图片，但仍有 {len(pages) - image_count} 页未导出")
    assets = manifest.get("assets", []) if isinstance(manifest, dict) else manifest if isinstance(manifest, list) else []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        file_value = first_value(asset, ["file", "path"])
        if not file_value or "://" in file_value:
            continue
        file_path = Path(file_value) if Path(file_value).is_absolute() else root / file_value
        try:
            file_path.resolve().relative_to(root)
        except ValueError:
            warnings.append(f"来源素材位于交付目录外：{asset.get('asset_id', file_path.name)}")
        else:
            if not file_path.is_file():
                warnings.append(f"来源素材文件缺失：{asset.get('asset_id', file_value)}")

    title = note_sections.get("标题") or root.name
    body = note_sections.get("正文", "")
    tags = note_sections.get("标签", "")
    cta = note_sections.get("互动问题", "") or note_sections.get("评论区互动", "")
    mode = requirements.get("mode", "xiaohongshu-package")
    style = requirements.get("style", "未记录")
    canvas = requirements.get("canvas", requirements.get("aspect_ratio", "未记录"))
    canvas_match = re.search(r"(\d+)\s*[x×]\s*(\d+)", str(canvas), flags=re.IGNORECASE)
    canvas_width = int(canvas_match.group(1)) if canvas_match else 1080
    canvas_height = int(canvas_match.group(2)) if canvas_match else 1440
    voice = requirements.get("narrative_voice", "未记录")
    theme = infer_theme(requirements, brief_values, pages, root)
    claim = brief_values.get("一句话主张", "") or brief_values.get("第一眼信息", "")
    visual_anchor = brief_values.get("核心视觉主体", "") or brief_values.get("情绪与质感", "")
    asset_rows = render_asset_rows(manifest, root)
    asset_count = asset_rows.count("<tr>")
    plan_by_number = {}
    for row in plan_rows:
        number = first_value(row, ["页码", "page", "Page"])
        if number:
            plan_by_number[number.lstrip("0") or "0"] = row
    page_cards = []
    for index, page in enumerate(pages, start=1):
        prefix_match = re.match(r"^(\d+)", str(page["stem"]))
        key = str(int(prefix_match.group(1))) if prefix_match else str(index)
        plan = plan_by_number.get(key, plan_rows[index - 1] if index <= len(plan_rows) else {})
        page_cards.append(render_page_card(page, index, plan, root, canvas_width, canvas_height))

    qa_text = read_text(root / "qa.md")
    status_label = "最终图片已齐" if image_count == len(pages) else "仍有页面待导出"
    warning_html = "".join(f"<li>{esc(item)}</li>" for item in warnings)
    theme_css = render_theme_css(theme)
    document = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' rx='4' fill='%23ff5a5f'/%3E%3C/svg%3E">
  <title>{esc(title)} | 小红书交付预览</title>
  <style>
    :root {{ color-scheme: light; --ink:#14213d; --muted:#667085; --line:#dbe2ea; --paper:#f5f7fb; --card:#fff; --accent:#ff5a5f; --blue:#315efb; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif; color:var(--ink); background:linear-gradient(135deg,#f7f9fc,#edf2ff); }}
    button,a {{ font:inherit; }} a {{ color:var(--blue); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
    .shell {{ width:min(1480px,calc(100% - 40px)); margin:0 auto; padding:42px 0 80px; }}
    .hero {{ padding:38px; border:1px solid rgba(255,255,255,.75); border-radius:28px; color:white; background:radial-gradient(circle at 85% 10%,rgba(255,255,255,.18),transparent 30%),linear-gradient(135deg,#1b2a52,#315efb 68%,#6e84ff); box-shadow:0 24px 70px rgba(35,57,120,.22); }}
    .eyebrow {{ margin:0 0 12px; font-size:13px; letter-spacing:.16em; opacity:.8; }} h1 {{ max-width:920px; margin:0; font-size:clamp(30px,4vw,58px); line-height:1.16; }}
    .summary {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:24px; }} .summary span,.badge {{ display:inline-flex; padding:7px 11px; border-radius:999px; font-size:13px; }} .summary span {{ background:rgba(255,255,255,.14); }}
    .dashboard {{ display:grid; grid-template-columns:minmax(0,1.15fr) minmax(320px,.85fr); gap:24px; margin-top:24px; }}
    .panel {{ padding:26px; border:1px solid var(--line); border-radius:22px; background:rgba(255,255,255,.92); box-shadow:0 12px 35px rgba(52,66,105,.08); }}
    .panel h2 {{ margin:0 0 18px; font-size:22px; }} .section-heading {{ display:flex; align-items:center; justify-content:space-between; gap:16px; }} .section-heading h3 {{ margin:0; font-size:15px; }}
    .copy-block + .copy-block {{ margin-top:18px; padding-top:18px; border-top:1px solid var(--line); }} .copy-text {{ margin-top:10px; white-space:pre-wrap; line-height:1.82; color:#344054; }}
    button[data-copy] {{ border:0; border-radius:9px; padding:7px 12px; color:var(--blue); background:#edf2ff; cursor:pointer; }}
    .stats {{ display:grid; grid-template-columns:repeat(2,1fr); gap:12px; }} .stat {{ padding:18px; border-radius:16px; background:var(--paper); }} .stat strong {{ display:block; font-size:28px; }} .stat span {{ color:var(--muted); font-size:13px; }}
    .status {{ margin-top:16px; padding:14px 16px; border-radius:14px; color:#175c36; background:#eaf8f0; }} .warnings {{ color:#8a4b08; background:#fff6e8; }}
    .section-title {{ display:flex; justify-content:space-between; align-items:end; gap:20px; margin:46px 0 18px; }} .section-title h2 {{ margin:0; font-size:28px; }} .section-title p {{ margin:0; color:var(--muted); }}
    .pages {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:22px; align-items:start; }} .page-card {{ overflow:hidden; border:1px solid var(--line); border-radius:22px; background:var(--card); box-shadow:0 12px 36px rgba(52,66,105,.09); }}
    .page-card header {{ display:flex; gap:14px; align-items:flex-start; padding:18px; }} .page-card h3 {{ margin:0 0 8px; font-size:17px; line-height:1.45; }} .page-number {{ flex:0 0 auto; display:grid; place-items:center; width:38px; height:38px; border-radius:12px; color:white; background:var(--ink); font-weight:700; }}
    .badge {{ padding:5px 9px; }} .badge.final {{ color:#175c36; background:#eaf8f0; }} .badge.draft {{ color:#8a4b08; background:#fff3dc; }}
    .page-preview {{ position:relative; overflow:hidden; background:#e8edf5; }} .page-preview img {{ width:100%; height:100%; border:0; object-fit:cover; }} .page-preview iframe {{ position:absolute; inset:0 auto auto 0; border:0; pointer-events:none; transform-origin:top left; }} .image-button {{ display:block; width:100%; height:100%; padding:0; border:0; cursor:zoom-in; background:none; }}
    .page-meta {{ min-height:104px; padding:16px 18px 18px; }} .page-meta p {{ margin:0 0 8px; color:var(--muted); font-size:13px; line-height:1.5; }} .page-meta strong {{ margin-right:8px; color:var(--ink); }} .page-meta nav {{ display:flex; gap:16px; margin-top:12px; font-size:14px; }}
    details.panel {{ margin-top:24px; }} summary {{ cursor:pointer; font-weight:700; }} table {{ width:100%; margin-top:18px; border-collapse:collapse; font-size:13px; }} th,td {{ padding:11px 9px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }} th {{ color:var(--muted); }}
    pre {{ max-height:480px; overflow:auto; padding:18px; border-radius:14px; white-space:pre-wrap; color:#344054; background:var(--paper); line-height:1.65; }}
    dialog {{ width:min(1000px,92vw); padding:0; border:0; border-radius:20px; box-shadow:0 30px 100px rgba(0,0,0,.35); }} dialog::backdrop {{ background:rgba(10,18,38,.78); }} dialog img {{ display:block; width:100%; max-height:88vh; object-fit:contain; background:#111827; }} .dialog-bar {{ display:flex; justify-content:space-between; align-items:center; padding:12px 16px; }} .dialog-bar button {{ border:0; padding:8px 13px; border-radius:9px; cursor:pointer; }}
    @media (max-width:850px) {{ .shell {{ width:min(100% - 24px,1480px); padding-top:18px; }} .hero {{ padding:26px; border-radius:22px; }} .dashboard {{ grid-template-columns:1fr; }} .panel {{ padding:20px; }} .section-title {{ align-items:start; flex-direction:column; }} table {{ display:block; overflow:auto; }} }}
  </style>
  {theme_css}
</head>
<body>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">XIAOHONGSHU DELIVERY DASHBOARD · {esc(theme['label'])}</p>
      <h1>{esc(title)}</h1>
      {f'<p class="hero-context"><strong>核心主张</strong>{esc(claim)}</p>' if claim else ''}
      {f'<p class="hero-context"><strong>视觉锚点</strong>{esc(visual_anchor)}</p>' if visual_anchor else ''}
      <div class="summary"><span>{esc(mode)}</span><span>{esc(style)}</span><span>{esc(canvas)}</span><span>{esc(voice)}</span><span>{esc(theme['label'])}</span></div>
    </section>
    <section class="dashboard">
      <article class="panel">
        <h2>发布文案</h2>
        {render_copy_block('标题', title, 'copy-title')}
        {render_copy_block('正文', body, 'copy-body')}
        {render_copy_block('标签', tags, 'copy-tags')}
        {render_copy_block('互动引导', cta, 'copy-cta')}
      </article>
      <aside class="panel">
        <h2>交付状态</h2>
        <div class="stats"><div class="stat"><strong>{len(pages)}</strong><span>页面总数</span></div><div class="stat"><strong>{image_count}</strong><span>最终图片</span></div><div class="stat"><strong>{html_count}</strong><span>HTML 页面</span></div><div class="stat"><strong>{asset_count}</strong><span>来源素材</span></div></div>
        <div class="status">{esc(status_label)}</div>
        {f'<ul class="status warnings">{warning_html}</ul>' if warnings else ''}
      </aside>
    </section>
    <div class="section-title"><h2>图片序列</h2><p>点击最终图片可放大查看，单页可独立打开或下载。</p></div>
    <section class="pages">{''.join(page_cards)}</section>
    <details class="panel"><summary>来源素材映射，共 {asset_count} 项</summary><table><thead><tr><th>编号</th><th>文件</th><th>尺寸</th><th>目标页面</th><th>作用或说明</th></tr></thead><tbody>{asset_rows}</tbody></table></details>
    <details class="panel"><summary>质量检查记录</summary><pre>{esc(qa_text or 'qa.md 尚未填写')}</pre></details>
  </main>
  <dialog id="viewer"><div class="dialog-bar"><strong id="viewer-name"></strong><button id="viewer-close">关闭</button></div><img id="viewer-image" alt="放大预览"></dialog>
  <script>
    document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {{
      const text = document.getElementById(button.dataset.copy).innerText;
      try {{ await navigator.clipboard.writeText(text); }} catch (_) {{ const area=document.createElement('textarea'); area.value=text; document.body.appendChild(area); area.select(); document.execCommand('copy'); area.remove(); }}
      const old=button.textContent; button.textContent='已复制'; setTimeout(() => button.textContent=old, 1200);
    }}));
    const viewer=document.getElementById('viewer'); const viewerImage=document.getElementById('viewer-image'); const viewerName=document.getElementById('viewer-name');
    document.querySelectorAll('[data-full]').forEach(button => button.addEventListener('click', () => {{ viewerImage.src=button.dataset.full; viewerName.textContent=button.dataset.name; viewer.showModal(); }}));
    document.getElementById('viewer-close').addEventListener('click', () => viewer.close()); viewer.addEventListener('click', event => {{ if(event.target===viewer) viewer.close(); }});
    const fitSourceFrames=() => document.querySelectorAll('.source-frame').forEach(frame => {{ const width=Number(frame.dataset.width); const height=Number(frame.dataset.height); const scale=frame.parentElement.clientWidth/width; frame.style.width=`${{width}}px`; frame.style.height=`${{height}}px`; frame.style.transform=`scale(${{scale}})`; }});
    fitSourceFrames(); window.addEventListener('resize', fitSourceFrames);
  </script>
</body>
</html>
"""
    return document, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path, help="Xiaohongshu package directory")
    parser.add_argument("--output", default="index.html", help="Output file relative to the package root")
    parser.add_argument("--require-images", action="store_true", help="Fail when any page has no exported image")
    args = parser.parse_args()

    root = args.output_dir.resolve()
    if not root.is_dir():
        print(f"PREVIEW_ERROR directory not found: {root}")
        return 1
    output = (root / args.output).resolve()
    try:
        output.relative_to(root)
    except ValueError:
        print("PREVIEW_ERROR output must stay inside the package directory")
        return 1

    document, warnings = build_html(root, output, args.require_images)
    output.write_text(document, encoding="utf-8")
    pages = find_pages(root)
    image_count = sum(bool(page["image"]) for page in pages)
    if args.require_images and warnings:
        print(f"PREVIEW_FAIL pages={len(pages)} images={image_count} warnings={len(warnings)} output={output}")
        return 1
    print(f"PREVIEW_PASS pages={len(pages)} images={image_count} warnings={len(warnings)} output={output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
