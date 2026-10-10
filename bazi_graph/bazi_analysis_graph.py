import os
from pathlib import Path
import json
from typing import Callable, Dict, Any, List, Optional

from langgraph.graph import StateGraph, END

from utils.bazi_states import BaziAnalysisState, BaziDebateState
from utils.memory import BaziAnalysisMemory
from utils.quality import build_rewrite_prompt, evaluate_analysis_quality, should_rewrite
from utils.time_utils import current_analysis_date, normalize_analysis_datetime
from utils.visualization import build_visualization_data
from bazi_agents import *
from env_loader import load_env_file


class BaziAnalysisGraph:
    """Main class that orchestrates the Bazi analysis agents framework."""

    def __init__(
        self,
        debug=False,
        config: Dict[str, Any] = None,
        llm_provider: str = "siliconflow",
        llm_model: str = "deepseek-ai/DeepSeek-V3",
        base_url: str = None,
        api_key: str = None,
    ):
        """Initialize the Bazi analysis graph and components.

        Args:
            debug: Whether to run in debug mode
            config: Configuration dictionary
            llm_provider: LLM provider (e.g., "siliconflow", "openai", "anthropic")
            llm_model: Model name
            base_url: Base URL for LLM API
        """
        self.debug = debug
        load_env_file()

        self.config = config or self._get_default_config()
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.base_url = base_url
        self.api_key = api_key

        # Create necessary directories
        os.makedirs(self.config["memory_dir"], exist_ok=True)
        os.makedirs(self.config["results_dir"], exist_ok=True)

        # Initialize LLM
        self.llm = self._create_llm()

        # Initialize memories
        self.traditional_memory = BaziAnalysisMemory(
            "traditional_memory", self.config
        )
        self.psychology_memory = BaziAnalysisMemory(
            "psychology_memory", self.config
        )

        # Set up the graph
        self.graph = self._setup_graph()

        # State tracking
        self.curr_state = None

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "memory_dir": "./memory",
            "results_dir": "./results",
            "max_debate_rounds": 3,
            "prompt_version": os.environ.get("PROMPT_VERSION", "phase2-prompt-v1"),
            "quality_min_score": float(os.environ.get("QUALITY_MIN_SCORE", "70")),
            "quality_rewrite_enabled": os.environ.get("QUALITY_REWRITE_ENABLED", "false"),
            "quality_llm_judge_enabled": os.environ.get("QUALITY_LLM_JUDGE_ENABLED", "false"),
        }

    def _create_llm(self):
        """Create LLM client."""
        import os

        # Import here to avoid issues if dependencies are not available
        try:
            from langchain_openai import ChatOpenAI

            if self.llm_provider == "siliconflow":
                api_key = self.api_key or os.environ.get("SILICONFLOW_API_KEY") or os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("SILICONFLOW_API_KEY or OPENAI_API_KEY environment variable is required")
                return ChatOpenAI(
                    model=self.llm_model,
                    base_url=self.base_url or "https://api.siliconflow.cn/v1",
                    temperature=0.7,
                    api_key=api_key,
                )
            elif self.llm_provider == "openai":
                api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable is required")
                return ChatOpenAI(
                    model=self.llm_model,
                    temperature=0.7,
                    api_key=api_key,
                )
            elif self.llm_provider == "anthropic":
                from langchain_anthropic import ChatAnthropic

                api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY environment variable is required")
                return ChatAnthropic(
                    model=self.llm_model,
                    temperature=0.7,
                    api_key=api_key,
                )
            else:
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")
        except ImportError as e:
            print(f"Error importing LLM library: {e}")
            print("Please install required dependencies: pip install langchain-openai langchain-anthropic")
            raise

    def _setup_graph(self):
        """Set up the Bazi analysis graph."""
        workflow = StateGraph(BaziAnalysisState)

        # Add nodes
        workflow.add_node("chart_calculator", create_chart_calculator(self.llm))
        workflow.add_node("day_master_analyst", create_day_master_analyst(self.llm))
        workflow.add_node("ten_gods_analyst", create_ten_gods_analyst(self.llm))
        workflow.add_node("pattern_analyst", create_pattern_analyst(self.llm))
        workflow.add_node("useful_god_analyst", create_useful_god_analyst(self.llm))
        workflow.add_node("luck_cycle_analyst", create_luck_cycle_analyst(self.llm))
        workflow.add_node(
            "traditional_analyst",
            create_traditional_analyst(self.llm, self.traditional_memory),
        )
        workflow.add_node(
            "psychology_analyst",
            create_psychology_analyst(self.llm, self.psychology_memory),
        )
        workflow.add_node("comprehensive_analyst", create_comprehensive_analyst(self.llm))

        # Define edges
        workflow.set_entry_point("chart_calculator")

        # Analysis pipeline
        workflow.add_edge("chart_calculator", "day_master_analyst")
        workflow.add_edge("day_master_analyst", "ten_gods_analyst")
        workflow.add_edge("ten_gods_analyst", "pattern_analyst")
        workflow.add_edge("pattern_analyst", "useful_god_analyst")
        workflow.add_edge("useful_god_analyst", "luck_cycle_analyst")

        # Debate phase
        workflow.add_edge("luck_cycle_analyst", "traditional_analyst")
        workflow.add_edge("traditional_analyst", "psychology_analyst")

        # Conditional routing for debate rounds
        workflow.add_conditional_edges(
            "psychology_analyst",
            self._should_continue_debate,
            {
                "continue": "traditional_analyst",
                "end": "comprehensive_analyst",
            },
        )

        # End
        workflow.add_edge("comprehensive_analyst", END)

        return workflow.compile()

    def _should_continue_debate(self, state: BaziAnalysisState) -> str:
        """Determine if debate should continue."""
        debate_count = state["bazi_debate_state"]["count"]
        max_rounds = self.config.get("max_debate_rounds", 3)

        if debate_count >= max_rounds * 2:  # Each round has 2 responses
            return "end"
        else:
            return "continue"

    def analyze(
        self,
        birth_info: str,
        analysis_date: str = None,
        analysis_datetime: str = None,
        progress_callback: Optional[Callable[[str, str, dict], None]] = None,
        case_metadata: Optional[Dict[str, Any]] = None,
    ):
        """Run the Bazi analysis.

        Args:
            birth_info: Birth information (year, month, day, hour, gender)
            analysis_date: Date of analysis (default: today)
            analysis_datetime: Current analysis timestamp (default: now)
            progress_callback: Optional callback receiving stage, message, state
            case_metadata: Optional metadata stored with the result log

        Returns:
            Tuple of (final_state, final_analysis)
        """
        if analysis_date is None:
            analysis_date = current_analysis_date()
        analysis_datetime = normalize_analysis_datetime(analysis_date, analysis_datetime)

        # Initialize state
        init_state = {
            "birth_info": birth_info,
            "analysis_date": analysis_date,
            "analysis_datetime": analysis_datetime,
            "sender": "user",
            "chart_report": "",
            "day_master_report": "",
            "ten_gods_report": "",
            "pattern_report": "",
            "useful_god_report": "",
            "luck_cycle_report": "",
            "bazi_debate_state": {
                "traditional_history": "",
                "psychology_history": "",
                "history": "",
                "current_response": "",
                "judge_decision": "",
                "count": 0,
            },
            "interpretation_plan": "",
            "psychology_translation": "",
            "final_analysis": "",
            "messages": [],
        }

        # Run the graph
        if self.debug or progress_callback is not None:
            # Debug mode with tracing. Use full state snapshots instead of node updates
            # so the final state still contains fields such as chart_report.
            trace = []
            emitted_stages = set()
            for chunk in self.graph.stream(init_state, stream_mode="values"):
                if self.debug:
                    print(f"Node: {chunk}")
                self._emit_progress(progress_callback, chunk, emitted_stages)
                trace.append(chunk)

            final_state = trace[-1] if trace else init_state
        else:
            # Standard mode
            final_state = self.graph.invoke(init_state)

        # Store current state
        final_state = self._attach_quality_report(final_state)
        final_state["visualization_data"] = build_visualization_data(final_state)
        self.curr_state = final_state

        # Log state
        self._log_state(birth_info, analysis_date, analysis_datetime, final_state, case_metadata)

        # Return final state and analysis
        return final_state, final_state["final_analysis"]

    def _emit_progress(self, progress_callback, state: dict, emitted_stages: set):
        """Emit coarse-grained progress updates for UI callers."""
        if progress_callback is None:
            return

        stage_checks = [
            ("chart_report", "排盘", "命盘计算完成"),
            ("day_master_report", "日主分析", "日主分析完成"),
            ("ten_gods_report", "十神分析", "十神分析完成"),
            ("pattern_report", "格局分析", "格局分析完成"),
            ("useful_god_report", "用神分析", "用神分析完成"),
            ("luck_cycle_report", "大运分析", "大运分析完成"),
            ("final_analysis", "综合分析", "综合分析完成"),
        ]
        for field, stage, message in stage_checks:
            if state.get(field) and stage not in emitted_stages:
                progress_callback(stage, message, state)
                emitted_stages.add(stage)

        debate_state = state.get("bazi_debate_state") or {}
        debate_count = debate_state.get("count", 0)
        debate_stage = f"传统/心理辩论-{debate_count}"
        if debate_count and debate_stage not in emitted_stages:
            progress_callback("传统/心理辩论", f"辩论轮次更新: {debate_count}", state)
            emitted_stages.add(debate_stage)

    def _attach_quality_report(self, final_state: dict) -> dict:
        """Evaluate final analysis quality and optionally trigger one rewrite."""
        quality_report = evaluate_analysis_quality(
            final_state.get("final_analysis", ""),
            final_state,
            self.config,
        )
        final_state["quality_report"] = quality_report

        if not should_rewrite(quality_report, self.config):
            return final_state

        try:
            rewrite_prompt = build_rewrite_prompt(
                final_state.get("final_analysis", ""),
                quality_report,
            )
            response = self.llm.invoke(rewrite_prompt)
            final_state["final_analysis"] = response.content
            final_state["quality_report"] = evaluate_analysis_quality(
                final_state.get("final_analysis", ""),
                final_state,
                self.config,
            )
            final_state["quality_report"]["rewrite_triggered"] = True
        except Exception as exc:
            final_state["quality_report"]["rewrite_triggered"] = False
            final_state["quality_report"]["rewrite_error"] = "模型重写失败"
        return final_state

    def _log_state(
        self,
        birth_info: str,
        analysis_date: str,
        analysis_datetime: str,
        final_state: dict,
        case_metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log the final state to a JSON file."""
        case_metadata = case_metadata or {}
        log_data = {
            "birth_info": birth_info,
            "analysis_date": analysis_date,
            "analysis_datetime": analysis_datetime,
            "user_id": case_metadata.get("user_id", ""),
            "username": case_metadata.get("username", ""),
            "focus_topics": case_metadata.get("focus_topics", []),
            "display_name": case_metadata.get("display_name", ""),
            "allow_record": case_metadata.get("allow_record", True),
            "prompt_version": self.config.get("prompt_version", "phase2-prompt-v1"),
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "chart_report": final_state["chart_report"],
            "day_master_report": final_state["day_master_report"],
            "ten_gods_report": final_state["ten_gods_report"],
            "pattern_report": final_state["pattern_report"],
            "useful_god_report": final_state["useful_god_report"],
            "luck_cycle_report": final_state["luck_cycle_report"],
            "bazi_debate_state": {
                "traditional_history": final_state["bazi_debate_state"][
                    "traditional_history"
                ],
                "psychology_history": final_state["bazi_debate_state"][
                    "psychology_history"
                ],
                "history": final_state["bazi_debate_state"]["history"],
                "count": final_state["bazi_debate_state"]["count"],
            },
            "final_analysis": final_state["final_analysis"],
            "quality_report": final_state.get("quality_report"),
            "visualization_data": final_state.get("visualization_data"),
        }

        # Save to file
        results_dir = Path(self.config["results_dir"])
        results_dir.mkdir(parents=True, exist_ok=True)

        # Create filename based on birth info (simplified)
        safe_birth_info = "".join(
            c for c in birth_info if c.isalnum() or c in (" ", "-", "_")
        ).replace(" ", "_")[:50]
        log_path = results_dir / f"bazi_analysis_{safe_birth_info}_{analysis_date}.json"

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        print(f"Analysis saved to: {log_path}")
