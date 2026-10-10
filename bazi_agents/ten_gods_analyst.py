def create_ten_gods_analyst(llm):
    """Create a ten gods analyst agent for Bazi analysis."""

    def ten_gods_analyst_node(state) -> dict:
        birth_info = state["birth_info"]
        chart_report = state["chart_report"]
        day_master_report = state["day_master_report"]

        prompt = f"""你是十神分析师，负责分析命盘中天干、地支藏干对应的十神分布、强弱和组合影响。

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

任务：
1. 识别明透天干和地支藏干中的十神。
2. 估计每类十神强弱，明透天干权重高于藏干。
3. 识别主导十神和相对薄弱的十神。
4. 分析关键组合及其影响：
   - 伤官见官：表达冲动与规则压力的冲突。
   - 食神制杀：以能力、创造力或稳定输出处理压力。
   - 杀印相生：压力转化为学习、资质或责任感。
   - 贪财坏印：资源追求可能削弱学习和内在稳定。
   - 枭印夺食：过度思虑可能抑制自然表达。
   - 官杀混杂：规则、标准或压力来源较复杂。
   - 比劫夺财：竞争、资源分配和边界议题。
   - 食伤生财：能力输出转化为资源。
   - 财官印连生：资源、规则、学习之间形成链条。

输出格式：
- 十神分布：
  * 十神名称：强弱、出现位置、依据。
- 主导十神：名称、命理含义、心理转译。
- 相对薄弱十神：名称、可能表现、注意边界。
- 关键组合：
  * 组合名称：命理含义、行为倾向、依据等级。
- 十神综合分析：概括人格结构和可发展方向。

请输出详细、清晰、中文化的十神分析。
"""

        response = llm.invoke(prompt)
        ten_gods_report = f"十神分析师：{response.content}"

        return {"ten_gods_report": ten_gods_report}

    return ten_gods_analyst_node
