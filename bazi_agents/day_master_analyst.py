def create_day_master_analyst(llm):
    """Create a day master analyst agent for Bazi analysis."""

    def day_master_analyst_node(state) -> dict:
        birth_info = state["birth_info"]
        chart_report = state["chart_report"]

        prompt = f"""You are a Day Master Analyst (日主分析师). Your task is to analyze the Day Master's strength and characteristics.

Birth Information:
{birth_info}

Chart Report:
{chart_report}

Your task:
1. Identify the Day Master (天干) and its Five Element (五行) and Yin-Yang (阴阳)
2. Analyze Day Master strength using these criteria:
   - Month Command (月令): 40% weight - is the Day Master in season?
   - Root Qi (根气): 30% weight - does the Day Master have roots in earthly branches?
   - Heavenly Stems support (天干帮身): 20% weight - are there supporting stems?
   - Overall Five Element balance: 10% weight
3. Determine if Day Master is Strong (身旺), Weak (身弱), or Balanced (中和)
4. Describe the Day Master's personality traits based on its Five Element
5. Note any special characteristics (e.g., if Day Master is in a special position)

Output format:
- Day Master: [天干] ([五行] [阴阳])
- Strength Analysis:
  * Month Command: [得令/失令] with explanation
  * Root Qi: [有根/无根] with explanation
  * Heavenly Stems Support: [有帮/无帮] with explanation
  * Overall Balance: [explanation]
- Conclusion: [身旺/身弱/中和]
- Personality Traits: [description based on Five Element]
- Special Notes: [any special characteristics]

Provide a detailed analysis following the traditional Bazi methodology.
"""

        response = llm.invoke(prompt)
        day_master_report = f"Day Master Analyst: {response.content}"

        return {"day_master_report": day_master_report}

    return day_master_analyst_node
