"""JSON report generator."""

from __future__ import annotations

import json
from pathlib import Path

from offsec_guard.core.models import EvalReport


class JSONReporter:
    """JSON-format report."""

    @staticmethod
    def render(report: EvalReport, *, include_samples: bool = False) -> str:
        """By default omit per-sample rows from summary (too large / write-risk); see sample_results.json."""
        data = report._serialize()
        counts = {k: len(v) for k, v in (data.get("sample_results") or {}).items()}
        if not include_samples:
            data["sample_results"] = {}
            data["sample_results_counts"] = counts
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def render_sample_results(report: EvalReport) -> str:
        """Serialize per-sample results only, for separate archive/analysis."""
        payload = report._serialize().get("sample_results", {})
        return json.dumps(
            {
                "eval_id": report.eval_id,
                "model": {
                    "provider": report.model.provider,
                    "model_id": report.model.model_id,
                    "display_name": report.model.display_name,
                },
                "sample_results": payload,
            },
            ensure_ascii=False,
            indent=2,
        )

    @staticmethod
    def save(report: EvalReport, path: str | Path, *, include_samples: bool = False) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            JSONReporter.render(report, include_samples=include_samples),
            encoding="utf-8",
        )
        return p
