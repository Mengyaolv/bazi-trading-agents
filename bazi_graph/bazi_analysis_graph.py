import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, List, Optional

from langgraph.graph import StateGraph, END

from utils.bazi_states import BaziAnalysisState, BaziDebateState
from bazi_agents import *


class BaziAnalysisGraph:
    """Main class that orchestrates the Bazi analysis agents framework."""

    def __init__(
        self,
        debug=False,
        config: Dict[str, Any] = None,
        llm_provider: str = "siliconflow",
        llm_model: str = "deepseek-ai/DeepSeek-V3",
        base_url: str = None,
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
        self.config = config or self._get_default_config()
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.base_url = base_url

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
        }

    def _create_llm(self):
        """Create LLM client."""
        # Import here to avoid issues if dependencies are not available
        try:
            from langchain_openai import ChatOpenAI

            if self.llm_provider == "siliconflow":
                return ChatOpenAI(
                    model=self.llm_model,
                    base_url=self.base_url or "https://api.siliconflow.cn/v1",
                    temperature=0.7,
                )
            elif self.llm_provider == "openai":
                return ChatOpenAI(
                    model=self.llm_model,
                    temperature=0.7,
                )
            elif self.llm_provider == "anthropic":
                from langchain_anthropic import ChatAnthropic

                return ChatAnthropic(
                    model=self.llm_model,
                    temperature=0.7,
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

    def analyze(self, birth_info: str, analysis_date: str = None):
        """Run the Bazi analysis.

        Args:
            birth_info: Birth information (year, month, day, hour, gender)
            analysis_date: Date of analysis (default: today)

        Returns:
            Tuple of (final_state, final_analysis)
        """
        if analysis_date is None:
            analysis_date = date.today().isoformat()

        # Initialize state
        init_state = {
            "birth_info": birth_info,
            "analysis_date": analysis_date,
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
        if self.debug:
            # Debug mode with tracing
            trace = []
            for chunk in self.graph.stream(init_state):
                if self.debug:
                    print(f"Node: {chunk}")
                trace.append(chunk)

            final_state = trace[-1]
        else:
            # Standard mode
            final_state = self.graph.invoke(init_state)

        # Store current state
        self.curr_state = final_state

        # Log state
        self._log_state(birth_info, analysis_date, final_state)

        # Return final state and analysis
        return final_state, final_state["final_analysis"]

    def _log_state(self, birth_info: str, analysis_date: str, final_state: dict):
        """Log the final state to a JSON file."""
        log_data = {
            "birth_info": birth_info,
            "analysis_date": analysis_date,
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
