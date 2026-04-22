def create_ten_gods_analyst(llm):
    """Create a ten gods analyst agent for Bazi analysis."""

    def ten_gods_analyst_node(state) -> dict:
        birth_info = state["birth_info"]
        chart_report = state["chart_report"]
        day_master_report = state["day_master_report"]

        prompt = f"""You are a Ten Gods Analyst (十神分析师). Your task is to analyze the distribution and effects of the Ten Gods (十神) in the chart.

Birth Information:
{birth_info}

Chart Report:
{chart_report}

Day Master Report:
{day_master_report}

Your task:
1. Identify all Ten Gods in the chart (both revealed stems and hidden stems)
2. Calculate the strength of each Ten God (revealed stems have higher weight)
3. Identify the dominant Ten God (主导人格) and the weakest Ten God (阴影面)
4. Analyze key Ten God combinations and their effects:
   - 伤官见官 (Hurting Officer meets Officer): Conflict between rebellion and authority
   - 食神制杀 (Eating God controls Seven Killings): Using talent to handle pressure
   - 杀印相生 (Seven Killings generates Seal): Converting pressure into learning
   - 贪财坏印 (Greed for wealth damages Seal): Material pursuit harms spiritual growth
   - 枭印夺食 (Owl Seal captures Eating God): Obsession suppresses creativity
   - 官杀混杂 (Officer and Seven Killings mixed): Confused standards
   - 比劫夺财 (Competitors seize wealth): Competition for resources
   - 食伤生财 (Eating God generates Wealth): Best path for monetizing talent
   - 财官印连生 (Wealth-Officer-Seal chain): Perfect life path

Output format:
- Ten Gods Distribution:
  * [Ten God]: [strength] - [location in chart]
- Dominant Ten God: [name] - [psychological translation]
- Weakest Ten God: [name] - [shadow aspect]
- Key Combinations:
  * [Combination]: [effect] - [psychological translation]
- Overall Ten God Analysis: [summary of personality structure]

Provide a detailed analysis with psychological translations for each Ten God.
"""

        response = llm.invoke(prompt)
        ten_gods_report = f"Ten Gods Analyst: {response.content}"

        return {"ten_gods_report": ten_gods_report}

    return ten_gods_analyst_node
