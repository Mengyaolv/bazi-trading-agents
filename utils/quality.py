"""Rule-based quality evaluation for Bazi analysis reports."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from .quality_rules import (
    ABSOLUTE_RISK_PATTERNS,
    ACTIONABLE_PATTERNS,
    CHART_TERMS,
    ETHICAL_BOUNDARY_PATTERNS,
    FABRICATED_EVIDENCE_PATTERNS,
    MOJIBAKE_MARKERS,
    REQUIRED_SECTIONS,
)


DEFAULT_PROMPT_VERSION = "phase2-prompt-v1"


def evaluate_analysis_quality(
    final_analysis: str,
    final_state: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    llm_judge: Any = None,
) -> Dict[str, Any]:
    """Evaluate the final report quality with deterministic rules.

    LLM judge is optional and disabled unless explicitly provided and enabled.
    """
    config = config or {}
    final_state = final_state or {}
    text = final_analysis or ""

    warnings: List[str] = []
    failed_rules: List[str] = []
    suggested_fixes: List[str] = []

    structure_score = _structure_score(text, warnings, failed_rules, suggested_fixes)
    language_score = _language_score(text, warnings, failed_rules, suggested_fixes)
    ethics_score = _ethics_score(text, warnings, failed_rules, suggested_fixes)
    actionability_score = _actionability_score(text, warnings, failed_rules, suggested_fixes)
    consistency_score = _consistency_score(
        text,
        final_state.get("chart_report", ""),
        warnings,
        failed_rules,
        suggested_fixes,
    )

    dimension_scores = {
        "structure": structure_score,
        "language": language_score,
        "ethics": ethics_score,
        "actionability": actionability_score,
        "consistency": consistency_score,
    }
    overall_score = round(
        structure_score * 0.25
        + language_score * 0.20
        + ethics_score * 0.25
        + actionability_score * 0.15
        + consistency_score * 0.15,
        2,
    )

    llm_judge_report = None
    if _truthy(config.get("quality_llm_judge_enabled", False)) and llm_judge is not None:
        llm_judge_report = _run_llm_judge(llm_judge, text)

    return {
        "version": "quality-v1",
        "evaluated_at": datetime.now().isoformat(),
        "overall_score": overall_score,
        "dimension_scores": dimension_scores,
        "warnings": warnings,
        "failed_rules": failed_rules,
        "suggested_fixes": suggested_fixes,
        "llm_judge": llm_judge_report,
    }


def should_rewrite(quality_report: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> bool:
    """Return whether backend rewrite should be triggered."""
    config = config or {}
    if not _truthy(config.get("quality_rewrite_enabled", False)):
        return False
    threshold = _as_float(config.get("quality_min_score", 70), 70)
    return _as_float(quality_report.get("overall_score"), 0) < threshold


def build_rewrite_prompt(final_analysis: str, quality_report: Dict[str, Any]) -> str:
    """Build a bounded rewrite prompt for a low-quality final report."""
    return f"""请在不新增命盘事实、不编造研究数据的前提下，重写以下八字分析报告。

必须修复质量评估中指出的问题，并保留这些栏目：
命盘摘要、传统命理分析、现代心理学转译、当前阶段策略、行动建议、风险与边界。

质量评估：
{quality_report}

原报告：
{final_analysis}
"""


def _structure_score(
    text: str,
    warnings: List[str],
    failed_rules: List[str],
    suggested_fixes: List[str],
) -> float:
    present_sections = [section for section in REQUIRED_SECTIONS if section in text]
    section_score = len(present_sections) / len(REQUIRED_SECTIONS) * 70
    has_birth = any(term in text for term in ("出生", "四柱", "日主"))
    has_core = any(term in text for term in ("核心", "主要结论", "命盘摘要"))
    has_advice = any(term in text for term in ("行动建议", "建议"))
    has_boundary = any(term in text for term in ("风险与边界", "伦理", "不能替代", "仅供参考"))
    bonus = sum([has_birth, has_core, has_advice, has_boundary]) / 4 * 30
    missing = [section for section in REQUIRED_SECTIONS if section not in text]
    if missing:
        failed_rules.append("missing_required_sections")
        warnings.append(f"缺少必需章节: {', '.join(missing)}")
        suggested_fixes.append("按固定报告结构补齐缺失章节。")
    return round(section_score + bonus, 2)


def _language_score(
    text: str,
    warnings: List[str],
    failed_rules: List[str],
    suggested_fixes: List[str],
) -> float:
    marker_count = sum(text.count(marker) for marker in MOJIBAKE_MARKERS)
    chinese_ratio = _chinese_ratio(text)
    score = 100.0
    if marker_count:
        score -= min(60, marker_count * 15)
        failed_rules.append("mojibake_detected")
        warnings.append("检测到疑似中文乱码。")
        suggested_fixes.append("重新生成报告，确保使用 UTF-8 中文输出。")
    if chinese_ratio < 0.35:
        score -= 25
        failed_rules.append("low_chinese_ratio")
        warnings.append("中文占比偏低，可能不符合默认中文输出要求。")
        suggested_fixes.append("默认使用中文，仅保留必要英文术语括注。")
    return round(max(score, 0.0), 2)


def _ethics_score(
    text: str,
    warnings: List[str],
    failed_rules: List[str],
    suggested_fixes: List[str],
) -> float:
    score = 100.0
    risky = [pattern for pattern in ABSOLUTE_RISK_PATTERNS if pattern in text]
    if risky:
        score -= min(70, len(risky) * 30)
        failed_rules.append("absolute_or_fatalistic_language")
        warnings.append(f"存在绝对化或命运化表达: {', '.join(risky)}")
        suggested_fixes.append("将绝对判断改写为倾向、可能性和可调整方向。")

    fabricated = [
        pattern for pattern in FABRICATED_EVIDENCE_PATTERNS
        if pattern in text and re.search(r"\d+\s*%", text)
    ]
    if fabricated:
        score -= 25
        failed_rules.append("unsupported_quantitative_claims")
        warnings.append("存在疑似无来源研究/百分比表述。")
        suggested_fixes.append("删除无来源百分比、研究或机构背书。")

    if not any(pattern in text for pattern in ETHICAL_BOUNDARY_PATTERNS):
        score -= 20
        failed_rules.append("missing_ethical_boundary")
        warnings.append("缺少明确伦理边界或专业求助提醒。")
        suggested_fixes.append("补充报告不能替代心理、医疗、法律、投资等专业建议的说明。")
    return round(max(score, 0.0), 2)


def _actionability_score(
    text: str,
    warnings: List[str],
    failed_rules: List[str],
    suggested_fixes: List[str],
) -> float:
    action_hits = sum(1 for pattern in ACTIONABLE_PATTERNS if pattern in text)
    has_time_horizon = any(pattern in text for pattern in ("短期", "中期", "长期", "当前阶段"))
    has_list = bool(re.search(r"(^|\n)\s*[-0-9一二三四五六七八九十]+[、.)．-]", text))
    score = min(100, action_hits * 12 + (20 if has_time_horizon else 0) + (20 if has_list else 0))
    if score < 60:
        failed_rules.append("low_actionability")
        warnings.append("行动建议不够具体或缺少阶段划分。")
        suggested_fixes.append("补充短期、中期、长期可执行建议。")
    return round(float(score), 2)


def _consistency_score(
    text: str,
    chart_report: str,
    warnings: List[str],
    failed_rules: List[str],
    suggested_fixes: List[str],
) -> float:
    if not chart_report:
        warnings.append("缺少 chart_report，无法完整检查命盘一致性。")
        return 70.0

    report_terms = [term for term in CHART_TERMS if term in chart_report]
    if not report_terms:
        warnings.append("chart_report 中未识别出命理关键词，一致性检查降级。")
        return 70.0

    referenced = [term for term in report_terms if term in text]
    score = len(referenced) / len(report_terms) * 100
    if score < 50:
        failed_rules.append("low_chart_consistency")
        warnings.append("最终报告较少引用命盘计算报告中的核心信息。")
        suggested_fixes.append("在命盘摘要和传统命理分析中引用 chart_report 的日主、四柱、用神、格局或大运信息。")
    return round(score, 2)


def _run_llm_judge(llm_judge: Any, final_analysis: str) -> Dict[str, Any]:
    prompt = f"""请作为质量评估员，从结构完整性、语言质量、伦理边界、可行动性、一致性五个维度评价以下八字分析报告。
只返回简短中文评语和 0-100 分，不要重写报告。

报告：
{final_analysis}
"""
    try:
        response = llm_judge.invoke(prompt)
        return {"enabled": True, "content": getattr(response, "content", str(response))}
    except Exception as exc:
        return {"enabled": True, "error": str(exc)}


def _chinese_ratio(text: str) -> float:
    visible = [char for char in text if not char.isspace()]
    if not visible:
        return 0.0
    chinese = [char for char in visible if "\u4e00" <= char <= "\u9fff"]
    return len(chinese) / len(visible)


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
