"""Security checks for the visitor-funded model flow."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from bazi_graph import BaziAnalysisGraph
from utils.public_access import PROVIDERS, analysis_slot, validate_request


def test_provider_and_input_bounds():
    validate_request("siliconflow", "visitor-key", "出生日期: 1990-01-01")
    for provider, key, birth in (
        ("custom", "visitor-key", "1990-01-01"),
        ("siliconflow", "", "1990-01-01"),
        ("siliconflow", "visitor-key", "a" * 701),
    ):
        try:
            validate_request(provider, key, birth)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid public request accepted")


def test_explicit_key_reaches_only_selected_client():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"memory_dir": tmpdir + "/memory", "results_dir": tmpdir + "/results", "embedding_enabled": False}
        with patch("langchain_openai.ChatOpenAI") as client, patch.object(BaziAnalysisGraph, "_setup_graph"):
            graph = BaziAnalysisGraph(config=config, llm_provider="siliconflow", llm_model=PROVIDERS["siliconflow"][1], base_url=PROVIDERS["siliconflow"][2], api_key="visitor-key")
            client.assert_called_once()
            assert client.call_args.kwargs["api_key"] == "visitor-key"
            assert client.call_args.kwargs["base_url"] == PROVIDERS["siliconflow"][2]
            assert graph.api_key == "visitor-key"


def test_rate_limit():
    for _ in range(6):
        with analysis_slot("rate-test-user"):
            pass
    try:
        with analysis_slot("rate-test-user"):
            pass
    except ValueError:
        pass
    else:
        raise AssertionError("per-user limit was not enforced")


def test_saved_report_does_not_contain_key():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"memory_dir": tmpdir + "/memory", "results_dir": tmpdir + "/results", "embedding_enabled": False}
        with patch("langchain_openai.ChatOpenAI"), patch.object(BaziAnalysisGraph, "_setup_graph"):
            graph = BaziAnalysisGraph(config=config, api_key="visitor-key")
        state = {name: "" for name in (
            "chart_report", "day_master_report", "ten_gods_report", "pattern_report",
            "useful_god_report", "luck_cycle_report", "final_analysis"
        )}
        state["bazi_debate_state"] = {name: "" for name in ("traditional_history", "psychology_history", "history")}
        state["bazi_debate_state"]["count"] = 0
        graph._log_state("1990-01-01", "2026-10-09", "2026-10-09T12:00:00", state)
        saved = next(Path(config["results_dir"]).glob("*.json")).read_text(encoding="utf-8")
        assert "visitor-key" not in saved


if __name__ == "__main__":
    test_provider_and_input_bounds()
    test_explicit_key_reaches_only_selected_client()
    test_rate_limit()
    test_saved_report_does_not_contain_key()
    print("public access checks OK")
