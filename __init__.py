# Bazi Trading Agents - 八字分析多智能体框架

"""
Bazi Trading Agents - A multi-agent framework for Bazi (Four Pillars) analysis
that combines traditional Chinese metaphysics with modern psychology.

This framework uses a multi-agent architecture inspired by TradingAgents,
but adapted for Bazi analysis with specialized agents for:
- Chart calculation (四柱排盘)
- Day master analysis (日主分析)
- Ten gods analysis (十神分析)
- Pattern analysis (格局分析)
- Useful god analysis (用神分析)
- Luck cycle analysis (大运分析)
- Traditional vs Psychological debate
- Comprehensive synthesis

Example usage:
    from bazi_graph import BaziAnalysisGraph

    # Initialize the graph
    graph = BaziAnalysisGraph(
        llm_provider="siliconflow",
        llm_model="deepseek-ai/DeepSeek-V3",
        base_url="https://api.siliconflow.cn/v1",
        debug=True
    )

    # Run analysis
    birth_info = "1990年9月5日8:00，男，农历"
    final_state, final_analysis = graph.analyze(birth_info)

    print(final_analysis)
"""

__version__ = "0.1.0"
__author__ = "Wu Zhongpei"

from bazi_graph import BaziAnalysisGraph
from utils import BaziAnalysisMemory, BaziAnalysisState, BaziDebateState

__all__ = [
    "BaziAnalysisGraph",
    "BaziAnalysisMemory",
    "BaziAnalysisState",
    "BaziDebateState",
]
