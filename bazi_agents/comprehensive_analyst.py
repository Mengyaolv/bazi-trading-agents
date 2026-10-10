from utils.prompt_loader import render_prompt


def create_comprehensive_analyst(llm):
    """Create a comprehensive analyst agent for final Bazi analysis."""

    def comprehensive_analyst_node(state) -> dict:
        birth_info = state["birth_info"]
        chart_report = state["chart_report"]
        day_master_report = state["day_master_report"]
        ten_gods_report = state["ten_gods_report"]
        pattern_report = state["pattern_report"]
        useful_god_report = state["useful_god_report"]
        luck_cycle_report = state["luck_cycle_report"]
        bazi_debate_state = state["bazi_debate_state"]

        traditional_history = bazi_debate_state.get("traditional_history", "")
        psychology_history = bazi_debate_state.get("psychology_history", "")
        debate_history = bazi_debate_state.get("history", "")

        prompt = render_prompt(
            "comprehensive_analyst.md",
            birth_info=birth_info,
            chart_report=chart_report,
            day_master_report=day_master_report,
            ten_gods_report=ten_gods_report,
            pattern_report=pattern_report,
            useful_god_report=useful_god_report,
            luck_cycle_report=luck_cycle_report,
            traditional_history=traditional_history,
            psychology_history=psychology_history,
            debate_history=debate_history,
        )

        response = llm.invoke(prompt)
        final_analysis = response.content

        return {"final_analysis": final_analysis}

    return comprehensive_analyst_node
