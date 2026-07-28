"""冻结 Capability Gold（仅 teacher_status=calibrated）。

来源：
  - datasets/v1/samples/capability/teacher_gapfill.jsonl
  - datasets/v1/samples/capability/llm_calibrated_batch.jsonl（仅 calibrated）

产出：
  - datasets/v1/gold/capability_tsr.jsonl
  - datasets/v1/gold/capability_oar.jsonl
  - datasets/v1/gold/capability_pqr.jsonl
  - datasets/v1/gold/capability.jsonl（合并）
  - datasets/distilled/capability_gold_freeze_report.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
CAP = REPO / "datasets" / "v1" / "samples" / "capability"
GOLD = REPO / "datasets" / "v1" / "gold"
REPORT = REPO / "datasets" / "distilled" / "capability_gold_freeze_report.json"


def _load(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(l)
        for l in path.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]


def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _norm_dim(dim: str | None) -> str:
    if dim == "pqr_seed":
        return "pqr"
    return dim or "tsr"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="cap-gold-v0.1")
    args = ap.parse_args()

    gap = _load(CAP / "teacher_gapfill.jsonl")
    llm = [
        r for r in _load(CAP / "llm_calibrated_batch.jsonl")
        if r.get("teacher_status") == "calibrated"
    ]
    # gapfill 优先
    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    for r in gap + llm:
        if r.get("teacher_status") != "calibrated":
            continue
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        row = dict(r)
        row["dim"] = _norm_dim(row.get("dim"))
        row["meta"] = {
            **(row.get("meta") or {}),
            "gold_version": args.version,
        }
        merged.append(row)

    by = {"tsr": [], "oar": [], "pqr": []}
    for r in merged:
        d = r["dim"]
        if d not in by:
            by.setdefault(d, [])
        if d in by:
            by[d].append(r)

    GOLD.mkdir(parents=True, exist_ok=True)
    _write(GOLD / "capability_tsr.jsonl", by["tsr"])
    _write(GOLD / "capability_oar.jsonl", by["oar"])
    _write(GOLD / "capability_pqr.jsonl", by["pqr"])
    _write(GOLD / "capability.jsonl", merged)

    tools = Counter(t["name"] for r in merged for t in (r.get("gold_tool_calls") or []))
    report = {
        "version": args.version,
        "n_total": len(merged),
        "by_dim": {k: len(v) for k, v in by.items()},
        "by_domain": dict(Counter(r.get("domain") for r in merged)),
        "by_source": dict(Counter(r.get("source") for r in merged)),
        "gold_tools": dict(tools.most_common()),
        "sources": {
            "teacher_gapfill": len(gap),
            "llm_calibrated_included": len(llm),
        },
        "paths": {
            "merged": str(GOLD / "capability.jsonl"),
            "tsr": str(GOLD / "capability_tsr.jsonl"),
            "oar": str(GOLD / "capability_oar.jsonl"),
            "pqr": str(GOLD / "capability_pqr.jsonl"),
        },
        "note": "Only teacher_status=calibrated. auto_rules / needs_human excluded.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
