"""
AI 题目提取服务。
"""
from __future__ import annotations

import json
import time
import re
from datetime import datetime
from typing import Iterable, List, Optional, Sequence, Tuple, Dict, Any, Callable

import httpx

from fastapi import HTTPException, status
from openai import OpenAI

from app.core.security import decrypt_api_key
from app.models.user import User, UserSettings
from app.schemas.file import ParsedOptionSchema, ParsedQuestionSchema
from app.services.question_parser import parse_questions

AI_PROVIDER_OPENAI = "openai"
AI_PROVIDER_SILICONFLOW = "siliconflow"
AI_PROVIDER_MOCK = "mock"

MAX_AI_CHARS = 1200
AI_CHUNK_OVERLAP = 100
AI_MAX_RETRY = 2
MIN_RESPLIT_CHARS = 400
DEFAULT_OPENAI_MAX_TOKENS = 1500
DEFAULT_TEMPERATURE = 0.2
HTTP_TIMEOUT = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=120.0)

MAX_TAGS = 3
MAX_TAG_LENGTH = 12  # 约等于 6 个汉字或 3 个英文单词

AI_SYSTEM_PROMPT = (
    "你是一个专业的题目结构化助手，负责将原始试题文本转换成严格的 JSON 数据。"
    "任何时候都必须只返回 JSON，不允许输出额外解释或自然语言。"
    "输出结构为：{\"questions\": [{\"index\": 整数, \"question\": 字符串, \"question_type\": "
    "\"single_choice|multiple_choice|true_false|fill_blank|short_answer\", \"options\": "
    "[{\"key\": \"A\", \"content\": \"...\"}], \"answer\": 字符串, \"explanation\": 字符串, "
    "\"tags\": [\"知识点标签1\", \"知识点标签2\"]}]}"
    "如果某题没有选项，可以让 options 为空数组。若存在多选题，answer 可包含多个选项字母（如 \"AC\"）。"
    "tags 字段必须是数组，包含 0~3 个字符串，用于描述题目的知识点。标签需简短（不超过 6 个汉字或 3 个英文单词），"
    "同一题目的标签须属于同一学科，无法确定时可返回空数组。"
    "请保持 JSON 可被直接解析，字段名必须使用双引号。"
)

AI_USER_PROMPT_TEMPLATE = (
    "请从以下原始试题片段中提取题目，补全题干、选项、答案、解析信息并返回 JSON。"
    "同时为每题生成 1~3 个知识点标签填入 tags 数组，保持标签精炼、同一学科且不包含标点；若无法判断则返回空数组。"
    "若文本中存在噪音或说明，请忽略与题目无关的内容。\n\n原始片段：\n{content}"
)


class AIExtractionError(Exception):
    """AI 提取失败"""


def _ensure_settings(user: User) -> UserSettings:
    settings = user.settings
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="尚未配置 AI 服务，请先在设置中心填写相关信息。",
        )
    return settings


def _normalize_question_type(raw: Optional[str]) -> str:
    value = (raw or "").strip().lower()
    if value in {"single", "single_choice", "single-choice"}:
        return "single_choice"
    if value in {"multiple", "multiple_choice", "multiple-choice"}:
        return "multiple_choice"
    if value in {"judge", "true_false", "boolean"}:
        return "true_false"
    if value in {"fill", "fill_blank", "fill-in-blank"}:
        return "fill_blank"
    if value in {"short", "short_answer"}:
        return "short_answer"
    return "short_answer"


def _normalize_options(options: Optional[Iterable]) -> List[ParsedOptionSchema]:
    if not options:
        return []
    normalized: List[ParsedOptionSchema] = []
    for item in options:
        key: Optional[str] = None
        content: Optional[str] = None
        if isinstance(item, dict):
            key = item.get("key") or item.get("label") or item.get("id") or item.get("option")
            content = item.get("content") or item.get("text") or item.get("value")
        elif isinstance(item, str):
            match = re.match(r"\s*([A-Ha-h])[\.．、\)]\s*(.+)", item)
            if match:
                key = match.group(1).upper()
                content = match.group(2).strip()
            else:
                key = None
                content = item.strip()
        if not content:
            continue
        if not key:
            # 自动生成选项字母
            key = chr(ord("A") + len(normalized))
        normalized.append(ParsedOptionSchema(key=key.upper(), content=content))
    return normalized


def _normalize_tags(raw_tags: Optional[Iterable]) -> List[str]:
    if not raw_tags:
        return []
    normalized: List[str] = []
    for raw in raw_tags:
        if not isinstance(raw, str):
            continue
        tag = raw.strip()
        if not tag:
            continue
        # 限制长度，超长时截断
        if len(tag) > MAX_TAG_LENGTH:
            tag = tag[:MAX_TAG_LENGTH]
        if tag.lower() in {existing.lower() for existing in normalized}:
            continue
        normalized.append(tag)
        if len(normalized) >= MAX_TAGS:
            break
    return normalized


def _convert_to_schema(items: Sequence[dict]) -> List[ParsedQuestionSchema]:
    converted: List[ParsedQuestionSchema] = []
    for idx, item in enumerate(items, start=1):
        question = (item.get("question") or item.get("question_text") or "").strip()
        answer = (item.get("answer") or item.get("correct_answer") or "").strip()
        if not question or not answer:
            continue
        question_type = _normalize_question_type(item.get("question_type"))
        explanation = (item.get("explanation") or item.get("analysis") or "").strip()
        options = _normalize_options(item.get("options") or item.get("choices"))
        tags = _normalize_tags(item.get("tags"))
        converted.append(
            ParsedQuestionSchema(
                index=int(item.get("index") or idx),
                question=question,
                question_type=question_type,
                options=options,
                answer=answer,
                explanation=explanation,
                raw_text=item.get("raw_text") or "",
                tags=tags,
            )
        )
    return converted


def _extract_json(text: str) -> Sequence[dict]:
    """
    从 AI 返回的文本中提取 JSON 数据，并在必要时清洗控制字符。
    """
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
        parts = candidate.split("json", maxsplit=1)
        candidate = parts[-1].strip()

    def _load(raw: str) -> Sequence[dict]:
        data = json.loads(raw, strict=False)
        if isinstance(data, dict):
            questions = data.get("questions") or data.get("items")
            if isinstance(questions, list):
                return questions
            raise AIExtractionError("AI 返回结果缺少 questions 列表。")
        if isinstance(data, list):
            return data
        raise AIExtractionError("AI 返回结果格式不正确。")

    try:
        return _load(candidate)
    except json.JSONDecodeError:
        allowed_controls = {"\n", "\r", "\t"}
        sanitized = "".join(
            ch for ch in candidate if ch >= " " or ch in allowed_controls
        )
        try:
            return _load(sanitized)
        except json.JSONDecodeError as exc:  # noqa: BLE001
            raise AIExtractionError(
                f"AI 返回结果无法解析为 JSON：{exc}"
            ) from exc


def _call_openai(model: str, api_key: str, text: str) -> Sequence[dict]:
    client = OpenAI(api_key=api_key)
    messages = [
        {"role": "system", "content": AI_SYSTEM_PROMPT},
        {"role": "user", "content": AI_USER_PROMPT_TEMPLATE.format(content=text)},
    ]
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=DEFAULT_TEMPERATURE,
        max_tokens=DEFAULT_OPENAI_MAX_TOKENS,
    )
    content = completion.choices[0].message.content or ""
    return _extract_json(content)


def _call_siliconflow(model: str, api_key: str, text: str) -> Sequence[dict]:
    endpoint = "https://api.siliconflow.cn/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": AI_SYSTEM_PROMPT},
            {"role": "user", "content": AI_USER_PROMPT_TEMPLATE.format(content=text)},
        ],
        "temperature": DEFAULT_TEMPERATURE,
        "max_tokens": 1500,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        response = httpx.post(
            endpoint, json=payload, headers=headers, timeout=HTTP_TIMEOUT
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SiliconFlow 请求失败：{exc}",
        ) from exc

    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        raise AIExtractionError("SiliconFlow 返回结果缺少 choices。")
    content = choices[0].get("message", {}).get("content") or ""
    return _extract_json(content)


def _split_text_for_ai(text: str, max_chars: int = MAX_AI_CHARS, overlap: int = AI_CHUNK_OVERLAP) -> List[str]:
    base = text.strip()
    if not base:
        return [base]
    if len(base) <= max_chars:
        return [base]
    chunks: List[str] = []
    length = len(base)
    start = 0
    while start < length:
        end = min(start + max_chars, length)
        if end < length:
            window_start = max(start + max_chars - 400, start)
            split_pos = base.rfind("\n", window_start, end)
            if split_pos == -1 or split_pos <= start:
                split_pos = base.rfind("。", window_start, end)
            if split_pos != -1 and split_pos > start:
                end = split_pos + 1
        chunk = base[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= length:
            break
        start = max(end - overlap, 0)
    return chunks or [base]


def _should_retry(exc: HTTPException) -> bool:
    detail_text = str(exc.detail)
    return exc.status_code >= 500 or "timeout" in detail_text.lower() or "超时" in detail_text


ProgressReporter = Callable[[List[str], List[Dict[str, Any]], Dict[str, Any]], None]


def extract_questions_ai(
    user: User,
    text: str,
    reporter: Optional[ProgressReporter] = None,
) -> Tuple[List[ParsedQuestionSchema], List[str], Dict[str, Any]]:
    """
    使用用户配置的 AI 服务提取题目。
    """
    settings = _ensure_settings(user)
    provider = (settings.ai_provider or AI_PROVIDER_OPENAI).lower()
    model = settings.ai_model or "gpt-3.5-turbo"

    if provider == AI_PROVIDER_MOCK:
        parsed = parse_questions(text)
        converted = [
            ParsedQuestionSchema(
                index=item.index,
                question=item.question,
                question_type=item.question_type,
                options=[
                    ParsedOptionSchema(key=opt.key, content=opt.content)
                    for opt in item.options
                ],
                answer=item.answer,
                explanation=item.explanation,
                raw_text=item.raw_text,
                tags=[],
            )
            for item in parsed
        ]
        stats = {
            "stats": {
                "initial_segments": 1,
                "processed_segments": 1,
                "auto_split_segments": 0,
                "provider": provider,
                "pending_segments": 0,
                "tag_source": "rule",
            },
            "events": [
                {
                    "type": "segment",
                    "segment": 1,
                    "status": "mock",
                    "elapsed": 0.0,
                    "message": "Mock 模式使用规则解析完成。",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
        }
        if reporter:
            reporter([], stats["events"], stats["stats"])
        return converted, [], stats

    api_key_encrypted = settings.encrypted_api_key or ""
    api_key = decrypt_api_key(api_key_encrypted)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未配置 AI API Key，请在设置中心填写后重试。",
        )

    chunks = _split_text_for_ai(text)
    pending: List[Tuple[str, int]] = [(chunk, MAX_AI_CHARS) for chunk in chunks]
    warnings: List[str] = []
    events: List[Dict[str, Any]] = []
    stats: Dict[str, Any] = {
        "initial_segments": len(pending),
        "processed_segments": 0,
        "auto_split_segments": 0,
        "provider": provider,
        "tag_source": "ai",
    }
    if len(pending) > 1:
        msg = f"文本较长，已拆分为 {len(pending)} 段逐段解析。"
        warnings.append(msg)
        events.append(
            {
                "type": "info",
                "message": msg,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    aggregated: List[ParsedQuestionSchema] = []

    def _notify_progress() -> None:
        if reporter:
            snapshot_stats = dict(stats)
            snapshot_stats["pending_segments"] = len(pending)
            reporter(warnings, events, snapshot_stats)

    def _extend_with_reindex(items: List[ParsedQuestionSchema]) -> None:
        for item in items:
            item.index = len(aggregated) + 1
            aggregated.append(item)

    idx = 0
    _notify_progress()
    while pending:
        chunk, current_limit = pending.pop(0)
        idx += 1
        segment_start = time.perf_counter()
        attempt = 0
        while True:
            try:
                if provider == AI_PROVIDER_OPENAI:
                    raw_items = _call_openai(model=model, api_key=api_key, text=chunk)
                elif provider == AI_PROVIDER_SILICONFLOW:
                    raw_items = _call_siliconflow(model=model, api_key=api_key, text=chunk)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"暂不支持的 AI 提取服务：{provider}",
                    )
                converted = _convert_to_schema(raw_items)
                _extend_with_reindex(converted)
                stats["tag_source"] = "ai"
                elapsed = time.perf_counter() - segment_start
                stats["processed_segments"] = stats.get("processed_segments", 0) + 1
                events.append(
                    {
                        "type": "segment",
                        "segment": idx,
                        "status": "success",
                        "elapsed": round(elapsed, 2),
                        "message": f"第 {idx} 段解析成功，生成 {len(converted)} 题。",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
                _notify_progress()
                break
            except HTTPException as exc:
                attempt += 1
                if attempt < AI_MAX_RETRY and _should_retry(exc):
                    continue
                parsed_fallback = parse_questions(chunk)
                if parsed_fallback:
                    fallback = [
                        ParsedQuestionSchema(
                            index=item.index,
                            question=item.question,
                            question_type=item.question_type,
                            options=[
                                ParsedOptionSchema(key=opt.key, content=opt.content)
                                for opt in (item.options or [])
                            ],
                            answer=item.answer,
                            explanation=item.explanation,
                            raw_text=item.raw_text,
                            tags=[],
                        )
                        for item in parsed_fallback
                    ]
                    warnings.append(
                        f"第 {idx} 段 AI 解析失败（{exc.detail}），已回退到规则解析。"
                    )
                    _extend_with_reindex(fallback)
                    stats["tag_source"] = "rule"
                    elapsed = time.perf_counter() - segment_start
                    stats["processed_segments"] = stats.get("processed_segments", 0) + 1
                    events.append(
                        {
                            "type": "segment",
                            "segment": idx,
                            "status": "fallback",
                            "elapsed": round(elapsed, 2),
                            "message": f"第 {idx} 段回退规则解析，生成 {len(fallback)} 题。",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                    _notify_progress()
                    break
                cleaned = chunk.strip()
                if len(cleaned) > max(MIN_RESPLIT_CHARS, current_limit // 2):
                    new_limit = max(current_limit // 2, MIN_RESPLIT_CHARS)
                    sub_chunks = _split_text_for_ai(cleaned, max_chars=new_limit, overlap=AI_CHUNK_OVERLAP // 2)
                    if len(sub_chunks) > 1:
                        warnings.append(
                            f"第 {idx} 段解析失败，自动细分为 {len(sub_chunks)} 个子段重试。"
                        )
                        stats["auto_split_segments"] = stats.get("auto_split_segments", 0) + len(sub_chunks)
                        events.append(
                            {
                                "type": "split",
                                "segment": idx,
                                "status": "retry",
                                "message": f"第 {idx} 段细分为 {len(sub_chunks)} 个子段后继续重试。",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                        for sub_chunk in reversed(sub_chunks):
                            pending.insert(0, (sub_chunk, new_limit))
                        idx -= 1
                        _notify_progress()
                        break
                raise HTTPException(
                    status_code=exc.status_code,
                    detail=f"第 {idx} 段解析失败：{exc.detail}",
                ) from exc
            except Exception as exc:  # noqa: BLE001
                attempt += 1
                if attempt < AI_MAX_RETRY:
                    continue
                parsed_fallback = parse_questions(chunk)
                if parsed_fallback:
                    fallback = [
                        ParsedQuestionSchema(
                            index=item.index,
                            question=item.question,
                            question_type=item.question_type,
                            options=[
                                ParsedOptionSchema(key=opt.key, content=opt.content)
                                for opt in (item.options or [])
                            ],
                            answer=item.answer,
                            explanation=item.explanation,
                            raw_text=item.raw_text,
                            tags=[],
                        )
                        for item in parsed_fallback
                    ]
                    warnings.append(
                        f"第 {idx} 段 AI 解析异常（{exc}），已回退到规则解析。"
                    )
                    _extend_with_reindex(fallback)
                    stats["tag_source"] = "rule"
                    elapsed = time.perf_counter() - segment_start
                    stats["processed_segments"] = stats.get("processed_segments", 0) + 1
                    events.append(
                        {
                            "type": "segment",
                            "segment": idx,
                            "status": "fallback",
                            "elapsed": round(elapsed, 2),
                            "message": f"第 {idx} 段回退规则解析，生成 {len(fallback)} 题。",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                    _notify_progress()
                    break
                cleaned = chunk.strip()
                if len(cleaned) > max(MIN_RESPLIT_CHARS, current_limit // 2):
                    new_limit = max(current_limit // 2, MIN_RESPLIT_CHARS)
                    sub_chunks = _split_text_for_ai(cleaned, max_chars=new_limit, overlap=AI_CHUNK_OVERLAP // 2)
                    if len(sub_chunks) > 1:
                        warnings.append(
                            f"第 {idx} 段解析异常，自动细分为 {len(sub_chunks)} 个子段重试。"
                        )
                        stats["auto_split_segments"] = stats.get("auto_split_segments", 0) + len(sub_chunks)
                        events.append(
                            {
                                "type": "split",
                                "segment": idx,
                                "status": "retry",
                                "message": f"第 {idx} 段细分为 {len(sub_chunks)} 个子段后继续重试。",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                        for sub_chunk in reversed(sub_chunks):
                            pending.insert(0, (sub_chunk, new_limit))
                        idx -= 1
                        _notify_progress()
                        break
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"第 {idx} 段解析失败：{exc}",
                ) from exc

    _notify_progress()
    stats["pending_segments"] = len(pending)
    return aggregated, warnings, {"events": events, "stats": stats}


def _list_openai_models(api_key: str) -> List[str]:
    client = OpenAI(api_key=api_key)
    try:
        response = client.models.list()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenAI 模型列表请求失败：{exc}",
        ) from exc
    models = [item.id for item in response.data]
    return sorted(models)


def _list_siliconflow_models(api_key: str) -> List[str]:
    endpoint = "https://api.siliconflow.cn/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        response = httpx.get(endpoint, headers=headers, timeout=60.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SiliconFlow 模型列表请求失败：{exc}",
        ) from exc

    data = response.json()
    items = data.get("data")
    if not isinstance(items, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="SiliconFlow 返回模型列表格式不正确。",
        )
    models: List[str] = []
    for item in items:
        if isinstance(item, dict):
            model_id = item.get("id") or item.get("model") or item.get("name")
        else:
            model_id = str(item)
        if model_id:
            models.append(str(model_id))
    return sorted(set(models))


def list_provider_models(provider: str, api_key: str) -> List[str]:
    """
    获取指定 provider 的可用模型列表。
    """
    provider_normalized = provider.lower()
    if provider_normalized == AI_PROVIDER_OPENAI:
        return _list_openai_models(api_key)
    if provider_normalized == AI_PROVIDER_SILICONFLOW:
        return _list_siliconflow_models(api_key)
    if provider_normalized == AI_PROVIDER_MOCK:
        # mock 模式返回空列表，由前端自由填写
        return []
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"暂不支持的 AI 服务商：{provider}",
    )
