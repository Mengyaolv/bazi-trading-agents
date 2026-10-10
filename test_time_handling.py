#!/usr/bin/env python3
"""Checks for runtime date handling without calling real APIs."""

import re

from bazi_agents.chart_calculator import create_chart_calculator
from utils.time_utils import current_analysis_date, current_analysis_datetime, normalize_analysis_datetime


class FakeResponse:
    content = "ok"


class FakeLLM:
    def __init__(self):
        self.prompt = ""

    def invoke(self, prompt):
        self.prompt = prompt
        return FakeResponse()


def test_current_date_and_datetime_are_runtime_values():
    analysis_date = current_analysis_date()
    analysis_datetime = current_analysis_datetime()
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", analysis_date)
    assert analysis_datetime.startswith(analysis_date)
    assert analysis_date != "2023-01-01"


def test_normalize_analysis_datetime_respects_explicit_date():
    assert normalize_analysis_datetime("2026-06-28", "2026-06-28T16:30:00+08:00") == "2026-06-28T16:30:00+08:00"
    assert normalize_analysis_datetime("2026-06-28").startswith("2026-06-28")


def test_chart_prompt_receives_current_analysis_datetime():
    llm = FakeLLM()
    node = create_chart_calculator(llm)
    node(
        {
            "birth_info": "birth info",
            "analysis_date": "2026-06-28",
            "analysis_datetime": "2026-06-28T16:30:00+08:00",
        }
    )
    assert "分析日期：2026-06-28" in llm.prompt
    assert "当前分析时间：2026-06-28T16:30:00+08:00" in llm.prompt
    assert "不要从示例、训练数据或历史对话推断当前年份" in llm.prompt


if __name__ == "__main__":
    test_current_date_and_datetime_are_runtime_values()
    test_normalize_analysis_datetime_respects_explicit_date()
    test_chart_prompt_receives_current_analysis_datetime()
    print("time handling checks OK")
