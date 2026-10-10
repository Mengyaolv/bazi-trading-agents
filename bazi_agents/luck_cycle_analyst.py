def create_luck_cycle_analyst(llm):
    """Create a luck cycle analyst agent for Bazi analysis."""

    def luck_cycle_analyst_node(state) -> dict:
        birth_info = state["birth_info"]
        chart_report = state["chart_report"]
        day_master_report = state["day_master_report"]
        useful_god_report = state["useful_god_report"]

        prompt = f"""你是大运分析师，负责分析每步大运与原局的关系、当前阶段主题和行动策略。

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

用神分析报告：
{useful_god_report}

任务：
1. 分析每步大运：
   - 判断大运干支对应的十神。
   - 判断对原局是偏喜、偏忌还是中性。
   - 标注与原局的刑冲合害、合化、生克关系。

2. 将大运映射到人生阶段，并做现代心理转译：

   0-15 岁：少年阶段
   - 家庭环境、依恋关系、自我认同萌芽。
   - 说明该阶段大运对早期发展的倾向。

   15-30 岁：青年阶段
   - 学业、职业探索、关系建立和身份确认。
   - 说明该阶段大运对探索和立足的影响。

   30-45 岁：壮年阶段
   - 事业承担、资源整合、家庭责任和成就压力。
   - 说明该阶段大运的机会与挑战。

   45-60 岁：中年阶段
   - 转型、整合、意义感和生活结构调整。
   - 说明该阶段大运的调整方向。

   60 岁以后：晚年阶段
   - 经验沉淀、传承、生活节奏和身心照顾。
   - 说明该阶段大运的稳定与回顾主题。

3. 识别当前所处大运和人生阶段。
4. 给出当前阶段的策略建议。

输出格式：
- 大运列表：
  * 年龄区间：大运干支、对应十神、喜忌判断、与原局互动。
- 当前阶段：
  * 当前年龄。
  * 当前大运。
  * 阶段主题。
  * 喜忌判断及理由。
- 人生阶段映射：
  * 年龄区间：传统阶段、心理阶段、阶段主题。
- 当前阶段策略：
  * 当前状态。
  * 推荐策略。
  * 需要谨慎的方向。
- 大运总结：总体评估和依据等级。

请输出详细、中文化、克制的大运分析。
"""

        response = llm.invoke(prompt)
        luck_cycle_report = f"大运分析师：{response.content}"

        return {"luck_cycle_report": luck_cycle_report}

    return luck_cycle_analyst_node
