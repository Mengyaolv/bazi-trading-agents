"""Rule constants for analysis quality evaluation."""

REQUIRED_SECTIONS = [
    "命盘摘要",
    "传统命理分析",
    "现代心理学转译",
    "当前阶段策略",
    "行动建议",
    "风险与边界",
]

MOJIBAKE_MARKERS = (
    "鍏",
    "鈫",
    "锛",
    "鐢",
    "涓",
    "闆",
    "鏃",
    "€",
    "�",
)

ABSOLUTE_RISK_PATTERNS = (
    "必然发生",
    "注定失败",
    "注定离婚",
    "一定会死亡",
    "一定死亡",
    "必离婚",
    "必有灾祸",
    "绝对会",
    "必死",
    "必破产",
)

FABRICATED_EVIDENCE_PATTERNS = (
    "研究表明",
    "数据显示",
    "实验显示",
    "统计显示",
    "临床证明",
)

ETHICAL_BOUNDARY_PATTERNS = (
    "不能替代",
    "不替代",
    "仅供参考",
    "参考框架",
    "专业人士",
    "心理咨询",
    "医疗",
    "法律",
    "投资",
    "婚姻决策",
)

ACTIONABLE_PATTERNS = (
    "建议",
    "可以",
    "优先",
    "避免",
    "保持",
    "观察",
    "短期",
    "中期",
    "长期",
)

CHART_TERMS = (
    "日主",
    "四柱",
    "年柱",
    "月柱",
    "日柱",
    "时柱",
    "用神",
    "格局",
    "大运",
    "十神",
    "五行",
)
