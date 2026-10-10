def create_useful_god_analyst(llm):
    """Create a useful god analyst agent for Bazi analysis."""

    def useful_god_analyst_node(state) -> dict:
        birth_info = state["birth_info"]
        chart_report = state["chart_report"]
        day_master_report = state["day_master_report"]
        ten_gods_report = state["ten_gods_report"]
        pattern_report = state["pattern_report"]

        prompt = f"""你是用神分析师，负责综合扶抑、调候、通关、病药四法判断用神和忌神。

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

格局分析报告：
{pattern_report}

任务：
1. 用四种方法判断用神：

   方法一：扶抑法
   - 身旺：考虑食伤、财、官杀等泄耗制化。
   - 身弱：考虑印星、比劫等生扶。

   方法二：调候法
   - 春月重疏泄平衡。
   - 夏月重水火调候。
   - 秋月重温润与生化。
   - 冬月重火暖局。
   - 辰戌丑未月重木疏土、调湿燥。

   方法三：通关法
   - 木土冲突，以火通关。
   - 金木冲突，以水通关。
   - 水火冲突，以木通关。
   - 火金冲突，以土通关。
   - 土水冲突，以金通关。

   方法四：病药法
   - 找出最明显的不平衡之处。
   - 找出可缓解该不平衡的五行或十神。

2. 综合四法结果。
3. 判断首要用神、辅助用神和忌神。
4. 说明判断依据和不确定点。
5. 给出现代行动转译：补充某元素在现实生活中对应什么行为策略。

输出格式：
- 扶抑法：结果和依据。
- 调候法：结果和依据。
- 通关法：结果和依据。
- 病药法：结果和依据。
- 首要用神：五行/十神及理由。
- 辅助用神：五行/十神及理由。
- 忌神或需节制之神：理由和边界。
- 现实行动转译：
  * 需要补充什么。
  * 对应的成长路径和可执行建议。
- 用神总结：综合结论和依据等级。

请输出完整、中文化、可追溯的用神分析。
"""

        response = llm.invoke(prompt)
        useful_god_report = f"用神分析师：{response.content}"

        return {"useful_god_report": useful_god_report}

    return useful_god_analyst_node
