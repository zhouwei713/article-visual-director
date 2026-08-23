# 路由示例

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

