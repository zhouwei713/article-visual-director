# 文章视觉导演

> 把文章里的核心主张、输入、动作、输出和边界，整理成可读、可检查、可交付的视觉资产。

`article-visual-director` 是一个 Codex Skill，支持公众号、X Article 和小红书的封面、正文配图、多页图文、概念海报，以及信息密集型小红书教程页面。

## 输出示例

用户输入：

```text
使用 $article-visual-director，把一篇关于 AI 写作 Skill 的文章做成小红书教程图文。
```

Skill 会先建立视觉简报和页面计划，再按内容选择图像生成或 HTML 确定性渲染路线。教程型小红书默认输出：

```text
note.md
brief.md
plan.md
requirements.json
html/*.html
images/*.png
qa.md
```

## 它解决什么

常见问题与处理方式：

| 常见问题 | Skill 的处理方式 |
| --- | --- |
| 封面只剩一句口号 | 从文章主张、冲突、视觉锚点和标题层级重新组织画面 |
| 配图和文章内容脱节 | 映射具体输入、动作、输出、场景和边界 |
| 小红书卡片文字不稳定 | 教程模式先制作 HTML 或 React 页面，再由浏览器导出 PNG |
| 多页图文像重复模板 | 为每页设置独立阅读任务、证据和视觉关系 |
| 生成结果无法复核 | 保存需求契约、计划、源文件或提示词，并检查实际产物 |

## 适用场景

支持以下平台和任务：

1. 公众号封面与正文配图
2. X Article 横幅与正文插图
3. 小红书封面和多页图文
4. 小红书教程型 HTML 图文
5. 概念海报与参考图驱动的视觉方向
6. 提示词编写、契约校验和成图质量检查

## 工作模式

主要路由包括：

| 模式 | 交付 |
| --- | --- |
| `cover-only` | 单张封面与提示词 |
| `full-package` | 封面、正文配图、平台变体和检查结果 |
| `xiaohongshu-cover` | 小红书 3:4 封面 |
| `xiaohongshu-carousel` | 小红书多页图文与逐页资产 |
| `xiaohongshu-tutorial` | HTML 或 React 教程页面与 3:4 PNG |
| `prompt-only` | 可复制的完整提示词，不调用生图工具 |
| `revision` | 保留已选视觉方向，修改指定维度 |

## 小红书教程模式

`xiaohongshu-tutorial` 适合步骤、方法、工具拆解、框架说明和信息密集型知识卡片。

它默认使用 HTML 优先路线：

1. 先拆解文章信息，确定每页的标题、输入、动作、输出和边界。
2. 使用 CSS、内嵌 SVG 和本地字体制作固定 1080×1440 页面。
3. 通过浏览器导出准确 3:4 的 PNG。
4. 分别检查 HTML 页面和最终 PNG 的文字、裁切、溢出、层级和缩略图可读性。

该模式默认不调用图片生成模型，适合需要保留较多中文信息的教程内容。

## 安装

在 Windows PowerShell 中复制完整 Skill 目录：

```powershell
git clone https://github.com/zhouwei713/article-visual-director.git
Copy-Item -Recurse -LiteralPath ".\article-visual-director" -Destination "$env:USERPROFILE\.codex\skills\"
```

预期入口路径：

```text
%USERPROFILE%\.codex\skills\article-visual-director\SKILL.md
```

安装后开启新任务，再使用 `$article-visual-director` 调用。

## 使用

先提供文章文件、正文、标题与摘要，或文章加参考图，再说明目标平台、资产范围和比例。没有明确指定风格时，Skill 会根据内容类型提出视觉方向；指定 `xiaohongshu-tutorial` 时，默认先生成 HTML 页面，再导出 PNG。

## 调用示例

公众号完整视觉包：

```text
使用 $article-visual-director，为这篇文章生成公众号封面和正文配图，封面保留标题层级，正文图解释文章中的机制和边界。
```

小红书教程图文：

```text
使用 $article-visual-director 的 xiaohongshu-tutorial 模式，把这篇教程先做成信息丰富的 HTML 页面，再转换成 3:4 PNG。
```

只要提示词：

```text
使用 $article-visual-director 的 prompt-only 模式，只输出封面和正文配图提示词，不生成图片。
```

## 仓库结构

| 路径 | 用途 |
| --- | --- |
| `SKILL.md` | 入口说明、路由和核心工作流 |
| `agents/openai.yaml` | Codex 界面名称和默认调用词 |
| `references/` | 平台策略、风格库、页面结构和质量规则 |
| `scripts/validate_prompt_contract.py` | 校验图片提示词与需求契约 |
| `scripts/render_html_pages.ps1` | 将教程 HTML 页面渲染为 PNG |

## 验证状态与边界

已执行：

1. `quick_validate.py` 结构校验通过。
2. 发布校验包含 UTF8、BOM、敏感信息、凭据模式和文件清单检查。
3. 教程 HTML 路线已用浏览器导出 1080×1440 PNG 并完成视觉检查。

图片生成模型的审美质量取决于具体模型输出，提示词契约通过不等同于每张图片都自动通过视觉检查。Skill 只负责文章到视觉资产的规划、生成、渲染和检查，不包含发布自动化、账号登录、Cookie 管理、定时发布、数据采集或数据运营。

## 设计理念

封面负责第一眼理解，正文页面负责补充关系、证据和行动路径。每一张图都要回答一个读者问题，并保留文章中可以核验的具体术语与边界。

## License

本项目使用 [MIT License](./LICENSE)。
