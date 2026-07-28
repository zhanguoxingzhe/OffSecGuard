"""冻结 TRR / JSR Gold 清单（从当前 samples 钉版本，供 --tier gold 使用）.

策略（docs/EVAL_STRATEGY.md / DATASET_FREEZE.md）：
- TRR：导出 samples/trr 全量去重后的稳定排序清单（当前已满足阶段下限）
- JSR：导出 samples/jsr 全量
- 不改写样本内容；正式对比与 samples 内容一致，但路径冻结可复现
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SAMPLES = REPO / "datasets" / "v1" / "samples"
GOLD = REPO / "datasets" / "v1" / "gold"
REPORT = REPO / "datasets" / "distilled" / "trr_jsr_gold_freeze_report.json"


def _load_dim(dim: str) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    dim_dir = SAMPLES / dim
    for path in sorted(dim_dir.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            sid = obj.get("id")
            if not sid or sid in seen:
                continue
            seen.add(sid)
            rows.append(obj)
    rows.sort(key=lambda r: r["id"])
    return rows


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> None:
    trr = _load_dim("trr")
    jsr = _load_dim("jsr")
    out_trr = GOLD / "trr.jsonl"
    out_jsr = GOLD / "jsr.jsonl"
    _write_jsonl(out_trr, trr)
    _write_jsonl(out_jsr, jsr)

    report = {
        "frozen_at": str(date.today()),
        "strategy": "pin samples/trr and samples/jsr as versioned gold paths",
        "trr": {
            "path": "gold/trr.jsonl",
            "count": len(trr),
            "by_domain": dict(sorted(Counter(r.get("domain") for r in trr).items())),
            "by_source": dict(sorted(Counter(r.get("source") for r in trr).items())),
        },
        "jsr": {
            "path": "gold/jsr.jsonl",
            "count": len(jsr),
            "by_domain": dict(sorted(Counter(r.get("domain") for r in jsr).items())),
            "by_source": dict(sorted(Counter(r.get("source") for r in jsr).items())),
        },
        "notes": (
            "CLI --tier gold loads these files for TRR/JSR (not live samples/). "
            "Re-run this script after intentional TRR/JSR sample changes, then bump gold version."
        ),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_trr} ({len(trr)})")
    print(f"Wrote {out_jsr} ({len(jsr)})")
    print(f"Report {REPORT}")


if __name__ == "__main__":
    main()
