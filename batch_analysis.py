#!/usr/bin/env python3
"""Run batch Bazi analysis from CSV or JSONL input."""

import argparse
import json

from utils.batch_analysis import BatchAnalysisRunner


def main():
    parser = argparse.ArgumentParser(description="Run batch Bazi analysis.")
    parser.add_argument("input_path", help="CSV or JSONL file containing batch cases")
    parser.add_argument("--output-dir", default="./batch_results", help="Batch output directory")
    parser.add_argument("--debug", action="store_true", help="Enable graph debug mode")
    parser.add_argument("--no-skip", action="store_true", help="Do not skip existing case outputs")
    parser.add_argument("--retries", type=int, default=0, help="Retry count per failed case")
    parser.add_argument("--analysis-date", default=None, help="Analysis date in YYYY-MM-DD")
    parser.add_argument(
        "--export-formats",
        default="",
        help="Optional comma-separated export formats: markdown,json,word,pdf",
    )
    parser.add_argument(
        "--export-mode",
        choices=["simple", "professional"],
        default="simple",
        help="Export report mode",
    )
    parser.add_argument(
        "--export-font-path",
        default=None,
        help="Chinese font path for PDF export, or set EXPORT_CHINESE_FONT_PATH",
    )
    args = parser.parse_args()

    def progress(event):
        print(f"[{event['position']}/{event['total']}] {event['case_id']}: {event['status']}")

    runner = BatchAnalysisRunner(
        input_path=args.input_path,
        output_dir=args.output_dir,
        debug=args.debug,
        skip_completed=not args.no_skip,
        retries=args.retries,
        analysis_date=args.analysis_date,
        progress_callback=progress,
        export_formats=args.export_formats.split(",") if args.export_formats else None,
        export_mode=args.export_mode,
        export_font_path=args.export_font_path,
    )
    summary = runner.run()
    print(json.dumps({key: value for key, value in summary.items() if key != "records"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
