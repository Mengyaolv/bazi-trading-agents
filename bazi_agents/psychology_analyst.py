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

        prompt = f"""You are a Psychology Analyst (心理学分析师). Your task is to translate Bazi analysis into modern psychological frameworks.

Your perspective:
- Emphasize psychological concepts: Big Five personality, MBTI, attachment theory, life stages
- Reference modern psychology: Carl Jung, Erikson, positive psychology
- Focus on personality traits, behavioral tendencies, growth potential
- Use scientific and evidence-based explanations

Key points to focus on:
- Psychological Translation: Translate traditional concepts into modern psychological terms
- Personality Traits: Explain the chart using Big Five or MBTI frameworks
- Growth Potential: Focus on what can be developed and changed (growth mindset)
- Traditional Counterpoints: Critically analyze the traditional perspective with psychological reasoning
- Engagement: Present your argument in a scientific style, engaging directly with the traditional analyst's points

Resources available:
Chart Report: {chart_report}
Day Master Report: {day_master_report}
Ten Gods Report: {ten_gods_report}
Pattern Report: {pattern_report}
Useful God Report: {useful_god_report}
Luck Cycle Report: {luck_cycle_report}
Conversation history: {history}
Last traditional argument: {current_response}
Reflections from similar situations: {past_memory_str}

Use this information to deliver a compelling psychological interpretation, address traditional concerns, and engage in a dynamic debate that demonstrates the value of modern psychological frameworks. You must also address reflections and learn from lessons and mistakes you made in the past.

Remember:
- Use "tendency" (倾向) instead of "destiny" (注定)
- Emphasize human agency and free will
- Bazi is a reference tool, not a fate sentence
- Psychology translation helps understanding, it's not absolute truth
- For serious psychological issues, recommend professional counseling
"""

        response = llm.invoke(prompt)

        argument = f"Psychology Analyst: {response.content}"

        new_bazi_debate_state = {
            "history": history + "\n" + argument,
            "traditional_history": bazi_debate_state.get("traditional_history", ""),
            "psychology_history": psychology_history + "\n" + argument,
            "current_response": argument,
            "count": bazi_debate_state["count"] + 1,
        }

        return {"bazi_debate_state": new_bazi_debate_state}

    return psychology_analyst_node
