"""Support helpers for the local Streamlit web interface."""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from env_loader import load_env_file
except Exception:
    load_env_file = None


SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"(?i)(api[_-]?key\s*=\s*)[^\s,;]+"),
    re.compile(r"(?i)(authorization:\s*bearer\s+)[^\s,;]+"),
)

REPORT_SECTION_TITLES = (
    "命盘摘要",
    "传统命理分析",
    "现代心理学转译",
    "当前阶段策略",
    "行动建议",
    "风险与边界",
)


def build_birth_info(
    free_text: str = "",
    birth_date: Any = "",
    birth_time: Any = "",
    gender: str = "",
    birth_place: str = "",
    calendar_type: str = "",
    notes: str = "",
    display_name: str = "",
) -> str:
    """Build a birth_info string. Free text takes precedence."""
    if free_text and str(free_text).strip():
        return str(free_text).strip()

    parts = []
    if display_name:
        parts.append(f"称谓: {_clean_value(display_name)}")
    if birth_date:
        parts.append(f"出生日期: {birth_date}")
    if birth_time:
        parts.append(f"出生时间: {birth_time}")
    if gender:
        parts.append(f"性别: {_clean_value(gender)}")
    if birth_place:
        parts.append(f"出生地点: {_clean_value(birth_place)}")
    if calendar_type:
        parts.append(f"历法: {_clean_value(calendar_type)}")
    if notes:
        parts.append(f"备注: {_clean_value(notes)}")
    return "；".join(parts)


def build_focus_notes(
    focus_topics: List[str],
    custom_question: str = "",
    output_language: str = "中文",
) -> str:
    """Build analysis notes from selected focus topics."""
    topics = [str(topic).strip() for topic in focus_topics or [] if str(topic).strip()]
    parts = [f"输出语言: {output_language or '中文'}"]
    if topics:
        parts.append("关注主题: " + "、".join(topics))
    if custom_question and custom_question.strip():
        parts.append("自定义问题: " + custom_question.strip())
    return "；".join(parts)


def load_analysis_history(
    results_dir: str = "./results",
    query: str = "",
    limit: int = 20,
    user_id: str = "",
) -> List[Dict[str, Any]]:
    """Load only the current account's saved analysis records."""
    if not user_id:
        return []
    root = Path(results_dir)
    if not root.exists():
        return []

    query_text = (query or "").strip().lower()
    records = []
    for path in root.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        owner_id = str(payload.get("user_id") or "")
        if owner_id != user_id:
            continue

        record = {
            "path": str(path),
            "file_name": path.name,
            "modified_at": path.stat().st_mtime,
            "birth_info": payload.get("birth_info", ""),
            "analysis_date": payload.get("analysis_date", ""),
            "user_id": owner_id,
            "username": payload.get("username", ""),
            "quality_score": _quality_score(payload.get("quality_report")),
            "llm_provider": payload.get("llm_provider", ""),
            "llm_model": payload.get("llm_model", ""),
            "final_analysis": payload.get("final_analysis", ""),
            "payload": payload,
        }
        searchable = " ".join(
            str(record.get(key, ""))
            for key in ("file_name", "birth_info", "analysis_date", "llm_provider", "llm_model", "username")
        ).lower()
        if query_text and query_text not in searchable:
            continue
        records.append(record)

    records.sort(key=lambda item: item["modified_at"], reverse=True)
    return records[:limit]


def extract_intermediate_reports(final_state: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract intermediate agent reports for collapsible UI sections."""
    fields = [
        ("命盘计算", "chart_report"),
        ("日主分析", "day_master_report"),
        ("十神分析", "ten_gods_report"),
        ("格局分析", "pattern_report"),
        ("用神分析", "useful_god_report"),
        ("大运分析", "luck_cycle_report"),
    ]
    reports = [
        {"title": title, "content": str(final_state.get(field, "") or "")}
        for title, field in fields
        if final_state.get(field)
    ]

    debate_state = final_state.get("bazi_debate_state") or {}
    debate_fields = [
        ("传统命理辩论", "traditional_history"),
        ("心理学转译辩论", "psychology_history"),
        ("完整辩论记录", "history"),
    ]
    for title, field in debate_fields:
        content = debate_state.get(field)
        if content:
            reports.append({"title": title, "content": str(content)})
    return reports


def extract_markdown_sections(markdown_text: str) -> Dict[str, str]:
    """Extract Markdown sections by heading title."""
    text = str(markdown_text or "")
    matches = list(re.finditer(r"^#{1,3}\s+(.+?)\s*$", text, flags=re.M))
    sections: Dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        sections[title] = content
    return sections


def build_report_overview(
    final_state: Dict[str, Any],
    final_analysis: str = "",
    focus_topics: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build report overview cards for the wireframe-style UI."""
    final_analysis = final_analysis or str(final_state.get("final_analysis") or "")
    sections = extract_markdown_sections(final_analysis)
    quality = final_state.get("quality_report") or {}
    quality_score = quality.get("overall_score")

    tags = []
    for topic in focus_topics or []:
        if topic and len(tags) < 3:
            tags.append(str(topic))
    day_master = _extract_day_master(final_state)
    if day_master:
        tags.append(f"日主{day_master}")
    if quality_score:
        tags.append(f"质量{quality_score}")
    if not tags:
        tags = ["自我观察", "双视角", "行动建议"]

    cards = [
        {
            "title": "优势倾向",
            "content": _section_text(
                sections,
                ("传统命理分析", "现代心理学转译", "命盘摘要"),
                "暂未提取到优势倾向，请查看完整报告。",
            ),
        },
        {
            "title": "可能的压力来源",
            "content": _section_text(
                sections,
                ("风险与边界", "当前阶段策略", "现代心理学转译"),
                "暂未提取到压力来源，请查看完整报告。",
            ),
        },
        {
            "title": "关系模式",
            "content": _clean_report_text(
                _debate_text(final_state, "psychology_history")
                or sections.get("现代心理学转译", ""),
                "暂未提取到关系模式，请查看双视角分析。",
            ),
        },
        {
            "title": "当前阶段观察",
            "content": _section_text(
                sections,
                ("当前阶段策略", "命盘摘要", "传统命理分析"),
                "暂未提取到当前阶段观察，请查看完整报告。",
            ),
        },
    ]
    actions = extract_action_plan(final_analysis)
    return {
        "tags": tags[:5],
        "cards": cards,
        "top_actions": (actions["today"] + actions["week"] + actions["long_term"])[:3],
        "quality_score": quality_score,
    }


def build_dual_view(
    final_state: Dict[str, Any],
    final_analysis: str = "",
    focus_topics: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build traditional/psychology comparison content."""
    final_analysis = final_analysis or str(final_state.get("final_analysis") or "")
    sections = extract_markdown_sections(final_analysis)
    traditional = _debate_text(final_state, "traditional_history") or sections.get("传统命理分析", "")
    psychology = _debate_text(final_state, "psychology_history") or sections.get("现代心理学转译", "")
    shared = sections.get("当前阶段策略") or sections.get("命盘摘要") or final_analysis
    focus_title = "、".join(focus_topics or []) or "性格与阶段主题"
    return {
        "title": f"关于{focus_title}",
        "traditional": _clean_report_text(traditional, "传统文化视角暂未生成，请查看完整报告。"),
        "psychology": _clean_report_text(psychology, "心理学视角暂未生成，请查看完整报告。"),
        "shared": _clean_report_text(shared, "两个视角都需要结合现实反馈继续校验。"),
        "difference": "传统视角更强调结构、五行与阶段节律；心理学视角更强调行为模式、情绪调节和可改变的行动。",
        "reflection": _reflection_question(focus_topics),
    }


def extract_action_plan(final_analysis: str) -> Dict[str, List[str]]:
    """Extract short/mid/long action suggestions from final analysis."""
    sections = extract_markdown_sections(final_analysis)
    action_text = sections.get("行动建议") or final_analysis or ""
    buckets = {"today": [], "week": [], "long_term": []}
    uncategorized = []
    current_bucket = ""

    for raw_line in action_text.splitlines():
        line = _normalize_action_line(raw_line)
        if not line:
            continue

        heading_bucket, remainder = _split_action_heading(line)
        if heading_bucket:
            current_bucket = heading_bucket
            line = remainder
            if not line:
                continue

        if "行动建议" in line and len(line) < 16:
            continue

        if len(line) >= 8:
            bucket = current_bucket or _infer_action_bucket(line)
            if bucket:
                buckets[bucket].append(line)
            else:
                uncategorized.append(line)

    fallback_order = ["today", "today", "week", "week", "long_term", "long_term"]
    for index, item in enumerate(uncategorized):
        bucket = fallback_order[min(index, len(fallback_order) - 1)]
        buckets[bucket].append(item)

    if not any(buckets.values()):
        buckets["today"] = [
            "今天记录一个最明显的情绪或身体信号。",
        ]
        buckets["week"] = [
            "一周内观察三次重复出现的行为模式。",
        ]
        buckets["long_term"] = [
            "每月回顾一次关键选择和现实反馈。",
        ]

    return {
        "today": _dedupe(buckets["today"])[:4],
        "week": _dedupe(buckets["week"])[:4] or _dedupe(buckets["today"])[:1],
        "long_term": _dedupe(buckets["long_term"])[:4] or _dedupe(buckets["week"])[-1:] or _dedupe(buckets["today"])[-1:],
    }


def save_feedback(results_dir: str, feedback: Dict[str, Any]) -> str:
    """Save one feedback record as JSON and return its path."""
    root = Path(results_dir or "./results") / "feedback"
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_id = re.sub(r"[^A-Za-z0-9_\-]+", "_", str(feedback.get("case_id") or "case")).strip("_")
    path = root / f"feedback_{safe_id or 'case'}_{timestamp}.json"
    payload = dict(feedback)
    payload["submitted_at"] = datetime.now().isoformat(timespec="seconds")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def get_runtime_settings(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return read-only runtime settings without exposing secret values."""
    if load_env_file is not None:
        load_env_file()
    config = config or {}

    return {
        "llm_provider": config.get("llm_provider") or os.environ.get("LLM_PROVIDER", "siliconflow"),
        "llm_model": config.get("llm_model") or os.environ.get("LLM_MODEL", "deepseek-ai/DeepSeek-V3"),
        "llm_base_url_configured": bool(config.get("base_url") or os.environ.get("LLM_BASE_URL")),
        "memory_dir": config.get("memory_dir") or os.environ.get("MEMORY_DIR", "./memory"),
        "results_dir": config.get("results_dir") or os.environ.get("RESULTS_DIR", "./results"),
        "api_keys": {
            "SILICONFLOW_API_KEY": bool(os.environ.get("SILICONFLOW_API_KEY")),
            "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
            "ANTHROPIC_API_KEY": bool(os.environ.get("ANTHROPIC_API_KEY")),
        },
        "debug": str(config.get("debug") or os.environ.get("DEBUG", "false")).lower() == "true",
    }


def sanitize_error(error: Any) -> str:
    """Mask likely secrets before showing errors in the web UI."""
    message = str(error)
    for pattern in SECRET_PATTERNS:
        message = pattern.sub(lambda match: _mask_match(match), message)
    return message


def _clean_value(value: Any) -> str:
    return str(value or "").strip()


def _quality_score(report: Any) -> Optional[float]:
    if isinstance(report, dict):
        score = report.get("overall_score")
        try:
            return float(score)
        except (TypeError, ValueError):
            return None
    return None


def _mask_match(match: re.Match) -> str:
    if match.lastindex:
        return f"{match.group(1)}***"
    return "***"


def _extract_day_master(final_state: Dict[str, Any]) -> str:
    text = str(final_state.get("chart_report") or final_state.get("day_master_report") or "")
    match = re.search(r"日主[：:\s]*([甲乙丙丁戊己庚辛壬癸])", text)
    return match.group(1) if match else ""


def _section_excerpt(
    sections: Dict[str, str],
    titles: tuple,
    fallback: str,
    max_chars: int = 150,
) -> str:
    for title in titles:
        if sections.get(title):
            return _excerpt(sections[title], max_chars, fallback)
    return fallback


def _section_text(sections: Dict[str, str], titles: tuple, fallback: str) -> str:
    for title in titles:
        if sections.get(title):
            return _clean_report_text(sections[title], fallback)
    return fallback


def _clean_report_text(text: str, fallback: str = "") -> str:
    cleaned = str(text or "").strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned or fallback


def _excerpt(text: str, max_chars: int, fallback: str = "") -> str:
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
    cleaned = re.sub(r"^[-*•\d.、\s]+", "", cleaned)
    if not cleaned:
        return fallback
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rstrip() + "..."


def _debate_text(final_state: Dict[str, Any], field: str) -> str:
    debate_state = final_state.get("bazi_debate_state") or {}
    return str(debate_state.get(field) or "")


def _normalize_action_line(line: str) -> str:
    cleaned = str(line or "").strip()
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned)
    cleaned = re.sub(r"^[-*•\d.、\s]+", "", cleaned).strip()
    cleaned = cleaned.replace("**", "").replace("__", "").replace("`", "")
    return cleaned.strip()


def _split_action_heading(line: str) -> tuple:
    normalized = line.strip()
    patterns = [
        ("today", r"^(短期建议|短期|今天可以尝试|今天|当下|立即)\s*(?:（[^）]*）|\([^)]*\))?\s*[：:、-]?\s*(.*)$"),
        ("week", r"^(中期建议|中期|一周内可以观察|一周内|本周|近期|一个月内|年前)\s*(?:（[^）]*）|\([^)]*\))?\s*[：:、-]?\s*(.*)$"),
        ("long_term", r"^(长期建议|长期|十年建议|10年以上|十年以上|长期可以记录)\s*(?:（[^）]*）|\([^)]*\))?\s*[：:、-]?\s*(.*)$"),
    ]
    for bucket, pattern in patterns:
        match = re.match(pattern, normalized)
        if match:
            return bucket, match.group(2).strip()
    return "", line


def _infer_action_bucket(line: str) -> str:
    if any(term in line for term in ("今天", "当下", "每日", "立即", "短期")):
        return "today"
    if any(term in line for term in ("一周", "本周", "近期", "一个月", "年前", "中期")):
        return "week"
    if any(term in line for term in ("长期", "十年", "10年", "10年以上", "十年以上", "大运", "岁后", "月度复盘")):
        return "long_term"
    return ""


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        key = re.sub(r"\s+", "", item)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _reflection_question(focus_topics: Optional[List[str]]) -> str:
    topics = set(focus_topics or [])
    if "职业与发展" in topics:
        return "最近一次职业选择中，你真正想争取的资源是什么？"
    if "情绪与压力" in topics:
        return "上一次压力明显升高时，你最先出现的是身体反应、情绪反应还是行动冲动？"
    if "人际与亲密关系" in topics:
        return "你在关系中最常隐藏的需求是什么？"
    if "当前阶段变化" in topics:
        return "最近反复出现的变化信号，是否正在提醒你调整节奏？"
    return "最近一次让你反复思考的选择，当时真正影响你的因素是什么？"
