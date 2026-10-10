def create_traditional_analyst(llm, memory):
    """Create a traditional Bazi analyst agent."""

    def traditional_analyst_node(state) -> dict:
        bazi_debate_state = state["bazi_debate_state"]
        history = bazi_debate_state.get("history", "")
        traditional_history = bazi_debate_state.get("traditional_history", "")

        current_response = bazi_debate_state.get("current_response", "")

        chart_report = state["chart_report"]
        day_master_report = state["day_master_report"]
        ten_gods_report = state["ten_gods_report"]
        pattern_report = state["pattern_report"]
        useful_god_report = state["useful_god_report"]
        luck_cycle_report = state["luck_cycle_report"]

        curr_situation = f"{chart_report}\n\n{day_master_report}\n\n{ten_gods_report}\n\n{pattern_report}\n\n{useful_god_report}\n\n{luck_cycle_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你是传统命理分析师，负责从传统八字视角解释命盘，并与现代心理分析观点进行克制辩论。

语言要求：
- 必须使用简体中文输出。
- 不要使用英文段落、英文表头或中英混杂表达。
- 若前序报告或记忆含英文，请先翻译为中文再引用。

你的视角：
- 强调传统概念：命理、五行生克、十神、格局、用神、大运。
- 可参考经典：《渊海子平》《三命通会》《滴天髓》《子平真诠》《穷通宝鉴》《神峰通考》。
- 使用传统术语，但必须解释给普通读者能理解。
- 讨论“倾向”和“阶段主题”，不要写成注定论。

重点任务：
- 用传统八字方法解释命盘结构。
- 说明五行、十神、格局、用神、大运之间的依据链。
- 对心理分析观点进行回应：指出可互补之处和需要保留的地方。
- 结合相似案例记忆，但不要照搬，不要泄露隐私。

可用资料：
命盘计算报告：{chart_report}
日主分析报告：{day_master_report}
十神分析报告：{ten_gods_report}
格局分析报告：{pattern_report}
用神分析报告：{useful_god_report}
大运分析报告：{luck_cycle_report}
对话历史：{history}
上一轮心理分析观点：{current_response}
相似案例反思：{past_memory_str}

请输出一段中文传统命理观点，包含依据、分歧、可采纳建议和风险边界。
"""

        response = llm.invoke(prompt)

        argument = f"传统命理分析师：{response.content}"

        new_bazi_debate_state = {
            "history": history + "\n" + argument,
            "traditional_history": traditional_history + "\n" + argument,
            "psychology_history": bazi_debate_state.get("psychology_history", ""),
            "current_response": argument,
            "count": bazi_debate_state["count"] + 1,
        }

        return {"bazi_debate_state": new_bazi_debate_state}

    return traditional_analyst_node
