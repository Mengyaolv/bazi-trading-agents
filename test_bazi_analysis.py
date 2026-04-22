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

    # Check for API key
    api_key = os.environ.get("SILICONFLOW_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("错误: 未找到API密钥")
        print("请设置以下环境变量之一:")
        print("  export SILICONFLOW_API_KEY=your_key")
        print("  或")
        print("  export OPENAI_API_KEY=your_key")
        print()
        return False

    # Determine provider and model
    if os.environ.get("SILICONFLOW_API_KEY"):
        llm_provider = "siliconflow"
        llm_model = "deepseek-ai/DeepSeek-V3"
        base_url = "https://api.siliconflow.cn/v1"
    elif os.environ.get("OPENAI_API_KEY"):
        llm_provider = "openai"
        llm_model = "gpt-4"
        base_url = None
    else:
        print("错误: 无法确定LLM提供商")
        return False

    # Initialize the graph
    print("正在初始化八字分析图...")
    print(f"  提供商: {llm_provider}")
    print(f"  模型: {llm_model}")
    if base_url:
        print(f"  API地址: {base_url}")
    print()

    try:
        graph = BaziAnalysisGraph(
            llm_provider=llm_provider,
            llm_model=llm_model,
            base_url=base_url,
            debug=True,
        )
        print("初始化完成！")
        print()
    except Exception as e:
        print(f"初始化失败: {e}")
        import traceback

        traceback.print_exc()
        return False

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
