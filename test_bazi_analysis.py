#!/usr/bin/env python3
"""
Test script for Bazi Trading Agents
八字分析多智能体框架测试脚本
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bazi_graph import BaziAnalysisGraph


def test_bazi_analysis():
    """Test Bazi analysis with a sample birth chart."""

    print("=" * 60)
    print("Bazi Trading Agents - 八字分析多智能体框架测试")
    print("=" * 60)
    print()

    # Initialize the graph
    print("正在初始化八字分析图...")
    graph = BaziAnalysisGraph(
        llm_provider="siliconflow",
        llm_model="deepseek-ai/DeepSeek-V3",
        base_url="https://api.siliconflow.cn/v1",
        debug=True,
    )
    print("初始化完成！")
    print()

    # Test with user's birth chart (from memory)
    birth_info = "1990年9月5日8:00，男，农历七月十七日辰时，海南万宁"
    print(f"出生信息: {birth_info}")
    print()

    print("开始八字分析...")
    print("-" * 60)
    print()

    try:
        # Run analysis
        final_state, final_analysis = graph.analyze(birth_info)

        print()
        print("-" * 60)
        print("分析完成！")
        print()
        print("=" * 60)
        print("最终分析结果")
        print("=" * 60)
        print()
        print(final_analysis)
        print()
        print("=" * 60)

        # Save to file
        results_dir = Path("./results")
        results_dir.mkdir(exist_ok=True)

        output_file = results_dir / "test_analysis_output.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("八字分析结果\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"出生信息: {birth_info}\n\n")
            f.write(final_analysis)
            f.write("\n\n" + "=" * 60 + "\n")

        print(f"\n结果已保存到: {output_file}")

        return True

    except Exception as e:
        print(f"错误: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_bazi_analysis()
    sys.exit(0 if success else 1)
