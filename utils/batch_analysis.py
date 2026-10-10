"""Batch analysis helpers for Bazi Trading Agents."""

import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from utils.exporter import export_report, normalize_export_formats
from utils.time_utils import current_analysis_date
from utils.web_support import build_birth_info, sanitize_error


BatchProgressCallback = Callable[[Dict[str, Any]], None]


def load_batch_cases(input_path: str) -> List[Dict[str, Any]]:
    """Load batch cases from CSV or JSONL."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Batch input file not found: {input_path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    elif suffix == ".jsonl":
        rows = []
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    rows.append(json.loads(stripped))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at line {line_no}: {exc}") from exc
    else:
        raise ValueError("Batch input must be a .csv or .jsonl file")

    cases = []
    for index, row in enumerate(rows, 1):
        case = normalize_batch_case(row, index)
        cases.append(case)
    return cases


def normalize_batch_case(row: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Normalize one batch row and build birth_info if needed."""
    case_id = str(row.get("id") or "").strip()
    if not case_id:
        raise ValueError(f"Case at row {index} is missing required field: id")

    birth_info = build_birth_info(
        free_text=str(row.get("birth_info") or ""),
        birth_date=row.get("birth_date") or "",
        birth_time=row.get("birth_time") or "",
        gender=row.get("gender") or "",
        birth_place=row.get("birth_place") or "",
        calendar_type=row.get("calendar_type") or "",
        notes=row.get("notes") or "",
    )
    if not birth_info:
        raise ValueError(f"Case {case_id} is missing required field: birth_info")

    return {
        "id": case_id,
        "name": row.get("name") or "",
        "birth_info": birth_info,
        "output_language": row.get("output_language") or "中文",
        "metadata": dict(row),
    }


def safe_case_id(case_id: str) -> str:
    """Return a filesystem-safe case id."""
    cleaned = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff_-]+", "_", str(case_id)).strip("_")
    return cleaned[:80] or "case"


class BatchAnalysisRunner:
    """Sequential batch runner with failure isolation."""

    def __init__(
        self,
        input_path: str,
        output_dir: str = "./batch_results",
        debug: bool = False,
        skip_completed: bool = True,
        retries: int = 0,
        analysis_date: Optional[str] = None,
        graph_factory: Optional[Callable[..., Any]] = None,
        progress_callback: Optional[BatchProgressCallback] = None,
        export_formats: Optional[List[str]] = None,
        export_mode: str = "simple",
        export_font_path: Optional[str] = None,
    ) -> None:
        self.input_path = input_path
        self.output_dir = Path(output_dir)
        self.cases_dir = self.output_dir / "cases"
        self.exports_dir = self.output_dir / "exports"
        self.debug = debug
        self.skip_completed = skip_completed
        self.retries = max(int(retries), 0)
        self.analysis_date = analysis_date or current_analysis_date()
        self.graph_factory = graph_factory or self._default_graph_factory
        self.progress_callback = progress_callback
        self.export_formats = normalize_export_formats(export_formats) if export_formats else []
        self.export_mode = export_mode
        self.export_font_path = export_font_path

    def run(self) -> Dict[str, Any]:
        """Run the batch and write per-case results plus summary files."""
        cases = load_batch_cases(self.input_path)
        self.cases_dir.mkdir(parents=True, exist_ok=True)

        records = []
        total = len(cases)
        for position, case in enumerate(cases, 1):
            self._emit("running", total, position, case)
            record = self._run_case(case)
            records.append(record)
            self._emit(record["status"], total, position, case, record)

        summary = self._build_summary(records)
        self._write_summary(records)
        return summary

    def _run_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        result_path = self.cases_dir / f"{safe_case_id(case['id'])}.json"
        base_record = {
            "id": case["id"],
            "name": case.get("name", ""),
            "birth_info": case["birth_info"],
            "analysis_date": self.analysis_date,
            "output_path": str(result_path),
            "export_paths": "",
            "export_errors": "",
            "quality_score": "",
            "error": "",
        }

        if self.skip_completed and result_path.exists():
            quality_score = self._read_quality_score(result_path)
            export_result = self._export_existing_case(case, result_path)
            return {
                **base_record,
                "status": "skipped",
                "quality_score": quality_score if quality_score is not None else "",
                "export_paths": self._json_for_summary(export_result.get("paths", {})),
                "export_errors": self._json_for_summary(export_result.get("errors", {})),
            }

        last_error = ""
        for attempt in range(self.retries + 1):
            try:
                graph = self.graph_factory(debug=self.debug, results_dir=str(self.cases_dir))
                final_state, final_analysis = graph.analyze(
                    case["birth_info"],
                    analysis_date=self.analysis_date,
                )
                payload = {
                    "id": case["id"],
                    "name": case.get("name", ""),
                    "birth_info": case["birth_info"],
                    "analysis_date": self.analysis_date,
                    "final_analysis": final_analysis,
                    "final_state": final_state,
                    "quality_report": final_state.get("quality_report"),
                    "metadata": case.get("metadata", {}),
                    "completed_at": datetime.now().isoformat(),
                }
                result_path.write_text(
                    json.dumps(payload, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                export_result = self._export_case_report(case, payload)
                return {
                    **base_record,
                    "status": "success",
                    "quality_score": self._quality_score(final_state.get("quality_report")),
                    "attempts": attempt + 1,
                    "export_paths": self._json_for_summary(export_result.get("paths", {})),
                    "export_errors": self._json_for_summary(export_result.get("errors", {})),
                }
            except Exception as exc:
                last_error = sanitize_error(exc)

        return {
            **base_record,
            "status": "failed",
            "attempts": self.retries + 1,
            "error": last_error,
        }

    def _default_graph_factory(self, debug: bool = False, results_dir: str = ""):
        from bazi_graph import BaziAnalysisGraph

        config = {
            "memory_dir": os.environ.get("MEMORY_DIR", "./memory"),
            "results_dir": results_dir or str(self.cases_dir),
            "max_debate_rounds": int(os.environ.get("MAX_DEBATE_ROUNDS", "3")),
        }
        return BaziAnalysisGraph(debug=debug, config=config)

    def _build_summary(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "total": len(records),
            "success": sum(1 for item in records if item["status"] == "success"),
            "failed": sum(1 for item in records if item["status"] == "failed"),
            "skipped": sum(1 for item in records if item["status"] == "skipped"),
            "output_dir": str(self.output_dir),
            "summary_csv": str(self.output_dir / "batch_summary.csv"),
            "summary_jsonl": str(self.output_dir / "batch_summary.jsonl"),
            "records": records,
        }

    def _write_summary(self, records: List[Dict[str, Any]]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "id",
            "name",
            "status",
            "analysis_date",
            "quality_score",
            "output_path",
            "export_paths",
            "export_errors",
            "error",
            "birth_info",
        ]
        with open(self.output_dir / "batch_summary.csv", "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow({key: record.get(key, "") for key in fieldnames})

        with open(self.output_dir / "batch_summary.jsonl", "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _emit(
        self,
        status: str,
        total: int,
        position: int,
        case: Dict[str, Any],
        record: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.progress_callback is None:
            return
        self.progress_callback(
            {
                "status": status,
                "total": total,
                "position": position,
                "case_id": case.get("id"),
                "record": record,
            }
        )

    def _read_quality_score(self, result_path: Path):
        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
        except Exception:
            return None
        return self._quality_score(payload.get("quality_report"))

    def _quality_score(self, quality_report: Any):
        if isinstance(quality_report, dict):
            return quality_report.get("overall_score", "")
        return ""

    def _export_existing_case(self, case: Dict[str, Any], result_path: Path) -> Dict[str, Dict[str, str]]:
        if not self.export_formats:
            return {"paths": {}, "errors": {}}
        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {"paths": {}, "errors": {"json": sanitize_error(exc)}}
        return self._export_case_report(case, payload)

    def _export_case_report(self, case: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        if not self.export_formats:
            return {"paths": {}, "errors": {}}
        try:
            return export_report(
                payload,
                output_dir=str(self.exports_dir / safe_case_id(case["id"])),
                formats=self.export_formats,
                case_id=case["id"],
                mode=self.export_mode,
                font_path=self.export_font_path,
            )
        except Exception as exc:
            return {"paths": {}, "errors": {"export": sanitize_error(exc)}}

    def _json_for_summary(self, value: Dict[str, Any]) -> str:
        return json.dumps(value, ensure_ascii=False) if value else ""
