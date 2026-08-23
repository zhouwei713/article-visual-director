---
name: article-visual-director
description: Plan and produce coordinated article covers, inline illustrations, concept posters, and visual packages for WeChat, X, and Xiaohongshu. Use for 公众号封面、小红书封面、小红书多页图文、教程型小红书 HTML 图文、文章配图、社交传播图、reference-matched covers, or prompt-led revisions. Preserve explicit aspect ratio, title hierarchy, text visibility, style, and prohibitions. For article visuals, map concrete inputs, actions, outputs, use cases, and risks into the image plan instead of generic labels. Save prompts or HTML sources, validate contracts, render raster images, and inspect actual outputs. Supports cover-only, prompt-led-cover, reference-led-cover, illustrations-only, full-package, xiaohongshu-cover, xiaohongshu-carousel, xiaohongshu-tutorial, xiaohongshu-package, prompt-only, and revision workflows.
---

# 文章视觉导演

把文章转化为一套有传播目标、视觉主张和系列一致性的图片。让封面承载一个核心主张和一个视觉钩子，只在正文理解确有收益的位置安排配图。

## 当前范围边界

本 Skill 只负责文章内容到视觉资产的规划、提示词、图片、图文卡片和质量检查。小红书扩展不包含发布自动化、账号登录、扫码登录、Cookie 管理、定时发布、数据采集、数据运营或发布后复盘。

## 约束优先级与提示词保真

按以下顺序处理信息：

1. 当前用户明确指定的比例、主文字、文字可见性、风格、构图和禁止项
2. 用户提供的原始视觉提示词
3. 用户提供的附件、文章和参考图
4. 本 Skill 的平台策略、风格库和默认工作流
5. 助手对缺失信息的推断

后续规则只能补充缺失信息，不能覆盖前面的硬约束。用户提供完整视觉提示词时，保存原文到 `source-prompt.md`，并进入 `prompt-led-cover` 路由。

生成前建立 `requirements.json`，至少记录 `mode`、`aspect_ratio`、`style`、`visible_text`、`text_policy`、`exact_text`、`palette_policy` 和 `allow_textless_fallback`。提示词元数据和正文必须与它一致。

如果编译结果改变了用户指定的比例、主文字可见性、主风格、输出类型或禁止项，立即阻断生成并修正。禁止用“跨平台适配”“模型容易错字”“统一系列风格”或类似理由静默改变用户约束。

参考图承担视觉方向证据，不自动替代用户的内容约束。参考图显示了标题层级、场景叙事、光线、空间深度或信息密度时，提取这些高层规则并重新组织。禁止把参考图默认压缩成单一口号、单个物体或无字背景。

## 资源路由

按任务需要读取以下文件，全部直接从本文件进入，避免继续追索更深层引用。

1. 涉及平台、比例或裁切时，读取 `references/platform-strategies.md`。
2. 分析账号调性、参考图或系列一致性时，读取 `references/visual-dna.md`。
3. 推荐或应用视觉风格时，读取 `references/style-library.md`。
4. 选择 `high-concept-poster` 风格时，额外读取 `references/high-concept-poster.md`。
5. 科技文章封面需要标题层级、系统场景或参考图复现时，读取 `references/editorial-tech-cover.md`。
6. 制作封面时，读取 `references/cover-archetypes.md`。
7. 制作正文配图时，读取 `references/illustration-archetypes.md`。
8. 写任何成图提示词前，读取 `references/prompt-compiler.md`。
9. 生成完成后，读取 `references/quality-gates.md` 并检查实际图片。
10. 小红书封面或多页图文时，读取 `references/xiaohongshu-strategies.md`、`references/xiaohongshu-cover-archetypes.md` 和 `references/xiaohongshu-carousel-structures.md`。
11. 只有在任务路由仍不明确时，读取 `references/examples.md`。

## 任务路由

先把请求归入一种模式。

| 模式 | 交付 |
|---|---|
| `cover-only` | 一张主封面及其提示词 |
| `prompt-led-cover` | 以用户提供的完整视觉提示词为主协议，保留原始硬约束并生成一张或多张变体 |
| `reference-led-cover` | 以用户提供的参考图提取版式、光线、空间和信息密度，同时保留文章内容与用户硬约束 |
| `illustrations-only` | 配图计划、独立提示词和正文配图 |
| `full-package` | 主封面、正文配图、平台变体和全部提示词 |
| `xiaohongshu-cover` | 小红书 3:4 主封面、封面提示词和缩略图检查 |
| `xiaohongshu-carousel` | 小红书 3:4 多页图文、逐页内容结构、逐页提示词和图片 |
| `xiaohongshu-tutorial` | 以 HTML 或 React 为源文件制作信息密集的小红书教程页，再渲染为 3:4 PNG |
| `xiaohongshu-package` | 小红书封面、多页图文、发布文案元数据和完整质量检查 |
| `prompt-only` | 完整可复制提示词，不调用生图工具 |
| `revision` | 保留已选视觉方向，只修改用户点名的维度 |

用户同时提出封面和配图时，选择 `full-package`。用户只给出文章且没有说明任务范围时，优先询问要封面、正文配图还是完整视觉包。

当用户指定小红书时，使用小红书专用路由。用户要求教程、步骤、方法、框架、工具对比或信息密集的知识卡片时，选择 `xiaohongshu-tutorial`，默认先制作 HTML 或 React 页面，再渲染为 PNG，不调用图片生成模型。`xiaohongshu-package` 只交付图片、提示词、页面计划、标题正文标签等文案元数据和检查结果，不执行发布。

## 交互规则

1. 用户提供参考图并要求接近参考图的视觉效果时，进入 `reference-led-cover`。如果同时提供完整提示词，完整提示词继续作为内容与硬约束协议。
2. 用户提供完整提示词，或提示词中出现“高级概念海报”“核心主文字”“第一眼看到主题”“第二眼理解隐喻”等明确协议时，直接进入 `prompt-led-cover`，不重新选择主风格和文字策略。
3. 当平台或视觉方向缺失时，只进行一次简短确认。给出三个编号方向，把推荐项放在第一位，并让用户可以回复数字。
4. 当用户说“直接出图”“不用问”“自动决定”“按默认生成”或同义表达时，进入快速模式。说明采用的平台、比例、风格、配图密度和文字策略，然后继续。
5. 当用户已经给出平台、比例和明确风格时，直接继续。
6. 在同一任务的后续修改中，保留已选择的平台、构图、色彩、人物、场景和视觉语言，只修改用户点名的内容。
7. 不承诺爆款、点击率或传播结果。描述视觉钩子、移动端可读性和传播潜力。

确认消息使用以下紧凑格式：

```text
发布位置：[平台或待选]

1. [推荐方向]：[一句视觉主张]
2. [方向二]：[一句视觉主张]
3. [方向三]：[一句视觉主张]

回复平台和数字即可，也可以回复“自动决定”。
```

## 核心工作流

### 1. 获取并保护素材

接受文章文件、粘贴正文、标题加摘要、主题草稿或参考图片。读取用户提供的文件，不通过宽泛目录扫描猜测来源。

如果文章链接无法读取，请用户粘贴正文，或提供导出的 HTML、PDF、Markdown、Word 文件或截图。不要用未取得的正文继续假装分析。

参考图片有本地路径时，记录准确路径和用途。对话图片没有可用路径时，从可见内容提取风格、配色和构图描述。只有文件真实存在时，才在提示词元数据中记录引用路径。

### 2. 建立视觉简报

从文章中提取并写入 `brief.md`：

1. 原始标题与可选视觉短标题
2. 一句话核心主张
3. 目标读者与发布位置
4. 读者第一眼应该理解的主题
5. 第二眼应该发现的冲突、洞察或隐喻
6. 核心视觉主体
7. 情绪、质感和颜色倾向
8. 可视化的数据、流程、对比和框架
9. 必须保留与禁止出现的元素
10. 文字策略和参考图用途

不要把标题中的修辞机械地画成字面场景。识别修辞背后的真实概念，再选择视觉表达。

如果用户提供了完整提示词，额外记录原始提示词、不可变约束、允许变化的字段、禁止变化的字段和冲突处理结果。原始提示词中的“必须出现”“只能出现”“严格使用”“不要出现”等表达均视为硬约束。只有用户明确写出“只允许出现某一句文字”时，才把它解释为画面唯一文字。若用户要求文章封面，默认建立主标题、副标题、核心概念和辅助标签的层级，不因错字风险删除文章识别信息。

将画面文字拆成四层：一级主标题、二级文章标题或副标题、三级文章关键词、四级解释性文案。公众号可以使用前三级，X Article 默认保留前两级和少量关键词。每层文字都必须来自文章、用户提示词或参考图中可确认的内容，禁止编造随机标签。

### 3. 选择平台、风格和视觉结构

先读取平台策略和视觉基因，再从原创风格库中推荐三个方向。每个方向必须同时包含：

1. 风格编号与名称
2. 一个主要视觉钩子
3. 一个封面结构或配图结构
4. 一句与文章内容直接相关的理由

封面只采用一种主风格和一种主要结构。完整视觉包可以让正文配图使用同一风格的简化表达。

用户明确要求高级海报、概念海报或以主文字驱动的极简海报时，必须选择 `high-concept-poster`。用户提供完整提示词时，不得用 `product-hero`、`dark-system-pulse`、`warm-workbench-map` 或其他内容匹配结果替换它。参考图显示科技文章的编辑型信息层级时，可以在 `high-concept-poster` 之下使用 `cinematic-editorial-tech` 视觉模式和 `editorial-system-landscape` 结构。把构图结构作为组织提示，禁止把它固化为重复模板。

用户要求多个高概念海报版本时，保持比例、主文字、文字可见性、概念海报风格和禁止项不变，只改变主要视觉关系、隐喻主体、尺度关系、配色逻辑或构图方向。多个版本不能只是同一套产品硬件换位置。

### 4. 规划资产

把计划写入 `plan.md`。每项资产记录：

1. 资产编号和用途
2. 平台与比例
3. 文章位置
4. 要解决的传播或理解问题
5. 视觉主体和结构
6. 风格、配色与文字策略
7. 文件名

正文配图默认采用 `balanced` 密度，共三至五张。短文或单一观点文章可降为一至两张。每张配图都必须有明确的信息功能。

小红书多页图文使用独立的页面计划。知识型文章默认五至八页，短内容可以使用三至五页，信息密集型内容可以扩展到九页。每页只承担一个主要任务，并记录 `page_role`、`information_answer`、`exact_text`、`visual_anchor`、`evidence`、`aspect_ratio` 和 `safe_crop_zone`。默认页面推进为：封面钩子、问题确认、核心观点、机制或步骤、案例或证据、边界或风险、行动建议、互动问题。页面数量必须服从文章信息量，禁止为了凑页数重复装饰。

小红书封面和卡片默认使用 `3:4`，推荐输出尺寸为 `1080x1440`。可以按内容选择 `1:1` 方形卡片或 `16:9` 机制图，但必须在简报、计划、需求契约和提示词元数据中分别记录比例。封面额外记录 `click_hook`、`visual_anchor`、`information_density` 和 `thumbnail_readability`。

文字密集型页面可以选择确定性卡片渲染路线，例如 HTML 或 React 页面渲染后导出 PNG。该路线只用于保证标题、数字、表格和流程文字的可读性，不改变当前 Skill 的图片生成和视觉检查流程，也不引入发布或登录能力。

当路由为 `xiaohongshu-tutorial` 时，确定性渲染路线升级为默认路线。教程页先写入 `html/`，使用 CSS、内嵌 SVG 和本地可用字体表达结构、流程、对比和边界，再通过浏览器导出 `images/` 中的 PNG。每页只承担一个主要问题，但必须同时呈现具体输入、关键动作、输出结果和适用边界。不要为了塞入更多文字而缩小字号，应通过增加页面或拆分模块保持移动端可读性。详细规则见 `references/xiaohongshu-tutorial-html.md`。

教程型小红书默认使用八至十二页。每个 Skill、方法或工具至少保留“解决什么、怎么用、交付什么、注意什么”四个信息块。路线总览页还要展示上游输出如何交给下游，行动页要给出读者可以立即执行的第一步。

### 4.1 建立文章信息证据映射

在选择版式和写提示词之前，为每张正文图建立一行内容证据映射，至少包含：

1. 文章位置和读者问题
2. 具体输入或对象
3. 关键动作、关系或决策点
4. 输出、结果或可观察变化
5. 适用场景、限制或风险
6. 来自原文的准确术语和短标签

默认优先使用 `input → action → output → boundary` 的压缩结构。教程可以表现为过程路径，系统文章可以表现为模块关系，产品文章可以表现为界面证据，观点文章可以表现为对照或隐喻。不要把每一张图都压成“标题、几个图标、三步流程、底部口号”。

总览图至少要同时包含文章的核心机制、读者行动路径和一个现实边界。章节图至少要包含两个文章专属术语、一个动作关系和一个结果或判断。若文章明确写出限制、风险或适用范围，至少保留一个边界标签。

### 4.2 信息不足时的修订纪律

如果用户反馈“配图和原图信息差不多”“总结不够”“看不出文章内容”，先重写内容证据映射和 `information answer`，再调整版式。保留已确认的视觉基因，但不能只改标题、颜色、箭头或卡片位置。新版本提示词必须写出新增的文章专属输入、动作、输出或边界，并使用新文件名保留旧候选。

### 5. 建立输出目录

文章有文件路径时，默认使用：

```text
{article-dir}/article-visuals/{topic-slug}/
```

输入是粘贴内容时，默认使用：

```text
{cwd}/article-visuals/{topic-slug}/
```

目录结构：

```text
article-visuals/{topic-slug}/
  source-prompt.md
  requirements.json
  source.md
  brief.md
  plan.md
  prompts/
    01-cover.md
    02-illustration-{slug}.md
  references/
  images/
    01-cover.png
    02-illustration-{slug}.png
```

只有用户提供原始视觉提示词时创建 `source-prompt.md`。创建 `requirements.json` 记录硬约束。只有粘贴内容时创建 `source.md`。只有参考文件真实存在时创建 `references/`。如果目标目录已存在，添加时间戳或递增编号，保留旧产物。

### 6. 编译并保存提示词

在任何生图调用之前，按 `references/prompt-compiler.md` 为每项资产写完整提示词。禁止把临时行内提示词直接交给生图工具。

保存提示词后运行 `scripts/validate_prompt_contract.py`。校验失败时停止，不得调用生图工具。至少检查比例、主风格、主文字、文字策略、文字可见性和禁止的降级路线。

提示词文件必须包含以下元数据：

```yaml
---
asset_id: 01
asset_type: cover
platform: wechat
aspect_ratio: 2.35:1
style: product-hero
text_policy: short-exact
visible_text: true
exact_text: ""
output: images/01-cover.png
---
```

仅在引用文件存在时加入 `references` 字段。把文章中的真实术语、数字、流程名称和短句写进提示词，禁止使用空泛占位词。

### 7. 生成图片

用户要求 `prompt-only` 时停止在提示词交付。

需要成图时，按以下顺序选择后端：

1. 用户当前请求指定的图片工具
2. 当前运行环境提供的原生位图生成工具，Codex 环境优先使用 `imagegen`
3. 唯一可用的其他位图生成工具
4. 没有可用位图工具时，说明限制并交付提示词

生成前必须确认提示词契约检查通过。用户要求可见文字时，禁止使用 `textless`、`reserved-title-zone` 或“画面不出现任何可见文字”作为替代策略，除非用户明确批准后续人工排字。

当路由为 `xiaohongshu-tutorial` 时，HTML、React、CSS、Canvas 和内嵌 SVG 是页面源文件，不属于替代成图。必须先保存可复用的页面源文件，再使用浏览器渲染为最终 PNG。该路由默认不调用 `imagegen`，并且需要同时检查 HTML 页面和导出的 PNG。其他路由仍然禁止用 SVG、HTML、Canvas 或程序化绘图替代用户明确要求的位图生成。多张图片优先使用工具原生批量能力，其次并行调用，每批最多四张。渲染失败时只重试失败项一次。

### 8. 检查真实产物

生成后必须打开并检查实际图片，按 `references/quality-gates.md` 完成缩略图、裁切、文字、内容、风格和人物质量检查。没有检查成图时，只能报告提示词或调用已完成，不能声称视觉质量通过。

对于 `xiaohongshu-tutorial`，额外检查 HTML 页面是否存在文字溢出、字体回退异常、卡片重叠、流程断裂、SVG 图标缺失和本地资源加载失败，并检查 PNG 是否仍为准确的 3:4 比例、标题层级清楚、缩略图可读、正文信息完整。记录 HTML 源文件检查和 PNG 实际视觉检查两项结果。

文字错误、裁切错误或构图失败时，创建新的提示词版本和新的图片文件。保留旧候选用于比较。禁止通过程序化覆盖方式修补错误文字。

分别记录“提示词契约检查”和“实际视觉检查”。高概念海报若缺少要求出现的主文字，或画面退化为产品广告、PPT 封面、硬件展示或固定模板，直接判定失败。

### 9. 完成交付

报告以下内容：

1. 采用的平台、风格和视觉主张
2. 生成数量和实际通过质量检查的数量
3. 图片、提示词、简报和计划的准确路径
4. 失败项、重试结果和仍未验证的部分
5. 提示词契约检查状态和实际视觉检查状态
6. 若文章文件允许修改，给出或插入相对路径 Markdown 图片引用

## 修改纪律

执行窄范围修改。用户要求换标题时保留构图、主体、场景、配色和风格。用户要求换平台时优先重构裁切和阅读路径，保持视觉基因。用户要求加强视觉冲击时，把一个决定性的主体、距离变化、色彩冲突或比例反差放进第一眼阅读区域。

## 原创与人物边界

把外部仓库、参考图片和现有封面当作方向证据，提取高层视觉特征并重新组织。禁止复制外部提示词正文、独特风格说明、示例文案或整套命名。

原创人物避免可识别的真实人物、著名角色、品牌吉祥物、具体影视作品和在世艺术家风格。人物外观可能显得年轻时，明确设定为成年。人物内容保持完整遮盖、非露骨和适合公开文章封面。
