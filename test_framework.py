#!/usr/bin/env python3
"""
Simple test to verify the framework works without calling LLM
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("Bazi Trading Agents - 框架验证测试")
print("=" * 60)
print()

# Test 1: Import all modules
print("测试1: 导入所有模块...")
try:
    from utils import BaziAnalysisMemory, BaziAnalysisState, BaziDebateState
    from bazi_agents import (
        create_chart_calculator,
        create_day_master_analyst,
        create_ten_gods_analyst,
        create_pattern_analyst,
        create_useful_god_analyst,
        create_luck_cycle_analyst,
        create_traditional_analyst,
        create_psychology_analyst,
        create_comprehensive_analyst,
    )
    from bazi_graph import BaziAnalysisGraph
    print("✓ 所有模块导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# Test 2: Check API keys
print()
print("测试2: 检查API密钥...")
api_keys = {
    "SILICONFLOW_API_KEY": os.environ.get("SILICONFLOW_API_KEY"),
    "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
    "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
}

found_keys = [k for k, v in api_keys.items() if v]
if found_keys:
    print(f"✓ 找到API密钥: {', '.join(found_keys)}")
else:
    print("✗ 未找到任何API密钥")
    print("  请设置以下环境变量之一:")
    print("  export SILICONFLOW_API_KEY=your_key")
    print("  export OPENAI_API_KEY=your_key")
    print("  export ANTHROPIC_API_KEY=your_key")

# Test 3: Create state
print()
print("测试3: 创建状态对象...")
try:
    state = BaziAnalysisState(
        birth_info="1990年9月5日8:00，男，农历",
        analysis_date="2026-04-22",
        sender="user",
        chart_report="",
        day_master_report="",
        ten_gods_report="",
        pattern_report="",
        useful_god_report="",
        luck_cycle_report="",
        bazi_debate_state={
            "traditional_history": "",
            "psychology_history": "",
            "history": "",
            "current_response": "",
            "judge_decision": "",
            "count": 0,
        },
        interpretation_plan="",
        psychology_translation="",
        final_analysis="",
        messages=[],
    )
    print("✓ 状态对象创建成功")
except Exception as e:
    print(f"✗ 状态对象创建失败: {e}")
    sys.exit(1)

# Test 4: Create memory
print()
print("测试4: 创建记忆系统...")
try:
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"memory_dir": tmpdir}
        memory = BaziAnalysisMemory("test_memory", config)
        memory.add_memory("test situation", "test recommendation")
        memories = memory.get_memories("test situation")
        print(f"✓ 记忆系统创建成功 (找到 {len(memories)} 条记忆)")
except Exception as e:
    print(f"✗ 记忆系统创建失败: {e}")
    sys.exit(1)

# Test 5: Initialize graph (without running)
print()
print("测试5: 初始化分析图...")
if found_keys:
    try:
        # Determine provider
        if os.environ.get("SILICONFLOW_API_KEY"):
            llm_provider = "siliconflow"
            llm_model = "deepseek-ai/DeepSeek-V3"
            base_url = "https://api.siliconflow.cn/v1"
        elif os.environ.get("OPENAI_API_KEY"):
            llm_provider = "openai"
            llm_model = "gpt-4"
            base_url = None
        elif os.environ.get("ANTHROPIC_API_KEY"):
            llm_provider = "anthropic"
            llm_model = "claude-3-opus-20240229"
            base_url = None
        else:
            raise ValueError("No API key found")

        graph = BaziAnalysisGraph(
            llm_provider=llm_provider,
            llm_model=llm_model,
            base_url=base_url,
            debug=False,
        )
        print(f"✓ 分析图初始化成功")
        print(f"  提供商: {llm_provider}")
        print(f"  模型: {llm_model}")
    except Exception as e:
        print(f"✗ 分析图初始化失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⊘ 跳过（需要API密钥）")

# Summary
print()
print("=" * 60)
print("测试总结")
print("=" * 60)
print()
print("✓ 框架基本功能正常")
print()
if found_keys:
    print("✓ API密钥已配置，可以运行完整测试:")
    print("  python3 test_bazi_analysis.py")
else:
    print("✗ 需要配置API密钥才能运行完整测试")
    print()
    print("配置方法:")
    print("  export SILICONFLOW_API_KEY=your_key")
    print("  或")
    print("  export OPENAI_API_KEY=your_key")
print()
print("=" * 60)
