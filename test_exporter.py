#!/usr/bin/env python3
"""Mock checks for report export without calling real APIs."""

import importlib.util
import json
import os
import tempfile
from pathlib import Path

from utils.exporter import (
    ETHICAL_STATEMENT,
    REQUIRED_SECTIONS,
    ExportDependencyError,
    build_export_filename,
    export_report,
    export_report_bytes,
    render_markdown_report,
)


FAKE_STATE = {
    "id": "case-001",
    "birth_info": "1990-09-05 08:00, male, Shanghai",
    "analysis_date": "2026-06-28",
    "chart_report": (
        "Year Pillar: \u7532\u5b50\n"
        "Month Pillar: \u4e59\u4e11\n"
        "Day Pillar: \u4e19\u5bc5\n"
        "Hour Pillar: \u4e01\u536f\n"
        "Day Master: \u4e19"
    ),
    "day_master_report": "\u65e5\u4e3b\u5206\u6790\u5185\u5bb9",
    "ten_gods_report": "\u5341\u795e\u5206\u6790\u5185\u5bb9",
    "pattern_report": "\u683c\u5c40\u5206\u6790\u5185\u5bb9",
    "useful_god_report": "\u7528\u795e\u5206\u6790\u5185\u5bb9",
    "luck_cycle_report": "10-19 \u7532\u5b50\n20-29 \u4e59\u4e11",
    "bazi_debate_state": {
        "traditional_history": "\u4f20\u7edf\u547d\u7406\u5206\u6790\u5185\u5bb9",
        "psychology_history": "\u73b0\u4ee3\u5fc3\u7406\u8f6c\u8bd1\u5185\u5bb9",
        "history": "\u8fa9\u8bba\u8bb0\u5f55",
        "count": 2,
    },
    "final_analysis": (
        "## \u547d\u76d8\u6458\u8981\n"
        "\u6d4b\u8bd5\u7efc\u5408\u62a5\u544a\n"
        "## \u884c\u52a8\u5efa\u8bae\n"
        "\u6bcf\u5468\u590d\u76d8\u4e00\u6b21\u3002"
    ),
    "quality_report": {
        "overall_score": 86,
        "dimension_scores": {"structure": 90, "ethics": 88},
    },
}


def test_markdown_contains_required_sections_and_ethics():
    markdown = render_markdown_report(FAKE_STATE, case_id="case-001", mode="professional")
    assert "# \u516b\u5b57\u7efc\u5408\u5206\u6790\u62a5\u544a" in markdown
    assert ETHICAL_STATEMENT in markdown
    for title in REQUIRED_SECTIONS:
        assert f"## {title}" in markdown
    assert "## \u6838\u5fc3\u56fe\u8868" in markdown
    assert "## Agent \u4e2d\u95f4\u62a5\u544a" in markdown
    assert "## \u8d28\u91cf\u8bc4\u5206" in markdown


def test_export_markdown_and_json_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = export_report(
            FAKE_STATE,
            output_dir=tmpdir,
            formats=["markdown", "json"],
            case_id="case/001",
            mode="professional",
        )
        assert result["errors"] == {}
        markdown_path = Path(result["paths"]["markdown"])
        json_path = Path(result["paths"]["json"])
        assert markdown_path.exists()
        assert json_path.exists()
        assert "\u4f26\u7406\u58f0\u660e" in markdown_path.read_text(encoding="utf-8")

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        assert payload["ethical_statement"] == ETHICAL_STATEMENT
        assert payload["quality_report"]["overall_score"] == 86
        assert "raw_state" in payload


def test_filename_is_safe():
    filename = build_export_filename(FAKE_STATE, case_id="case/001 test", ext="md")
    assert filename.startswith("bazi_analysis_case_001_test_2026-06-28")
    assert "/" not in filename
    simple = build_export_filename(FAKE_STATE, case_id="case/001 test", ext="md", mode="simple")
    professional = build_export_filename(FAKE_STATE, case_id="case/001 test", ext="md", mode="professional")
    assert simple != professional
    assert simple.endswith("_simple.md")
    assert professional.endswith("_professional.md")


def test_word_and_pdf_optional_dependencies_are_controlled():
    if importlib.util.find_spec("docx"):
        assert export_report_bytes(FAKE_STATE, "word").startswith(b"PK")
    else:
        try:
            export_report_bytes(FAKE_STATE, "word")
        except ExportDependencyError as exc:
            assert "python-docx" in str(exc)
        else:
            raise AssertionError("Word export should require python-docx when it is missing")

    old_font = os.environ.pop("EXPORT_CHINESE_FONT_PATH", None)
    try:
        try:
            data = export_report_bytes(FAKE_STATE, "pdf")
        except ExportDependencyError as exc:
            assert "reportlab" in str(exc) or "Chinese PDF export requires" in str(exc)
        else:
            assert data.startswith(b"%PDF")
    finally:
        if old_font is not None:
            os.environ["EXPORT_CHINESE_FONT_PATH"] = old_font


if __name__ == "__main__":
    test_markdown_contains_required_sections_and_ethics()
    test_export_markdown_and_json_files()
    test_filename_is_safe()
    test_word_and_pdf_optional_dependencies_are_controlled()
    print("export checks OK")
