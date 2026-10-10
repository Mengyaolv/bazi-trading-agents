def create_pattern_analyst(llm):
    """Create a pattern analyst agent for Bazi analysis."""

    def pattern_analyst_node(state) -> dict:
        birth_info = state["birth_info"]
        chart_report = state["chart_report"]
        day_master_report = state["day_master_report"]
        ten_gods_report = state["ten_gods_report"]

        prompt = f"""你是格局分析师，负责根据月令、透干、藏干、十神结构识别命局格局并评估质量。

语言要求：
- 必须使用简体中文输出。
- 不要使用英文段落、英文表头或中英混杂表达。
- 若前序报告含英文，请先翻译为中文再引用。

出生信息：
{birth_info}

命盘计算报告：
{chart_report}

日主分析报告：
{day_master_report}

十神分析报告：
{ten_gods_report}

任务：
1. 依据月令和透干识别格局：
   - 检查月支藏干。
   - 判断月令中的十神是否透出天干。
   - 判断属于正格还是特殊格。

2. 若为正格，识别具体格局：
   - 正官格、七杀格、正印格、偏印格。
   - 正财格、偏财格、食神格、伤官格。
   - 建禄格、月刃格。

3. 评价格局质量：
   - 上格：用神有力，格局较清，配合有情。
   - 中格：用神可用，但存在小瑕疵。
   - 下格：用神较弱，结构混杂或冲克较重。

4. 给出现代心理学转译，但不得写成诊断。

输出格式：
- 格局类型：正格/特殊格，具体格局名称。
- 格局成因：
  * 月支藏干。
  * 透出十神。
  * 格局质量：上格/中格/下格。
- 格局评价：
  * 优势：结构成立的有利条件。
  * 瑕疵：混杂、冲克或用神不足处。
- 心理转译：对应的行为倾向和成长空间。
- 格局总结：总体判断和依据等级。

请输出详细、清晰、中文化的格局分析。
"""

        response = llm.invoke(prompt)
        pattern_report = f"格局分析师：{response.content}"

        return {"pattern_report": pattern_report}

    return pattern_analyst_node
