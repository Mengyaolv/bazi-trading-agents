#!/usr/bin/env python3
"""Checks that agent prompts and report prefixes prefer Chinese output."""

from bazi_agents.chart_calculator import create_chart_calculator
from bazi_agents.day_master_analyst import create_day_master_analyst
from bazi_agents.luck_cycle_analyst import create_luck_cycle_analyst
from bazi_agents.pattern_analyst import create_pattern_analyst
from bazi_agents.psychology_analyst import create_psychology_analyst
from bazi_agents.ten_gods_analyst import create_ten_gods_analyst
from bazi_agents.traditional_analyst import create_traditional_analyst
from bazi_agents.useful_god_analyst import create_useful_god_analyst


class FakeResponse:
    content = "中文结果"


class FakeLLM:
    def __init__(self):
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        return FakeResponse()


class FakeMemory:
    def get_memories(self, *_args, **_kwargs):
        return []


def base_state():
    return {
        "birth_info": "2002年8月6日，山东枣庄，男",
        "analysis_date": "2026-06-29",
        "analysis_datetime": "2026-06-29T10:00:00+08:00",
        "chart_report": "命盘计算师：年柱壬午，月柱丁未，日主丁火。",
        "day_master_report": "日主分析师：日主丁火，偏弱。",
        "ten_gods_report": "十神分析师：比肩、食神、正财较明显。",
        "pattern_report": "格局分析师：食神格。",
        "useful_god_report": "用神分析师：以木火为用。",
        "luck_cycle_report": "大运分析师：当前庚戌大运。",
        "bazi_debate_state": {
            "traditional_history": "",
            "psychology_history": "",
            "history": "",
            "current_response": "",
            "judge_decision": "",
            "count": 0,
        },
    }


def assert_chinese_prompt(prompt):
    assert "必须使用简体中文输出" in prompt
    assert "不要使用英文段落" in prompt


def test_analysis_agents_use_chinese_prompt_and_prefixes():
    llm = FakeLLM()
    state = base_state()

    chart_result = create_chart_calculator(llm)(state)
    day_result = create_day_master_analyst(llm)(state)
    ten_result = create_ten_gods_analyst(llm)(state)
    pattern_result = create_pattern_analyst(llm)(state)
    useful_result = create_useful_god_analyst(llm)(state)
    luck_result = create_luck_cycle_analyst(llm)(state)

    for prompt in llm.prompts:
        assert_chinese_prompt(prompt)

    assert chart_result["chart_report"].startswith("命盘计算师：")
    assert day_result["day_master_report"].startswith("日主分析师：")
    assert ten_result["ten_gods_report"].startswith("十神分析师：")
    assert pattern_result["pattern_report"].startswith("格局分析师：")
    assert useful_result["useful_god_report"].startswith("用神分析师：")
    assert luck_result["luck_cycle_report"].startswith("大运分析师：")


def test_debate_agents_use_chinese_prompt_and_prefixes():
    llm = FakeLLM()
    state = base_state()
    memory = FakeMemory()

    traditional_result = create_traditional_analyst(llm, memory)(state)
    state["bazi_debate_state"] = traditional_result["bazi_debate_state"]
    psychology_result = create_psychology_analyst(llm, memory)(state)

    for prompt in llm.prompts:
        assert_chinese_prompt(prompt)

    assert traditional_result["bazi_debate_state"]["current_response"].startswith("传统命理分析师：")
    assert psychology_result["bazi_debate_state"]["current_response"].startswith("心理学转译分析师：")


if __name__ == "__main__":
    test_analysis_agents_use_chinese_prompt_and_prefixes()
    test_debate_agents_use_chinese_prompt_and_prefixes()
    print("chinese output checks OK")
