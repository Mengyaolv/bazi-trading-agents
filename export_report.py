#!/usr/bin/env python3
"""Export a saved Bazi analysis JSON report."""

import argparse
import json
from pathlib import Path

from utils.exporter import export_report, normalize_export_formats


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a saved Bazi analysis JSON report.")
    parser.add_argument("input_json", help="Saved analysis JSON file")
    parser.add_argument("--output-dir", default="./exports", help="Directory for exported reports")
    parser.add_argument(
        "--formats",
        default="markdown,json",
        help="Comma-separated formats: markdown,json,word,pdf",
    )
    parser.add_argument(
        "--mode",
        choices=["simple", "professional"],
        default="simple",
        help="Export mode",
    )
    parser.add_argument("--case-id", default="", help="Optional case id for filename and cover")
    parser.add_argument(
        "--font-path",
        default=None,
        help="Chinese font path for PDF export, or set EXPORT_CHINESE_FONT_PATH",
    )
    args = parser.parse_args()

    input_path = Path(args.input_json)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    result = export_report(
        payload,
        output_dir=args.output_dir,
        formats=normalize_export_formats(args.formats),
        case_id=args.case_id,
        mode=args.mode,
        font_path=args.font_path,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
