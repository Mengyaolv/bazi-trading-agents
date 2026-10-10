#!/usr/bin/env python3
"""Checks for Streamlit web support helpers without importing Streamlit."""

import json
import tempfile
from pathlib import Path

from utils.web_support import (
    build_birth_info,
    build_dual_view,
    build_focus_notes,
    build_report_overview,
    extract_action_plan,
    extract_intermediate_reports,
    extract_markdown_sections,
    get_runtime_settings,
    load_analysis_history,
    sanitize_error,
    save_feedback,
)


FAKE_FINAL_ANALYSIS = """# 综合八字分析

## 命盘摘要

日主丁火，当前阶段重在稳定节奏。

## 传统命理分析

食神与财星较明显，适合通过稳定输出积累资源。

## 现代心理学转译

表现为重视秩序、需要安全边界，同时具备持续学习能力。

## 当前阶段策略

先降低信息噪音，再做关键选择。

## 行动建议

- 今天记录一个最明显的压力信号。
- 今天完成一件确定的小事。
- 一周内观察三次重复出现的行为模式。
- 一周内安排一次深度沟通。
- 长期建立月度复盘习惯。

## 风险与边界

本报告不能替代医疗、法律、投资或心理咨询建议。
"""


FAKE_STATE = {
    "birth_info": "出生日期: 2002-08-06",
    "analysis_date": "2026-06-29",
    "chart_report": "命盘计算师：日主：丁火",
    "day_master_report": "日主分析师：丁火偏弱",
    "bazi_debate_state": {
        "traditional_history": "传统命理分析师：火土结构明显，需要木火调和。",
        "psychology_history": "心理学转译分析师：倾向于谨慎、重视秩序与稳定反馈。",
    },
    "quality_report": {"overall_score": 86},
    "final_analysis": FAKE_FINAL_ANALYSIS,
}


def test_build_birth_info_and_focus_notes():
    assert build_birth_info(free_text="already formatted") == "already formatted"
    built = build_birth_info(
        birth_date="1990-09-05",
        birth_time="08:00",
        gender="男",
        birth_place="海南万宁",
        calendar_type="农历",
        notes="测试",
        display_name="观友",
    )
    assert "称谓: 观友" in built
    assert "出生日期: 1990-09-05" in built
    assert "出生地点: 海南万宁" in built
    assert "备注: 测试" in built

    notes = build_focus_notes(["性格与优势", "当前阶段变化"], "我适合换工作吗？")
    assert "关注主题: 性格与优势、当前阶段变化" in notes
    assert "自定义问题: 我适合换工作吗？" in notes


def test_history_loading_and_filtering():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "case.json"
        path.write_text(
            json.dumps(
                {
                    "birth_info": "1990 海南万宁",
                    "analysis_date": "2026-06-28",
                    "user_id": "u1",
                    "username": "alice",
                    "final_analysis": "报告",
                    "quality_report": {"overall_score": 88},
                    "llm_provider": "mock",
                    "llm_model": "mock-model",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        for filename, owner in (("other.json", "u2"), ("admin.json", "admin"), ("legacy.json", "")):
            (Path(tmpdir) / filename).write_text(
                json.dumps({"user_id": owner, "birth_info": f"private-{owner}"}),
                encoding="utf-8",
            )
        records = load_analysis_history(tmpdir, query="海南", limit=5, user_id="u1")
        assert len(records) == 1
        assert records[0]["quality_score"] == 88
        assert load_analysis_history(tmpdir, query="海南", limit=5) == []
        assert [record["user_id"] for record in load_analysis_history(tmpdir, user_id="u2")] == ["u2"]
        assert [record["user_id"] for record in load_analysis_history(tmpdir, user_id="admin")] == ["admin"]
        assert len(load_analysis_history(tmpdir, user_id="u1", limit=1)) == 1
        assert load_analysis_history(tmpdir, query="不存在", limit=5, user_id="u1") == []


def test_extract_intermediate_reports():
    reports = extract_intermediate_reports(FAKE_STATE)
    titles = [item["title"] for item in reports]
    assert "命盘计算" in titles
    assert "日主分析" in titles
    assert "传统命理辩论" in titles


def test_report_overview_dual_view_and_actions():
    sections = extract_markdown_sections(FAKE_FINAL_ANALYSIS)
    assert "行动建议" in sections

    overview = build_report_overview(FAKE_STATE, FAKE_FINAL_ANALYSIS, ["性格与优势"])
    assert "性格与优势" in overview["tags"]
    assert overview["quality_score"] == 86
    assert len(overview["cards"]) == 4
    assert overview["top_actions"]

    dual = build_dual_view(FAKE_STATE, FAKE_FINAL_ANALYSIS, ["情绪与压力"])
    assert "传统文化视角" not in dual["traditional"]
    assert "火土结构" in dual["traditional"]
    assert "谨慎" in dual["psychology"]
    assert "压力" in dual["reflection"]

    actions = extract_action_plan(FAKE_FINAL_ANALYSIS)
    assert actions["today"]
    assert actions["week"]
    assert actions["long_term"]


def test_feedback_sanitize_and_runtime_settings():
    message = sanitize_error("failed with sk-abcdefghijklmnopqrstuvwxyz and API_KEY=secret")
    assert "sk-abcdefghijklmnopqrstuvwxyz" not in message
    assert "API_KEY=secret" not in message
    assert "***" in message

    with tempfile.TemporaryDirectory() as tmpdir:
        path = save_feedback(tmpdir, {"case_id": "case/001", "feedback": "部分准确"})
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        assert payload["feedback"] == "部分准确"
        assert "submitted_at" in payload

    settings = get_runtime_settings({"llm_provider": "mock", "memory_dir": "./m"})
    assert settings["llm_provider"] == "mock"
    assert "api_keys" in settings
    assert all(isinstance(value, bool) for value in settings["api_keys"].values())


if __name__ == "__main__":
    test_build_birth_info_and_focus_notes()
    test_history_loading_and_filtering()
    test_extract_intermediate_reports()
    test_report_overview_dual_view_and_actions()
    test_feedback_sanitize_and_runtime_settings()
    print("web support checks OK")
