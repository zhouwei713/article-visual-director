# prompt-led-cover 回归样例

## 输入特征

用户提供完整的封面生成提示词，明确指定：

1. 高级概念海报
2. `2.35:1`
3. 主文字必须出现在画面中
4. 主文字成为第一视觉焦点
5. 不使用固定颜色、固定构图和固定元素
6. 图像元素服务于文字隐喻

## 预期契约

```json
{
  "mode": "prompt-led-cover",
  "style": "high-concept-poster",
  "aspect_ratio": "2.35:1",
  "visible_text": true,
  "text_policy": "short-exact",
  "allow_textless_fallback": false,
  "palette_policy": "topic-derived",
  "user_prompt_locked": true
}
```

## 必须阻断的回归

1. 将比例改成 `5:2` 主图后再裁切
2. 把 `short-exact` 改成 `reserved-title-zone` 或 `textless`
3. 把高级概念海报改成 `product-hero`、`dark-system-pulse` 或硬件展示
4. 自动固定深色、金属、霓虹、模块、线缆或工作台等视觉模板
5. 用户要求文字出现时，提示词却写入无字指令

## 编辑型科技封面回归

当用户提供参考图，或明确反馈单一口号海报信息不足时，必须允许：

1. `editorial-hierarchy` 文字策略
2. 文章项目名、二级副标题和少量真实模块标签
3. 电影化系统场景、入口光、模块结构和远景人物
4. 参考图提供的标题层级、空间重心、光线和信息密度

必须阻断：

1. 把文章封面再次压缩成一句口号和一个装饰物
2. 因为担心错字而删除项目名、文章标题或核心模块
3. 把参考图的编辑型场景改成米白纸张、单一几何物体或无字背景

结构校验通过只代表提示词契约一致。实际图片仍需按 `quality-gates.md` 检查主文字、隐喻、模板感和视觉质量。
