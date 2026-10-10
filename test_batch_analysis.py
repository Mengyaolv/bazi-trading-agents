#!/usr/bin/env python3
"""Mock checks for batch analysis without calling real APIs."""

import csv
import json
import tempfile
from pathlib import Path

from utils.batch_analysis import BatchAnalysisRunner, load_batch_cases


class FakeGraph:
    def __init__(self, fail_on=None):
        self.fail_on = fail_on or set()

    def analyze(self, birth_info, analysis_date=None):
        if birth_info in self.fail_on:
            raise RuntimeError("fake failure sk-abcdefghijklmnopqrstuvwxyz")
        state = {
            "final_analysis": f"analysis for {birth_info}",
            "quality_report": {"overall_score": 88},
        }
        return state, state["final_analysis"]


def test_load_csv_and_jsonl():
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "cases.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "birth_info"])
            writer.writeheader()
            writer.writerow({"id": "a", "birth_info": "birth a"})
        assert load_batch_cases(str(csv_path))[0]["birth_info"] == "birth a"

        jsonl_path = Path(tmpdir) / "cases.jsonl"
        jsonl_path.write_text('{"id":"b","birth_info":"birth b"}\n', encoding="utf-8")
        assert load_batch_cases(str(jsonl_path))[0]["id"] == "b"


def test_batch_run_success_failure_and_skip():
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "cases.csv"
        with open(input_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "birth_info"])
            writer.writeheader()
            for i in range(5):
                writer.writerow({"id": f"case-{i}", "birth_info": "bad" if i == 2 else f"birth-{i}"})

        def factory(debug=False, results_dir=""):
            return FakeGraph(fail_on={"bad"})

        output_dir = Path(tmpdir) / "out"
        runner = BatchAnalysisRunner(
            str(input_path),
            output_dir=str(output_dir),
            graph_factory=factory,
            analysis_date="2026-06-28",
            export_formats=["markdown", "json"],
            export_mode="professional",
        )
        summary = runner.run()
        assert summary["total"] == 5
        assert summary["success"] == 4
        assert summary["failed"] == 1
        assert (output_dir / "batch_summary.csv").exists()
        assert (output_dir / "batch_summary.jsonl").exists()
        assert len(list((output_dir / "cases").glob("*.json"))) == 4
        success_records = [item for item in summary["records"] if item["status"] == "success"]
        for record in success_records:
            export_paths = json.loads(record["export_paths"])
            assert Path(export_paths["markdown"]).exists()
            assert Path(export_paths["json"]).exists()
        failed = [item for item in summary["records"] if item["status"] == "failed"][0]
        assert "sk-" not in failed["error"]
        assert "***" in failed["error"]

        skipped = BatchAnalysisRunner(
            str(input_path),
            output_dir=str(output_dir),
            graph_factory=factory,
            analysis_date="2026-06-28",
            export_formats=["markdown"],
        ).run()
        assert skipped["skipped"] == 4
        assert skipped["failed"] == 1
        skipped_records = [item for item in skipped["records"] if item["status"] == "skipped"]
        for record in skipped_records:
            export_paths = json.loads(record["export_paths"])
            assert Path(export_paths["markdown"]).exists()


if __name__ == "__main__":
    test_load_csv_and_jsonl()
    test_batch_run_success_failure_and_skip()
    print("batch analysis checks OK")
