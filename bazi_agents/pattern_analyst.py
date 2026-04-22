def create_pattern_analyst(llm):
    """Create a pattern analyst agent for Bazi analysis."""

    def pattern_analyst_node(state) -> dict:
        birth_info = state["birth_info"]
        chart_report = state["chart_report"]
        day_master_report = state["day_master_report"]
        ten_gods_report = state["ten_gods_report"]

        prompt = f"""You are a Pattern Analyst (格局分析师). Your task is to identify and evaluate the chart's pattern (格局).

Birth Information:
{birth_info}

Chart Report:
{chart_report}

Day Master Report:
{day_master_report}

Ten Gods Report:
{ten_gods_report}

Your task:
1. Identify the pattern based on the Month Branch (月令) and revealed stems:
   - Check the hidden stems in the Month Branch
   - See if any Ten God from the Month Branch is revealed in the stems
   - Determine the pattern (正格 or 特殊格)

2. For 正格 (Normal Patterns), identify which of the 10 patterns:
   - 正官格 (Officer Pattern)
   - 七杀格 (Seven Killings Pattern)
   - 正印格 (Direct Seal Pattern)
   - 偏印格 (Indirect Seal Pattern)
   - 正财格 (Direct Wealth Pattern)
   - 偏财格 (Indirect Wealth Pattern)
   - 食神格 (Eating God Pattern)
   - 伤官格 (Hurting Officer Pattern)
   - 建禄格 (Establishing Prosperity Pattern)
   - 月刃格 (Month Blade Pattern)

3. Evaluate pattern quality (格局高低):
   - Upper Grade (上格): Useful God is effective + pattern is pure +有情
   - Middle Grade (中格): Useful God is acceptable + minor flaws
   - Lower Grade (下格): Useful God is weak + pattern is mixed

4. Provide psychological translation for the pattern

Output format:
- Pattern Type: [正格/特殊格] - [specific pattern name]
- Pattern Formation:
  * Month Branch Hidden Stems: [list]
  * Revealed Ten God: [name]
  * Pattern Quality: [上格/中格/下格]
- Pattern Evaluation:
  * Strengths: [what makes this pattern good]
  * Weaknesses: [potential issues]
- Psychological Translation: [modern psychological interpretation]
- Pattern Summary: [overall assessment]

Provide a detailed pattern analysis with traditional and modern interpretations.
"""

        response = llm.invoke(prompt)
        pattern_report = f"Pattern Analyst: {response.content}"

        return {"pattern_report": pattern_report}

    return pattern_analyst_node
