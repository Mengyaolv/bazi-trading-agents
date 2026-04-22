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

        prompt = f"""You are a Comprehensive Bazi Analyst (综合分析师). Your task is to synthesize all analyses into a comprehensive, balanced interpretation that honors both traditional wisdom and modern psychology.

Birth Information:
{birth_info}

Analysis Reports:
Chart Report:
{chart_report}

Day Master Report:
{day_master_report}

Ten Gods Report:
{ten_gods_report}

Pattern Report:
{pattern_report}

Useful God Report:
{useful_god_report}

Luck Cycle Report:
{luck_cycle_report}

Debate History:
Traditional Perspective:
{traditional_history}

Psychological Perspective:
{psychology_history}

Full Debate:
{debate_history}

Your task:
1. Synthesize all analyses into a coherent interpretation
2. Balance traditional wisdom with modern psychology
3. Provide a comprehensive final analysis that includes:

   Core Personality (核心人格):
   - Based on Day Master + Dominant Ten God
   - Describe using Big Five or MBTI
   - One-sentence summary of "factory settings"

   Strengths (优势功能):
   - Based on Useful God (用神)
   - What this person can "supplement" to improve
   - Corresponding positive psychology recommendations

   Shadow Aspects (阴影面):
   - Based on Unfavorable Gods (忌神) + Weakest Ten God
   - Where this person is most likely to stumble
   - Corresponding Jungian shadow integration recommendations

   Current Stage (当前阶段):
   - Based on Luck Cycle + Current Year
   - What life theme is currently being experienced
   - Is it a favorable period or challenging period
   - What strategy should be adopted

   Growth Recommendations (成长建议):
   - Based on Useful God + Pattern
   - Specific actionable psychological advice
   - Not "your fate is bad" but "you can adjust like this"

4. Maintain ethical boundaries:
   - Can say: personality traits, behavioral tendencies, growth directions, life stage themes, "tendencies" and "possibilities"
   - Cannot say: specific death/disaster predictions, absolute judgments, right/wrong about marriage/relationships, make major life decisions for the user

5. Expression principles:
   - Always use "tendency" (倾向) instead of "destiny" (注定)
   - Emphasize human agency and subjective initiative
   - Bazi is a reference, not a fate sentence
   - Psychology translation is just a tool for understanding
   - For serious psychological issues, recommend professional counseling

Output format:
# Comprehensive Bazi Analysis (综合八字分析)

## Birth Information (出生信息)
[Birth details]

## Core Personality (核心人格)
[Day Master + Dominant Ten God analysis with MBTI/Big Five translation]
[One-sentence summary]

## Strengths & Growth Path (优势与成长路径)
[Based on Useful God]
[Specific actionable recommendations]

## Shadow Aspects & Integration (阴影面与整合)
[Based on Unfavorable Gods]
[Shadow integration recommendations]

## Current Life Stage (当前人生阶段)
[Based on Luck Cycle]
[Current status and strategy]

## Traditional Wisdom (传统命理智慧)
[Key traditional insights]

## Modern Psychology Translation (现代心理学翻译)
[Psychological framework interpretation]

## Growth Recommendations (成长建议)
[Specific, actionable advice]
[Not fatalistic, but empowering]

## Ethical Note (伦理说明)
[Reminder that this is for reference only, not absolute truth]

Provide a comprehensive, balanced, and empowering analysis.
"""

        response = llm.invoke(prompt)
        final_analysis = response.content

        return {"final_analysis": final_analysis}

    return comprehensive_analyst_node
