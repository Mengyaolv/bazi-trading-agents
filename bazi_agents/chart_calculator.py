def create_chart_calculator(llm):
    """Create a chart calculator agent for Bazi analysis."""

    def chart_calculator_node(state) -> dict:
        birth_info = state["birth_info"]
        analysis_date = state.get("analysis_date", "")
        analysis_datetime = state.get("analysis_datetime", analysis_date)

        prompt = f"""你是八字排盘师，负责根据出生信息计算四柱、日主、藏干、大运和基础关系。

语言要求：
- 必须使用简体中文输出。
- 不要使用英文段落、英文表头或中英混杂表达。
- 必要术语可以保留英文括注，但正文、标题、表格字段必须是中文。
- 如果输入资料里有英文，请先转写为中文再整合。

出生信息：
{birth_info}

分析日期：{analysis_date}
当前分析时间：{analysis_datetime}

请以上面的当前分析时间作为判断当前阶段和大运阶段的唯一当前时间依据，不要从示例、训练数据或历史对话推断当前年份。

任务：
1. 计算四柱：年柱、月柱、日柱、时柱。
2. 识别日主。
3. 计算大运及起运年龄。
4. 标注重要组合：六合、三合、六冲、三刑、六害、相破等。
5. 对不确定信息要明确说明“需要进一步校验”，不要伪造精确结论。

输出格式：
- 年柱：[天干][地支]
- 月柱：[天干][地支]
- 日柱：[天干][地支]
- 时柱：[天干][地支]
- 日主：[天干]（五行、阴阳）
- 藏干：列出各地支藏干。
- 大运：列出每步大运、起运年龄、年龄区间。
- 重要关系：列出明显合冲刑害破。

请用传统八字方法给出清晰、可追溯的中文排盘报告。
"""

        response = llm.invoke(prompt)
        chart_report = f"命盘计算师：{response.content}"

        return {"chart_report": chart_report}

    return chart_calculator_node
