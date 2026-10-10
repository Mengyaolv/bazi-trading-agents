def create_psychology_analyst(llm, memory):
    """Create a psychology analyst agent for Bazi analysis."""

    def psychology_analyst_node(state) -> dict:
        bazi_debate_state = state["bazi_debate_state"]
        history = bazi_debate_state.get("history", "")
        psychology_history = bazi_debate_state.get("psychology_history", "")

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

        prompt = f"""你是现代心理学转译分析师，负责把八字分析转译成更容易理解的心理倾向、行为模式和成长建议。

语言要求：
- 必须使用简体中文输出。
- 不要使用英文段落、英文表头或中英混杂表达。
- Big Five、MBTI 等必要术语可以保留英文括注，但解释必须是中文。
- 若前序报告或记忆含英文，请先翻译为中文再引用。

你的视角：
- 可以参考大五人格、MBTI、依恋关系、人生发展阶段、积极心理学等框架。
- 重点讨论人格倾向、行为模式、成长空间和可行动建议。
- 不要把心理转译写成临床诊断。
- 不要把八字判断包装成科学结论。

重点任务：
- 将传统命理概念转译为现代心理语言。
- 对传统命理观点进行回应：指出可解释之处和需要谨慎之处。
- 强调人的主观能动性和现实行动。
- 如涉及严重心理压力，应建议寻求专业心理咨询。

可用资料：
命盘计算报告：{chart_report}
日主分析报告：{day_master_report}
十神分析报告：{ten_gods_report}
格局分析报告：{pattern_report}
用神分析报告：{useful_god_report}
大运分析报告：{luck_cycle_report}
对话历史：{history}
上一轮传统命理观点：{current_response}
相似案例反思：{past_memory_str}

请输出一段中文心理转译观点，包含可理解的心理解释、对传统观点的回应、行动建议和边界提醒。
"""

        response = llm.invoke(prompt)

        argument = f"心理学转译分析师：{response.content}"

        new_bazi_debate_state = {
            "history": history + "\n" + argument,
            "traditional_history": bazi_debate_state.get("traditional_history", ""),
            "psychology_history": psychology_history + "\n" + argument,
            "current_response": argument,
            "count": bazi_debate_state["count"] + 1,
        }

        return {"bazi_debate_state": new_bazi_debate_state}

    return psychology_analyst_node
