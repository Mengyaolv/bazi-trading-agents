#!/usr/bin/env python3
"""Rule-based quality evaluation checks."""

from utils.quality import evaluate_analysis_quality, should_rewrite


GOOD_REPORT = """
# 综合八字分析

## 命盘摘要
- 出生信息：1990-09-05 08:00
- 四柱与日主：日主癸水，参考四柱、五行与十神信息。

## 传统命理分析
- 核心格局：结合格局、用神和大运判断阶段倾向。（依据等级：A）

## 现代心理学转译
- 可参考的人格倾向：这只是理解工具，不是心理诊断。（依据等级：C）

## 当前阶段策略
- 当前阶段适合观察节奏，保持稳健调整。

## 行动建议
- 短期：记录精力变化。
- 中期：优化工作节奏。
- 长期：根据现实反馈修正目标。

## 风险与边界
- 本报告仅供参考，不能替代心理咨询、医疗、法律、投资或婚姻决策建议。
"""


BAD_REPORT = "鍏 鈫 锛 你注定失败，一定会死亡。研究表明成功率提升88%。"


def test_good_report_passes():
    state = {"chart_report": "日主 四柱 用神 格局 大运 十神 五行"}
    report = evaluate_analysis_quality(GOOD_REPORT, state)
    assert report["overall_score"] >= 75, report
    assert "mojibake_detected" not in report["failed_rules"]
    assert "absolute_or_fatalistic_language" not in report["failed_rules"]


def test_bad_report_is_flagged():
    state = {"chart_report": "日主 四柱 用神 格局 大运 十神 五行"}
    report = evaluate_analysis_quality(BAD_REPORT, state)
    assert "mojibake_detected" in report["failed_rules"]
    assert "absolute_or_fatalistic_language" in report["failed_rules"]
    assert "unsupported_quantitative_claims" in report["failed_rules"]
    assert report["overall_score"] < 70


def test_rewrite_threshold_config():
    report = {"overall_score": 60}
    assert should_rewrite(report, {"quality_rewrite_enabled": "true", "quality_min_score": 70})
    assert not should_rewrite(report, {"quality_rewrite_enabled": "false", "quality_min_score": 70})


if __name__ == "__main__":
    test_good_report_passes()
    test_bad_report_is_flagged()
    test_rewrite_threshold_config()
    print("quality checks OK")
