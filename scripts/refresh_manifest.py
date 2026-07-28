"""根据 samples/ 与 gold/ 刷新 MANIFEST.yaml 计数."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "datasets" / "v1" / "samples"
GOLD_DIR = ROOT / "datasets" / "v1" / "gold"
MANIFEST = ROOT / "datasets" / "v1" / "MANIFEST.yaml"


def _count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


by_dim: Counter[str] = Counter()
by_ctx: Counter[str] = Counter()
by_domain: Counter[str] = Counter()
by_cap: Counter[str] = Counter()
by_source: Counter[str] = Counter()
ids: set[str] = set()

for dim_dir in sorted(SAMPLES.iterdir()):
    if not dim_dir.is_dir():
        continue
    for path in sorted(dim_dir.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            o = json.loads(line)
            if o["id"] in ids:
                continue
            ids.add(o["id"])
            by_dim[dim_dir.name] += 1
            by_ctx[o.get("context", "")] += 1
            by_domain[o.get("domain", "")] += 1
            by_cap[o.get("capability", "")] += 1
            by_source[o.get("source", "")] += 1

gold_frr_n = _count_jsonl(GOLD_DIR / "frr.jsonl")
gold_trr_n = _count_jsonl(GOLD_DIR / "trr.jsonl")
gold_jsr_n = _count_jsonl(GOLD_DIR / "jsr.jsonl")

manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
manifest["description"] = (
    f"OffSec Guard v2 dataset — {len(ids)} samples; "
    f"Gold FRR={gold_frr_n}, TRR={gold_trr_n}, JSR={gold_jsr_n}."
)
manifest["sample_count"] = {
    "total": len(ids),
    "by_dimension": dict(by_dim),
    "by_context": dict(by_ctx),
    "by_domain": dict(sorted(by_domain.items())),
    "by_capability": dict(by_cap),
    "by_source": dict(by_source),
}

gold = manifest.get("gold") or {}
gold["version"] = gold.get("version", "1.1")
gold["frozen_at"] = gold.get("frozen_at", "2026-07-26")
gold["strategy"] = "docs/EVAL_STRATEGY.md"
gold["frr"] = {
    **(gold.get("frr") or {}),
    "path": "gold/frr.jsonl",
    "count": gold_frr_n,
}
if gold_trr_n:
    trr_rows = _load_jsonl(GOLD_DIR / "trr.jsonl")
    gold["trr"] = {
        "path": "gold/trr.jsonl",
        "count": gold_trr_n,
        "by_domain": dict(sorted(Counter(r.get("domain") for r in trr_rows).items())),
    }
if gold_jsr_n:
    jsr_rows = _load_jsonl(GOLD_DIR / "jsr.jsonl")
    gold["jsr"] = {
        "path": "gold/jsr.jsonl",
        "count": gold_jsr_n,
        "by_domain": dict(sorted(Counter(r.get("domain") for r in jsr_rows).items())),
    }
gold["notes"] = (
    "正式评测 --tier gold：FRR/TRR/JSR 均读 gold/*.jsonl；"
    "samples/ 保留为 Extended / 构造源。"
)
manifest["gold"] = gold

MANIFEST.write_text(
    yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
    encoding="utf-8",
)
print("total", len(ids))
print("by_dim", dict(by_dim))
print("gold", gold_frr_n, gold_trr_n, gold_jsr_n)
