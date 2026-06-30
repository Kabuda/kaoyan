# Doubao 图片分析与每日复盘设计文档

## 背景

当前系统已经支持每日计划、学习计时、学习记录和周复盘。新目标是在每次计时结束时上传本次完成的题目图片，用 Doubao 视觉模型分析图片内容，并把分析结果沉淀到学习记录里；每日复盘时，可以基于当天所有学习记录和图片分析，总结今日完成内容、薄弱点和明日建议。

第一版不做题库、OCR 校对、自动批改分数或异步任务队列。目标是让学习闭环变成：

计时任务 -> 结束计时 -> 上传题目图片 -> Doubao 分析 -> 写入记录 -> 每日复盘汇总。

## 功能范围

### 计时结束上传图片

计时页在结束计时时增加图片上传入口，支持上传多张题目图片。图片会随结束计时请求一起提交。后端完成三件事：

1. 结束当前计时，生成 `StudyRecord`。
2. 保存图片到本地 `uploads/record-images/`。
3. 调用 Doubao 视觉模型分析图片，生成结构化结果并写入 `StudyRecordImage`。

如果没有配置 Doubao API Key，系统不会阻断结束计时。它会保存图片并写入一条 `skipped` 状态的分析记录，提示需要配置模型环境变量。

### 已有记录补传图片

记录页后续可以给已有学习记录补传题目图片。第一版提供后端 API 和基础前端入口，便于把线下补录的学习记录也纳入图片分析。

### 每日复盘总结

复盘页新增“今日复盘”模块。点击生成后，后端会读取当天学习记录、任务信息和图片分析结果，调用 Doubao 文本模型生成总结，并写入 `DailyReview`。

总结内容包括：

- 今日完成内容
- 涉及科目和知识点
- 题目/错题暴露的问题
- 明日调整建议

如果没有配置 Doubao API Key，则使用本地规则生成一个简短总结，保证复盘功能仍可用。

## 数据模型

### StudyRecordImage

字段：

- `id`
- `user_id`
- `record_id`
- `original_filename`
- `stored_path`
- `content_type`
- `file_size`
- `analysis_status`: `pending`、`completed`、`failed`、`skipped`
- `analysis_text`: Doubao 原始分析文本
- `knowledge_points`: JSON 字符串
- `mistakes`: JSON 字符串
- `suggestions`: JSON 字符串
- `error_message`
- `created_at`
- `updated_at`

### DailyReview

字段：

- `id`
- `user_id`
- `review_date`
- `summary`
- `completed_content`
- `weak_points`
- `next_actions`
- `source_record_ids`: JSON 字符串
- `model_status`: `completed`、`fallback`、`failed`
- `created_at`
- `updated_at`

同一用户同一天只保留一条每日复盘，重复生成时更新原记录。

## Doubao 接入

使用火山方舟 OpenAI 兼容接口，后端新增环境变量：

- `ARK_API_KEY`
- `ARK_BASE_URL`，默认 `https://ark.cn-beijing.volces.com/api/v3`
- `ARK_VISION_MODEL`
- `ARK_TEXT_MODEL`

后端新增 `app/services/doubao.py`，集中处理：

- 图片分析 prompt
- 每日复盘 prompt
- OpenAI-compatible Chat Completions 请求
- API Key 缺失、网络异常、模型异常时的降级返回

图片分析输入使用 base64 data URL。模型返回尽量要求 JSON，但服务层需要能处理非 JSON 文本，避免模型输出格式波动导致主流程失败。

## API 设计

### `POST /api/timer/finish-with-images`

`multipart/form-data`：

- `summary`
- `blockers`
- `quality`
- `files`: 多张图片

返回：

- `record`: 学习记录
- `images`: 图片分析结果列表

### `POST /api/records/{record_id}/images`

给已有记录补传图片并分析。

### `GET /api/records/{record_id}/images`

读取某条记录关联的图片分析。

### `POST /api/reviews/daily/generate?date=YYYY-MM-DD`

生成或更新每日复盘。

### `GET /api/reviews/daily?date=YYYY-MM-DD`

读取每日复盘；不传日期时返回最近若干条。

## 前端设计

### 计时页

结束记录区域新增：

- 图片选择控件
- 已选图片列表
- “结束并分析”按钮
- 分析中状态

结束成功后刷新记录和统计，并展示本次图片分析摘要。

### 记录页

记录卡片显示图片分析状态和简短分析文本。后续可在卡片内补传图片。

### 复盘页

新增“今日复盘”模块：

- 今日完成记录数量和总时长
- “生成今日总结”按钮
- 总结、完成内容、薄弱点、明日建议

## 错误处理

- 图片类型只允许 `image/jpeg`、`image/png`、`image/webp`。
- 单张图片默认限制 8MB。
- Doubao 失败不影响计时结束和记录保存。
- 未配置 API Key 时写入 `skipped` 状态，前端显示“未配置模型，已保存图片”。
- 每个用户只能访问自己的记录、图片分析和每日复盘。

## 测试

后端测试覆盖：

- 无 API Key 时，结束计时上传图片仍能生成记录和图片分析占位。
- 已有记录补传图片。
- 每日复盘无 API Key 时能生成 fallback 总结。
- 用户认证保护仍然生效。

前端验证覆盖：

- 计时页能选择图片并调用 `finish-with-images`。
- 复盘页能调用每日总结接口并展示结果。
- `npm run build` 通过。
