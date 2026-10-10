#!/usr/bin/env python3
"""Checks for visualization data extraction."""

from utils.visualization import build_visualization_data


def test_visualization_data():
    state = {
        "chart_report": "\n".join(
            [
                "Year Pillar: 庚午",
                "Month Pillar: 甲申",
                "Day Pillar: 癸酉",
                "Hour Pillar: 丙辰",
                "Day Master: 癸",
            ]
        ),
        "day_master_report": "日主癸水",
        "ten_gods_report": "正印 正印 伤官 正财",
        "pattern_report": "格局分析",
        "useful_god_report": "用神: 火 木",
        "luck_cycle_report": "33-43岁 戊子 大运；43-53岁 己丑 大运",
        "bazi_debate_state": {"count": 2, "history": "debate"},
        "final_analysis": "综合报告",
        "quality_report": {
            "overall_score": 88,
            "dimension_scores": {"structure": 90, "language": 85},
        },
    }
    data = build_visualization_data(state)
    assert data["day_master"] == "癸"
    assert len(data["pillars"]) == 4
    assert data["pillars"][0]["value"] == "庚午"
    assert any(item["element"] == "火" and item["count"] > 0 for item in data["element_distribution"])
    assert any(item["ten_god"] == "正印" and item["count"] >= 2 for item in data["ten_gods_distribution"])
    assert data["luck_cycles"][0]["pillar"] == "戊子"
    assert any(item["step"] == "传统/心理辩论" and item["complete"] for item in data["flow_steps"])
    assert {"dimension": "structure", "score": 90} in data["quality_dimensions"]


if __name__ == "__main__":
    test_visualization_data()
    print("visualization checks OK")
