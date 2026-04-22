def create_luck_cycle_analyst(llm):
    """Create a luck cycle analyst agent for Bazi analysis."""

    def luck_cycle_analyst_node(state) -> dict:
        birth_info = state["birth_info"]
        chart_report = state["chart_report"]
        day_master_report = state["day_master_report"]
        useful_god_report = state["useful_god_report"]

        prompt = f"""You are a Luck Cycle Analyst (大运分析师). Your task is to analyze the Luck Cycles (大运) and their impact on the chart.

Birth Information:
{birth_info}

Chart Report:
{chart_report}

Day Master Report:
{day_master_report}

Useful God Report:
{useful_god_report}

Your task:
1. Analyze each Luck Cycle pillar:
   - Identify the Ten God of each pillar
   - Determine if it's favorable (喜) or unfavorable (忌) to the original chart
   - Note any interactions with the original chart (刑冲合害)

2. Map Luck Cycles to life stages with psychological translation:

   Age 0-15 (少年运 - Youth):
   - Attachment + Self-identity formation
   - Family environment shaping
   - What this Luck Cycle means for early development

   Age 15-30 (青年运 - Young Adult):
   - Exploration + Establishment
   - Education/Career/Relationship beginnings
   - What this Luck Cycle means for early adulthood

   Age 30-45 (壮年运 - Prime Adult):
   - Struggle + Achievement
   - Career peak/Family responsibilities
   - What this Luck Cycle means for prime years

   Age 45-60 (中年运 - Middle Age):
   - Transition + Integration
   - Career adjustment/Meaning seeking
   - What this Luck Cycle means for middle age

   Age 60+ (晚年运 - Late Life):
   - Wisdom + Transcendence
   - Legacy/Enjoyment/Reflection
   - What this Luck Cycle means for later years

3. Identify current life stage and Luck Cycle
4. Provide strategic advice for the current period

Output format:
- Luck Cycle Analysis:
  * [Age range]: [Pillar] - [Ten God] - [Favorable/Unfavorable] - [Interactions]
- Current Life Stage:
  * Age: [current age]
  * Luck Cycle: [current pillar]
  * Stage Theme: [psychological theme]
  * Is it Favorable: [Yes/No] - [explanation]
- Life Stage Mapping:
  * [Age range]: [traditional name] - [psychological stage] - [Luck Cycle theme]
- Current Period Strategy:
  * Current Status: [favorable period or challenging period]
  * Recommended Strategy: [specific actionable advice]
- Luck Cycle Summary: [overall assessment of luck cycles]

Provide a detailed analysis with psychological translations for each life stage.
"""

        response = llm.invoke(prompt)
        luck_cycle_report = f"Luck Cycle Analyst: {response.content}"

        return {"luck_cycle_report": luck_cycle_report}

    return luck_cycle_analyst_node
