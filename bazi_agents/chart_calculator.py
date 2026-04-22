def create_chart_calculator(llm):
    """Create a chart calculator agent for Bazi analysis."""

    def chart_calculator_node(state) -> dict:
        birth_info = state["birth_info"]
        analysis_date = state.get("analysis_date", "")

        prompt = f"""You are a Bazi Chart Calculator (八字排盘师). Your task is to calculate the Four Pillars (四柱) and Luck Cycles (大运) based on birth information.

Birth Information:
{birth_info}

Analysis Date: {analysis_date}

Your task:
1. Calculate the Four Pillars (Year Pillar, Month Pillar, Day Pillar, Hour Pillar)
2. Identify the Day Master (日主)
3. Calculate the Luck Cycles (大运) with starting ages
4. Note any special combinations (六合, 三合, 六冲, 三刑, 六害, 相破)

Output format:
- Year Pillar: [天干][地支]
- Month Pillar: [天干][地支]
- Day Pillar: [天干][地支]
- Hour Pillar: [天干][地支]
- Day Master: [天干] ([五行] [阴阳])
- Hidden Stems (藏干): List all hidden stems in each earthly branch
- Luck Cycles: List each luck pillar with starting age
- Special Combinations: Note any significant combinations

Provide a detailed and accurate chart calculation. Use traditional Bazi calculation methods.
"""

        response = llm.invoke(prompt)
        chart_report = f"Chart Calculator: {response.content}"

        return {"chart_report": chart_report}

    return chart_calculator_node
