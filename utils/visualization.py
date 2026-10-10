"""Visualization data extraction for Bazi analysis results."""

import re
from typing import Any, Dict, List


ELEMENTS = ["木", "火", "土", "金", "水"]
STEM_ELEMENTS = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}
BRANCH_ELEMENTS = {
    "寅": "木",
    "卯": "木",
    "巳": "火",
    "午": "火",
    "辰": "土",
    "戌": "土",
    "丑": "土",
    "未": "土",
    "申": "金",
    "酉": "金",
    "亥": "水",
    "子": "水",
}
TEN_GODS = ["比肩", "劫财", "食神", "伤官", "正财", "偏财", "正官", "七杀", "正印", "偏印"]
FLOW_STEPS = [
    ("chart_report", "命盘计算"),
    ("day_master_report", "日主分析"),
    ("ten_gods_report", "十神分析"),
    ("pattern_report", "格局分析"),
    ("useful_god_report", "用神分析"),
    ("luck_cycle_report", "大运分析"),
    ("bazi_debate_state", "传统/心理辩论"),
    ("final_analysis", "综合分析"),
    ("quality_report", "质量评估"),
]


def build_visualization_data(final_state: Dict[str, Any]) -> Dict[str, Any]:
    """Build reusable visualization data from an analysis state/log."""
    chart_report = str(final_state.get("chart_report") or "")
    all_text = "\n".join(
        str(final_state.get(field) or "")
        for field in (
            "chart_report",
            "day_master_report",
            "ten_gods_report",
            "pattern_report",
            "useful_god_report",
            "luck_cycle_report",
            "final_analysis",
        )
    )
    pillars = extract_pillars(chart_report)
    return {
        "pillars": pillars,
        "day_master": extract_day_master(chart_report, pillars),
        "element_distribution": extract_element_distribution(all_text, pillars),
        "ten_gods_distribution": extract_ten_gods_distribution(all_text),
        "luck_cycles": extract_luck_cycles(str(final_state.get("luck_cycle_report") or chart_report)),
        "flow_steps": extract_flow_steps(final_state),
        "quality_dimensions": extract_quality_dimensions(final_state.get("quality_report") or {}),
    }


def extract_pillars(chart_report: str) -> List[Dict[str, str]]:
    """Extract year/month/day/hour pillar values from chart text."""
    labels = [
        ("年柱", ("Year Pillar", "年柱")),
        ("月柱", ("Month Pillar", "月柱")),
        ("日柱", ("Day Pillar", "日柱")),
        ("时柱", ("Hour Pillar", "时柱")),
    ]
    pillars = []
    for label, aliases in labels:
        value = ""
        for alias in aliases:
            match = re.search(rf"{re.escape(alias)}\s*[:：]\s*([^\n\r]+)", chart_report, re.I)
            if match:
                value = match.group(1).strip()
                break
        pillars.append({"name": label, "value": value, "element": pillar_element(value)})

    if any(item["value"] for item in pillars):
        return pillars

    match = re.search(r"(?:Bazi Chart|四柱|八字)\s*[:：]\s*([甲乙丙丁戊己庚辛壬癸A-Za-z\s]+[子丑寅卯辰巳午未申酉戌亥A-Za-z\s]*)", chart_report, re.I)
    if match:
        tokens = [token for token in re.split(r"[\s,，、]+", match.group(1).strip()) if token][:4]
        while len(tokens) < 4:
            tokens.append("")
        return [
            {"name": name, "value": value, "element": pillar_element(value)}
            for name, value in zip(["年柱", "月柱", "日柱", "时柱"], tokens)
        ]
    return pillars


def extract_day_master(chart_report: str, pillars: List[Dict[str, str]]) -> str:
    match = re.search(r"(?:Day Master|日主)\s*[:：]\s*([甲乙丙丁戊己庚辛壬癸A-Za-z]+)", chart_report, re.I)
    if match:
        return match.group(1).strip()
    day_pillar = next((item["value"] for item in pillars if item["name"] == "日柱"), "")
    for char in day_pillar:
        if char in STEM_ELEMENTS:
            return char
    return ""


def extract_element_distribution(text: str, pillars: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    counts = {element: 0 for element in ELEMENTS}
    for pillar in pillars:
        for char in pillar.get("value", ""):
            if char in STEM_ELEMENTS:
                counts[STEM_ELEMENTS[char]] += 1
            elif char in BRANCH_ELEMENTS:
                counts[BRANCH_ELEMENTS[char]] += 1

    if not any(counts.values()):
        for element in ELEMENTS:
            counts[element] += text.count(element)
    return [{"element": element, "count": counts[element]} for element in ELEMENTS]


def extract_ten_gods_distribution(text: str) -> List[Dict[str, Any]]:
    return [
        {"ten_god": ten_god, "count": text.count(ten_god)}
        for ten_god in TEN_GODS
    ]


def extract_luck_cycles(text: str) -> List[Dict[str, str]]:
    cycles = []
    for match in re.finditer(r"(?:(\d{1,2})\s*[-~到至]\s*(\d{1,2})\s*岁?)?[^\n\r甲乙丙丁戊己庚辛壬癸]{0,8}([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])", text):
        start_age = match.group(1) or ""
        end_age = match.group(2) or ""
        pillar = match.group(3)
        item = {"pillar": pillar, "start_age": start_age, "end_age": end_age}
        if item not in cycles:
            cycles.append(item)
        if len(cycles) >= 12:
            break
    return cycles


def extract_flow_steps(final_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    steps = []
    for field, title in FLOW_STEPS:
        value = final_state.get(field)
        complete = bool(value)
        if field == "bazi_debate_state":
            debate_state = value or {}
            complete = bool(debate_state.get("count") or debate_state.get("history"))
        steps.append({"step": title, "complete": complete})
    return steps


def extract_quality_dimensions(quality_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    dimensions = quality_report.get("dimension_scores") if isinstance(quality_report, dict) else {}
    if not isinstance(dimensions, dict):
        return []
    return [
        {"dimension": key, "score": value}
        for key, value in dimensions.items()
    ]


def pillar_element(value: str) -> str:
    elements = []
    for char in str(value):
        if char in STEM_ELEMENTS:
            elements.append(STEM_ELEMENTS[char])
        elif char in BRANCH_ELEMENTS:
            elements.append(BRANCH_ELEMENTS[char])
    return "/".join(elements)
