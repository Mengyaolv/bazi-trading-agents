def create_day_master_analyst(llm):
    """Create a day master analyst agent for Bazi analysis."""

    def day_master_analyst_node(state) -> dict:
        birth_info = state["birth_info"]
        chart_report = state["chart_report"]

        prompt = f"""你是日主分析师，负责分析日主五行、阴阳、强弱和基本性情倾向。

语言要求：
- 必须使用简体中文输出。
- 不要使用英文段落、英文表头或中英混杂表达。
- 若前序报告含英文，请先翻译为中文再引用。

出生信息：
{birth_info}

命盘计算报告：
{chart_report}

任务：
1. 识别日主天干、五行和阴阳。
2. 按以下维度分析日主强弱：
   - 月令：约 40%，判断是否得令。
   - 根气：约 30%，判断地支是否有根。
   - 天干帮身：约 20%，判断是否有同类或生扶。
   - 五行整体平衡：约 10%，判断耗泄克制情况。
3. 判断日主是身旺、身弱还是中和。
4. 结合五行性质描述性格倾向，避免绝对化。
5. 标注特殊情况和不确定点。

输出格式：
- 日主：天干、五行、阴阳。
- 强弱分析：
  * 月令：得令/失令及依据。
  * 根气：有根/无根及依据。
  * 天干帮身：有帮/无帮及依据。
  * 整体平衡：耗泄、生扶、克制的综合判断。
- 结论：身旺/身弱/中和。
- 性格倾向：基于五行的温和描述。
- 特别说明：需要校验或不可过度断言之处。

请按传统八字方法输出完整中文分析。
"""

        response = llm.invoke(prompt)
        day_master_report = f"日主分析师：{response.content}"

        return {"day_master_report": day_master_report}

    return day_master_analyst_node
