#!/usr/bin/env python3
"""
Simple test to verify imports work correctly
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Testing imports...")

try:
    print("1. Importing utils...")
    from utils import BaziAnalysisMemory, BaziAnalysisState, BaziDebateState
    print("   [OK] Utils imported successfully")

    print("2. Importing bazi_agents...")
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
    print("   [OK] All agents imported successfully")

    print("3. Importing bazi_graph...")
    from bazi_graph import BaziAnalysisGraph
    print("   [OK] Graph imported successfully")

    print("4. Testing BaziAnalysisState...")
    state = BaziAnalysisState(
        birth_info="test",
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
    print("   [OK] State created successfully")

    print("5. Testing BaziAnalysisMemory...")
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"memory_dir": tmpdir}
        memory = BaziAnalysisMemory("test_memory", config)
        memory.add_memory("test situation", "test recommendation")
        memories = memory.get_memories("test situation")
        print(f"   [OK] Memory created and tested successfully (found {len(memories)} memories)")

    print()
    print("=" * 60)
    print("All imports and basic tests passed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Set up your LLM API credentials")
    print("2. Run: python test_bazi_analysis.py")
    print()

except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
