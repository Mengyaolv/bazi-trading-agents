def create_useful_god_analyst(llm):
    """Create a useful god analyst agent for Bazi analysis."""

    def useful_god_analyst_node(state) -> dict:
        birth_info = state["birth_info"]
        chart_report = state["chart_report"]
        day_master_report = state["day_master_report"]
        ten_gods_report = state["ten_gods_report"]
        pattern_report = state["pattern_report"]

        prompt = f"""You are a Useful God Analyst (用神分析师). Your task is to identify the Useful God (用神) using traditional methods.

Birth Information:
{birth_info}

Chart Report:
{chart_report}

Day Master Report:
{day_master_report}

Ten Gods Report:
{ten_gods_report}

Pattern Report:
{pattern_report}

Your task:
1. Apply the four methods to identify the Useful God:

   Method 1: Support/Suppress Method (扶抑法)
   - If Day Master is Strong (身旺): Use Eating God (食神), Hurting Officer (伤官), Wealth (财), or Officer (七杀) to drain or control
   - If Day Master is Weak (身弱): Use Seal (印) or Self/Rob Wealth (比劫) to support

   Method 2: Climate Adjustment Method (调候法 - from 穷通宝鉴)
   - Spring (寅卯): Use Geng Metal (庚金) to split Jia and attract Ding
   - Summer (巳午): Use Ren Water (壬水) to adjust climate
   - Autumn (申酉): Use Bing Fire (丙火) to warm the chart
   - Winter (亥子): Use Bing Fire (丙火) or Ding Fire (丁火) as priority
   - Earth months (辰戌丑未): Use Jia Wood (甲木) to break through earth

   Method 3: Mediation Method (通关法)
   - Wood vs Earth: Use Fire to mediate
   - Metal vs Wood: Use Water to mediate
   - Water vs Fire: Use Wood to mediate
   - Fire vs Metal: Use Earth to mediate
   - Earth vs Water: Use Metal to mediate

   Method 4: Disease-Cure Method (病药法)
   - Identify the disease (most prominent imbalance)
   - Find the cure (Five Element or Ten God that treats the disease)

2. Synthesize the results from all methods
3. Identify the primary Useful God and secondary Useful God
4. Explain why this is the Useful God
5. Provide psychological translation (what "supplementing" this element means for personal growth)

Output format:
- Method 1 - Support/Suppress: [result] - [explanation]
- Method 2 - Climate Adjustment: [result] - [explanation]
- Method 3 - Mediation: [result] - [explanation]
- Method 4 - Disease-Cure: [result] - [explanation]
- Primary Useful God: [Five Element/Ten God] - [reason]
- Secondary Useful God: [Five Element/Ten God] - [reason]
- Psychological Translation:
  * What to supplement: [description]
  * Growth path: [specific actionable advice]
- Useful God Summary: [overall conclusion]

Provide a comprehensive analysis using all four traditional methods.
"""

        response = llm.invoke(prompt)
        useful_god_report = f"Useful God Analyst: {response.content}"

        return {"useful_god_report": useful_god_report}

    return useful_god_analyst_node
