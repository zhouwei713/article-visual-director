# 路由示例

这些案例用于复现决策过程。成图案例见 README，具体内容仍以当前文章和用户约束为准。

## 公众号 AI 封面配方

输入：AI 视频提示词教程，核心关系是文字指令逐步变成镜头、动作和拍摄方案。

决策：`cover-only`，公众号 `2.35:1`，`editorial-system-landscape` 结构，电影化编辑视觉。画面用纸页、胶片、摄影轨道和暖色放映光表达转换，短标题使用“提示词变成拍摄方案”。

契约要点：

```json
{
  "mode": "cover-only",
  "platform": "wechat",
  "asset_type": "cover",
  "aspect_ratio": "2.35:1",
  "style": "high-concept-poster",
  "visible_text": true,
  "text_policy": "editorial-hierarchy",
  "exact_text": "提示词变成拍摄方案",
  "visual_mode": "cinematic-editorial-tech",
  "allow_textless_fallback": false
}
```

预期结果：第一眼识别标题和影视生产语境，第二眼看懂从提示词到镜头序列的关系。禁止缩成一台泛化电脑或一句口号。

## 小红书 AI 封面与教程内页配方

输入：中文短剧制作海外版的个人复盘，核心钩子是普通创作者通过 AI 完成跨语言改造。

决策：`xiaohongshu-tutorial`，封面用 `imagegen` 表达人物行动、画面转换和跨文化张力，内页用 HTML 承载步骤、对比、截图解释与边界。发布文案使用 `author-first-person`。

封面契约要点：

```json
{
  "mode": "xiaohongshu-cover",
  "platform": "xiaohongshu",
  "asset_type": "xiaohongshu-cover",
  "render_method": "imagegen",
  "aspect_ratio": "3:4",
  "visible_text": true,
  "text_policy": "short-exact",
  "exact_text": "短剧出海 没有门槛了",
  "impact_mechanism": "type-subject-interlock",
  "allow_textless_fallback": false
}
```

预期结果：封面承担点击钩子，内页按问题、步骤、证据、结果和风险分工。截图事实保持原样，制作说明只进入交付记录。

## 观点型概念海报配方

输入：讨论一个系统如何把分散能力连接成稳定工作流。核心关系是孤立模块通过唯一通路形成闭环。

决策：`cover-only`，`high-concept-poster` 风格，`conceptual-tension` 结构。使用一个断开的巨大环和穿过缺口的明亮路径，文字与缺口共享视觉重心。

预期结果：去掉标题后仍能读出连接、缺口和闭环。画面不依赖工作台、发光电脑或功能列表。

## 公众号完整视觉包

用户请求：

```text
给这篇 AI 工具介绍文章做公众号封面和四张正文配图。
```

路由：`full-package`

默认建议：

1. `product-hero` 加 `single-hero`
2. `warm-workbench-map` 加 `system-landscape`
3. `tactile-interface-collage` 加 `evidence-collage`

选择后生成一张宽幅封面。正文配图根据文章内容选择总览、流程、对比和证据卡，沿用主色与材质。

## X 观点文章封面

用户请求：

```text
这篇文章讨论 AI 让内容越来越相似，直接给我做一张 X 首图。
```

路由：`cover-only` 加快速模式

优先方向：`concept-metaphor` 加 `conceptual-tension`。使用一个可解释的冲突、强轮廓和大面积留白。默认避免长标题，把完整标题保留在帖子正文。

## 教程正文配图

用户请求：

```text
给这篇安装教程配图，不要封面。
```

路由：`illustrations-only`

优先方向：`warm-workbench-map`。默认采用 `balanced` 密度，使用总览图、安装流程和验证清单。每张图必须对应具体章节和真实步骤。

## 只要提示词

用户请求：

```text
帮我分析文章并写公众号封面提示词，不要生成图片。
```

路由：`prompt-only`

完成视觉简报、方向选择和提示词保存，交付准确文件路径和完整提示词。质量状态标记为 `未验证`。

## 窄范围修改

用户请求：

```text
保留第二版构图，把主色改成黑红，标题换成“AI 同质化”。
```

路由：`revision`

保留主体、场景、层级、镜头和留白，只修改配色与标题字段。生成新版本，保留旧候选。
