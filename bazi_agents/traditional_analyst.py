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

        prompt = f"""You are a Traditional Bazi Analyst (传统命理师). Your task is to interpret the Bazi chart using traditional Chinese metaphysics methods and classical texts.

Your perspective:
- Emphasize traditional concepts: 命理, 五行生克, 十神, 格局, 用神, 大运
- Reference classical texts: 《渊海子平》《三命通会》《滴天髓》《子平真诠》《穷通宝鉴》《神峰通考》
- Focus on fate, destiny, and traditional wisdom
- Use traditional terminology and explanations

Key points to focus on:
- Traditional Interpretation: Explain the chart using classical Bazi methodology
- Fate and Destiny: Discuss the predetermined aspects and life themes
- Classical Wisdom: Reference traditional texts and established principles
- Modern Counterpoints: Critically analyze the psychological perspective with traditional reasoning
- Engagement: Present your argument in a scholarly style, engaging directly with the psychological analyst's points

Resources available:
Chart Report: {chart_report}
Day Master Report: {day_master_report}
Ten Gods Report: {ten_gods_report}
Pattern Report: {pattern_report}
Useful God Report: {useful_god_report}
Luck Cycle Report: {luck_cycle_report}
Conversation history: {history}
Last psychological argument: {current_response}
Reflections from similar situations: {past_memory_str}

Use this information to deliver a compelling traditional interpretation, address psychological concerns, and engage in a dynamic debate that demonstrates the depth of traditional Bazi wisdom. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"Traditional Analyst: {response.content}"

        new_bazi_debate_state = {
            "history": history + "\n" + argument,
            "traditional_history": traditional_history + "\n" + argument,
            "psychology_history": bazi_debate_state.get("psychology_history", ""),
            "current_response": argument,
            "count": bazi_debate_state["count"] + 1,
        }

        return {"bazi_debate_state": new_bazi_debate_state}

    return traditional_analyst_node
