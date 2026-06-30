from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx

from app.core.config import Settings
from app.models.study import StudyRecord, StudyRecordImage


@dataclass
class ImageAnalysisResult:
    status: str
    analysis_text: str
    knowledge_points: list[str]
    mistakes: list[str]
    suggestions: list[str]
    error_message: str = ""


@dataclass
class DailyReviewResult:
    status: str
    summary: str
    completed_content: str
    weak_points: str
    next_actions: str


class DoubaoService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def analyze_problem_image(
        self,
        *,
        image_bytes: bytes,
        content_type: str,
        record: StudyRecord,
    ) -> ImageAnalysisResult:
        if not self.settings.ark_api_key:
            return ImageAnalysisResult(
                status="skipped",
                analysis_text="未配置 Doubao API Key，图片已保存但未调用模型分析。",
                knowledge_points=[],
                mistakes=[],
                suggestions=["在 .env 中配置 ARK_API_KEY、ARK_VISION_MODEL 后重新上传图片分析。"],
            )

        data_url = f"data:{content_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        prompt = (
            "你是考研 11408 学习复盘助手。请分析这张题目/解题图片，返回 JSON，字段包括："
            "analysis_text（100字内总结做了什么题）、knowledge_points（数组）、"
            "mistakes（数组，若看不出错误则写可能风险）、suggestions（数组，下一步复习建议）。"
            f"本次学习记录：科目={record.subject}，模块={record.module}，任务={record.title}。"
        )
        try:
            content = self._chat(
                model=self.settings.ark_vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    }
                ],
            )
            parsed = parse_jsonish(content)
            return ImageAnalysisResult(
                status="completed",
                analysis_text=str(parsed.get("analysis_text") or content).strip(),
                knowledge_points=ensure_str_list(parsed.get("knowledge_points")),
                mistakes=ensure_str_list(parsed.get("mistakes")),
                suggestions=ensure_str_list(parsed.get("suggestions")),
            )
        except Exception as exc:  # noqa: BLE001 - model failures should not break study logging
            return ImageAnalysisResult(
                status="failed",
                analysis_text="Doubao 图片分析失败，图片和学习记录已保存。",
                knowledge_points=[],
                mistakes=[],
                suggestions=[],
                error_message=str(exc),
            )

    def generate_daily_review(
        self,
        *,
        review_date: date,
        records: list[StudyRecord],
        images: list[StudyRecordImage],
    ) -> DailyReviewResult:
        if not records:
            return DailyReviewResult(
                status="fallback",
                summary="今天还没有学习记录。",
                completed_content="暂无完成内容。",
                weak_points="暂无可分析薄弱点。",
                next_actions="先完成一次计时或手动补录记录，再生成复盘。",
            )

        fallback = build_fallback_daily_review(review_date, records, images)
        if not self.settings.ark_api_key:
            return fallback

        record_lines = [
            f"- {record.subject}/{record.module}: {record.title}，{record.duration_minutes}分钟，总结：{record.summary or '无'}"
            for record in records
        ]
        image_lines = [
            f"- {image.original_filename}: {image.analysis_text}; 知识点={image.knowledge_points}; 错因={image.mistakes}"
            for image in images
            if image.analysis_text
        ]
        prompt = (
            "你是考研 11408 每日复盘助手。请基于学习记录和题目图片分析生成 JSON，字段包括："
            "summary（今日总体评价，100字内）、completed_content（完成内容）、"
            "weak_points（薄弱点）、next_actions（明日建议）。\n"
            f"日期：{review_date.isoformat()}\n"
            "学习记录：\n" + "\n".join(record_lines) + "\n"
            "图片分析：\n" + ("\n".join(image_lines) if image_lines else "无图片分析")
        )
        try:
            content = self._chat(
                model=self.settings.ark_text_model,
                messages=[{"role": "user", "content": prompt}],
            )
            parsed = parse_jsonish(content)
            return DailyReviewResult(
                status="completed",
                summary=str(parsed.get("summary") or fallback.summary).strip(),
                completed_content=str(parsed.get("completed_content") or fallback.completed_content).strip(),
                weak_points=str(parsed.get("weak_points") or fallback.weak_points).strip(),
                next_actions=str(parsed.get("next_actions") or fallback.next_actions).strip(),
            )
        except Exception:
            return fallback

    def _chat(self, *, model: str, messages: list[dict[str, Any]]) -> str:
        url = self.settings.ark_base_url.rstrip("/") + "/chat/completions"
        payload = {"model": model, "messages": messages, "temperature": 0.2}
        with httpx.Client(timeout=60) as client:
            response = client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {self.settings.ark_api_key}"},
            )
            response.raise_for_status()
            data = response.json()
        return str(data["choices"][0]["message"]["content"])


def parse_jsonish(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        return {"analysis_text": content}


def ensure_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return [str(value)]


def build_fallback_daily_review(
    review_date: date,
    records: list[StudyRecord],
    images: list[StudyRecordImage],
) -> DailyReviewResult:
    total_minutes = sum(record.duration_minutes for record in records)
    subjects = sorted({record.subject for record in records})
    completed = "；".join(f"{record.subject}：{record.title}" for record in records[:6])
    image_findings = [image.analysis_text for image in images if image.analysis_text]
    weak_points = "；".join(image_findings[:4]) or "暂无图片分析结论，先根据学习记录保持数学和408复盘节奏。"
    return DailyReviewResult(
        status="fallback",
        summary=f"{review_date.isoformat()} 共记录 {len(records)} 次学习，累计 {total_minutes} 分钟，覆盖 {'、'.join(subjects)}。",
        completed_content=completed or "暂无完成内容。",
        weak_points=weak_points,
        next_actions="明天优先补齐未完成任务；数学记录错题原因，英语保持不断档，408 做完后及时复盘。",
    )
